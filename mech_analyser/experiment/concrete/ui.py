"""Chinese, single-specimen Qt workspace integrated with MechAnalyser plots."""
from dataclasses import asdict, replace
from pathlib import Path
import html
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QDialogButtonBox, QMessageBox,
    QFileDialog, QTabWidget, QSplitter, QScrollArea, QGroupBox, QHeaderView, QApplication,
    QListWidget, QListWidgetItem, QInputDialog, QGridLayout)
from mech_analyser.experiment.ui import PlotWidget as BasePlotWidget
from .data import (CHANNELS, LABELS, UNITS, ImportSettings, RawData, workbook_sheets,
                   sheet_preview, infer_columns, sheet_identity)
from .analyser import Analyser
from .phase import default_branch
from .collation import AXIAL, HOOP, SELECTED, FIT, MODE_LABELS, export_current
from .persistence import save_analysis, load_analysis, source_state, save_workspace, load_workspace
from .presentation import rich, parameter_text, band, arrow_x, poisson_html, clear_box, unpressurized
from .defaults import DEFAULT_METADATA, fill_defaults
from .import_check import compare_layout


class ChoiceField(QComboBox):
    def __init__(self, choices):
        super().__init__()
        self.addItem("请选择", "")
        for label, value in choices:
            self.addItem(label, value)
        self.addItem('自定义…', None)
        self._last_value = ''
        self.currentIndexChanged.connect(self._remember)
        self.activated.connect(self._custom)

    def _remember(self):
        if self.currentData() is not None:
            self._last_value = self.text()

    def _custom(self):
        if self.currentData() is not None:
            return
        value, ok = QInputDialog.getText(self, '自定义', '请输入数值或内容（时间可写“30分钟”或“2小时”）：', text=self._last_value)
        self.setText(value if ok and value.strip() else self._last_value)

    def text(self):
        return str(self.currentData() or "")

    def setText(self, text):
        text = str(text).strip()
        index = self.findData(text)
        if index < 0 and text:
            self.addItem(text + "（自定义）", text)
            index = self.count()-1
        self.setCurrentIndex(max(0, index))


class ConfiningPressureField(ChoiceField):
    def _custom(self):
        if self.currentData() is not None:
            return
        try:
            initial = float(self._last_value)
        except ValueError:
            initial = 2.5
        value, ok = QInputDialog.getDouble(self, '自定义围压', '围压压强 (MPa)：',
                                         initial, 0, 1000000, 6)
        self.setText(f'{value:g}' if ok else self._last_value)


class ImportDialog(QDialog):
    """Choose a sheet before reading its cells; only explicit units are proposed."""
    def __init__(self, path, parent=None, preset=None):
        super().__init__(parent)
        self.path, self.settings, self.busy = Path(path), None, False
        self.setWindowTitle("导入当前试样 · sheet、列与单位")
        self.resize(960, 720)
        layout = QVBoxLayout(self)
        file_label = QLabel(str(path))
        file_label.setWordWrap(True)
        layout.addWidget(file_label)
        form = QFormLayout()
        self.sheet = QComboBox()
        self.sheet.addItem("请选择一个 sheet", "")
        for name in workbook_sheets(path):
            self.sheet.addItem(name, name)
        self.header = QSpinBox()
        self.header.setRange(1, 1000000)
        self.header.setValue(1)
        form.addRow("当前 sheet（只导入一个）", self.sheet)
        form.addRow("表头所在 Excel 行", self.header)
        layout.addLayout(form)
        self.preview = QTableWidget()
        self.preview.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview.setMinimumHeight(170)
        layout.addWidget(self.preview)
        self.mapping = QTableWidget(3, 4)
        self.mapping.setHorizontalHeaderLabels(["通道", "工作簿列", "原始单位（必填）", "转换至分析符号"])
        self.mapping.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mapping.setMaximumHeight(155)
        self.columns, self.units, self.signs = {}, {}, {}
        for i, (c, label) in enumerate(zip(CHANNELS, LABELS)):
            item = QTableWidgetItem(label)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.mapping.setItem(i, 0, item)
            self.columns[c], self.units[c], self.signs[c] = QComboBox(), QComboBox(), QComboBox()
            self.units[c].addItem("请选择单位", "")
            for u in UNITS[c]:
                self.units[c].addItem(u, u)
            self.signs[c].addItem("保持原值 × +1", 1)
            self.signs[c].addItem("明确反转 × −1", -1)
            self.mapping.setCellWidget(i, 1, self.columns[c])
            self.mapping.setCellWidget(i, 2, self.units[c])
            self.mapping.setCellWidget(i, 3, self.signs[c])
            self.columns[c].currentIndexChanged.connect(lambda _, channel=c: self.column_changed(channel))
        layout.addWidget(self.mapping)
        force_form = QFormLayout()
        self.force_column, self.force_unit, self.force_sign = QComboBox(), QComboBox(), QComboBox()
        self.force_unit.addItems(["请选择单位", "N", "kN", "MN"])
        self.force_sign.addItem("压缩为正（保持 ×+1）", 1)
        self.force_sign.addItem("压缩为负（转换 ×−1）", -1)
        self.area = QLineEdit()
        self.area.setPlaceholderText("缺少轴力列时输入；例如 10000，单位 mm²；可暂留空")
        force_form.addRow("轴力列（可选）", self.force_column)
        force_form.addRow("轴力单位", self.force_unit)
        force_form.addRow("轴力符号", self.force_sign)
        force_form.addRow("试样截面积 mm²", self.area)
        layout.addLayout(force_form)
        self.sign_note = QLineEdit("保持原符号；轴压正、环胀负约定待核查")
        self.source_note = QLineEdit("此前整理的横向应变通道；来源/传感器原理待核查")
        notes = QFormLayout()
        notes.addRow("符号约定及转换理由", self.sign_note)
        notes.addRow("环向通道来源", self.source_note)
        layout.addLayout(notes)
        self.info = QLabel("按表头匹配列；单位不明须选择。内部应变 mm/mm、应力 MPa。\n"
                           "约定：轴向压缩为正，环向膨胀为负。原始值保留，不自动修正符号。\n"
                           "数值为 Excel 存储值；% 单位除以 100。Excel 百分比显示格式请核对预览的存储值。")
        self.info.setWordWrap(True)
        layout.addWidget(self.info)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("导入这个试样")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        buttons.accepted.connect(self.validate_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.sheet.currentIndexChanged.connect(self.refresh_preview)
        self.header.valueChanged.connect(self.refresh_preview)
        if preset:
            self.header.setValue(preset.header_row)
            self.sheet.setCurrentIndex(self.sheet.findData(preset.sheet))
            for c in CHANNELS:
                self.columns[c].setCurrentIndex(self.columns[c].findData(preset.columns[c]))
                self.units[c].setCurrentIndex(self.units[c].findData(preset.units[c]))
                self.signs[c].setCurrentIndex(self.signs[c].findData(preset.signs[c]))
            self.sign_note.setText(preset.sign_note)
            self.source_note.setText(preset.channel_source)
            self.force_column.setCurrentIndex(max(0, self.force_column.findData(preset.force_column)))
            self.force_unit.setCurrentText(preset.force_unit or "请选择单位")
            self.force_sign.setCurrentIndex(self.force_sign.findData(preset.force_sign))
            self.area.setText("" if preset.area_mm2 is None else str(preset.area_mm2))
        elif self.sheet.count() == 2:
            self.sheet.setCurrentIndex(1)

    def refresh_preview(self):
        name = self.sheet.currentData()
        if not name:
            return
        try:
            self.busy = True
            rows, total, ncols = sheet_preview(self.path, name, self.header.value())
            self.headers = list(rows[0]) if rows else []
            self.force_column.clear()
            self.force_column.addItem("无轴力列（使用截面积换算或暂不提供）", None)
            for i, h in enumerate(self.headers):
                self.force_column.addItem(f"{i+1}: {h or '(空表头)'}", i)
            import re
            candidates = [i for i, h in enumerate(self.headers) if re.search(r"轴力|荷载|载荷|force|load", str(h), re.I)]
            self.force_unit.setCurrentIndex(0)
            if len(candidates) == 1:
                self.force_column.setCurrentIndex(self.force_column.findData(candidates[0]))
                found = re.search(r"(?<![a-zA-Z])(kN|MN|N)(?![a-zA-Z])", str(self.headers[candidates[0]]))
                if found:
                    self.force_unit.setCurrentText(found[1])
            columns, units = infer_columns(self.headers)
            self.preview.setRowCount(len(rows))
            self.preview.setColumnCount(len(self.headers))
            self.preview.setHorizontalHeaderLabels([f"列 {i + 1}" for i in range(len(self.headers))])
            self.preview.setVerticalHeaderLabels([str(i + self.header.value()) for i in range(len(rows))])
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.preview.setItem(i, j, QTableWidgetItem("" if value is None else str(value)))
            self.preview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            for c in CHANNELS:
                self.columns[c].clear()
                self.columns[c].addItem("请选择列", None)
                for i, h in enumerate(self.headers):
                    self.columns[c].addItem(f"{i + 1}: {h or '(空表头)'}", i)
                self.columns[c].setCurrentIndex(self.columns[c].findData(columns[c]))
                self.units[c].setCurrentIndex(self.units[c].findData(units[c]))
        except Exception as exc:
            QMessageBox.warning(self, "读取 sheet 失败", str(exc))
        finally:
            self.busy = False

    def column_changed(self, c):
        if self.busy:
            return
        col = self.columns[c].currentData()
        unit = ""
        if col is not None:
            # Unit parsing is independent of the channel name for manual mapping.
            text = str(self.headers[col])
            import re
            candidates = [u for u in UNITS[c] if (u in text if c != "stress" else bool(re.search(r"(?<![a-zA-Z])"+u+r"(?![a-zA-Z])", text)))]
            unit = candidates[0] if len(candidates) == 1 else ""
        self.units[c].setCurrentIndex(self.units[c].findData(unit))

    def build_settings(self):
        if not self.sheet.currentData():
            raise ValueError("请选择一个 sheet")
        if (any(self.signs[c].currentData() == -1 for c in CHANNELS)
                and self.sign_note.text() == "保持原符号；轴压正、环胀负约定待核查"):
            raise ValueError("已选择反转符号，请在符号说明中记录原始约定和转换理由，避免仍标为保持原符号")
        s = ImportSettings(self.sheet.currentData(), self.header.value(),
                           {c: self.columns[c].currentData() for c in CHANNELS},
                           {c: self.units[c].currentData() for c in CHANNELS},
                           {c: self.signs[c].currentData() for c in CHANNELS},
                           self.sign_note.text(), self.source_note.text())
        s.validate()
        s.force_column = self.force_column.currentData()
        s.force_unit = self.force_unit.currentText() if s.force_column is not None else ""
        s.force_sign = self.force_sign.currentData()
        try:
            s.area_mm2 = float(self.area.text()) if self.area.text().strip() else None
        except ValueError:
            raise ValueError("截面积请输入数值，单位 mm²")
        s.validate()
        return s

    def validate_accept(self):
        try:
            self.settings = self.build_settings()
        except ValueError as exc:
            QMessageBox.warning(self, "请补全导入设置", str(exc))
            return
        self.accept()


class WorkbookImportDialog(ImportDialog):
    """Explicit multi-sheet selection sharing a verified identical column layout."""
    def __init__(self, path, parent=None):
        super().__init__(path, parent)
        self.setWindowTitle("导入工作簿 · 勾选多个试样")
        self.resize(1050, 900)
        self.choices = QListWidget()
        self.choices.setMaximumHeight(120)
        for name in workbook_sheets(path):
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.choices.addItem(item)
        self.layout().insertWidget(1, QLabel("勾选要导入的 sheet；下方选择一个作为列/单位模板。校验前9列及额外选用列；其他辅助列表头差异仅提醒。"))
        self.layout().insertWidget(2, self.choices)
        self.sheet.setCurrentIndex(1 if self.sheet.count() > 1 else 0)
        for label in self.findChildren(QLabel):
            if label.text() == "当前 sheet（只导入一个）":
                label.setText("列与单位模板 sheet")
        for button in self.findChildren(QPushButton):
            if button.text() == "导入这个试样":
                button.setText("导入勾选试样")
        self.all_settings = []
        # Keep all controls reachable on smaller displays; submission stays fixed.
        outer = self.layout()
        buttons = outer.takeAt(outer.count() - 1).widget()
        content = QWidget()
        inner = QVBoxLayout(content)
        while outer.count():
            item = outer.takeAt(0)
            if item.widget() is not None:
                inner.addWidget(item.widget())
            elif item.layout() is not None:
                sublayout = item.layout()
                sublayout.setParent(None)
                inner.addLayout(sublayout)
            else:
                inner.addItem(item)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        outer.addWidget(buttons)
        available = QApplication.instance().primaryScreen().availableGeometry()
        self.resize(min(1050, available.width()-60), min(880, available.height()-80))

    def validate_accept(self):
        try:
            template = self.build_settings()
            names = [self.choices.item(i).text() for i in range(self.choices.count())
                     if self.choices.item(i).checkState() == Qt.CheckState.Checked]
            if not names:
                raise ValueError("请至少勾选一个 sheet")
            reference = sheet_preview(self.path, template.sheet, template.header_row)[0]
            selected = set(template.columns.values())
            if template.force_column is not None:
                selected.add(template.force_column)
            settings, ignored = [], []
            for name in names:
                rows = sheet_preview(self.path, name, template.header_row)[0]
                if compare_layout(reference, rows, selected, name):
                    ignored.append(name)
                settings.append(replace(template, sheet=name))
            if ignored:
                QMessageBox.information(self, '辅助列差异已忽略',
                    '前9列及额外选用列的列名和单位一致，可以批量导入。以下sheet的未使用辅助列表头不同，已忽略：\n' + '、'.join(ignored))
            self.settings, self.all_settings = template, settings
        except (ValueError, IndexError) as exc:
            QMessageBox.warning(self, "请检查导入设置", str(exc))
            return
        self.accept()


class CurvePanel(BasePlotWidget):
    """Extends MechAnalyser's existing Qt plot wrapper with movable boundaries."""
    def __init__(self, view, changed):
        self.plot = pg.PlotWidget(background="w")
        super().__init__(self.plot)
        self.view = view
        self.plot.showGrid(x=True, y=True, alpha=0.18)
        self.plot.addLegend(offset=(12, 12))
        self.plot.setFont(QFont("SimSun", 11))
        for axis in ("left", "bottom"):
            self.plot.getAxis(axis).enableAutoSIPrefix(False)
            self.plot.getAxis(axis).setTextPen("#435469")
            self.plot.getAxis(axis).setTickFont(QFont("Times New Roman", 11))
        self.plot.setMenuEnabled(True)
        self.curves = []
        for label, color, style in (("轴向应变" if view in (0, 3) else "横向应变", AXIAL if view in (0, 3) else HOOP, "raw"),
                                    ("同步选中点", SELECTED, "points"), ("拟合线", FIT, "fit")):
            self.curves.append(self.plot.plot(name=label,
                pen=None if style == "points" else pg.mkPen(color, width=2, style=Qt.PenStyle.DashLine if style == "fit" else Qt.PenStyle.SolidLine),
                symbol="o" if style == "points" else None,
                symbolSize=5, symbolBrush=color, symbolPen=None, connect="finite"))
        self.extra = []
        if view == 3:
            for label, color, style in (("横向应变", HOOP, "raw"), ("横向同步选中点", SELECTED, "points"), ("横向拟合线", FIT, "fit")):
                self.extra.append(self.plot.plot(name=label, pen=None if style == "points" else pg.mkPen(color, width=2, style=Qt.PenStyle.DashLine if style == "fit" else Qt.PenStyle.SolidLine),
                    symbol="t" if style == "points" else None, symbolBrush=color, symbolPen=None, symbolSize=6, connect="finite"))
        legend=self.plot.getPlotItem().legend
        legend.clear()
        legend.addItem(self.curves[0], '轴向应变' if view in (0,3) else '横向应变')
        if view == 3: legend.addItem(self.extra[0], '横向应变')
        legend.addItem(self.curves[2], '拟合曲线')
        for group in [self.curves]+([self.extra] if self.extra else []):
            group[1].hide()
            group[2].setPen(pg.mkPen('#c62828',width=1.8))
        self.result_footer=QLabel()
        self.result_footer.hide()
        self.layout().addWidget(self.result_footer)
        self._placing=False
        self.region = None
        self.changed = changed
        self.orientation = None
        for _, label in self.plot.getPlotItem().legend.items:
            label.setText(rich(label.text, 11))
        self.annotation_a = None
        self.zero_axis = None
        if view != 2:
            vb = self.plot.getViewBox()
            self.zero_axis = pg.AxisItem('left', parent=vb)
            self.zero_axis.linkToView(vb)
            self.zero_axis.setWidth(55)
            self.zero_axis.setTickFont(QFont('Times New Roman', 11))
            self.zero_axis.setTextPen('#333333')
            self.zero_axis.setPen(pg.mkPen('#333333', width=1.2))
            self.zero_axis.setZValue(15)
            self.plot.getAxis('left').setStyle(showValues=False)
            self.plot.getAxis('left').setPen(pg.mkPen(None))
        self.annotation_items = []
        def text_item(anchor=(0,0)):
            item = pg.TextItem(anchor=anchor, color='#111111')
            self.plot.addItem(item, ignoreBounds=True)
            item.setZValue(20)
            self.annotation_items.append(item)
            return item
        self.band_label = text_item((1,.5))
        self.modulus_label = text_item((0,.5))
        self.peak_label = text_item()
        self.parameter_label = text_item()
        self.formula_label = text_item()
        self.peak_point = pg.ScatterPlotItem(size=12, brush='#e02020', pen=None)
        self.plot.addItem(self.peak_point, ignoreBounds=True)
        self.arrow_line = pg.PlotDataItem(pen=pg.mkPen('#4371a8',width=1.5))
        self.plot.addItem(self.arrow_line, ignoreBounds=True)
        self.arrow_heads = [pg.ArrowItem(angle=angle, headLen=9, tipAngle=35, brush='#4371a8', pen='#4371a8') for angle in (-90,90)]
        for item in self.arrow_heads:
            self.plot.addItem(item, ignoreBounds=True)
            item.setZValue(20)
        self.plot.getViewBox().sigRangeChanged.connect(self.position_annotations)
        self.plot.getViewBox().sigResized.connect(self.position_annotations)

    def position_annotations(self, *args):
        a = self.annotation_a
        if a is None:
            return
        vb = self.plot.getViewBox()
        (xmin,xmax),(ymin,ymax) = vb.viewRange()
        dx,dy = xmax-xmin,ymax-ymin
        if self.zero_axis is not None:
            self.zero_axis.setHeight(vb.height())
            self.zero_axis.setPos(vb.mapFromView(QPointF(0,ymax)).x()-55,0)
            self.zero_axis.setVisible(xmin <= 0 <= xmax)
        bounds = band(a)
        enabled = self.view != 2 and bounds is not None
        for item in [self.band_label,self.modulus_label,self.arrow_line,*self.arrow_heads]:
            item.setVisible(enabled)
        if enabled:
            lo,hi = bounds
            x = arrow_x(a,xmin,xmax,lo,hi)
            self.arrow_line.setData([x,x],[lo,hi])
            self.arrow_heads[0].setPos(x,lo)
            self.arrow_heads[1].setPos(x,hi)
            self.band_label.setHtml(rich('线性弹性区间',12))
            self.band_label.setPos(x-.015*dx,(lo+hi)/2)
            self.modulus_label.setHtml(rich(f'E = {a.result["E_GPa"]:.3f} GPa',12) if 'E_GPa' in a.result else '')
            self.modulus_label.setPos(x+.025*dx,(lo+hi)/2)
        overlay = self.view == 3
        self.parameter_label.setVisible(overlay)
        self.formula_label.setVisible(overlay)
        if overlay:
            self.parameter_label.setHtml(rich(parameter_text(a),11))
            self.parameter_label.setPos(xmin+.015*dx,ymax-.025*dy)
            self.formula_label.setPos(xmin+.03*dx,ymin+.15*dy)
            self.formula_label.setHtml(poisson_html(a))
            self.plot.getPlotItem().legend.anchor((0,0),(.30,.025))
        peak = a.result.get('peak_stress_MPa')
        px = a.result.get('peak_axial_strain')
        peak_enabled = self.view in (0,3) and peak is not None and px is not None
        self.peak_label.setVisible(peak_enabled)
        self.peak_point.setData([px] if peak_enabled else [],[peak] if peak_enabled else [])
        if peak_enabled:
            self.peak_label.setHtml(f'<span style="font-family:Times New Roman;font-size:11pt"><i>f<sub>c</sub></i> = {peak:.3f} MPa</span>')
            self.peak_label.setAnchor((1,1) if px > xmin+.88*dx else (0,1))
            self.peak_label.setPos(px-.02*dx if px > xmin+.88*dx else px+.02*dx,peak+.035*dy)
        self.tidy_annotations()

    def tidy_annotations(self):
        if self._placing or self.annotation_a is None: return
        self._placing=True
        try:
            for item in [self.arrow_line,*self.arrow_heads]: item.hide()
            a=self.annotation_a
            vb=self.plot.getViewBox()
            (xmin,xmax),(ymin,ymax)=ranges=vb.viewRange()
            dx,dy=xmax-xmin,ymax-ymin
            self.plot.getPlotItem().legend.anchor((0,0),(.36,.025))
            if self.view != 3:
                return
            self.modulus_label.hide()
            result=rich(f'E = {a.result["E_GPa"]:.3f} GPa',11) if 'E_GPa' in a.result else ''
            if a.result.get('nu') is not None:
                result += ('<table cellspacing="0" cellpadding="1" style="font-family:Times New Roman;font-size:11pt"><tr>'
                    '<td rowspan="2"><i>ν</i> = −</td><td style="border-bottom:1px solid black"><i>E</i></td>'
                    f'<td rowspan="2"> = {a.result["nu"]:.3f}</td></tr><tr><td><i>k</i><sub style="font-family:SimSun">横</sub></td></tr></table>')
            self.formula_label.setHtml(result)
            self.formula_label.setAnchor((0,1))
            self.band_label.setAnchor((0,1))
            obstacles=[]
            for item in (self.parameter_label,self.plot.getPlotItem().legend,self.peak_label):
                if item.isVisible():
                    rect=item.sceneBoundingRect()
                    tl=vb.mapSceneToView(rect.topLeft())
                    br=vb.mapSceneToView(rect.bottomRight())
                    obstacles.append(((tl.x()-xmin)/dx,(br.y()-ymin)/dy,(br.x()-xmin)/dx,(tl.y()-ymin)/dy))
            bounds=band(a)
            cy=((sum(bounds)/2-ymin)/dy) if bounds else .2
            for item,preferred in [(self.formula_label,.51),(self.band_label,.30)]:
                rect=item.boundingRect()
                size=(rect.width()/max(vb.width(),1),rect.height()/max(vb.height(),1))
                pos=clear_box(a,ranges,size,(preferred,cy-size[1]/2),obstacles)
                item.setVisible(pos is not None and bool(bounds))
                if pos:
                    item.setPos(xmin+pos[0]*dx,ymin+pos[1]*dy)
                    obstacles.append((*pos,pos[0]+size[0],pos[1]+size[1]))
                if item is self.formula_label:
                    self.result_footer.setText(result)
                    self.result_footer.setVisible(pos is None and bool(result))
        finally:
            self._placing=False

    def update_data(self, a):
        view = self.view
        x, y, key = [("axial", "stress", "E"), ("hoop", "stress", "kh"),
                     ("axial", "hoop", "poisson"), ("axial", "stress", "E")][view]
        r, s = a.result, a.selected
        f = a.raw_data.frame.copy()
        f.loc[~f.valid, ["axial", "hoop", "stress"]] = np.nan
        def curves_set(curves, xc, yc, fitkey):
            curves[0].setData(f[xc].to_numpy(), f[yc].to_numpy())
            curves[1].setData(s[xc].to_numpy(), s[yc].to_numpy())
            if fitkey in r and len(s):
                xx = np.array([s[xc].min(), s[xc].max()])
                curves[2].setData(xx, r[fitkey]["intercept"] + r[fitkey]["slope"] * xx)
            else:
                curves[2].setData([], [])
        curves_set(self.curves, x, y, key)
        if view == 3:
            curves_set(self.extra, "hoop", "stress", "kh")
        self.plot.setLabel("bottom", rich("应变" if view != 2 else "轴向应变",12,True))
        self.plot.setLabel("left", rich("应力(MPa)" if view != 2 else "横向应变",12,True))
        p = a.parameters
        enabled = (p.mode == "strain" and view in (0, 2, 3)) or (p.mode != "strain" and view in (0, 1, 3))
        orientation = "vertical" if p.mode == "strain" else "horizontal"
        if self.region is None or self.orientation != orientation:
            if self.region is not None:
                self.plot.removeItem(self.region)
            self.region = pg.LinearRegionItem(orientation=orientation, brush=pg.mkBrush(80, 110, 140, 18),
                pen=pg.mkPen("#7890a8", width=1), hoverPen=pg.mkPen("#dd7f00", width=2))
            self.region.setZValue(8)
            self.plot.addItem(self.region)
            self.region.sigRegionChanged.connect(lambda: self.changed(self))
            self.orientation = orientation
        self.region.setVisible(enabled)
        scale = r.get("branch_peak_stress_MPa", 1) if p.mode == "ratio" else 1
        self.region.setRegion((p.low * scale, p.high * scale))
        self.plot.setTitle(rich("拖动灰色边界调整区间；滚轮缩放" if enabled else "此视图联动相同采样点",10))
        self.annotation_a = a
        self.position_annotations()


class ConcreteWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyser = None
        self.analysis_path = None
        self.dirty = False
        self.updating = False
        self.sessions = []
        self.active_session = -1
        self.workspace_path = None
        self.setWindowTitle("MechAnalyser · 混凝土单轴压缩")
        app = QApplication.instance()
        app.setStyle("Fusion")
        palette = QPalette()
        for role, color in ((QPalette.ColorRole.Window, "#f4f6f8"), (QPalette.ColorRole.WindowText, "#183347"),
                (QPalette.ColorRole.Base, "#ffffff"), (QPalette.ColorRole.AlternateBase, "#edf2f6"),
                (QPalette.ColorRole.Text, "#183347"), (QPalette.ColorRole.Button, "#eaf0f5"),
                (QPalette.ColorRole.ButtonText, "#183347"), (QPalette.ColorRole.Highlight, "#2166ac"),
                (QPalette.ColorRole.HighlightedText, "#ffffff")):
            palette.setColor(role, QColor(color))
        app.setPalette(palette)
        self.setPalette(palette)
        available = app.primaryScreen().availableGeometry()
        self.resize(min(1440, available.width()-40), min(940, available.height()-65))
        self.setMinimumSize(960, 600)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setStyleSheet("QWidget {color:#183347;} QMainWindow,QWidget#central {background:#f4f6f8;} QGroupBox {font-weight:600; border:1px solid #ccd6df; border-radius:5px; margin-top:14px; padding-top:12px;} QGroupBox::title {subcontrol-origin:margin;left:10px;} QPushButton {padding:6px 12px; background:#eaf0f5; color:#183347; border:1px solid #b8c8d5; border-radius:4px;} QPushButton:hover {background:#dce9f4;} QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QTextEdit {background:white; color:#183347; min-height:25px;} QToolTip {color:#172b3b;background:white;}")
        central = QWidget()
        central.setObjectName("central")
        outer = QVBoxLayout(central)
        self.setCentralWidget(central)
        bar = QHBoxLayout()
        for text, name, callback in (("导入数据", "import_button", self.import_clicked), ("打开分析", "open_button", self.open_clicked),
            ("保存分析", "save_button", self.save_clicked), ("导出结果", "export_button", self.export_clicked),
            ("单位 / 符号 / 重新导入", "settings_button", self.settings_clicked), ("数据问题", "issues_button", self.show_issues)):
            b = QPushButton(text)
            b.setObjectName(name)
            b.clicked.connect(callback)
            setattr(self, name, b)
            bar.addWidget(b)
        outer.addLayout(bar)
        sheet_bar = QHBoxLayout()
        sheet_bar.addWidget(QLabel("当前试样"))
        self.specimens = QComboBox()
        self.specimens.currentIndexChanged.connect(self.switch_specimen)
        sheet_bar.addWidget(self.specimens, 1)
        self.save_all_button = QPushButton("保存全部试样进度")
        self.save_all_button.clicked.connect(self.save_all_clicked)
        sheet_bar.addWidget(self.save_all_button)
        outer.addLayout(sheet_bar)
        self.source_label = QLabel("导入工作簿后勾选多个 sheet，通过上方切换试样；各试样独立保留拟合区间。")
        self.source_label.setTextFormat(Qt.TextFormat.PlainText)
        self.source_label.setWordWrap(True)
        outer.addWidget(self.source_label)
        self.fields = {}
        options = {
            'test_type': [(x,x) for x in ('单轴压缩试验','三轴压缩试验')],
            'material': [(x,x) for x in ('混凝土','水泥砂浆')],
            'aggregate_ratio': [(str(x),str(x)) for x in (1.5,2,3,4)],
            'water_content': [(str(x),str(x)) for x in (13,15,17)],
            'pressure': [('0 MPa（不加压组）','0')]+[(f'{x} MPa',str(x)) for x in (2.5,5,7.5,10)],
            'injection_hours': [('10分钟',str(1/6)),('1小时','1'),('3小时','3'),('24小时','24')],
            'curing_days': [(f'{x} 天',str(x)) for x in (7,14,21,28)],
        }
        rows = [
            [('specimen','完整编号'),('test_type','试验类型'),('material','材料'),('cement_ratio','水泥/细骨料'),('aggregate_ratio',':')],
            [('water_content','含水率 (%)'),('pressure','压注压强 MPa'),('injection_hours','压注时间'),('curing_days','养护天数')],
        ]
        for row in rows:
            layout = QHBoxLayout()
            for key,label in row:
                layout.addWidget(QLabel(label))
                if key in options:
                    field=ChoiceField(options[key])
                    field.removeItem(0)
                    field.setText(DEFAULT_METADATA.get(key,''))
                    field.currentIndexChanged.connect(self.metadata_changed)
                else:
                    field=QLineEdit()
                    field.setPlaceholderText('请输入')
                    if key=='cement_ratio':
                        field.setText('1'); field.setReadOnly(True); field.setMaximumWidth(40)
                    field.textEdited.connect(self.metadata_changed)
                self.fields[key]=field
                layout.addWidget(field,2 if key=='specimen' else 0 if key=='cement_ratio' else 1)
            outer.addLayout(layout)
        self.confining_row = QWidget()
        confining_layout = QHBoxLayout(self.confining_row)
        confining_layout.setContentsMargins(0, 0, 0, 0)
        confining_layout.addWidget(QLabel('三轴试验参数  ·  围压压强 (MPa)'))
        self.fields['confining_pressure'] = ConfiningPressureField(
            [(f'{x} MPa', str(x)) for x in (2.5, 5, 7.5, 10)])
        self.fields['confining_pressure'].setMaximumWidth(200)
        self.fields['confining_pressure'].currentIndexChanged.connect(self.metadata_changed)
        confining_layout.addWidget(self.fields['confining_pressure'])
        confining_layout.addStretch()
        outer.addWidget(self.confining_row)
        self.confining_row.hide()
        splitter = QSplitter()
        outer.addWidget(splitter, 1)
        self.tabs = QTabWidget()
        self.panels = [CurvePanel(i, self.region_changed) for i in range(4)]
        for p, name in zip(self.panels, ("轴向应力—轴向应变", "轴向应力—环向应变", "环向应变—轴向应变", "轴向与环向叠加")):
            self.tabs.addTab(p, name)
        self.tabs.setCurrentIndex(3)
        splitter.addWidget(self.tabs)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        right = QWidget()
        side = QVBoxLayout(right)
        scroll.setWidget(right)
        splitter.addWidget(scroll)
        splitter.setSizes([990, 450])
        splitter.setStretchFactor(0, 1)
        branch_box = QGroupBox("1  限定加载分支（原始 Excel 行号）")
        branch_form = QFormLayout(branch_box)
        self.branch_start, self.branch_end = QSpinBox(), QSpinBox()
        for w in (self.branch_start, self.branch_end):
            w.setRange(1, 10000000)
            w.valueChanged.connect(self.parameters_changed)
        branch_form.addRow("起始行", self.branch_start)
        branch_form.addRow("终止行", self.branch_end)
        self.auto_branch = QPushButton("恢复峰前建议分支")
        self.auto_branch.clicked.connect(self.reset_branch)
        branch_form.addRow(self.auto_branch)
        side.addWidget(branch_box)
        range_box = QGroupBox("2  选择拟合区间")
        range_form = QFormLayout(range_box)
        self.mode = QComboBox()
        for key, label in MODE_LABELS.items():
            self.mode.addItem(label, key)
        self.mode.currentIndexChanged.connect(self.mode_changed)
        range_form.addRow("选择依据", self.mode)
        self.low, self.high = QDoubleSpinBox(), QDoubleSpinBox()
        for w in (self.low, self.high):
            w.setDecimals(12)
            w.setRange(-1e9, 1e9)
            w.setSingleStep(0.01)
            w.valueChanged.connect(self.parameters_changed)
        range_form.addRow("下限（比例用 0–1）", self.low)
        range_form.addRow("上限（比例用 0–1）", self.high)
        self.origin = QCheckBox("三项拟合均强制过原点（默认不勾选）")
        self.origin.toggled.connect(self.parameters_changed)
        range_form.addRow(self.origin)
        hint = QLabel("比例为所选分支峰值的比例。默认 0.2–0.4 仅作初始区间，需人工检查。应变范围用 mm/mm。")
        hint.setWordWrap(True)
        range_form.addRow(hint)
        side.addWidget(range_box)
        result_box = QGroupBox("主要结果")
        result_layout = QHBoxLayout(result_box)
        result_layout.setSpacing(18)
        result_form = QFormLayout()
        result_layout.addLayout(result_form, 1)
        self.metrics = {}
        for key, title in (("stress", "峰值应力"), ("force", "峰值轴力"), ("E", "弹性模量"), ("nu", "泊松比")):
            value = QLabel("—")
            value.setStyleSheet("font-size:17px; font-weight:600; color:#155a85;")
            result_form.addRow(title, value)
            self.metrics[key] = value
        fit_grid = QGridLayout()
        fit_grid.setHorizontalSpacing(12)
        fit_grid.addWidget(QLabel('拟合质量'), 0, 0)
        fit_grid.addWidget(QLabel('R²'), 0, 1)
        fit_grid.addWidget(QLabel('n'), 0, 2)
        self.fit_metrics = {}
        for row, (key, label) in enumerate((('E', '轴向'), ('kh', '环向')), 1):
            fit_grid.addWidget(QLabel(label), row, 0)
            for col, metric in enumerate(('r2', 'n'), 1):
                value = QLabel('—')
                value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                value.setStyleSheet('font-weight:600; color:#155a85;')
                fit_grid.addWidget(value, row, col)
                self.fit_metrics[(key, metric)] = value
        fit_grid.setRowStretch(3, 1)
        result_layout.addLayout(fit_grid)
        side.addWidget(result_box)
        self.force_note = QLabel("")
        self.force_note.setWordWrap(True)
        side.addWidget(self.force_note)
        self.alert = QLabel("")
        self.alert.setWordWrap(True)
        side.addWidget(self.alert)
        self.more_button = QPushButton("更多详情 ▸")
        self.more_button.setCheckable(True)
        side.addWidget(self.more_button)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(220)
        self.result_text.setVisible(False)
        self.more_button.toggled.connect(self.toggle_details)
        side.addWidget(self.result_text)
        self.review = QCheckBox("已人工检查当前区间与结果")
        self.review.toggled.connect(self.review_changed)
        side.addWidget(self.review)
        side.addWidget(QLabel("备注（通道或数据来源未核实可记为待核查）"))
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(90)
        self.notes.textChanged.connect(self.notes_changed)
        side.addWidget(self.notes)
        bottom = QHBoxLayout()
        self.status_label = QLabel("尚未导入")
        bottom.addWidget(self.status_label, 1)
        focus = QPushButton("聚焦拟合区间")
        focus.clicked.connect(self.focus_selection)
        bottom.addWidget(focus)
        reset = QPushButton("适应全部曲线")
        reset.clicked.connect(self.autorange)
        bottom.addWidget(reset)
        outer.addLayout(bottom)
        help_menu = self.menuBar().addMenu("帮助")
        help_menu.addAction("计算与操作说明", self.show_help)
        self.source_timer = QTimer(self)
        self.source_timer.setInterval(30000)
        self.source_timer.timeout.connect(self.check_source)
        self.source_timer.start()
        self.update_enabled()

    def show_help(self):
        QMessageBox.information(self, "使用说明", "流程：导入 → 核对 sheet / 列 / 单位 / 符号 → 核对试样信息 → 选加载分支和区间 → 检查 → 保存 / 导出。\n\n"
            "E：σa=a+Eεa；k横（kh）：σa=c+khεh。主要泊松比 ν=−E/k横，采用 ASTM D7012-14 公式(7)的斜率比法；E与k横使用相同单位。应变回归 ν_strain=−b 仅供参考。\n"
            "名称为选定区间回归模量，未核验符合任何试验标准。kh 不是径向弹性模量。\n"
            "三种拟合共享同一组有效原始行；无效行整行同步排除并列出。不会平滑、取绝对值、重排或自行纠正符号。\n"
            "默认从首次峰值逆向识别最终上升段，以峰值 5% 为明显卸载阈值。复杂卸载/再加载必须人工用原始行修正。\n"
            "拖动灰色线选区间；滚轮缩放、右键坐标菜单。所有图共享选点。改动区间会取消已检查状态。\n"
            "保存为 .mca.json，含当前 sheet 原始快照；导出独立文件夹，含 Excel / CSV / PNG / 分析记录。\n\n"
            "基于 MechAnalyser，MIT，ksonter95；基准提交 76d8ea65704edee4bffa385eb404e557f47401c7。")

    def toggle_details(self, checked):
        self.result_text.setVisible(checked)
        self.more_button.setText("收起详情 ▾" if checked else "更多详情 ▸")

    def stash_session(self):
        if 0 <= self.active_session < len(self.sessions):
            self.sessions[self.active_session] = dict(analyser=self.analyser, path=self.analysis_path, dirty=self.dirty)

    def install_sessions(self, analysers, saved=False):
        self.sessions = [dict(analyser=a, path=None, dirty=not saved) for a in analysers]
        self.active_session = -1
        self.workspace_path = None
        self.specimens.blockSignals(True)
        self.specimens.clear()
        for a in analysers:
            self.specimens.addItem(a.raw_data.settings.sheet)
        self.specimens.blockSignals(False)
        self.switch_specimen(0)

    def switch_specimen(self, index):
        if index < 0 or index >= len(self.sessions):
            return
        self.stash_session()
        self.active_session = index
        entry = self.sessions[index]
        self.set_analyser(entry["analyser"], entry["path"])
        self.dirty = entry["dirty"]
        self.refresh_status()

    def save_all_clicked(self):
        self.stash_session()
        if not self.sessions:
            return self.save_clicked()
        path, _ = QFileDialog.getSaveFileName(self, "保存全部试样进度", str(self.workspace_path or ""), "工作簿分析 (*.mcw.json)")
        if not path:
            return False
        if not path.endswith(".mcw.json"):
            path += ".mcw.json"
        try:
            save_workspace([s["analyser"] for s in self.sessions], path, self.active_session)
            self.workspace_path = path
            for entry in self.sessions:
                entry["dirty"] = False
            self.dirty = False
            self.refresh_status()
            return True
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", str(exc))
            return False

    def update_enabled(self):
        active = self.analyser is not None
        for widget in (self.save_button, self.export_button, self.settings_button, self.issues_button,
                       self.branch_start, self.branch_end, self.auto_branch, self.mode, self.low, self.high,
                       self.origin, self.review, self.notes, *self.fields.values()):
            widget.setEnabled(active)
        self.sync_pressure_time()

    def sync_pressure_time(self):
        self.fields['injection_hours'].setEnabled(self.analyser is not None and not unpressurized(self.fields['pressure'].text()))
        triaxial = '三轴' in self.fields['test_type'].text()
        self.confining_row.setVisible(triaxial)
        self.fields['confining_pressure'].setEnabled(self.analyser is not None and triaxial)

    def confirm_unsaved(self):
        self.stash_session()
        if not self.dirty and not any(s["dirty"] for s in self.sessions):
            return True
        msg = QMessageBox(self)
        msg.setWindowTitle("尚未保存的分析")
        msg.setText("有试样分析尚未保存。继续前如何处理？（切换已导入的试样不会丢失进度）")
        save = msg.addButton("保存后继续", QMessageBox.ButtonRole.AcceptRole)
        discard = msg.addButton("放弃本次改动", QMessageBox.ButtonRole.DestructiveRole)
        msg.addButton("取消切换", QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        return (self.save_all_clicked() if len(self.sessions) > 1 else self.save_clicked()) if msg.clickedButton() == save else msg.clickedButton() == discard

    def import_clicked(self):
        if not self.confirm_unsaved():
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择 Excel 工作簿", "", "Excel 工作簿 (*.xlsx)")
        if path:
            self.import_dialog(path)

    def import_dialog(self, path, preset=None):
        try:
            dialog = ImportDialog(path, self, preset) if preset else WorkbookImportDialog(path, self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return False
            if not preset:
                analysers = []
                for settings in dialog.all_settings:
                    raw = RawData.load_sheet(path, settings)
                    specimen, pressure = sheet_identity(settings.sheet)
                    analysers.append(Analyser(raw, metadata={"specimen": specimen, "pressure": pressure,
                                                          "injection_hours": "", "curing_days": ""}))
                self.install_sessions(analysers)
                return True
            raw = RawData.load_sheet(path, dialog.settings)
            specimen, pressure = sheet_identity(dialog.settings.sheet)
            metadata = {"specimen": specimen, "pressure": pressure, "injection_hours": "", "curing_days": ""}
            if preset and self.analyser:
                metadata = self.analyser.metadata.copy()
            a = Analyser(raw, metadata=metadata)
            self.set_analyser(a)
            self.stash_session()
            if raw.issues:
                QMessageBox.warning(self, "导入数据需检查", f"发现 {len(raw.issues)} 条数据问题。无效行按三通道同步排除；原始值和行号已保留。点击“数据问题”查看。")
            return True
        except Exception as exc:
            QMessageBox.critical(self, "导入失败", str(exc))
            return False

    def settings_clicked(self):
        if self.analyser and self.confirm_unsaved():
            self.import_dialog(self.analyser.raw_data.source, self.analyser.raw_data.settings)

    def set_analyser(self, a, path=None):
        self.analyser, self.analysis_path = a, Path(path) if path else None
        self.updating = True
        cement = str(a.metadata.get('cement_ratio', '')).strip()
        aggregate = str(a.metadata.get('aggregate_ratio', '')).strip()
        if cement and cement != '1':
            try:
                denominator = float(cement)
                if denominator <= 0: raise ValueError()
                a.metadata['aggregate_ratio'] = f'{float(aggregate)/denominator:g}'
                a.metadata['cement_ratio'] = '1'
            except ValueError:
                a.result['warnings'].append('旧配比不能归一化为1:Y，请重新确认细骨料比例')
        for key, widget in self.fields.items():
            value = str(a.metadata.get(key, ""))
            if key == 'test_type' and not value: value='单轴压缩试验'
            if key == 'cement_ratio': value='1'
            if key == 'pressure' and value:
                try:
                    value = f'{float(value):g}'
                except ValueError:
                    pass
            widget.setText(value)
        self.notes.setPlainText(a.notes)
        self.sync_parameters()
        self.updating = False
        self.dirty = path is None
        self.update_enabled()
        self.refresh()
        self.autorange()

    def sync_parameters(self):
        p = self.analyser.parameters
        self.mode.setCurrentIndex(self.mode.findData(p.mode))
        self.low.setValue(p.low)
        self.high.setValue(p.high)
        self.low.setSingleStep(0.00001 if p.mode == "strain" else 0.01 if p.mode == "ratio" else 0.1)
        self.high.setSingleStep(self.low.singleStep())
        self.branch_start.setValue(p.branch_start)
        self.branch_end.setValue(p.branch_end)
        self.origin.setChecked(p.through_origin)

    def parameters_changed(self):
        if self.updating or not self.analyser:
            return
        a, p = self.analyser, self.analyser.parameters
        if p.branch_start != self.branch_start.value() or p.branch_end != self.branch_end.value():
            p.branch_method = "人工指定原始起止行"
        p.branch_start, p.branch_end = self.branch_start.value(), self.branch_end.value()
        p.low, p.high, p.mode = self.low.value(), self.high.value(), self.mode.currentData()
        p.through_origin = self.origin.isChecked()
        a.analyse()
        self.dirty = True
        self.refresh()

    def mode_changed(self):
        if self.updating or not self.analyser:
            return
        a = self.analyser
        mode = self.mode.currentData()
        actual = a.result.get("actual", {})
        limits = actual.get("axial" if mode == "strain" else "stress")
        if limits:
            lo, hi = limits
            if mode == "ratio":
                peak = a.result.get("branch_peak_stress_MPa", 1)
                lo, hi = lo / peak, hi / peak
        else:
            lo, hi = (0.2, 0.4) if mode == "ratio" else (0, 0.001) if mode == "strain" else (0, 10)
        self.updating = True
        self.low.setValue(lo)
        self.high.setValue(hi)
        self.low.setSingleStep(0.00001 if mode == "strain" else 0.01 if mode == "ratio" else 0.1)
        self.high.setSingleStep(self.low.singleStep())
        self.updating = False
        self.parameters_changed()

    def region_changed(self, panel):
        if self.updating or not self.analyser:
            return
        lo, hi = panel.region.getRegion()
        p = self.analyser.parameters
        if p.mode == "ratio":
            scale = self.analyser.result.get("branch_peak_stress_MPa", 1)
            lo, hi = lo / scale, hi / scale
        self.updating = True
        self.low.setValue(lo)
        self.high.setValue(hi)
        self.updating = False
        self.parameters_changed()

    def reset_branch(self):
        if not self.analyser:
            return
        try:
            start, end = default_branch(self.analyser.raw_data.frame)
            self.updating = True
            self.branch_start.setValue(start)
            self.branch_end.setValue(end)
            self.updating = False
            self.parameters_changed()
            self.analyser.parameters.branch_method = "从首次峰值逆向识别最终上升段；5%峰值回落阈值（建议，待人工检查）"
        except ValueError as exc:
            QMessageBox.warning(self, "无法识别建议分支", str(exc))

    def metadata_changed(self):
        if self.updating or not self.analyser:
            return
        self.analyser.metadata.update({k: w.text().strip() for k, w in self.fields.items()})
        self.sync_pressure_time()
        self.analyser.reviewed = False
        self.dirty = True
        self.refresh()

    def notes_changed(self):
        if self.updating or not self.analyser:
            return
        self.analyser.notes = self.notes.toPlainText()
        self.dirty = True
        self.refresh_status()

    def review_changed(self, checked):
        if self.updating or not self.analyser:
            return
        self.analyser.reviewed = checked
        self.dirty = True
        self.refresh_status()

    def refresh_status(self):
        a = self.analyser
        self.status_label.setText((a.status + (" · 有未保存改动" if self.dirty else " · 已保存")) if a else "尚未导入")
        kind=(a.metadata.get('test_type') or '单轴压缩试验') if a else '压缩试验'
        self.setWindowTitle("MechAnalyser · " + kind + (" *" if self.dirty else ""))

    def refresh(self):
        if not self.analyser:
            return
        self.updating = True
        a, r = self.analyser, self.analyser.result
        self.source_label.setText(f'{a.raw_data.source}  |  sheet: {a.raw_data.settings.sheet}\n'
            f'内部单位：应变 mm/mm · 应力 MPa  |  {a.raw_data.settings.sign_note}  |  {a.source_state}')
        for panel in self.panels:
            panel.update_data(a)
        def number(v):
            return "不可用" if v is None else f"{v:.8g}"
        lines = ["<b>选定区间回归模量</b>（未核验标准）", f'<b>有效同步点数：{r["n"]}</b>']
        if "E" in r:
            lines += [f'<b>E = {number(r["E"]["slope"])} MPa = {number(r["E_GPa"])} GPa</b>',
                      f'<b>ν = −E/k横（ASTM D7012-14 公式7）= {number(r["nu"])}</b>', f'ν_strain（应变回归参考）= {number(r["nu_strain"])}',
                      f'轴向应力—环向应变斜率 kh = {number(r["kh"]["slope"])} MPa']
            for key, label in (("E", "轴向"), ("kh", "环向"), ("poisson", "应变—应变")):
                fit = r[key]
                lines.append(f'{label}：截距 {number(fit["intercept"])}；R² {number(fit["r2"])}；n={fit["n"]}')
        if "actual" in r:
            for key, label in (("stress", "实际应力 MPa"), ("axial", "实际轴向应变"), ("hoop", "实际环向应变"), ("row", "实际原始行范围")):
                lo, hi = r["actual"][key]
                lines.append(f'{label}：{number(lo)} ～ {number(hi)}')
        lines.append(f'全曲线峰值应力 {number(r.get("peak_stress_MPa"))} MPa；对应 εa {number(r.get("peak_axial_strain"))}；原始行 {r.get("peak_row", "不可用")}')
        if r["errors"]:
            lines.append('<b style="color:#a6292c">计算失败：' + html.escape("；".join(r["errors"])) + '</b>')
        for warn in r["warnings"]:
            lines.append('<span style="color:#87520a">检查：' + html.escape(warn) + '</span>')
        self.result_text.setHtml("<br><br>".join(lines))
        def short(v, digits, unit=""):
            return "未提供" if v is None else f"{v:.{digits}f}{unit}"
        self.metrics["stress"].setText(short(r.get("peak_stress_MPa"), 3, " MPa"))
        self.metrics["force"].setText(short(r.get("peak_force_kN"), 3, " kN"))
        self.metrics["E"].setText(short(r.get("E_GPa"), 3, " GPa") if not r["errors"] else "计算失败")
        self.metrics["nu"].setText(short(r.get("nu"), 4) if not r["errors"] else "计算失败")
        for key in ('E', 'kh'):
            fit = r.get(key, {})
            r2 = fit.get('r2')
            self.fit_metrics[(key, 'r2')].setText('—' if r2 is None else f'{r2:.6f}')
            self.fit_metrics[(key, 'n')].setText(str(fit.get('n', r.get('n', 0))))
        self.force_note.setText("轴力：" + r.get("peak_force_source", "缺少轴力列或截面积；可在“单位 / 符号 / 重新导入”中补充"))
        lines.append("峰值轴力 kN：" + number(r.get("peak_force_kN")) + "；来源：" + html.escape(r.get("peak_force_source", "未提供")))
        lines.append("峰值轴力原始行：" + str(r.get("peak_force_row", "未提供")))
        self.result_text.setHtml("<br><br>".join(lines))
        self.alert.setText("计算失败，展开详情查看原因" if r["errors"] else
                           f'有 {len(r["warnings"])} 项检查提示，点击“更多详情”查看' if r["warnings"] else "")
        self.review.setChecked(a.reviewed)
        self.review.setEnabled(not r["errors"] and a.source_state == "匹配")
        self.refresh_status()
        self.updating = False

    def autorange(self):
        for panel in self.panels:
            panel.plot.autoRange()
            if self.analyser and panel.view != 2:
                f = self.analyser.raw_data.frame
                values = f.stress[f.valid]
                if len(values):
                    panel.plot.setYRange(min(0,float(values.min())), max(1,float(values.max())*1.2),padding=0)

    def focus_selection(self):
        if not self.analyser or self.analyser.selected.empty:
            return
        s = self.analyser.selected
        for i, panel in enumerate(self.panels):
            x, y = [(s.axial, s.stress), (s.hoop, s.stress),
                    (s.axial, s.hoop), (np.concatenate((s.axial, s.hoop)), s.stress)][i]
            def bounds(v):
                lo, hi = float(np.min(v)), float(np.max(v))
                pad = max((hi-lo)*.18, 1e-12)
                return lo-pad, hi+pad
            panel.plot.setRange(xRange=bounds(x), yRange=bounds(y), padding=0)

    def check_source(self):
        if self.analyser:
            old = self.analyser.source_state
            source_state(self.analyser)
            if old != self.analyser.source_state:
                self.dirty = True
                self.refresh()

    def save_clicked(self):
        if not self.analyser:
            return False
        path = str(self.analysis_path) if self.analysis_path else ""
        path, _ = QFileDialog.getSaveFileName(self, "保存当前试样分析", path, "MechAnalyser 分析 (*.mca.json)")
        if not path:
            return False
        if not path.endswith(".mca.json"):
            path += ".mca.json"
        try:
            save_analysis(self.analyser, path)
            self.analysis_path = Path(path)
            self.dirty = False
            self.refresh()
            return True
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", str(exc))
            return False

    def open_clicked(self):
        if not self.confirm_unsaved():
            return
        path, _ = QFileDialog.getOpenFileName(self, "打开试样或工作簿分析", "", "MechAnalyser 分析 (*.mca.json *.mcw.json)")
        if path:
            try:
                if path.endswith(".mcw.json"):
                    analysers, active = load_workspace(path)
                    self.install_sessions(analysers, saved=True)
                    self.workspace_path = path
                    self.specimens.setCurrentIndex(active)
                    if any(a.source_state != "匹配" for a in analysers):
                        QMessageBox.warning(self, "源文件核对", "部分源文件改变或不可用，当前为保存快照重算结果，请核查各试样来源。")
                    return
                a = load_analysis(path)
                self.sessions = []
                self.active_session = -1
                self.specimens.clear()
                self.set_analyser(a, path)
                if a.source_state != "匹配":
                    QMessageBox.warning(self, "源文件核对", a.source_state + "。当前展示保存快照的重算结果；请重新导入更新后的工作簿。")
            except Exception as exc:
                QMessageBox.critical(self, "打开失败", str(exc))

    def export_clicked(self):
        if not self.analyser:
            return
        parent = QFileDialog.getExistingDirectory(self, "选择导出目录（自动新建当前试样子目录）")
        if parent:
            try:
                folder = export_current(self.analyser, parent)
                self.refresh()
                QMessageBox.information(self, "已导出当前试样", f"导出目录：\n{folder}\n\n包含 Excel、Origin CSV、检查图和分析记录。")
            except Exception as exc:
                QMessageBox.critical(self, "导出失败", str(exc))

    def show_issues(self):
        if not self.analyser:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("原始数据问题 · 不独立压缩三列")
        dialog.resize(800, 480)
        layout = QVBoxLayout(dialog)
        table = QTableWidget(len(self.analyser.raw_data.issues), 3)
        table.setHorizontalHeaderLabels(["原始 Excel 行", "原因", "同步排除"])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for i, issue in enumerate(self.analyser.raw_data.issues):
            for j, v in enumerate((issue["row"], issue["reason"], "是" if issue["excluded"] else "否")):
                table.setItem(i, j, QTableWidgetItem(str(v)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(table)
        layout.addWidget(QLabel("空值、非数值和公式未求值整行同步排除；文本数字转换单独记录。原始值保存在分析记录与导出中。"))
        dialog.exec()

    def closeEvent(self, event):
        if self.confirm_unsaved():
            event.accept()
        else:
            event.ignore()

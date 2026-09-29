import numpy as np
import pytest
from PySide6.QtCore import Qt, QPointF, QTimer, QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QMessageBox, QApplication
from mech_analyser.experiment.concrete.ui import ConcreteWindow, ImportDialog
from mech_analyser.experiment.registry import Registry
from mech_analyser.config import DEFAULT_DESKTOP_EXPERIMENT


@pytest.fixture
def window(qtbot, analysis):
    w = ConcreteWindow()
    qtbot.addWidget(w, before_close_func=lambda widget: setattr(widget, 'dirty', False))
    w.set_analyser(analysis)
    w.show()
    qtbot.wait(80)
    yield w
    w.dirty = False
    w.close()


def test_workspace_registered(qtbot):
    w = Registry.desktop_registry().create_desktop(DEFAULT_DESKTOP_EXPERIMENT)
    qtbot.addWidget(w)
    assert isinstance(w, ConcreteWindow)


def test_single_sheet_auto_selection(workbook):
    d = ImportDialog(workbook)
    assert d.sheet.currentData() == '5.0MPa_TEST-1350-1'
    assert d.build_settings().units['axial'] == 'mm/mm'
    d.close()


def test_sign_flip_requires_consistent_note(workbook):
    d = ImportDialog(workbook)
    d.signs['hoop'].setCurrentIndex(1)
    with pytest.raises(ValueError, match='反转符号'):
        d.build_settings()
    d.sign_note.setText('源环胀为正，乘 -1 转为环胀负；来源仍待核查')
    assert d.build_settings().signs['hoop'] == -1
    d.close()


def test_multi_sheet_waits_for_choice(workbook):
    import openpyxl
    wb = openpyxl.load_workbook(workbook)
    ws = wb.create_sheet('second')
    ws.append(['轴向应变','环向应变','轴向应力'])
    ws.append([1,2,3])
    wb.save(workbook)
    d = ImportDialog(workbook)
    assert d.sheet.currentData() == ''
    assert d.preview.rowCount() == 0
    d.sheet.setCurrentText('second')
    with pytest.raises(ValueError,match='单位未知'):
        d.build_settings()
    d.close()


def test_numeric_region_three_views_link(window):
    window.low.setValue(.25)
    window.high.setValue(.45)
    a = window.analyser
    n = len(a.selected)
    for panel in window.panels:
        assert len(panel.curves[1].xData) == n
    window.panels[0].region.setRegion((.3*122,.5*122))
    assert window.low.value() == pytest.approx(.3)
    assert a.parameters.low == pytest.approx(.3)
    assert np.array_equal(window.panels[2].curves[1].xData, a.selected.axial)
    assert np.array_equal(window.panels[1].curves[1].xData, a.selected.hoop)


def test_actual_mouse_drag_updates_result(window, qtbot):
    panel = window.panels[0]
    plot = panel.plot
    vb = plot.getPlotItem().vb
    low = panel.region.getRegion()[0]
    x = .0025
    start = plot.mapFromScene(vb.mapViewToScene(QPointF(x, low)))
    end = plot.mapFromScene(vb.mapViewToScene(QPointF(x, 122*.28)))
    before = window.analyser.selected.row.tolist()
    qtbot.mouseMove(plot.viewport(), pos=start)
    qtbot.wait(30)
    qtbot.mousePress(plot.viewport(), Qt.MouseButton.LeftButton, pos=start)
    for t in np.linspace(.1, 1, 10):
        pos = start + (end-start)*float(t)
        event = QMouseEvent(QEvent.Type.MouseMove, QPointF(pos),
            QPointF(plot.viewport().mapToGlobal(pos)), Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(plot.viewport(), event)
        qtbot.wait(15)
    qtbot.mouseRelease(plot.viewport(), Qt.MouseButton.LeftButton, pos=end)
    qtbot.wait(80)
    assert window.analyser.selected.row.tolist() != before
    assert window.low.value() == pytest.approx(.28, abs=.02)


def test_mode_origin_branch_changes(window):
    window.mode.setCurrentIndex(window.mode.findData('strain'))
    window.low.setValue(.001)
    window.high.setValue(.002)
    window.origin.setChecked(True)
    assert window.analyser.parameters.through_origin
    assert window.analyser.result['E']['intercept'] == 0
    window.review.setChecked(True)
    window.branch_start.setValue(40)
    assert not window.review.isChecked()
    assert window.analyser.selected.row.min() >= 40


@pytest.mark.parametrize('choice,expected', [('取消切换',False),('放弃本次改动',True)])
def test_unsaved_real_dialog(window, choice, expected):
    def click():
        msg = QApplication.activeModalWidget()
        assert isinstance(msg, QMessageBox)
        next(b for b in msg.buttons() if b.text() == choice).click()
    QTimer.singleShot(30, click)
    assert window.confirm_unsaved() == expected

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import pytest
from mech_analyser.experiment.concrete.preferences import load_default, save_default, settings_path
from mech_analyser.experiment.concrete.analyser import Analyser
from mech_analyser.experiment.concrete.persistence import save_analysis, load_analysis
from mech_analyser.experiment.concrete.collation import export_current
from mech_analyser.experiment.concrete.presentation import fit_result_html


def test_defaults_survive_restart_but_not_override_analysis(analysis, tmp_path):
    assert (analysis.parameters.low, analysis.parameters.high) == (.2, .5)
    path = tmp_path / 'saved.mca.json'
    save_analysis(analysis, path)
    save_default('ratio', .3, .6)
    output = subprocess.check_output([sys.executable, '-c', 'import json; from mech_analyser.experiment.concrete.preferences import load_default; print(json.dumps(load_default()))'], env=os.environ.copy())
    assert json.loads(output)['high'] == .6
    new = Analyser(analysis.raw_data)
    assert (new.parameters.low, new.parameters.high) == (.3, .6)
    old = load_analysis(path)
    assert (old.parameters.low, old.parameters.high) == (.2, .5)
    with pytest.raises(ValueError): save_default('ratio', .6, .3)
    assert load_default()['high'] == .6
    settings_path().write_text('broken', encoding='utf-8')
    assert load_default()['high'] == .5


def test_export_formats(analysis, tmp_path):
    folder = export_current(analysis, tmp_path, ('png', 'svg'))
    for stem in ('全范围图', '局部放大图'):
        assert (folder / (stem+'.png')).is_file()
        root = ET.parse(folder / (stem+'.svg')).getroot()
        assert root.tag.endswith('svg')
    other = export_current(analysis, tmp_path, ('svg',))
    assert len(list(other.glob('*.svg'))) == 2
    assert not list(other.glob('*.png'))
    with pytest.raises(ValueError): export_current(analysis, tmp_path, ())


def test_plot_r2_uses_two_stress_regressions(analysis):
    analysis.result['E']['r2'] = .98761
    analysis.result['kh']['r2'] = .34561
    rendered = fit_result_html(analysis)
    assert '0.988' in rendered and '0.346' in rendered
    assert '轴' in rendered and '环' in rendered


def test_ui_save_and_export_selection(qtbot, analysis, monkeypatch, tmp_path):
    from mech_analyser.experiment.concrete import ui
    w = ui.ConcreteWindow()
    qtbot.addWidget(w, before_close_func=lambda widget: setattr(widget, 'dirty', False))
    w.set_analyser(analysis)
    monkeypatch.setattr(ui.QMessageBox, 'information', lambda *args: None)
    monkeypatch.setattr(ui.QMessageBox, 'warning', lambda *args: None)
    w.low.setValue(.25)
    w.high.setValue(.55)
    w.save_default_button.click()
    assert load_default() == dict(mode='ratio', low=.25, high=.55)
    assert '0.25' in w.default_hint.text()
    exported = []
    monkeypatch.setattr(ui.QFileDialog, 'getExistingDirectory', lambda *args: str(tmp_path))
    monkeypatch.setattr(ui, 'export_current', lambda a, parent, formats: exported.append(formats) or tmp_path)
    w.export_formats['svg'].setChecked(True)
    w.export_clicked()
    assert exported == [['png', 'svg']]
    for check in w.export_formats.values(): check.setChecked(False)
    w.export_clicked()
    assert len(exported) == 1

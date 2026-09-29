import pytest
from PySide6.QtWidgets import QInputDialog
from mech_analyser.experiment.concrete.ui import ConcreteWindow
from mech_analyser.experiment.concrete.presentation import parameter_text, parameter_rows
from mech_analyser.experiment.concrete.persistence import save_analysis, load_analysis
from mech_analyser.experiment.concrete.collation import summary


def window(qtbot, analysis):
    w = ConcreteWindow()
    qtbot.addWidget(w, before_close_func=lambda widget: setattr(widget, 'dirty', False))
    w.set_analyser(analysis)
    w.show()
    return w


def test_fit_statistics_refresh_and_failure(qtbot, analysis):
    w = window(qtbot, analysis)
    for key in ('E', 'kh'):
        assert w.fit_metrics[key, 'r2'].text() == f"{analysis.result[key]['r2']:.6f}"
        assert w.fit_metrics[key, 'n'].text() == str(analysis.result[key]['n'])
    w.low.setValue(.8)
    assert analysis.result['errors']
    assert w.fit_metrics['E', 'r2'].text() == '—'
    assert w.fit_metrics['kh', 'n'].text() == '0'
    w.low.setValue(.2)
    assert not analysis.result['errors']
    assert w.fit_metrics['E', 'r2'].text() != '—'


def test_triaxial_metadata_visibility_and_roundtrip(qtbot, analysis, tmp_path):
    w = window(qtbot, analysis)
    assert not w.confining_row.isVisible()
    original = analysis.result['nu']
    w.fields['test_type'].setText('三轴压缩试验')
    assert w.confining_row.isVisible()
    assert '围压：未填写 MPa' in parameter_text(analysis)
    w.fields['confining_pressure'].setText('2.5')
    assert parameter_text(analysis).startswith('三轴压缩试验\n围压：2.5 MPa\n材料：')
    assert parameter_rows(analysis)[0] == ('围压', '2.5 MPa')
    assert summary(analysis)['围压_MPa'] == '2.5'
    assert analysis.result['nu'] == original
    save_analysis(analysis, tmp_path/'tri.mca.json')
    restored = load_analysis(tmp_path/'tri.mca.json')
    w.set_analyser(restored)
    assert w.confining_row.isVisible()
    assert w.fields['confining_pressure'].text() == '2.5'
    w.fields['test_type'].setText('单轴压缩试验')
    assert not w.confining_row.isVisible()
    assert '围压' not in parameter_text(restored)
    assert summary(restored)['围压_MPa'] == ''
    w.fields['test_type'].setText('三轴压缩试验')
    assert w.fields['confining_pressure'].text() == '2.5'


def test_custom_confining_pressure(qtbot, analysis, monkeypatch):
    w = window(qtbot, analysis)
    w.fields['test_type'].setText('三轴压缩试验')
    f = w.fields['confining_pressure']
    assert all(f.findData(str(x)) >= 0 for x in (2.5, 5, 7.5, 10))
    monkeypatch.setattr(QInputDialog, 'getDouble', lambda *args: (6.25, True))
    f.setCurrentIndex(f.findText('自定义…'))
    f._custom()
    assert analysis.metadata['confining_pressure'] == '6.25'
    monkeypatch.setattr(QInputDialog, 'getDouble', lambda *args: (0, False))
    f.setCurrentIndex(f.findText('自定义…'))
    f._custom()
    assert analysis.metadata['confining_pressure'] == '6.25'

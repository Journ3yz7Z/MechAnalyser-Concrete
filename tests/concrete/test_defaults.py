from mech_analyser.experiment.concrete.defaults import DEFAULT_METADATA, fill_defaults
from mech_analyser.experiment.concrete.analyser import Analyser
from mech_analyser.experiment.concrete.persistence import save_analysis, load_analysis
from mech_analyser.experiment.concrete.ui import ConcreteWindow, ChoiceField
from mech_analyser.experiment.concrete.presentation import parameter_text


def test_defaults_preserve_existing_and_roundtrip(analysis, tmp_path):
    a = Analyser(analysis.raw_data, metadata={'material': '混凝土', 'pressure': '5', 'water_content': ' ', 'curing_days': '14'})
    assert a.metadata['material'] == '混凝土'
    assert a.metadata['pressure'] == '5'
    assert a.metadata['curing_days'] == '14'
    assert a.metadata['water_content'] == '13'
    assert a.metadata['injection_hours'] == '24'
    save_analysis(a, tmp_path/'a.mca.json')
    b = load_analysis(tmp_path/'a.mca.json')
    assert b.metadata == a.metadata
    assert not fill_defaults(b.metadata)


def test_default_controls_and_custom_water(qtbot, analysis):
    a = Analyser(analysis.raw_data)
    w = ConcreteWindow()
    qtbot.addWidget(w, before_close_func=lambda widget: setattr(widget,'dirty',False))
    w.set_analyser(a)
    for key, value in DEFAULT_METADATA.items():
        assert w.fields[key].text() == value
        assert a.metadata[key] == value
    f = w.fields['water_content']
    assert isinstance(f, ChoiceField)
    assert all(f.findData(v)>=0 for v in ('13','15','17'))
    assert f.findText('自定义…')>=0
    f.setText('16.5')
    assert a.metadata['water_content'] == '16.5'
    assert '含水率：16.5 %' in parameter_text(a)
    assert '养护天数：28 天' in parameter_text(a)


def test_zero_pressure_time_link(qtbot, analysis, tmp_path):
    a=Analyser(analysis.raw_data)
    w=ConcreteWindow()
    qtbot.addWidget(w,before_close_func=lambda widget:setattr(widget,'dirty',False))
    w.set_analyser(a)
    assert not w.fields['injection_hours'].isEnabled()
    assert '压注时间' not in parameter_text(a)
    w.fields['pressure'].setText('2.5')
    assert w.fields['injection_hours'].isEnabled()
    w.fields['injection_hours'].setText('3')
    w.fields['pressure'].setText('0.0')
    assert not w.fields['injection_hours'].isEnabled()
    assert a.metadata['injection_hours']=='3'
    assert '压注时间' not in parameter_text(a)
    save_analysis(a,tmp_path/'zero.mca.json')
    restored=load_analysis(tmp_path/'zero.mca.json')
    w.set_analyser(restored)
    assert not w.fields['injection_hours'].isEnabled()
    w.fields['pressure'].setText('5')
    assert w.fields['injection_hours'].isEnabled()
    assert w.fields['injection_hours'].text()=='3'
    assert '压注时间：3 小时' in parameter_text(restored)

import pytest
from mech_analyser.experiment.concrete.import_check import compare_layout


def test_auxiliary_and_whitespace():
    base=[[' a ']+['x']*8+[None]*4+['Stress'],['mm']*9]
    other=[['a']+['x']*8+[None]*5+['Stress'],[' mm ']*9]
    assert compare_layout(base,other,{2,5,7,8},'other')
    with pytest.raises(ValueError,match='第14列'):
        compare_layout(base,other,{13},'other')


def test_units_and_order():
    base=[list('abcdefghi'),['mm']*9]
    other=[list('abcdefghi'),['mm']*8+['%']]
    with pytest.raises(ValueError,match='第9列单位'):
        compare_layout(base,other,{7,8},'other')
    other=[list('bacdefghi'),['mm']*9]
    with pytest.raises(ValueError,match='第1列列名'):
        compare_layout(base,other,{7,8},'other')


def test_data_not_units():
    assert not compare_layout([list('abc'),[1,2,3]],[list('abc'),[4,5,6]],{0,1,2},'other')

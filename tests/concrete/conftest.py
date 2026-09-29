import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import numpy as np
import openpyxl
import pytest
from mech_analyser.experiment.concrete.data import ImportSettings, RawData
from mech_analyser.experiment.concrete.analyser import Analyser


@pytest.fixture(autouse=True)
def qt_runtime(qapp):
    return qapp


@pytest.fixture
def workbook(tmp_path):
    path = tmp_path / "SYNTHETIC_TEST_ONLY.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "5.0MPa_TEST-1350-1"
    ws.append(["轴向应变（mm/mm）", "环向应变（mm/mm）", "轴向应力（MPa）"])
    for e in np.linspace(0, .004, 121):
        ws.append([float(e), float(-.00001 - .2 * e), float(2 + 30000 * e)])
    for i, stress in enumerate(np.linspace(120, 5, 100)):
        ws.append([.0041 + i * .0001, -.001 - i * .00002, float(stress)])
    wb.save(path)
    return path


@pytest.fixture
def settings():
    return ImportSettings("5.0MPa_TEST-1350-1", 1,
        dict(axial=0, hoop=1, stress=2), dict(axial="mm/mm", hoop="mm/mm", stress="MPa"),
        dict(axial=1, hoop=1, stress=1), "测试用途：轴压正环胀负", "明确标注为测试用途的合成数据")


@pytest.fixture
def analysis(workbook, settings):
    return Analyser(RawData.load_sheet(workbook, settings), metadata={"specimen": "TEST-1350-1", "pressure": "5.0"})

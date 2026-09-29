"""Concrete regression within the upstream Analyser/Data/Phase architecture."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from mech_analyser.experiment.analyser import Analyser as BaseAnalyser, Parameters as BaseParameters
from mech_analyser.experiment.data import SummaryData, SummaryTranscoder, ProcessedData, ProcessedTranscoder
from mech_analyser.experiment.phase import Phase
from .phase import default_branch, select_points
from .defaults import fill_defaults


@dataclass
class Parameters(BaseParameters):
    mode: str = "ratio"
    low: float = 0.2
    high: float = 0.5
    branch_start: int = 2
    branch_end: int = 3
    through_origin: bool = False
    branch_method: str = "从首次峰值逆向识别最终上升段；5%峰值回落阈值（建议，待人工检查）"


def regression(x, y, through_origin=False):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 3:
        raise ValueError(f"有效同步点不足 3 个（当前 {len(x)} 个）")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("拟合数据含非有限值")
    if np.ptp(x) <= 1e-12:
        raise ValueError("应变变化过小（≤ 1e-12），无法拟合")
    if through_origin:
        slope = float(np.dot(x, y) / np.dot(x, x))
        intercept = 0.0
    else:
        # Centred least squares is stable for concrete strains of order 1e-4.
        dx, dy = x - x.mean(), y - y.mean()
        slope = float(np.dot(dx, dy) / np.dot(dx, dx))
        intercept = float(y.mean() - slope * x.mean())
    predicted = intercept + slope * x
    total = float(np.dot(y - y.mean(), y - y.mean()))
    residual = float(np.dot(y - predicted, y - predicted))
    r2 = None if total <= 1e-30 else 1 - residual / total
    if not np.isfinite([slope, intercept]).all() or (r2 is not None and not np.isfinite(r2)):
        raise ValueError("回归数值溢出，无法生成有效结果")
    return dict(slope=slope, intercept=intercept, r2=r2, n=len(x))


class Analyser(BaseAnalyser):
    def __init__(self, raw_data, parameters=None, metadata=None):
        if parameters is None:
            from .preferences import load_default
            parameters = Parameters(**load_default())
            try:
                parameters.branch_start, parameters.branch_end = default_branch(raw_data.frame)
            except ValueError:
                parameters.branch_start = int(raw_data.frame.row.min())
                parameters.branch_end = int(raw_data.frame.row.max())
        super().__init__(parameters, raw_data, SummaryData(pd.DataFrame(), SummaryTranscoder()), [])
        self.metadata = metadata or {}
        fill_defaults(self.metadata)
        self.result = {}
        self.selected = raw_data.frame.iloc[0:0].copy()
        self.reviewed = False
        self.notes = ""
        self.source_state = "匹配"
        self.analyse()

    def analyse(self):
        self.reviewed = False
        self.result = {"status": "计算失败", "errors": [], "warnings": [], "n": 0}
        self.selected = self.raw_data.frame.iloc[0:0].copy()
        r, f = self.result, self.raw_data.frame
        settings = self.raw_data.settings
        force = f.get("force_kN")
        if settings.force_column is not None:
            good_force = f[np.isfinite(force)] if force is not None else f.iloc[:0]
            if not good_force.empty:
                peak_force = good_force.loc[good_force.force_kN.idxmax()]
                r.update(peak_force_kN=float(peak_force.force_kN), peak_force_row=int(peak_force.row),
                         peak_force_source="轴力列实测（按记录单位/符号转换）")
            else:
                r["warnings"].append("已指定轴力列但没有有效数值，请核查；未自动改用换算")
        elif settings.area_mm2 is not None:
            good_stress = f[np.isfinite(f.stress)]
            if not good_stress.empty:
                peak_force = good_stress.loc[good_stress.stress.idxmax()]
                r.update(peak_force_kN=float(peak_force.stress * settings.area_mm2 / 1000),
                         peak_force_row=int(peak_force.row), peak_force_source="应力×输入截面积换算")
        finite = f[np.isfinite(f.stress)]
        if not finite.empty:
            peak = finite.loc[finite.stress.idxmax()]
            r.update(peak_stress_MPa=float(peak.stress), peak_row=int(peak.row),
                     peak_axial_strain=float(peak.axial) if np.isfinite(peak.axial) else None)
        try:
            self.selected, info, warns = select_points(f, self.parameters)
            r.update(info)
            r["warnings"].extend(warns)
            s = self.selected
            r["n"] = len(s)
            if len(s) < 3:
                raise ValueError(f"有效同步点不足 3 个（当前 {len(s)} 个）")
            r["actual"] = {c: [float(s[c].min()), float(s[c].max())] for c in ("axial", "hoop", "stress", "row")}
            r["E"] = regression(s.axial, s.stress, self.parameters.through_origin)
            r["kh"] = regression(s.hoop, s.stress, self.parameters.through_origin)
            r["poisson"] = regression(s.axial, s.hoop, self.parameters.through_origin)
            r["nu_strain"] = -r["poisson"]["slope"]
            r["nu_method"] = "ASTM D7012-14 Eq. (7): -E/kh"
            r["E_GPa"] = r["E"]["slope"] / 1000
            if abs(r["kh"]["slope"]) <= 1e-9:
                r["nu_ratio"] = None
                r["warnings"].append("环向曲线斜率接近零（|kh| ≤ 1e-9 MPa），斜率比不可用")
            else:
                r["nu_ratio"] = -r["E"]["slope"] / r["kh"]["slope"]
            r["nu"] = r["nu_ratio"]
            for key, label in (("E", "轴向"), ("kh", "环向"), ("poisson", "应变—应变参考")):
                fit = r[key]
                if fit["r2"] is None or fit["r2"] < 0.95:
                    r["warnings"].append(f"{label} R² 低于 0.95 或不可定义：请检查区间；未自动删点")
            if r["E"]["slope"] <= 0 or r["kh"]["slope"] >= 0:
                r["warnings"].append("斜率符号与轴压正、环胀负约定不符，请核查；未取绝对值")
            if r["nu"] is not None and not 0 <= r["nu"] <= 0.5:
                r["warnings"].append("主要方法泊松比不在 [0, 0.5] 检查范围内，请核查通道、符号和区间")
            if not 0 <= r["nu_strain"] <= 0.5:
                r["warnings"].append("应变回归参考泊松比不在 [0, 0.5] 检查范围内")
            r["status"] = "已计算（未人工检查）"
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as exc:
            r["errors"].append(str(exc))
            # No partial modulus masquerading as a complete three-channel calculation.
            for key in ("E", "kh", "poisson", "nu", "E_GPa", "nu_ratio", "nu_strain", "nu_method"):
                r.pop(key, None)
        excluded = sum(i["excluded"] for i in self.raw_data.issues)
        if excluded:
            r["warnings"].append(f"全 sheet 有 {excluded} 行无效，三通道同步排除；详见数据问题表")
        if "待核" in self.raw_data.settings.channel_source or "待核" in self.raw_data.settings.sign_note:
            r["warnings"].append("通道来源或符号约定待核查，结果仅为所选数据的回归结果")
        self._summary_data._frame = pd.DataFrame([{"status": r["status"], "n": r["n"]}])
        processed = ProcessedData(self.selected, ProcessedTranscoder())
        if self.phases:
            old = self.phases[0].processed_data
            self.phases[0].processed_data = processed
            old.plot.deleteLater()
        else:
            self.phases.append(Phase(self.raw_data, processed, "选定加载分支内同步拟合点"))
        return r

    @property
    def status(self):
        if self.source_state != "匹配":
            return f"{self.source_state}（保存快照结果）"
        return "已人工检查" if self.reviewed else self.result["status"]

    def save(self, output_file, **kwargs):
        from .persistence import save_analysis
        return save_analysis(self, output_file)

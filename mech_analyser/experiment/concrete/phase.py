"""Loading branch selection; range masks are never applied to the whole curve."""
import numpy as np


def default_branch(frame):
    # Identify peak using every finite stress, even when another channel is missing.
    finite = frame[np.isfinite(frame.stress)]
    if finite.empty:
        raise ValueError("轴向应力通道没有有效值")
    peak_idx = finite.stress.idxmax()
    peak = float(frame.loc[peak_idx, "stress"])
    if peak <= 0:
        raise ValueError("最大轴向应力不为正，请核查压缩应力符号设置")
    pre = finite.loc[:peak_idx]
    # Walk backwards along the final rising branch. A prior stress above the
    # running valley by >5% of peak indicates a substantial unload/reload cycle.
    # The threshold is an explicit heuristic, not a material standard.
    start_idx = peak_idx
    valley = peak
    for idx, stress in reversed(list(pre.stress.items())):
        if stress > valley + 0.05 * peak:
            break
        if stress < valley:
            valley, start_idx = float(stress), idx
    return int(frame.loc[start_idx, "row"]), int(frame.loc[peak_idx, "row"])


def select_points(frame, parameters):
    start, end = parameters.branch_start, parameters.branch_end
    if start >= end or start < frame.row.min() or end > frame.row.max():
        raise ValueError("加载分支起止行无效：须在原始行范围内，且起行小于止行")
    branch = frame[(frame.row >= start) & (frame.row <= end)]
    finite_stress = branch[np.isfinite(branch.stress)]
    if finite_stress.empty:
        raise ValueError("所选分支没有有效应力")
    peak_idx = finite_stress.stress.idxmax()
    peak = float(frame.loc[peak_idx, "stress"])
    if peak <= 0:
        raise ValueError("分支峰值应力不为正，请核查分支和符号")
    if parameters.low >= parameters.high or not np.isfinite([parameters.low, parameters.high]).all():
        raise ValueError("区间下限必须小于上限且均为有限数值")
    if parameters.mode == "ratio":
        if not 0 <= parameters.low < parameters.high <= 1:
            raise ValueError("峰值比例必须满足 0 ≤ 下限 < 上限 ≤ 1")
        values = branch.stress
        low, high = parameters.low * peak, parameters.high * peak
    elif parameters.mode == "stress":
        values, low, high = branch.stress, parameters.low, parameters.high
    elif parameters.mode == "strain":
        values, low, high = branch.axial, parameters.low, parameters.high
    else:
        raise ValueError("未知区间选择规则")
    mask = branch.valid & (values >= low) & (values <= high)
    selected = branch.loc[mask].copy()
    # Small decreases from quantisation/noise are retained, never silently removed.
    stresses = finite_stress.stress.to_numpy()
    significant = np.where(np.diff(stresses) < -0.05 * peak)[0]
    warnings = []
    if len(significant):
        warnings.append("分支内有超过峰值 5% 的单步应力下降，请检查卸载/再加载并人工修正起止行")
    if int(frame.loc[peak_idx, "row"]) < end:
        warnings.append("人工分支包含峰后采样点，请确认加载分支终止行")
    return selected, dict(branch_peak_stress_MPa=peak, branch_peak_row=int(frame.loc[peak_idx, "row"]),
                          threshold_low=float(low), threshold_high=float(high)), warnings

"""Per-user defaults for new imports; saved analyses retain their parameters."""
import json
import math
import os
from pathlib import Path

FACTORY = dict(mode="ratio", low=0.2, high=0.5)


def settings_path():
    override = os.environ.get("MECHANALYSER_PREFERENCES")
    return Path(override) if override else Path(os.environ.get("APPDATA", Path.home())) / "MechAnalyser-Concrete" / "preferences.json"


def validate(value):
    mode = value["mode"]
    low, high = float(value["low"]), float(value["high"])
    if mode not in ("ratio", "stress", "strain") or not all(map(math.isfinite, (low, high))) or low >= high:
        raise ValueError("请选择有效的依据，且下限必须小于上限。")
    if mode == "ratio" and not 0 <= low < high <= 1:
        raise ValueError("峰值比例必须满足 0 ≤ 下限 < 上限 ≤ 1。")
    return dict(mode=mode, low=low, high=high)


def load_default():
    try:
        return validate(json.loads(settings_path().read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, KeyError):
        return FACTORY.copy()


def save_default(mode, low, high):
    value = validate(dict(mode=mode, low=low, high=high))
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)
    return value

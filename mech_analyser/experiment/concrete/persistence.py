"""Versioned single-specimen JSON; no dynamic class loading from saved records."""
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import uuid
import tempfile
from . import VERSION, UPSTREAM_COMMIT
from .data import RawData, file_hash
from .analyser import Analyser, Parameters

SCHEMA = "MechAnalyser.concrete.single.v1"


def source_state(analyser):
    path = Path(analyser.raw_data.source)
    try:
        state = "匹配" if file_hash(path) == analyser.raw_data.fingerprint else "源文件已改变，需重新导入计算"
    except OSError:
        state = "源文件不可用，使用保存快照"
    analyser.source_state = state
    if state != "匹配":
        analyser.reviewed = False
    return state


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":"))


def save_analysis(analyser, path):
    path = Path(path)
    if path.resolve() == Path(analyser.raw_data.source).resolve() or (
            path.exists() and Path(analyser.raw_data.source).exists() and
            os.path.samefile(path, analyser.raw_data.source)):
        raise ValueError("禁止覆盖原始工作簿")
    if not path.name.endswith(".mca.json"):
        raise ValueError("分析记录必须使用 .mca.json 扩展名")
    source_state(analyser)
    payload = dict(schema=SCHEMA, app_version=VERSION, upstream_commit=UPSTREAM_COMMIT,
                   saved_utc=datetime.now(timezone.utc).isoformat(), raw=analyser.raw_data.snapshot(),
                   parameters=asdict(analyser.parameters), metadata=analyser.metadata,
                   result=analyser.result, reviewed=analyser.reviewed, notes=analyser.notes,
                   source_state=analyser.source_state)
    payload["content_sha256"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return path


def load_analysis(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    checksum = d.pop("content_sha256", None)
    if checksum != hashlib.sha256(canonical(d).encode("utf-8")).hexdigest():
        raise ValueError("分析记录校验失败，文件可能被修改或损坏")
    if d["schema"] != SCHEMA:
        raise ValueError("不支持的分析记录版本")
    a = Analyser(RawData.from_snapshot(d["raw"]), Parameters(**d["parameters"]), d["metadata"])
    if canonical(a.result) != canonical(d["result"]):
        if d['result'].get('nu_method') != a.result.get('nu_method'):
            a.result["warnings"].append("旧版记录已按1.6斜率比法重新计算主要泊松比（ν=-E/kh）；原选区保留，应变回归值转为参考，请重新检查")
        else:
            a.result["warnings"].append("当前计算与保存结果不一致，请重新检查（可能因软件版本变化）")
        a.reviewed = False
    else:
        a.reviewed = bool(d["reviewed"])
    a.notes = d["notes"]
    source_state(a)
    return a


def save_workspace(analysers, path, active=0):
    path = Path(path)
    if not path.name.endswith(".mcw.json"):
        raise ValueError("工作簿分析必须使用 .mcw.json")
    if any(path.resolve() == Path(a.raw_data.source).resolve() for a in analysers):
        raise ValueError("禁止覆盖原始工作簿")
    records = []
    with tempfile.TemporaryDirectory(prefix="mechanalyser-") as td:
        for i, a in enumerate(analysers):
            record = Path(td) / f"{i}.mca.json"
            save_analysis(a, record)
            records.append(json.loads(record.read_text(encoding="utf-8")))
    payload = dict(schema="MechAnalyser.concrete.workbook.v1", active=active, records=records)
    payload["content_sha256"] = hashlib.sha256(canonical(payload).encode()).hexdigest()
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def load_workspace(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    checksum = d.pop("content_sha256", None)
    if checksum != hashlib.sha256(canonical(d).encode()).hexdigest() or d.get("schema") != "MechAnalyser.concrete.workbook.v1":
        raise ValueError("工作簿分析记录校验失败")
    if not d["records"] or not 0 <= d["active"] < len(d["records"]):
        raise ValueError("工作簿试样列表或当前索引无效")
    analysers = []
    with tempfile.TemporaryDirectory(prefix="mechanalyser-") as td:
        for i, record in enumerate(d["records"]):
            p = Path(td) / f"{i}.mca.json"
            p.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            analysers.append(load_analysis(p))
    return analysers, d["active"]

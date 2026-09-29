"""Single-specimen concrete workspace for MechAnalyser (MIT)."""
INSTRUMENT = "Excel 三通道"
EXPERIMENT = "混凝土单轴压缩"
SINGLE_SAMPLE = True
UPSTREAM_COMMIT = "76d8ea65704edee4bffa385eb404e557f47401c7"
VERSION = "1.6.4"


def create_workspace():
    from .ui import ConcreteWindow
    return ConcreteWindow()

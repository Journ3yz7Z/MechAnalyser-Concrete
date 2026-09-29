# Modules to be dynamically imported
EXPERIMENT_MODULES: list[str] = [
    "mech_analyser.experiment.instron_68tm.failure",
    "mech_analyser.experiment.instron_68tm.stepwise",
    "mech_analyser.experiment.microtester_g2.microindentation",
    "mech_analyser.experiment.concrete",
]

DEFAULT_DESKTOP_EXPERIMENT = "混凝土单轴压缩"

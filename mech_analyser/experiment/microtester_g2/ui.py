import mech_analyser.experiment.microtester_g2.analyser as ma_analyser
import mech_analyser.experiment.ui as ma_ui

from typing import cast


class ConfigWidget(ma_ui.ConfigWidget):
    """
    Base class for all Microtester G2 user interface configuration widgets.

    Args:
        view: Generated user interface configuration widget.
        parameters: The parameters to use when analysing the experiment.
    """

    def __init__(self, view: ma_ui.ViewBase, parameters: ma_analyser.Parameters) -> None:
        super().__init__(view, parameters)

    @property
    def parameters(self) -> ma_analyser.Parameters:
        return cast(ma_analyser.Parameters, self._parameters)

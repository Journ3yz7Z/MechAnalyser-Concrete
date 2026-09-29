import mech_analyser.experiment.microtester_g2.microindentation.analyser as ma_analyser
import mech_analyser.experiment.microtester_g2.microindentation.data as ma_data
import mech_analyser.experiment.microtester_g2.microindentation.view as ma_view
import mech_analyser.experiment.microtester_g2.ui as ma_ui
import mech_analyser.study.sample as ma_sample

from typing import cast


class ConfigWidget(ma_ui.ConfigWidget):
    """
    Microtester G2 microindentation experiment user interface configuration widget.
    """

    def __init__(self) -> None:
        super().__init__(ma_view.Ui_w_Microindentation(), ma_analyser.Parameters())  # type: ignore

    @property
    def parameters(self) -> ma_analyser.Parameters:
        return cast(ma_analyser.Parameters, self._parameters)

    @property
    def view(self) -> ma_view.Ui_w_Microindentation:  # type: ignore
        return cast(ma_view.Ui_w_Microindentation, self._view)

    def create_analyser(
        self,
        sample: ma_sample.Sample,
        raw_transcoder: ma_data.ma_data.ma_data.RawTranscoder,
        processed_transcoder: ma_data.ma_data.ma_data.ProcessedTranscoder,
        summary_transcoder: ma_data.ma_data.ma_data.SummaryTranscoder,
    ) -> None:
        """
        Creates the experiment analyser.

        Args:
            sample: The sample being tested in the experiment.
            raw_transcoder: The raw data transcoder.
            processed_transcoder: The processed data transcoder.
            summary_transcoder: The summary data transcoder.
        """

        sample.analyser = ma_analyser.Analyser(
            sample.input_file,
            self.parameters,
            cast(ma_data.ma_data.RawTranscoder, raw_transcoder),
            cast(ma_data.ProcessedTranscoder, processed_transcoder),
            cast(ma_data.SummaryTranscoder, summary_transcoder),
        )

    def init(self) -> None:
        """
        Initialises the configuration widget by setting the input fields to the defaults
        of the parameters to use when analysing the experiment and connecting any signals
        with an associated slot.
        """

        # Set the input fields to the parameter defaults
        self.view.sb_Cycles.setValue(self.parameters.cycles)
        self.view.sb_SamplesToSkip.setValue(self.parameters.samples_to_skip)
        self.view.sb_IndenterRadius.setValue(self.parameters.R_um)
        self.view.sb_PoissonsRatio.setValue(self.parameters.v)
        self.view.sb_DeltaRThreshold.setValue(self.parameters.delta_R_threshold)
        self.view.cb_RegressionOffsets.setChecked(self.parameters.use_regression_offsets)
        self.view.cb_OffsetBounds.setChecked(
            self.parameters.use_regression_offsets
            and self.parameters.a_max_um is not None
            and self.parameters.b_max_uN is not None
        )
        self.view.sb_OffsetTipDisplacement.setValue(self.parameters.a_max_um or 0.0)
        self.view.sb_OffsetForce.setValue(self.parameters.b_max_uN or 0.0)

        # Connect signals with slots
        self.view.cb_RegressionOffsets.checkStateChanged.connect(
            self._handle_cb_RegressionOffsets_changed
        )
        self.view.cb_OffsetBounds.checkStateChanged.connect(
            self._handle_cb_OffsetBounds_changed
        )

        # Set initial views
        self._handle_cb_RegressionOffsets_changed()
        self._handle_cb_OffsetBounds_changed()

    def sync_parameters(self) -> None:
        """
        Synchronise the parameters to use when analysing the experiment with the
        configuration widget input fields.
        """

        self.parameters.cycles = self.view.sb_Cycles.value()
        self.parameters.samples_to_skip = self.view.sb_SamplesToSkip.value()
        self.parameters.R_um = self.view.sb_IndenterRadius.value()
        self.parameters.v = self.view.sb_PoissonsRatio.value()
        self.parameters.delta_R_threshold = self.view.sb_DeltaRThreshold.value()
        self.parameters.use_regression_offsets = (
            self.view.cb_RegressionOffsets.isChecked()
        )
        self.parameters.a_max_um = (
            self.view.sb_OffsetTipDisplacement.value()
            if self.view.cb_RegressionOffsets.isChecked()
            and self.view.cb_OffsetBounds.isChecked()
            else None
        )
        self.parameters.b_max_uN = (
            self.view.sb_OffsetForce.value()
            if self.view.cb_RegressionOffsets.isChecked()
            and self.view.cb_OffsetBounds.isChecked()
            else None
        )

    def _handle_cb_OffsetBounds_changed(self) -> None:
        """
        Sets the visibility of sb_OffsetTipDisplacement and sb_OffsetForce to the state of
        cb_RegressionOffsets and cb_OffsetBounds.
        """

        self.view.l_OffsetTipDisplacement.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )
        self.view.l_OffsetForce.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )
        self.view.sb_OffsetTipDisplacement.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )
        self.view.sb_OffsetForce.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )

    def _handle_cb_RegressionOffsets_changed(self) -> None:
        """
        Sets the visibility of cb_OffsetBounds to the state of cb_RegressionOffsets and
        sets the visibility of sb_OffsetTipDisplacement and sb_OffsetForce to the state of
        cb_RegressionOffsets and cb_OffsetBounds.
        """

        self.view.cb_OffsetBounds.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
        )
        self.view.l_OffsetTipDisplacement.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )
        self.view.l_OffsetForce.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )
        self.view.sb_OffsetTipDisplacement.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )
        self.view.sb_OffsetForce.setDisabled(
            not self.view.cb_RegressionOffsets.isChecked()
            or not self.view.cb_OffsetBounds.isChecked()
        )

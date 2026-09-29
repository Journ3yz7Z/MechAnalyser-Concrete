import mech_analyser.experiment.instron_68tm.stepwise.analyser as ma_analyser
import mech_analyser.experiment.instron_68tm.stepwise.data as ma_data
import mech_analyser.experiment.instron_68tm.stepwise.view as ma_view
import mech_analyser.experiment.instron_68tm.ui as ma_ui
import mech_analyser.study.sample as ma_sample

from PySide6.QtWidgets import QFileDialog
from pathlib import Path
from typing import Optional, cast


class ConfigWidget(ma_ui.ConfigWidget):
    """
    Instron 68TM stepwise compression experiment user interface configuration widget.
    """

    def __init__(self) -> None:
        super().__init__(ma_view.Ui_w_Stepwise(), ma_analyser.Parameters())  # type: ignore

        self._properties_csv: Optional[Path] = None

    @property
    def parameters(self) -> ma_analyser.Parameters:
        return cast(ma_analyser.Parameters, self._parameters)

    @property
    def view(self) -> ma_view.Ui_w_Stepwise:  # type: ignore
        return cast(ma_view.Ui_w_Stepwise, self._view)

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

        self.parameters.calculate_sample_parameters(sample.name)

        sample.analyser = ma_analyser.Analyser(
            sample.input_file,
            # NOTE: needed to avoid multiple analysers sharing the one parameters instance
            self.parameters.copy(),
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
        self.view.sb_RelaxationStrainsIntervals.setValue(
            self.parameters.relaxation_strain_intervals
        )
        self.view.sb_RelaxationStrainsStart.setValue(
            self.parameters.relaxation_strain_start_pct
        )
        self.view.sb_Epsilon.setValue(self.parameters.epsilon_pct)
        self.view.sb_RegressionPoints.setValue(
            self.parameters.regression_data_points or 0
        )
        self.view.cb_RegressionPoints.setChecked(
            self.parameters.regression_data_points is not None
        )
        self.view.cb_Properties.setChecked(False)
        self.view.tb_ReadProperties.setText("")
        self.view.sb_Area.setValue(self.parameters.cross_sectional_area_m2 * 1e6)
        self.view.cb_Area.setChecked(
            self.parameters.read_cross_sectional_area
            and self.parameters.properties_file is not None
        )
        self.view.sb_Length.setValue(self.parameters.initial_length_m * 1e3)
        self.view.cb_Length.setChecked(
            self.parameters.read_initial_length
            and self.parameters.properties_file is not None
        )

        # Connect signals with slots
        self.view.cb_RegressionPoints.checkStateChanged.connect(
            self._handle_cb_RegressionPoints_changed
        )
        self.view.cb_Properties.toggled.connect(self._handle_cb_Properties_toggled)
        self.view.pb_ReadProperties.clicked.connect(
            self._handle_pb_ReadProperties_clicked
        )
        self.view.cb_Area.toggled.connect(self._handle_cb_Area_toggled)
        self.view.cb_Length.toggled.connect(self._handle_cb_Length_toggled)

        # Set initial views
        self._handle_cb_RegressionPoints_changed()
        self._handle_cb_Properties_toggled()

    def sync_parameters(self) -> None:
        """
        Synchronise the parameters to use when analysing the experiment with the
        configuration widget input fields.
        """

        self.parameters.relaxation_strain_intervals = (
            self.view.sb_RelaxationStrainsIntervals.value()
        )
        self.parameters.relaxation_strain_start_pct = (
            self.view.sb_RelaxationStrainsStart.value()
        )
        self.parameters.epsilon_pct = self.view.sb_Epsilon.value()
        self.parameters.regression_data_points = (
            self.view.sb_RegressionPoints.value()
            if self.view.cb_RegressionPoints.isChecked()
            else None
        )
        self.parameters.properties_file = (
            self._properties_csv if self.view.cb_Properties.isChecked() else None
        )
        self.parameters.read_cross_sectional_area = (
            self.view.cb_Properties.isChecked() and self.view.cb_Area.isChecked()
        )
        self.parameters.read_initial_length = (
            self.view.cb_Properties.isChecked() and self.view.cb_Length.isChecked()
        )
        self.parameters.cross_sectional_area_m2 = self.view.sb_Area.value() * 1e-6
        self.parameters.initial_length_m = self.view.sb_Length.value() * 1e-3

    def _handle_cb_Area_toggled(self) -> None:
        """
        Enables/disables l_Area and sb_Area.
        """

        self.view.l_Area.setEnabled(not self.view.cb_Area.isChecked())
        self.view.sb_Area.setEnabled(not self.view.cb_Area.isChecked())
        self.view.pb_ReadProperties.setEnabled(
            self.view.cb_Area.isChecked() or self.view.cb_Length.isChecked()
        )
        self.view.tb_ReadProperties.setEnabled(
            self.view.cb_Area.isChecked() or self.view.cb_Length.isChecked()
        )

    def _handle_cb_Length_toggled(self) -> None:
        """
        Enables/disables l_Length and sb_Length.
        """

        self.view.l_Length.setEnabled(not self.view.cb_Length.isChecked())
        self.view.sb_Length.setEnabled(not self.view.cb_Length.isChecked())
        self.view.pb_ReadProperties.setEnabled(
            self.view.cb_Area.isChecked() or self.view.cb_Length.isChecked()
        )
        self.view.tb_ReadProperties.setEnabled(
            self.view.cb_Area.isChecked() or self.view.cb_Length.isChecked()
        )

    def _handle_cb_Properties_toggled(self) -> None:
        """
        Enables/disables pb_ReadProperties, tb_ReadProperties, l_Area, sb_Area, cb_Area,
        l_Length, sb_Length, and cb_Length.
        """

        self.view.pb_ReadProperties.setEnabled(self.view.cb_Properties.isChecked())
        self.view.tb_ReadProperties.setEnabled(self.view.cb_Properties.isChecked())
        self.view.cb_Area.setEnabled(self.view.cb_Properties.isChecked())
        self.view.cb_Length.setEnabled(self.view.cb_Properties.isChecked())

        if self.view.cb_Properties.isChecked():
            self._handle_cb_Area_toggled()
            self._handle_cb_Length_toggled()
        else:
            self.view.l_Area.setEnabled(False)
            self.view.sb_Area.setEnabled(False)
            self.view.l_Length.setEnabled(False)
            self.view.sb_Length.setEnabled(False)

    def _handle_cb_RegressionPoints_changed(self) -> None:
        """
        Sets the visibility of sb_RegressionPoints to the state of
        cb_RegressionPoints.
        """

        self.view.sb_RegressionPoints.setDisabled(
            not self.view.cb_RegressionPoints.isChecked()
        )

    def _handle_pb_ReadProperties_clicked(self) -> None:
        """
        Opens a file dialogue to select a physical properties file.
        """

        # Obtain the CSV
        properties_csv, _ = QFileDialog.getOpenFileName(
            self,
            "Select Physical Properties CSV File",
            "",
            "CSV File (*.csv)",
        )

        # User cancelled the file search
        if not properties_csv:
            return

        self._properties_csv = Path(properties_csv)

        # Update the GUI
        self._update_tb_ReadProperties()

    def _update_tb_ReadProperties(self) -> None:
        """
        Updates the text box showing the selected physical properties file.
        """

        self.view.tb_ReadProperties.setText(
            str(self._properties_csv) if self._properties_csv is not None else ""
        )

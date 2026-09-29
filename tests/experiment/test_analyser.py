import tempfile
from mech_analyser.experiment.analyser import Analyser, Parameters, SerialisedAnalyser
from mech_analyser.experiment.data import (
    ProcessedData,
    ProcessedTranscoder,
    RawData,
    RawTranscoder,
    SummaryData,
    SummaryTranscoder,
    Transcoder,
)
from mech_analyser.experiment.phase import Phase, SerialisedPhase
from mech_analyser.util.serialiser import Serialiser
import pandas as pd
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from typing import Any, Union, cast
import unittest


class TestAnalyser(unittest.TestCase):
    """
    Unit tests for the Analyser class.
    """

    def setUp(self) -> None:
        """
        Set up an Analyser instance and related objects for testing.
        """

        self.app: Union[QApplication, QCoreApplication] = (
            QApplication.instance() or QApplication([])
        )
        self.parameters = Parameters(id="1234")
        self.columns: dict[str, Transcoder.Column] = {
            "Column1": Transcoder.Column(
                name="Column1",
                input_name="Input1 (units)",
                input_header_rows=[0, 1],
                input_header_column=0,
                output_name="Output1 (units)",
                output_header_column=0,
            ),
            "Column2": Transcoder.Column(
                name="Column2",
                input_name="Input2 (units)",
                input_header_rows=[0, 1],
                input_header_column=1,
                output_name="Output2 (units)",
                output_header_column=1,
            ),
        }
        self.raw_data = RawData(
            pd.DataFrame({"Column1": [1, 2, 3], "Column2": ["A", "B", "C"]}),
            RawTranscoder(self.columns),
        )
        self.processed_data: list[ProcessedData] = [
            ProcessedData(
                pd.DataFrame({"Column1": [10, 20, 30], "Column2": ["X1", "Y1", "Z1"]}),
                ProcessedTranscoder(self.columns),
            ),
            ProcessedData(
                pd.DataFrame({"Column1": [11, 21, 31], "Column2": ["X2", "Y2", "Z2"]}),
                ProcessedTranscoder(self.columns),
            ),
        ]
        self.summary_data = SummaryData(
            pd.DataFrame({"Column1": [100, 200, 300], "Column2": ["M", "N", "O"]}),
            SummaryTranscoder(self.columns),
        )
        self.phases: list[Phase] = [
            Phase(self.raw_data, processed_data, f"Phase {i+1}")
            for i, processed_data in enumerate(self.processed_data)
        ]
        self.analyser = Analyser(
            parameters=self.parameters,
            raw_data=self.raw_data,
            summary_data=self.summary_data,
            phases=self.phases,
        )
        self.test_xlsx = Path(
            tempfile.NamedTemporaryFile(delete=True, prefix="test_", suffix=".xlsx").name
        )

    def tearDown(self) -> None:
        """
        Clean up after tests.
        """

        self.test_xlsx.unlink(missing_ok=True)
        self.app.quit()

    def test_initialisation(self) -> None:
        """
        Test that the Analyser class initializes correctly with valid inputs.
        """

        self.assertEqual(self.analyser.parameters, self.parameters)
        self.assertEqual(self.analyser.raw_data, self.raw_data)
        self.assertEqual(self.analyser.summary_data, self.summary_data)
        self.assertEqual(self.analyser.phases, self.phases)
        for i in range(len(self.phases)):
            self.assertEqual(self.analyser.phases[i].raw_data, self.raw_data)
            self.assertEqual(
                self.analyser.phases[i].processed_data, self.processed_data[i]
            )

    def test_parameters_property(self) -> None:
        """
        Test that the parameters property returns the correct value.
        """

        self.assertEqual(self.analyser.parameters, self.parameters)

    def test_phases_property(self) -> None:
        """
        Test that the phases property returns the correct value.
        """

        self.assertEqual(self.analyser.phases, self.phases)

    def test_raw_data_property(self) -> None:
        """
        Test that the raw_data property returns the correct value.
        """

        self.assertEqual(self.analyser.raw_data, self.raw_data)

    def test_summary_data_property(self) -> None:
        """
        Test that the summary_data property returns the correct value.
        """

        self.assertEqual(self.analyser.summary_data, self.summary_data)

    def test_analyse_not_implemented(self) -> None:
        """
        Test that the analyse method raises NotImplementedError.
        """

        with self.assertRaises(NotImplementedError):
            self.analyser.analyse()

    def test_save(self) -> None:
        """
        Test that the Analyser class can save its data to an Excel file.
        """

        self.analyser.save(self.test_xlsx)
        self.assertTrue(self.test_xlsx.exists())

    def test_serialise(self) -> None:
        """
        Test that the Analyser class serialises correctly into a dictionary.
        """

        serialised: SerialisedAnalyser = self.analyser.serialise()
        self.assertEqual(serialised["parameters"], self.parameters.serialise())
        self.assertEqual(serialised["raw_data"], self.raw_data.serialise())
        self.assertEqual(serialised["summary_data"], self.summary_data.serialise())
        self.assertEqual(len(serialised["phases"]), len(self.phases))
        for i in range(len(self.phases)):
            self.assertEqual(
                cast(list[SerialisedPhase], serialised["phases"])[i],
                self.phases[i].serialise(),
            )

    def test_deserialise(self) -> None:
        """
        Test that the Analyser class deserialises correctly from a dictionary.
        """

        serialised: SerialisedAnalyser = self.analyser.serialise()
        deserialised: Analyser = cast(Analyser, Serialiser.deserialise(serialised))
        self.assertIsInstance(deserialised, Analyser)
        self.assertEqual(serialised, deserialised.serialise())

    def test_deserialise_invalid_parameters(self) -> None:
        """
        Test that deserialising with invalid parameters raises a ValueError.
        """

        serialised: dict[str, Any] = cast(dict[str, Any], self.analyser.serialise())
        serialised["parameters"] = "Invalid Parameters"
        with self.assertRaises(ValueError):
            Serialiser.deserialise(serialised)

    def test_deserialise_invalid_raw_data(self) -> None:
        """
        Test that deserialising with invalid raw data raises a ValueError.
        """
        serialised: dict[str, Any] = cast(dict[str, Any], self.analyser.serialise())
        serialised["raw_data"] = "Invalid Raw Data"
        with self.assertRaises(ValueError):
            Serialiser.deserialise(serialised)

    def test_deserialise_invalid_summary_data(self) -> None:
        """
        Test that deserialising with invalid summary data raises a ValueError.
        """
        serialised: dict[str, Any] = cast(dict[str, Any], self.analyser.serialise())
        serialised["summary_data"] = "Invalid Summary Data"
        with self.assertRaises(ValueError):
            Serialiser.deserialise(serialised)

    def test_deserialise_invalid_phases(self) -> None:
        """
        Test that deserialising with invalid phases raises a ValueError.
        """
        serialised: dict[str, Any] = cast(dict[str, Any], self.analyser.serialise())
        serialised["phases"] = "Invalid Phases"
        with self.assertRaises(ValueError):
            Serialiser.deserialise(serialised)


if __name__ == "__main__":
    unittest.main()

from mech_analyser.experiment.data import (
    ProcessedTranscoder,
    RawData,
    ProcessedData,
    RawTranscoder,
    Transcoder,
)
from mech_analyser.experiment.phase import Phase, Parameters, SerialisedPhase
from mech_analyser.util.serialiser import Serialiser
import pandas as pd
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from typing import Any, Union, cast
import unittest


class TestPhase(unittest.TestCase):
    """
    Unit tests for the Phase class.
    """

    def setUp(self) -> None:
        """
        Set up a Phase instance and related objects for testing.
        """

        self.app: Union[QApplication, QCoreApplication] = (
            QApplication.instance() or QApplication([])
        )
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
        self.processed_data = ProcessedData(
            pd.DataFrame({"Column1": [10, 20, 30], "Column2": ["X", "Y", "Z"]}),
            ProcessedTranscoder(self.columns),
        )
        self.phase = Phase(self.raw_data, self.processed_data)

    def tearDown(self) -> None:
        """
        Cleans up after tests.
        """

        self.app.quit()

    def test_initialisation(self) -> None:
        """
        Test that the Phase class initializes correctly with valid inputs.
        """

        self.assertEqual(self.phase.raw_data, self.raw_data)
        self.assertEqual(self.phase.processed_data, self.processed_data)

    def test_name_property(self) -> None:
        """
        Test that the name property returns the correct value.
        """

        self.assertEqual(self.phase.name, "Phase")

    def test_raw_data_property(self) -> None:
        """
        Test that the raw_data property returns the correct value.
        """

        self.assertEqual(self.phase.raw_data, self.raw_data)

    def test_processed_data_property(self) -> None:
        """
        Test that the processed_data property returns the correct value.
        """

        self.assertEqual(self.phase.processed_data, self.processed_data)

    def test_processed_data_setter(self) -> None:
        """
        Test that the processed_data setter updates the processed data correctly.
        """

        new_processed_data = ProcessedData(
            pd.DataFrame({"NewColumn": [100, 200, 300]}),
            ProcessedTranscoder(
                columns={
                    "NewColumn": Transcoder.Column(
                        name="NewColumn",
                        input_name="Input1 (units)",
                        output_name="Output1 (units)",
                        input_header_rows=[0, 1],
                        input_header_column=0,
                        output_header_column=0,
                        data_type=int,
                    ),
                }
            ),
        )
        self.phase.processed_data = new_processed_data
        self.assertEqual(self.phase.processed_data, new_processed_data)

    def test_process_not_implemented(self) -> None:
        """
        Test that the process method raises NotImplementedError.
        """

        with self.assertRaises(NotImplementedError):
            self.phase.process(Parameters())

    def test_serialise(self) -> None:
        """
        Test that the Phase class serialises correctly into a dictionary.
        """

        serialised: SerialisedPhase = self.phase.serialise()
        self.assertEqual(serialised["name"], "Phase")
        self.assertIn("processed_data", serialised)
        self.assertEqual(serialised["processed_data"], self.processed_data.serialise())

    def test_deserialise(self) -> None:
        """
        Test that the Phase class deserialises correctly from a dictionary.
        """

        serialised: SerialisedPhase = self.phase.serialise()
        deserialised: Phase = cast(
            Phase,
            Serialiser.deserialise(serialised, raw_data=self.raw_data),
        )
        self.assertIsInstance(deserialised, Phase)
        self.assertEqual(serialised, deserialised.serialise())

    def test_deserialise_invalid_processed_data(self) -> None:
        """
        Test that deserialising with invalid processed data raises a ValueError.
        """

        serialised: dict[str, Any] = cast(dict[str, Any], self.phase.serialise())
        serialised["processed_data"] = "Invalid Data"
        with self.assertRaises(ValueError):
            Serialiser.deserialise(serialised, raw_data=self.raw_data)


if __name__ == "__main__":
    unittest.main()

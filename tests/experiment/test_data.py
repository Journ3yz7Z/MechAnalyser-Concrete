import unittest
import dataclasses

import pint
from mech_analyser.experiment.data import (
    Data,
    ProcessedTranscoder,
    ProcessedData,
    RawData,
    RawTranscoder,
    SerialisedData,
    SerialisedFrame,
    SerialisedTranscoder,
    SummaryData,
    SummaryTranscoder,
    Transcoder,
)
from mech_analyser.util.serialiser import Serialiser
import pandas as pd
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
import tempfile
from typing import Union, cast


class TestBase(unittest.TestCase):
    """
    Base class for unit tests, providing common setup and teardown methods.
    """

    def setUp(self) -> None:
        """
        Set up the unit test environment.
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
                output_name="Output1\n(units)",
                output_header_column=0,
                data_type=int,
            ),
            "Column2": Transcoder.Column(
                name="Column2",
                input_name="Input2 (units)",
                input_header_rows=[0, 1],
                input_header_column=1,
                output_name="Output2 (units)",
                output_header_column=1,
                data_type=str,
            ),
            "Column3": Transcoder.Column(
                name="Column3",
                input_name="Input3 (units)",
                input_units=pint.Unit("ms"),
                input_header_rows=[0, 1],
                input_header_column=2,
                output_name="Output3 (units)",
                output_units=pint.Unit("us"),
                output_header_column=2,
                data_type=float,
            ),
        }
        self.sample_frame = pd.DataFrame(
            {
                "Column1": [1, 2, 3],
                "Column2": ["A", "B", "C"],
                "Column3": [0.004, 0.005, 0.006],
            }
        )

        self._create_temporary_file_paths()

    def tearDown(self) -> None:
        """
        Cleans up after tests.
        """

        self.test_csv.unlink(missing_ok=True)
        self.test_xlsx.unlink(missing_ok=True)
        self.app.quit()

    def _create_temporary_file_paths(self) -> None:
        """
        Create temporary file paths for testing.
        """

        self.test_csv = Path(
            tempfile.NamedTemporaryFile(delete=True, prefix="test_", suffix=".csv").name
        )
        self.test_xlsx = Path(
            tempfile.NamedTemporaryFile(delete=True, prefix="test_", suffix=".xlsx").name
        )


class TestTranscoder(TestBase):
    """
    Unit tests for the Transcoder class.
    """

    def setUp(self) -> None:
        """
        Set up a sample Transcoder object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = Transcoder(columns=self.columns)

    def test_initialisation(self) -> None:
        """
        Test that the Transcoder class initializes correctly with valid inputs.
        """

        self.assertEqual(self.transcoder.columns, self.columns)

    def test_columns_property(self) -> None:
        """
        Test that the columns property returns the correct column names.
        """

        self.assertEqual(self.transcoder.columns, self.columns)

    def test_get_column(self) -> None:
        """
        Test that the get_column method returns the correct column.
        """

        column: Transcoder.Column = self.transcoder.get_column("Column1")
        self.assertEqual(column.name, "Column1")

    def test_get_input_name(self) -> None:
        """
        Test that the get_input_name method returns the correct input name.
        """

        input_name: str = self.transcoder.get_input_name("Column1")
        self.assertEqual(input_name, self.columns["Column1"].input_name)

    def test_get_output_name(self) -> None:
        """
        Test that the get_output_name method returns the correct output name.
        """

        output_name: str = self.transcoder.get_output_name("Column1")
        self.assertEqual(output_name, self.columns["Column1"].output_name)

    def test_add_column(self) -> None:
        """
        Test adding a new column to the Transcoder.
        """

        new_column = Transcoder.Column(
            name="Column4",
            input_name="Input4 (units)",
            output_name="Output4 (units)",
            output_header_column=3,
        )
        self.transcoder.add_column(new_column)
        self.assertEqual(
            self.transcoder.get_column(new_column.name).name, new_column.name
        )
        self.assertEqual(
            self.transcoder.get_column(new_column.name).input_name, new_column.input_name
        )
        self.assertEqual(
            self.transcoder.get_column(new_column.name).output_name,
            new_column.output_name,
        )
        self.assertEqual(
            self.transcoder.get_column(new_column.name).output_header_column,
            new_column.output_header_column,
        )

    def test_remove_column(self) -> None:
        """
        Test removing a column from the Transcoder.
        """

        self.transcoder.remove_column("Column1")
        with self.assertRaises(KeyError):
            self.transcoder.get_column("Column1")

    def test_load(self) -> None:
        """
        Test loading data using the Transcoder.
        """

        # Create a CSV file to be loaded with sample data
        sample_frame: pd.DataFrame = self.sample_frame.copy(deep=True)
        sample_frame["Column3"] = sample_frame["Column3"] * 1000.0
        sample_frame.rename(columns={"Column1": ("Input1", "(units)")}, inplace=True)
        sample_frame.rename(columns={"Column2": ("Input2 (units)", "")}, inplace=True)
        sample_frame.rename(columns={"Column3": ("Input3", "(units)")}, inplace=True)
        sample_frame.columns = pd.MultiIndex.from_tuples(sample_frame.columns)  # type: ignore
        sample_frame.to_csv(self.test_csv, index=False)

        # Load and verify the sample data
        loaded_frame: pd.DataFrame = self.transcoder.load(self.test_csv)
        self.assertTrue(loaded_frame.equals(self.sample_frame))  # type: ignore

    def test_save(self) -> None:
        """
        Test saving data using the Transcoder.
        """

        # Save the sample data
        self.transcoder.save(self.test_xlsx, self.sample_frame, name="TestSheet")
        self.assertTrue(self.test_xlsx.exists())

        # Verify the sample data
        saved_frame: pd.DataFrame = pd.read_excel(  # type: ignore
            self.test_xlsx,
            sheet_name="TestSheet",
            header=[0, 1],
            index_col=0,
        )
        # Merge multi-line headers into single line, separated by space
        saved_frame.columns = [
            "\n".join(
                ["" if row.startswith("Unnamed") else row for row in column]
            ).strip()
            for column in saved_frame.columns
        ]
        saved_frame.rename(
            columns={c.output_name: c.name for c in self.columns.values()},
            inplace=True,
        )
        saved_frame["Column3"] = saved_frame["Column3"] / 1000000.0
        self.assertTrue(saved_frame.equals(self.sample_frame))  # type: ignore

    def test_serialise(self) -> None:
        """
        Test serialising the Transcoder.
        """

        serialised: SerialisedTranscoder = self.transcoder.serialise()
        self.assertIn("columns", serialised)
        self.assertIn("Column1", serialised["columns"])
        self.assertIn("Column2", serialised["columns"])
        self.assertIn("Column3", serialised["columns"])

    def test_deserialise(self) -> None:
        """
        Test deserialising the Transcoder.
        """

        serialised: SerialisedTranscoder = self.transcoder.serialise()
        deserialised: Transcoder = Transcoder.deserialise(serialised)
        self.assertIsInstance(deserialised, Transcoder)
        self.assertEqual(serialised, deserialised.serialise())


class TestData(TestBase):
    """
    Unit tests for the Data class.
    """

    def setUp(self) -> None:
        """
        Set up a sample DataFrame and initialize a Data object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = Transcoder(columns=self.columns)
        self.data = Data(self.sample_frame, self.transcoder)

    def test_initialisation(self) -> None:
        """
        Test that the Data class initializes correctly with valid inputs.
        """

        self.assertTrue(self.data.frame.equals(self.sample_frame))  # type: ignore
        self.assertEqual(self.data.transcoder, self.transcoder)

    def test_frame_property(self) -> None:
        """
        Test that the frame property returns the correct DataFrame.
        """

        self.assertTrue(self.data.frame.equals(self.sample_frame))  # type: ignore

    def test_transcoder_property(self) -> None:
        """
        Test that the transcoder property returns the correct Transcoder.
        """

        self.assertIs(self.data.transcoder, self.transcoder)

    def test_columns_property(self) -> None:
        """
        Test that the columns property returns the correct column names.
        """

        self.assertEqual(self.data.columns, ["Column1", "Column2", "Column3"])

    def test_save(self) -> None:
        """
        Test saving the Data object to an Excel file.
        """

        # Save the sample data
        self.data.save(self.test_xlsx, name="Test Data")
        self.assertTrue(self.test_xlsx.exists())

        # Verify the sample data
        saved_frame: pd.DataFrame = pd.read_excel(  # type: ignore
            self.test_xlsx,
            sheet_name="Test Data",
            header=[0, 1],
            index_col=0,
        )
        # Merge multi-line headers into single line, separated by space
        saved_frame.columns = [
            "\n".join(
                ["" if row.startswith("Unnamed") else row for row in column]
            ).strip()
            for column in saved_frame.columns
        ]
        saved_frame.rename(
            columns={c.output_name: c.name for c in self.columns.values()},
            inplace=True,
        )
        saved_frame["Column3"] = saved_frame["Column3"] / 1000000.0
        self.assertTrue(saved_frame.equals(self.sample_frame))  # type: ignore

    def test_serialise(self) -> None:
        """
        Test that the Data object is correctly serialised into a dictionary.
        """

        serialised: SerialisedData = self.data.serialise()
        self.assertIn("frame", serialised)
        self.assertIn("Column1", cast(SerialisedFrame, serialised["frame"]))
        self.assertIn("Column2", cast(SerialisedFrame, serialised["frame"]))
        self.assertEqual(cast(SerialisedFrame, serialised["frame"])["Column1"], [1, 2, 3])
        self.assertEqual(
            cast(SerialisedFrame, serialised["frame"])["Column2"], ["A", "B", "C"]
        )
        self.assertEqual(
            cast(SerialisedFrame, serialised["frame"])["Column3"], [0.004, 0.005, 0.006]
        )

    def test_deserialise(self) -> None:
        """
        Test that a serialised Data object can be correctly deserialised.
        """

        serialised: SerialisedData = self.data.serialise()
        deserialised: Data = cast(Data, Serialiser.deserialise(serialised))
        self.assertIsInstance(deserialised, Data)
        self.assertEqual(serialised, deserialised.serialise())


class TestRawTranscoder(TestTranscoder):
    """
    Unit tests for the RawTranscoder class.
    """

    def setUp(self) -> None:
        """
        Set up a sample RawTranscoder object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = RawTranscoder(columns=self.columns)

    def test_save(self) -> None:
        """
        Test saving data using the RawTranscoder.
        """

        # Save the sample data
        self.transcoder.save(self.test_xlsx, self.sample_frame)
        self.assertTrue(self.test_xlsx.exists())

        # Verify the sample data
        saved_frame: pd.DataFrame = pd.read_excel(  # type: ignore
            self.test_xlsx,
            sheet_name="Raw Data",
            header=[0, 1],
            index_col=0,
        )
        # Merge multi-line headers into single line, separated by space
        saved_frame.columns = [
            "\n".join(
                ["" if row.startswith("Unnamed") else row for row in column]
            ).strip()
            for column in saved_frame.columns
        ]
        saved_frame.rename(
            columns={c.output_name: c.name for c in self.columns.values()},
            inplace=True,
        )
        saved_frame["Column3"] = saved_frame["Column3"] / 1000000.0
        self.assertTrue(saved_frame.equals(self.sample_frame))  # type: ignore

    def test_deserialise(self) -> None:
        """
        Test deserialising the RawTranscoder.
        """

        serialised: SerialisedTranscoder = self.transcoder.serialise()
        deserialised: RawTranscoder = RawTranscoder.deserialise(serialised)
        self.assertIsInstance(deserialised, RawTranscoder)
        self.assertEqual(serialised, deserialised.serialise())


class TestRawData(TestData):
    """
    Unit tests for the RawData class.
    """

    def setUp(self) -> None:
        """
        Set up a sample DataFrame and initialize a RawData object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = RawTranscoder(columns=self.columns)
        self.data = RawData(self.sample_frame, self.transcoder)

    def test_load(self) -> None:
        """
        Test that a data file can be loaded correctly.
        """

        # Create a CSV file to be loaded with sample data
        sample_frame: pd.DataFrame = self.sample_frame.copy(deep=True)
        sample_frame["Column3"] = sample_frame["Column3"] * 1000.0
        sample_frame.rename(columns={"Column1": ("Input1", "(units)")}, inplace=True)
        sample_frame.rename(columns={"Column2": ("Input2 (units)", "")}, inplace=True)
        sample_frame.rename(columns={"Column3": ("Input3", "(units)")}, inplace=True)
        sample_frame.columns = pd.MultiIndex.from_tuples(sample_frame.columns)  # type: ignore
        sample_frame.to_csv(self.test_csv, index=False)

        # Load and verify the sample data
        loaded_data: RawData = RawData.load(self.test_csv, self.transcoder)
        self.assertTrue(loaded_data.frame.equals(self.sample_frame))  # type: ignore

    def test_deserialise(self) -> None:
        """
        Test that a serialised RawData object can be correctly deserialised.
        """

        serialised: SerialisedData = self.data.serialise()
        deserialised: RawData = cast(RawData, Serialiser.deserialise(serialised))
        self.assertIsInstance(deserialised, RawData)
        self.assertEqual(serialised, deserialised.serialise())


class TestProcessedTranscoder(TestTranscoder):
    """
    Unit tests for the ProcessedTranscoder class.
    """

    def setUp(self) -> None:
        """
        Set up a sample ProcessedTranscoder object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = ProcessedTranscoder(columns=self.columns)

    def test_deserialise(self) -> None:
        """
        Test deserialising the ProcessedTranscoder.
        """

        serialised: SerialisedTranscoder = self.transcoder.serialise()
        deserialised: ProcessedTranscoder = ProcessedTranscoder.deserialise(serialised)
        self.assertIsInstance(deserialised, ProcessedTranscoder)
        self.assertEqual(serialised, deserialised.serialise())


class TestProcessedData(TestData):
    """
    Unit tests for the ProcessedData class.
    """

    def setUp(self) -> None:
        """
        Set up a sample DataFrame and initialize a ProcessedData object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = ProcessedTranscoder(columns=self.columns)
        self.data = ProcessedData(self.sample_frame, self.transcoder)

    def test_deserialise(self) -> None:
        """
        Test that a serialised ProcessedData object can be correctly deserialised.
        """

        serialised: SerialisedData = self.data.serialise()
        deserialised: ProcessedData = cast(
            ProcessedData,
            Serialiser.deserialise(serialised),
        )
        self.assertIsInstance(deserialised, ProcessedData)
        self.assertEqual(serialised, deserialised.serialise())


class TestSummaryTranscoder(TestTranscoder):
    """
    Unit tests for the SummaryTranscoder class.
    """

    def setUp(self) -> None:
        """
        Set up a sample SummaryTranscoder object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = SummaryTranscoder(columns=self.columns)

    def test_save(self) -> None:
        """
        Test saving data using the SummaryTranscoder.
        """

        # Save the sample data
        self.transcoder.save(self.test_xlsx, self.sample_frame)
        self.assertTrue(self.test_xlsx.exists())

        # Verify the sample data
        saved_frame: pd.DataFrame = pd.read_excel(  # type: ignore
            self.test_xlsx,
            sheet_name="Summary",
            header=[0, 1],
            index_col=0,
        )
        # Merge multi-line headers into single line, separated by space
        saved_frame.columns = [
            "\n".join(
                ["" if row.startswith("Unnamed") else row for row in column]
            ).strip()
            for column in saved_frame.columns
        ]
        saved_frame.rename(
            columns={c.output_name: c.name for c in self.columns.values()},
            inplace=True,
        )
        saved_frame["Column3"] = saved_frame["Column3"] / 1000000.0
        self.assertTrue(saved_frame.equals(self.sample_frame))  # type: ignore

    def test_deserialise(self) -> None:
        """
        Test deserialising the SummaryTranscoder.
        """

        serialised: SerialisedTranscoder = self.transcoder.serialise()
        deserialised: SummaryTranscoder = SummaryTranscoder.deserialise(serialised)
        self.assertIsInstance(deserialised, SummaryTranscoder)
        self.assertEqual(serialised, deserialised.serialise())


class TestSummaryData(TestData):
    """
    Unit tests for the SummaryData class.
    """

    @dataclasses.dataclass
    class SampleRow(SummaryData.Row):
        """
        Sample row structure for testing the SummaryData class.
        """

        Column1: int = dataclasses.field(metadata={"column_name": "Column1"})
        Column2: str = dataclasses.field(metadata={"column_name": "Column2"})
        Column3: float = dataclasses.field(metadata={"column_name": "Column3"})

    def setUp(self) -> None:
        """
        Set up a sample DataFrame and initialize a SummaryData object for testing.
        """

        TestBase.setUp(self)

        self.transcoder = SummaryTranscoder(columns=self.columns)
        self.data = SummaryData(self.sample_frame, self.transcoder)

    def test_append_row(self) -> None:
        """
        Test that a row can be appended to the SummaryData object.
        """

        row = self.SampleRow(Column1=4, Column2="D", Column3=0.007)
        self.data.append_row(row)
        self.assertEqual(len(self.data.frame), 4)
        self.assertEqual(self.data.frame.iloc[-1]["Column1"], 4)
        self.assertEqual(self.data.frame.iloc[-1]["Column2"], "D")
        self.assertEqual(self.data.frame.iloc[-1]["Column3"], 0.007)

    def test_clear_all_rows(self) -> None:
        """
        Test that all rows in the SummaryData object can be cleared.
        """

        self.data.clear_all_rows()
        self.assertTrue(self.data.frame.empty)

    def test_deserialise(self) -> None:
        """
        Test that a serialised SummaryData object can be correctly deserialised.
        """

        serialised: SerialisedData = self.data.serialise()
        deserialised: SummaryData = cast(
            SummaryData,
            Serialiser.deserialise(serialised),
        )
        self.assertIsInstance(deserialised, SummaryData)
        self.assertEqual(serialised, deserialised.serialise())


if __name__ == "__main__":
    unittest.main()

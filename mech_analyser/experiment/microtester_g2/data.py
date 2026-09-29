import mech_analyser.experiment.data as ma_data
import mech_analyser.util.units as ma_units
import pandas as pd

from pathlib import Path
from typing import Any, Self, cast


class Data:
    """
    Base class for all Microtester G2 data.
    """

    @property
    def base_displacement(self) -> "pd.Series[float]":
        return self._frame["Base displacement"]  # type: ignore

    @property
    def size(self) -> "pd.Series[float]":
        return self._frame["Size"]  # type: ignore

    @property
    def cycle(self) -> "pd.Series[str]":
        return self._frame["Cycle"]  # type: ignore

    @property
    def force(self) -> "pd.Series[float]":
        return self._frame["Force"]  # type: ignore

    @property
    def name(self) -> "pd.Series[str]":
        return self._frame["Name"]  # type: ignore

    @property
    def temperature(self) -> "pd.Series[float]":
        return self._frame["Temperature"]  # type: ignore

    @property
    def time(self) -> "pd.Series[int]":
        return self._frame["Time"]  # type: ignore

    @property
    def tip_displacement(self) -> "pd.Series[float]":
        return self._frame["Tip displacement"]  # type: ignore


class RawTranscoder(ma_data.RawTranscoder):
    """
    Base class for all Microtester G2 raw data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the analyser.  If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        columns: dict[str, ma_data.RawTranscoder.Column] = {},
        id: str = "",
    ) -> None:
        if columns:
            assert "Name" in columns, "Name column must be specified"
            assert "Cycle" in columns, "Cycle column must be specified"
            assert "Time" in columns, "Time column must be specified"
            assert "Force" in columns, "Force column must be specified"
            assert (
                "Tip displacement" in columns
            ), "Tip displacement column must be specified"
            assert (
                "Base displacement" in columns
            ), "Base displacement column must be specified"
            assert "Current size" in columns, "Current size column must be specified"
            assert "Temperature" in columns, "Temperature column must be specified"

            super().__init__(columns, id)
        else:
            super().__init__(
                {
                    "Name": ma_data.RawTranscoder.Column(
                        name="Name",
                        input_name="Set Name",
                        input_header_rows=[0],
                        input_header_column=0,
                        output_name="Name",
                        output_header_column=0,
                        data_type=str,
                    ),
                    "Cycle": ma_data.RawTranscoder.Column(
                        name="Cycle",
                        input_name="Cycle",
                        input_header_rows=[0],
                        input_header_column=1,
                        output_name="Cycle",
                        output_header_column=1,
                        data_type=str,
                    ),
                    "Time": ma_data.RawTranscoder.Column(
                        name="Time",
                        input_name="Time (s)",
                        input_units=ma_units.unit_registry.parse_units("s"),
                        input_header_rows=[0],
                        input_header_column=2,
                        output_name="Time (s)",
                        output_units=ma_units.unit_registry.parse_units("s"),
                        output_header_column=2,
                    ),
                    "Force": ma_data.RawTranscoder.Column(
                        name="Force",
                        input_name="Force (N)",
                        input_units=ma_units.unit_registry.parse_units("N"),
                        input_header_rows=[0],
                        input_header_column=3,
                        output_name="Force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=3,
                    ),
                    "Tip displacement": ma_data.RawTranscoder.Column(
                        name="Tip displacement",
                        input_name="Tip Displacement (mm)",
                        input_units=ma_units.unit_registry.parse_units("mm"),
                        input_header_rows=[0],
                        input_header_column=4,
                        output_name="Tip displacement (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=4,
                    ),
                    "Base displacement": ma_data.RawTranscoder.Column(
                        name="Base displacement",
                        input_name="Base Displacement (mm)",
                        input_units=ma_units.unit_registry.parse_units("mm"),
                        input_header_rows=[0],
                        input_header_column=5,
                        output_name="Base displacement (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=5,
                    ),
                    "Size": ma_data.RawTranscoder.Column(
                        name="Size",
                        input_name="Current Size (mm)",
                        input_units=ma_units.unit_registry.parse_units("mm"),
                        input_header_rows=[0],
                        input_header_column=6,
                        output_name="Size (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=6,
                    ),
                    "Temperature": ma_data.RawTranscoder.Column(
                        name="Temperature",
                        input_name="Temperature (°C)",
                        input_units=ma_units.unit_registry.parse_units("C"),
                        input_header_rows=[0],
                        input_header_column=7,
                        output_name="Temperature (°C)",
                        output_units=ma_units.unit_registry.parse_units("C"),
                        output_header_column=7,
                    ),
                },
                id,
            )

    @property
    def encoding(self) -> str:
        return "cp1252"


class RawData(ma_data.RawData, Data):
    """
    Base class for all Microtester G2 raw data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: ma_data.RawTranscoder,
        id: str = "",
    ) -> None:
        super().__init__(frame, transcoder, id)

    @property
    def transcoder(self) -> RawTranscoder:
        return cast(RawTranscoder, self._transcoder)

    def generate_plot(self, **kwargs: Any) -> None:
        """
        Generates a plot of the raw data.

        TODO: evaluate if plotting should be external to the class
        """

        x_series: "pd.Series[float]" = self.tip_displacement
        y_series: "pd.Series[float]" = self.force
        x_column: RawTranscoder.Column = self.transcoder.get_column("Tip displacement")
        y_column: RawTranscoder.Column = self.transcoder.get_column("Force")
        title: str = "Force-displacement"

        # Plot the data
        self._plot.getPlotItem().setTitle(title)  # type: ignore
        self._plot.getPlotItem().setLabel("bottom", x_column.output_name)  # type: ignore
        self._plot.getPlotItem().setLabel("left", y_column.output_name)  # type: ignore
        self._plot.getPlotItem().plot(  # type: ignore
            [
                ma_units.convert_from_base_units(x, x_column.output_units)
                for x in cast(list[float], list(x_series.values))
            ],
            [
                ma_units.convert_from_base_units(y, y_column.output_units)
                for y in cast(list[float], list(y_series.values))
            ],
        )

    @classmethod
    def load(
        cls,
        input_file: Path,
        transcoder: ma_data.RawTranscoder,
        **kwargs: Any,
    ) -> Self:
        """
        Loads the raw data from the input file.

        Args:
            input_file: The path to the input file.
            transcoder: The transcoder used to load the data.

        Returns:
            RawData: The loaded raw data.
        """

        return cls(transcoder.load(input_file, **kwargs), transcoder)


class ProcessedTranscoder(ma_data.ProcessedTranscoder):
    """
    Base class for all Microtester G2 processed data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class ProcessedData(ma_data.ProcessedData, Data):
    """
    Base class for all Microtester G2 processed data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: ProcessedTranscoder,
        id: str = "",
    ) -> None:
        super().__init__(frame, transcoder, id)

    @property
    def transcoder(self) -> ProcessedTranscoder:
        return cast(ProcessedTranscoder, self._transcoder)


class SummaryTranscoder(ma_data.SummaryTranscoder):
    """
    Base class for all Microtester G2 summary data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class SummaryData(ma_data.SummaryData):
    """
    Base class for all Microtester G2 summary data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: SummaryTranscoder,
        id: str = "",
    ) -> None:
        super().__init__(frame, transcoder, id)

    @property
    def transcoder(self) -> SummaryTranscoder:
        return cast(SummaryTranscoder, self._transcoder)

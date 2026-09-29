import mech_analyser.experiment.data as ma_data
import mech_analyser.util.units as ma_units
import pandas as pd

from pathlib import Path
from typing import Any, Self, cast


class Data:
    """
    Base class for all Instron 68TM data.
    """

    @property
    def displacement(self) -> "pd.Series[float]":
        return self._frame["Displacement"]  # type: ignore

    @property
    def force(self) -> "pd.Series[float]":
        return self._frame["Force"]  # type: ignore

    @property
    def strain(self) -> "pd.Series[float]":
        return self._frame["Strain"]  # type: ignore

    @strain.setter
    def strain(self, value: "pd.Series[float]") -> None:
        self._frame["Strain"] = value  # type: ignore

    @property
    def stress(self) -> "pd.Series[float]":
        return self._frame["Stress"]  # type: ignore

    @stress.setter
    def stress(self, value: "pd.Series[float]") -> None:
        self._frame["Stress"] = value  # type: ignore

    @property
    def time(self) -> "pd.Series[float]":
        return self._frame["Time"]  # type: ignore


class RawTranscoder(ma_data.RawTranscoder):
    """
    Base class for all Instron 68TM raw data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        columns: dict[str, ma_data.RawTranscoder.Column] = {},
        id: str = "",
    ) -> None:
        if columns:
            assert "Time" in columns, "Time column must be specified"
            assert "Displacement" in columns, "Displacement column must be specified"
            assert "Force" in columns, "Force column must be specified"
            assert "Strain" in columns, "Strain column must be specified"
            assert "Stress" in columns, "Stress column must be specified"

            super().__init__(columns, id)
        else:
            super().__init__(
                {
                    "Time": ma_data.RawTranscoder.Column(
                        name="Time",
                        input_name="Time (s)",
                        input_units=ma_units.unit_registry.parse_units("s"),
                        input_header_rows=[0],
                        input_header_column=0,
                        output_name="Time (s)",
                        output_units=ma_units.unit_registry.parse_units("s"),
                        output_header_column=0,
                    ),
                    "Displacement": ma_data.RawTranscoder.Column(
                        name="Displacement",
                        input_name="Displacement (mm)",
                        input_units=ma_units.unit_registry.parse_units("mm"),
                        input_header_rows=[0],
                        input_header_column=1,
                        output_name="Displacement (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=1,
                    ),
                    "Force": ma_data.RawTranscoder.Column(
                        name="Force",
                        input_name="Force (N)",
                        input_units=ma_units.unit_registry.parse_units("N"),
                        input_header_rows=[0],
                        input_header_column=2,
                        output_name="Force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=2,
                    ),
                    "Strain": ma_data.RawTranscoder.Column(
                        name="Strain",
                        input_included_editing=True,
                        input_name="Strain (%)",
                        input_units=ma_units.unit_registry.parse_units("%"),
                        input_header_rows=[0],
                        input_header_column=3,
                        output_name="Strain (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=3,
                    ),
                    "Stress": ma_data.RawTranscoder.Column(
                        name="Stress",
                        input_included_editing=True,
                        input_name="Compressive stress (Pa)",
                        input_units=ma_units.unit_registry.parse_units("Pa"),
                        input_header_rows=[0],
                        input_header_column=4,
                        output_name="Compressive Stress (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=4,
                    ),
                },
                id,
            )


class RawData(ma_data.RawData, Data):
    """
    Base class for all Instron 68TM raw data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        tare_force_N: The force which will be used to tare the experiment.  All raw data
            points with force less than the tare force will be discarded, and all data
            points with force greater than the tare force will be offset accordingly.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    def __init__(
        self,
        frame: pd.DataFrame,
        transcoder: ma_data.RawTranscoder,
        tare_force_N: float,
        id: str = "",
    ) -> None:
        self._tare_displacement_m: float = 0.0
        self._tare_force_N: float = 0.0
        self._tare_strain: float = 0.0
        self._tare_stress_Pa: float = 0.0
        self._tare_time_s: float = 0.0

        # Use raw data without taring
        if tare_force_N == 0.0:
            return super().__init__(frame, transcoder, id)

        # Tare the raw data
        tare_id: int = frame.loc[frame["Force"] >= tare_force_N].index.min()  # type: ignore
        filtered_frame: pd.DataFrame = frame.iloc[tare_id:]
        filtered_frame.reset_index(drop=True, inplace=True)

        self._tare_displacement_m = filtered_frame["Displacement"][0]
        self._tare_force_N = filtered_frame["Force"][0]
        if transcoder.get_column("Strain").input_included:
            self._tare_strain = filtered_frame["Strain"][0]
        if transcoder.get_column("Stress").input_included:
            self._tare_stress_Pa = filtered_frame["Stress"][0]
        self._tare_time_s = filtered_frame["Time"][0]

        tared_frame: pd.DataFrame = pd.concat(
            [
                filtered_frame["Time"] - self._tare_time_s,  # type: ignore
                filtered_frame["Displacement"] - self._tare_displacement_m,  # type: ignore
                filtered_frame["Force"] - self._tare_force_N,  # type: ignore
            ],
            axis=1,
        )
        if transcoder.get_column("Strain").input_included:
            tared_frame = pd.concat(
                [
                    tared_frame,
                    filtered_frame["Strain"] - self._tare_strain,  # type: ignore
                ],
                axis=1,
            )
        if transcoder.get_column("Stress").input_included:
            tared_frame = pd.concat(
                [
                    tared_frame,
                    filtered_frame["Stress"] - self._tare_stress_Pa,  # type: ignore
                ],
                axis=1,
            )
        tared_frame.columns = filtered_frame.columns

        super().__init__(tared_frame, transcoder, id)

    @property
    def transcoder(self) -> RawTranscoder:
        return cast(RawTranscoder, self._transcoder)

    @property
    def tare_displacement_m(self) -> float:
        return self._tare_displacement_m

    @property
    def tare_force_N(self) -> float:
        return self._tare_force_N

    @property
    def tare_strain(self) -> float:
        return self._tare_strain

    @property
    def tare_stress_Pa(self) -> float:
        return self._tare_stress_Pa

    @property
    def tare_time_s(self) -> float:
        return self._tare_time_s

    def generate_plot(self, **kwargs: Any) -> None:
        """
        Generates a plot of the raw data.

        TODO: evaluate if plotting should be external to the class
        """

        x_series: "pd.Series[float]"
        y_series: "pd.Series[float]"
        x_column: RawTranscoder.Column
        y_column: RawTranscoder.Column
        title: str

        # Determine which data to plot
        if (
            self.transcoder.get_column("Strain").input_included
            and self.transcoder.get_column("Stress").input_included
        ):
            title = "Stress-strain"
            x_column = self.transcoder.get_column("Strain")
            y_column = self.transcoder.get_column("Stress")
            x_series = self.strain
            y_series = self.stress
        else:
            title = "Force-displacement"
            x_column = self.transcoder.get_column("Displacement")
            y_column = self.transcoder.get_column("Force")
            x_series = self.displacement
            y_series = self.force

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
            tare_force_N: The force which will be used to tare the experiment.

        Returns:
            RawData: The loaded raw data.
        """

        tare_force_N: float = cast(float, kwargs.get("tare_force_N", 0.0))

        return cls(transcoder.load(input_file, **kwargs), transcoder, tare_force_N)


class ProcessedTranscoder(ma_data.ProcessedTranscoder):
    """
    Base class for all Instron 68TM processed data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class ProcessedData(ma_data.ProcessedData, Data):
    """
    Base class for all Instron 68TM processed data.

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
    Base class for all Instron 68TM summary data file transcoders.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    pass


class SummaryData(ma_data.SummaryData):
    """
    Base class for all Instron 68TM summary data.

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

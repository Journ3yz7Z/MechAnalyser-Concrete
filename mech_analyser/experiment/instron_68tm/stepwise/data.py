import dataclasses
import mech_analyser.experiment.instron_68tm.data as ma_data
import mech_analyser.util.units as ma_units
import pandas as pd
import pyqtgraph as pg  # type: ignore

# NOTE: this is to ensure that the RawTranscoder gets appropriately imported
from mech_analyser.experiment.instron_68tm.data import RawTranscoder  # type: ignore
from typing import Any, cast


class ProcessedTranscoder(ma_data.ProcessedTranscoder):
    """
    Instron 68TM stepwise compression experiment processed data file transcoders.

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
            assert "Relative time" in columns, "Relative time column must be specified"
            assert "Displacement" in columns, "Displacement column must be specified"
            assert "Force" in columns, "Force column must be specified"
            assert "Strain" in columns, "Strain column must be specified"
            assert "Stress" in columns, "Stress column must be specified"
            assert (
                "Regression stress" in columns
            ), "Regression stress column must be specified"

            super().__init__(columns, id)
        else:
            super().__init__(
                {
                    "Time": ma_data.ProcessedTranscoder.Column(
                        name="Time",
                        input_included=False,
                        output_name="Time (s)",
                        output_units=ma_units.unit_registry.parse_units("s"),
                        output_header_column=0,
                    ),
                    "Relative time": ma_data.ProcessedTranscoder.Column(
                        name="Relative time",
                        input_included=False,
                        output_name="Relative time (s)",
                        output_units=ma_units.unit_registry.parse_units("s"),
                        output_header_column=1,
                    ),
                    "Displacement": ma_data.ProcessedTranscoder.Column(
                        name="Displacement",
                        input_included=False,
                        output_name="Displacement (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=2,
                    ),
                    "Force": ma_data.ProcessedTranscoder.Column(
                        name="Force",
                        input_included=False,
                        output_name="Force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=3,
                    ),
                    "Strain": ma_data.ProcessedTranscoder.Column(
                        name="Strain",
                        input_included=False,
                        output_name="Strain (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=4,
                    ),
                    "Stress": ma_data.ProcessedTranscoder.Column(
                        name="Stress",
                        input_included=False,
                        output_name="Compressive stress (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=5,
                    ),
                    "Regression stress": ma_data.ProcessedTranscoder.Column(
                        name="Regression stress",
                        input_included=False,
                        output_name="Regression stress (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=6,
                    ),
                },
                id,
            )


class ProcessedData(ma_data.ProcessedData):
    """
    Instron 68TM stepwise compression experiment processed data.

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

        # Initially populate the processed data columns with default values
        if "Strain" not in self._frame.columns:  # type: ignore
            self.strain = pd.Series([0.0] * self._frame.index.size)  # type: ignore
        if "Stress" not in self._frame.columns:  # type: ignore
            self.stress = pd.Series([0.0] * self._frame.index.size)  # type: ignore
        self.relative_time = pd.Series([0.0] * self._frame.index.size)  # type: ignore
        self.regression_stress = pd.Series([0.0] * self._frame.index.size)  # type: ignore

    @property
    def initial_time_s(self) -> float:
        return self.time[0]

    @property
    def regression_stress(self) -> "pd.Series[float]":
        return self._frame["Regression stress"]  # type: ignore

    @regression_stress.setter
    def regression_stress(self, value: "pd.Series[float]") -> None:
        self._frame["Regression stress"] = value

        # Move the regression stress column to be directly after the stress column
        column: pd.Series = self._frame.pop("Regression stress")  # type: ignore
        self._frame.insert(  # type: ignore
            self._frame.columns.get_loc("Stress") + 1,  # type: ignore
            "Regression stress",
            column,
        )

    @property
    def relative_time(self) -> "pd.Series[float]":
        return self._frame["Relative time"]  # type: ignore

    @relative_time.setter
    def relative_time(self, value: "pd.Series[float]") -> None:
        self._frame["Relative time"] = value

        # Move the relative time column to be directly after the time column
        column: pd.Series = self._frame.pop("Relative time")  # type: ignore
        self._frame.insert(  # type: ignore
            self._frame.columns.get_loc("Time") + 1,  # type: ignore
            "Relative time",
            column,
        )

    @property
    def transcoder(self) -> ProcessedTranscoder:
        return cast(ProcessedTranscoder, self._transcoder)

    def generate_plot(self, **kwargs: Any) -> None:
        """
        Generates a plot of the processed data.

        TODO: evaluate if plotting should be external to the class

        Args:
            regression_data_points: Maximum number of data points to be included
                in the regression analysis.
            tau_r2: Reduced modulus of the exponential decay regression.
        """

        regression_data_points: int = cast(
            int,
            kwargs.get("regression_data_points") or self.frame.index.size,  # type: ignore
        )
        tau_r2: float = cast(float, kwargs.get("tau_r2", 1.0))

        x_series: "pd.Series[float]" = self.relative_time
        y_series: "pd.Series[float]" = self.stress
        y_regression_series: "pd.Series[float]" = self.regression_stress
        x_column: ma_data.ProcessedTranscoder.Column = self.transcoder.get_column(
            "Relative time"
        )
        y_column: ma_data.ProcessedTranscoder.Column = self.transcoder.get_column(
            "Stress"
        )
        y_regression_column: ma_data.ProcessedTranscoder.Column = (
            self.transcoder.get_column("Regression stress")
        )
        title: str = "Exponential decay stress-time regression"

        # Plot the data
        self._plot.getPlotItem().setTitle(title)  # type: ignore
        self._plot.getPlotItem().setLabel("bottom", x_column.output_name)  # type: ignore
        self._plot.getPlotItem().setLabel("left", y_column.output_name)  # type: ignore
        self._plot.getPlotItem().addLegend()  # type: ignore
        self._plot.getPlotItem().plot(  # type: ignore
            [
                ma_units.convert_from_base_units(x, x_column.output_units)
                for x in cast(list[float], list(x_series.values))
            ],
            [
                ma_units.convert_from_base_units(y, y_column.output_units)
                for y in cast(list[float], list(y_series.values))
            ],
            name=y_column.name,
        )
        self._plot.getPlotItem().plot(  # type: ignore
            [
                ma_units.convert_from_base_units(x, x_column.output_units)
                for x in cast(list[float], list(x_series.values))
            ],
            [
                ma_units.convert_from_base_units(y, y_regression_column.output_units)
                for y in cast(list[float], list(y_regression_series.values))
            ],
            name=y_regression_column.name,
            pen=pg.mkPen("r"),  # type: ignore
        )

        # Add the regression domain
        self._plot.getPlotItem().plot(  # type: ignore
            [
                0.0,
                ma_units.convert_from_base_units(
                    x_series.iloc[regression_data_points - 1],
                    x_column.output_units,
                ),
            ],
            [
                ma_units.convert_from_base_units(
                    y_series.iloc[0],
                    y_column.output_units,
                )
            ]
            * 2,
            name="Regression domain",
            pen=None,
            fillLevel=ma_units.convert_from_base_units(
                y_series.iloc[regression_data_points - 1],
                y_column.output_units,
            ),
            brush=pg.mkBrush(200, 200, 255, 100),  # type: ignore
        )

        # Add the regression coefficient of determination
        self._plot.getPlotItem().plot(  # type: ignore
            [],
            [],
            name=f"R² = {round(tau_r2, 4)}",
            pen=None,
        )


class SummaryTranscoder(ma_data.SummaryTranscoder):
    """
    Instron 68TM stepwise compression experiment summary data file transcoders.

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
            assert "Strain" in columns, "Strain column must be specified"
            assert "Min stress" in columns, "Minimum stress column must be specified"
            assert "Max stress" in columns, "Maximum stress column must be specified"
            assert "Min force" in columns, "Minimum force column must be specified"
            assert "Max force" in columns, "Maximum force column must be specified"
            assert "a" in columns, "a column must be specified"
            assert "b" in columns, "b column must be specified"
            assert "tau" in columns, "tau column must be specified"
            assert "tau R²" in columns, "tau R² column must be specified"

            super().__init__(columns, id)
        else:
            super().__init__(
                {
                    "Strain": ma_data.SummaryTranscoder.Column(
                        name="Strain",
                        input_included=False,
                        output_name="Strain (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=0,
                    ),
                    "Min stress": ma_data.SummaryTranscoder.Column(
                        name="Min stress",
                        input_included=False,
                        output_name="Min stress (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=1,
                    ),
                    "Max stress": ma_data.SummaryTranscoder.Column(
                        name="Max stress",
                        input_included=False,
                        output_name="Max stress (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=2,
                    ),
                    "Min force": ma_data.SummaryTranscoder.Column(
                        name="Min force",
                        input_included=False,
                        output_name="Min force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=3,
                    ),
                    "Max force": ma_data.SummaryTranscoder.Column(
                        name="Max force",
                        input_included=False,
                        output_name="Max force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=4,
                    ),
                    "a": ma_data.SummaryTranscoder.Column(
                        name="a",
                        input_included=False,
                        output_name="a (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=5,
                    ),
                    "b": ma_data.SummaryTranscoder.Column(
                        name="b",
                        input_included=False,
                        output_name="b (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=6,
                    ),
                    "tau": ma_data.SummaryTranscoder.Column(
                        name="tau",
                        input_included=False,
                        output_name="tau (s)",
                        output_units=ma_units.unit_registry.parse_units("s"),
                        output_header_column=7,
                    ),
                    "tau R²": ma_data.SummaryTranscoder.Column(
                        name="tau R²",
                        input_included=False,
                        output_name="tau R² (s²/s²)",
                        output_header_column=8,
                    ),
                },
                id,
            )


class SummaryData(ma_data.SummaryData):
    """
    Instron 68TM stepwise compression experiment summary data.

    Args:
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    @dataclasses.dataclass
    class Row(ma_data.SummaryData.Row):
        """
        Instron 68TM stepwise compression experiment summary data row.

        Args:
            strain_Pa: The strain at which the other parameters were measured.
            min_stress_Pa: The minimum stress recorded for the specified strain.
            max_stress_Pa: The maximum stress recorded for the specified strain.
            min_force_Pa: The minimum force recorded for the specified strain.
            max_force_Pa: The maximum force recorded for the specified strain.
            a_Pa: The parameter determining the initial stress of the exponential
                stress-strain regression.
            b_Pa: Steady-state value of the exponential stress-strain regression.
            tau_s: Time constant of the exponential stress-strain regression.
            tau_r2: Coefficient of determination of the exponential stress-strain
                regression.
        """

        strain_Pa: float = dataclasses.field(metadata={"column_name": "Strain"})
        min_stress_Pa: float = dataclasses.field(metadata={"column_name": "Min stress"})
        max_stress_Pa: float = dataclasses.field(metadata={"column_name": "Max stress"})
        min_force_Pa: float = dataclasses.field(metadata={"column_name": "Min force"})
        max_force_Pa: float = dataclasses.field(metadata={"column_name": "Max force"})
        a_Pa: float = dataclasses.field(metadata={"column_name": "a"})
        b_Pa: float = dataclasses.field(metadata={"column_name": "b"})
        tau_s: float = dataclasses.field(metadata={"column_name": "tau"})
        tau_r2: float = dataclasses.field(metadata={"column_name": "tau R²"})

    def __init__(self, transcoder: SummaryTranscoder, id: str = "") -> None:
        super().__init__(
            pd.DataFrame(columns=list(transcoder.columns.keys())),
            transcoder,
            id,
        )

    @property
    def transcoder(self) -> SummaryTranscoder:
        return cast(SummaryTranscoder, self._transcoder)

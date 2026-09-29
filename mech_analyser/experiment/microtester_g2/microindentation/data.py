import dataclasses
import mech_analyser.experiment.microtester_g2.data as ma_data
import mech_analyser.util.units as ma_units
import pandas as pd
import pyqtgraph as pg  # type: ignore

# NOTE: this is to ensure that the RawTranscoder gets appropriately imported
from mech_analyser.experiment.microtester_g2.data import RawTranscoder  # type: ignore
from typing import Any, cast


class ProcessedTranscoder(ma_data.ProcessedTranscoder):
    """
    Microtester G2 microindentation experiment processed data file transcoders.

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
            assert "Name" in columns, "Name column must be specified"
            assert "Cycle" in columns, "Cycle column must be specified"
            assert "Time" in columns, "Time column must be specified"
            assert "Force" in columns, "Force column must be specified"
            assert (
                "Indentation force" in columns
            ), "Indentation force column must be specified"
            assert (
                "Regression force" in columns
            ), "Regression force column must be specified"
            assert (
                "Tip displacement" in columns
            ), "Tip displacement column must be specified"
            assert (
                "Indentation depth" in columns
            ), "Indentation depth column must be specified"
            assert "δ/R" in columns, "δ/R column must be specified"
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
                        input_included=False,
                        output_name="Name",
                        output_header_column=0,
                        data_type=str,
                    ),
                    "Cycle": ma_data.RawTranscoder.Column(
                        name="Cycle",
                        input_included=False,
                        output_name="Cycle",
                        output_header_column=1,
                        data_type=str,
                    ),
                    "Time": ma_data.RawTranscoder.Column(
                        name="Time",
                        input_included=False,
                        output_name="Time (s)",
                        output_units=ma_units.unit_registry.parse_units("s"),
                        output_header_column=2,
                    ),
                    "Force": ma_data.RawTranscoder.Column(
                        name="Force",
                        input_included=False,
                        output_name="Force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=3,
                    ),
                    "Indentation force": ma_data.RawTranscoder.Column(
                        name="Indentation force",
                        input_included=False,
                        output_name="Indentation force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=4,
                    ),
                    "Regression force": ma_data.RawTranscoder.Column(
                        name="Regression force",
                        input_included=False,
                        output_name="Regression force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=5,
                    ),
                    "Tip displacement": ma_data.RawTranscoder.Column(
                        name="Tip displacement",
                        input_included=False,
                        output_name="Tip displacement (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=6,
                    ),
                    "Indentation depth": ma_data.RawTranscoder.Column(
                        name="Indentation depth",
                        input_included=False,
                        output_name="Indentation depth (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=7,
                    ),
                    "δ/R": ma_data.RawTranscoder.Column(
                        name="δ/R",
                        input_included=False,
                        output_name="δ/R (mm/mm)",
                        output_header_column=8,
                    ),
                    "Base displacement": ma_data.RawTranscoder.Column(
                        name="Base displacement",
                        input_included=False,
                        output_name="Base displacement (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=9,
                    ),
                    "Size": ma_data.RawTranscoder.Column(
                        name="Size",
                        input_included=False,
                        output_name="Size (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=10,
                    ),
                    "Temperature": ma_data.RawTranscoder.Column(
                        name="Temperature",
                        input_included=False,
                        output_name="Temperature (°C)",
                        output_units=ma_units.unit_registry.parse_units("C"),
                        output_header_column=11,
                    ),
                },
                id,
            )


class ProcessedData(ma_data.ProcessedData):
    """
    Microtester G2 microindentation experiment processed data.

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
        self.indentation_force = pd.Series([0.0] * self._frame.index.size)  # type: ignore
        self.regression_force = pd.Series([0.0] * self._frame.index.size)  # type: ignore
        self.indentation_depth = pd.Series([0.0] * self._frame.index.size)  # type: ignore
        self.delta_R = pd.Series([0.0] * self._frame.index.size)  # type: ignore

    @property
    def delta_R(self) -> "pd.Series[float]":
        return self._frame["δ/R"]  # type: ignore

    @delta_R.setter
    def delta_R(self, value: "pd.Series[float]") -> None:
        self._frame["δ/R"] = value

        # Move the delta/R column to be directly after the indentation depth column
        column: pd.Series = self._frame.pop("δ/R")  # type: ignore
        self._frame.insert(  # type: ignore
            self._frame.columns.get_loc("Indentation depth") + 1,  # type: ignore
            "δ/R",
            column,
        )

    @property
    def indentation_depth(self) -> "pd.Series[float]":
        return self._frame["Indentation depth"]  # type: ignore

    @indentation_depth.setter
    def indentation_depth(self, value: "pd.Series[float]") -> None:
        self._frame["Indentation depth"] = value

        # Move the indentation depth column to be directly after the tip displacement
        # column
        column: pd.Series = self._frame.pop("Indentation depth")  # type: ignore
        self._frame.insert(  # type: ignore
            self._frame.columns.get_loc("Tip displacement") + 1,  # type: ignore
            "Indentation depth",
            column,
        )

    @property
    def indentation_force(self) -> "pd.Series[float]":
        return self._frame["Indentation force"]  # type: ignore

    @indentation_force.setter
    def indentation_force(self, value: "pd.Series[float]") -> None:
        self._frame["Indentation force"] = value

        # Move the indentation force column to be directly after the force column
        column: pd.Series = self._frame.pop("Indentation force")  # type: ignore
        self._frame.insert(  # type: ignore
            self._frame.columns.get_loc("Force") + 1,  # type: ignore
            "Indentation force",
            column,
        )

    @property
    def regression_force(self) -> "pd.Series[float]":
        return self._frame["Regression force"]  # type: ignore

    @regression_force.setter
    def regression_force(self, value: "pd.Series[float]") -> None:
        self._frame["Regression force"] = value

        # Move the regression force column to be directly after the indentation
        # force column
        column: pd.Series = self._frame.pop("Regression force")  # type: ignore
        self._frame.insert(  # type: ignore
            self._frame.columns.get_loc("Indentation force") + 1,  # type: ignore
            "Regression force",
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
            e_modulus_r2: Reduced modulus of the Hertz equation regression.
        """

        e_modulus_r2: float = cast(float, kwargs.get("e_modulus_r2", 1.0))

        x_series: "pd.Series[float]" = self.tip_displacement
        y_series: "pd.Series[float]" = self.force
        y_regression_series: "pd.Series[float]" = self.regression_force
        x_column: ma_data.ProcessedTranscoder.Column = self.transcoder.get_column(
            "Tip displacement"
        )
        y_column: ma_data.ProcessedTranscoder.Column = self.transcoder.get_column("Force")
        y_regression_column: ma_data.ProcessedTranscoder.Column = (
            self.transcoder.get_column("Regression force")
        )
        title: str = "Hertz equation force-displacement regression"

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
                ma_units.convert_from_base_units(x_series.min(), x_column.output_units),  # type: ignore
                ma_units.convert_from_base_units(x_series.max(), x_column.output_units),  # type: ignore
            ],
            [
                max(
                    ma_units.convert_from_base_units(
                        y_series.max(),  # type: ignore
                        y_column.output_units,
                    ),
                    ma_units.convert_from_base_units(
                        y_regression_series.max(),  # type: ignore
                        y_regression_column.output_units,
                    ),
                )
            ]
            * 2,
            name="Regression domain",
            pen=None,
            fillLevel=min(
                ma_units.convert_from_base_units(
                    y_series.min(),  # type: ignore
                    y_column.output_units,
                ),
                ma_units.convert_from_base_units(
                    y_regression_series.min(),  # type: ignore
                    y_regression_column.output_units,
                ),
            ),
            brush=pg.mkBrush(200, 200, 255, 100),  # type: ignore
        )

        # Add the regression coefficient of determination
        self._plot.getPlotItem().plot(  # type: ignore
            [],
            [],
            name=f"R² = {round(e_modulus_r2, 4)}",
            pen=None,
        )


class SummaryTranscoder(ma_data.SummaryTranscoder):
    """
    Microtester G2 microindentation experiment summary data file transcoders.

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
            assert "Cycle" in columns, "Cycle column must be specified"
            assert "a" in columns, "a column must be specified"
            assert "b" in columns, "b column must be specified"
            assert "E-modulus" in columns, "E-modulus column must be specified"
            assert "E-modulus R²" in columns, "E-modulus R² column must be specified"
            assert (
                "Energy dissipated" in columns
            ), "Energy dissipated column must be specified"

            super().__init__(columns, id)
        else:
            super().__init__(
                {
                    "Cycle": ma_data.SummaryTranscoder.Column(
                        name="Cycle",
                        input_included=False,
                        output_name="Cycle",
                        output_header_column=0,
                        data_type=str,
                    ),
                    "a": ma_data.SummaryTranscoder.Column(
                        name="a",
                        input_included=False,
                        output_name="a (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=1,
                    ),
                    "b": ma_data.SummaryTranscoder.Column(
                        name="b",
                        input_included=False,
                        output_name="b (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=2,
                    ),
                    "E-modulus": ma_data.SummaryTranscoder.Column(
                        name="E-modulus",
                        input_included=False,
                        output_name="E-modulus (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=3,
                    ),
                    "E-modulus R²": ma_data.SummaryTranscoder.Column(
                        name="E-modulus R²",
                        input_included=False,
                        output_name="E-modulus R² (Pa²/Pa²)",
                        output_header_column=4,
                    ),
                    "Energy dissipated": ma_data.SummaryTranscoder.Column(
                        name="Energy dissipated",
                        input_included=False,
                        output_name="Energy dissipated (J)",
                        output_units=ma_units.unit_registry.parse_units("J"),
                        output_header_column=5,
                    ),
                },
                id,
            )


class SummaryData(ma_data.SummaryData):
    """
    Microtester G2 microindentation experiment summary data.

    Args:
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data.  If empty, a new identifier is generated.
    """

    @dataclasses.dataclass
    class Row(ma_data.SummaryData.Row):
        """
        Microtester G2 microindentation experiment summary data row.

        Args:
            Cycle: The cycle identifier.
            a_m: The parameter determining the initial tip displacement of the Hertz model
                regression equation.
            b_N: The parameter determining the initial force of the Hertz model regression
                equation.
            e_modulus_Pa: The scaling factor of the Hertz model regression equation.
            e_modulus_r2: The coefficient of determination of the Hertz model regression
                equation.
            energy_dissipated_J: The energy dissipated during the indentation cycle.
        """

        cycle: float = dataclasses.field(metadata={"column_name": "Cycle"})
        a_m: float = dataclasses.field(metadata={"column_name": "a"})
        b_N: float = dataclasses.field(metadata={"column_name": "b"})
        e_modulus_Pa: float = dataclasses.field(metadata={"column_name": "E-modulus"})
        e_modulus_r2: float = dataclasses.field(metadata={"column_name": "E-modulus R²"})
        energy_dissipated_J: float = dataclasses.field(
            metadata={"column_name": "Energy dissipated"}
        )

    def __init__(self, transcoder: SummaryTranscoder, id: str = "") -> None:
        super().__init__(
            pd.DataFrame(columns=list(transcoder.columns.keys())),
            transcoder,
            id,
        )

    @property
    def transcoder(self) -> SummaryTranscoder:
        return cast(SummaryTranscoder, self._transcoder)

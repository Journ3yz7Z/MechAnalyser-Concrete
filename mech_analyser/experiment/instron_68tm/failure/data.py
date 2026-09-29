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
    Instron 68TM compression-to-failure experiment processed data file transcoder.

    Args:
        columns: The mapping between the column name that the program recognises, the
            column name in the input file, and the column name in the output file.
        id: The unique identifier for the transcoder. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        columns: dict[str, ma_data.ProcessedTranscoder.Column] = {},
        id: str = "",
    ) -> None:
        if columns:
            assert "Time" in columns, "Time column must be specified"
            assert "Displacement" in columns, "Displacement column must be specified"
            assert "Force" in columns, "Force column must be specified"
            assert "Strain" in columns, "Strain column must be specified"
            assert "Stress" in columns, "Stress column must be specified"
            assert (
                "Regression stress" in columns
            ), "Regression stress column must be specified"
            assert "Toughness" in columns, "Toughness column must be specified"

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
                    "Displacement": ma_data.ProcessedTranscoder.Column(
                        name="Displacement",
                        input_included=False,
                        output_name="Displacement (mm)",
                        output_units=ma_units.unit_registry.parse_units("mm"),
                        output_header_column=1,
                    ),
                    "Force": ma_data.ProcessedTranscoder.Column(
                        name="Force",
                        input_included=False,
                        output_name="Force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=2,
                    ),
                    "Strain": ma_data.ProcessedTranscoder.Column(
                        name="Strain",
                        input_included=False,
                        output_name="Strain (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=3,
                    ),
                    "Stress": ma_data.ProcessedTranscoder.Column(
                        name="Stress",
                        input_included=False,
                        output_name="Compressive stress (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=4,
                    ),
                    "Regression stress": ma_data.ProcessedTranscoder.Column(
                        name="Regression stress",
                        input_included=False,
                        output_name="Regression stress (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=5,
                    ),
                    "Toughness": ma_data.ProcessedTranscoder.Column(
                        name="Toughness",
                        input_included=False,
                        output_name="Toughness (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=6,
                    ),
                },
                id,
            )


class ProcessedData(ma_data.ProcessedData):
    """
    Instron 68TM compression-to-failure experiment processed data.

    Args:
        frame: The underlying pd.DataFrame representation of the data.
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data. If empty, a new identifier is generated.
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
        self.regression_stress = pd.Series([0.0] * self._frame.index.size)  # type: ignore
        self.toughness = pd.Series([0.0] * self._frame.index.size)  # type: ignore

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
    def toughness(self) -> "pd.Series[float]":
        return self._frame["Toughness"]  # type: ignore

    @toughness.setter
    def toughness(self, value: "pd.Series[float]") -> None:
        self._frame["Toughness"] = value

    @property
    def transcoder(self) -> ProcessedTranscoder:
        return cast(ProcessedTranscoder, self._transcoder)

    def generate_plot(self, **kwargs: Any) -> None:
        """
        Generates a plot of the processed data.

        TODO: evaluate if plotting should be external to the class

        Args:
            strain1: Strain at which the regression begins.
            strain2: Strain at which the regression ends.
            e_modulus_r2: Reduced modulus of the linear regression.
        """

        strain1: float = cast(float, kwargs.get("strain1", 0.0))
        strain2: float = cast(float, kwargs.get("strain2", 1.0))
        e_modulus_r2: float = cast(float, kwargs.get("e_modulus_r2", 1.0))

        x_series: "pd.Series[float]" = self.strain
        y_series: "pd.Series[float]" = self.stress
        y_regression_series: "pd.Series[float]" = self.regression_stress
        x_column: ma_data.ProcessedTranscoder.Column = self.transcoder.get_column(
            "Strain"
        )
        y_column: ma_data.ProcessedTranscoder.Column = self.transcoder.get_column(
            "Stress"
        )
        y_regression_column: ma_data.ProcessedTranscoder.Column = (
            self.transcoder.get_column("Regression stress")
        )
        title: str = "Linear stress-strain regression"

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
                ma_units.convert_from_base_units(strain1, x_column.output_units),
                ma_units.convert_from_base_units(strain2, x_column.output_units),
            ],
            [
                ma_units.convert_from_base_units(
                    y_series.iloc[(x_series[x_series > strain2]).idxmin()],  # type: ignore
                    y_column.output_units,
                )
            ]
            * 2,
            name="Regression domain",
            pen=None,
            fillLevel=ma_units.convert_from_base_units(
                y_series.iloc[(x_series[x_series < strain1]).idxmax()],  # type: ignore
                y_column.output_units,
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
    Instron 68TM compression-to-failure experiment summary data file transcoder.

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
            assert "Ultimate force" in columns, "Ultimate force column must be specified"
            assert (
                "Ultimate strain" in columns
            ), "Ultimate strain column must be specified"
            assert (
                "Ultimate strength" in columns
            ), "Ultimate strength column must be specified"
            assert (
                "E-modulus strain 1" in columns
            ), "E-modulus strain 1 column must be specified"
            assert (
                "E-modulus strain 2" in columns
            ), "E-modulus strain 2 column must be specified"
            assert "c" in columns, "c column must be specified"
            assert "E-modulus" in columns, "E-modulus column must be specified"
            assert "E-modulus R²" in columns, "E-modulus R² column must be specified"
            assert (
                "Toughness strain" in columns
            ), "Toughness strain column must be specified"
            assert "Toughness" in columns, "Toughness column must be specified"

            super().__init__(columns, id)
        else:
            super().__init__(
                {
                    "Ultimate force": ma_data.SummaryTranscoder.Column(
                        name="Ultimate force",
                        input_included=False,
                        output_name="Ultimate force (N)",
                        output_units=ma_units.unit_registry.parse_units("N"),
                        output_header_column=0,
                    ),
                    "Ultimate strain": ma_data.SummaryTranscoder.Column(
                        name="Ultimate strain",
                        input_included=False,
                        output_name="Ultimate strain (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=1,
                    ),
                    "Ultimate strength": ma_data.SummaryTranscoder.Column(
                        name="Ultimate strength",
                        input_included=False,
                        output_name="Ultimate strength (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=2,
                    ),
                    "E-modulus strain 1": ma_data.SummaryTranscoder.Column(
                        name="E-modulus strain 1",
                        input_included=False,
                        output_name="E-modulus strain 1 (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=3,
                    ),
                    "E-modulus strain 2": ma_data.SummaryTranscoder.Column(
                        name="E-modulus strain 2",
                        input_included=False,
                        output_name="E-modulus strain 2 (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=4,
                    ),
                    "c": ma_data.SummaryTranscoder.Column(
                        name="c",
                        input_included=False,
                        output_name="c (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=5,
                    ),
                    "E-modulus": ma_data.SummaryTranscoder.Column(
                        name="E-modulus",
                        input_included=False,
                        output_name="E-modulus (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=6,
                    ),
                    "E-modulus R²": ma_data.SummaryTranscoder.Column(
                        name="E-modulus R²",
                        input_included=False,
                        output_name="E-modulus R² (Pa²/Pa²)",
                        output_header_column=7,
                    ),
                    "Toughness strain": ma_data.SummaryTranscoder.Column(
                        name="Toughness strain",
                        input_included=False,
                        output_name="Toughness strain (%)",
                        output_units=ma_units.unit_registry.parse_units("%"),
                        output_header_column=8,
                    ),
                    "Toughness": ma_data.SummaryTranscoder.Column(
                        name="Toughness",
                        input_included=False,
                        output_name="Toughness (Pa)",
                        output_units=ma_units.unit_registry.parse_units("Pa"),
                        output_header_column=9,
                    ),
                },
                id,
            )


class SummaryData(ma_data.SummaryData):
    """
    Instron 68TM compression-to-failure experiment summary data.

    Args:
        transcoder: The transcoder used to load and save the data.
        id: The unique identifier for the data. If empty, a new identifier is generated.
    """

    @dataclasses.dataclass
    class Row(ma_data.SummaryData.Row):
        """
        Instron 68TM compression-to-failure experiment summary data row.

        Args:
            ultimate_force_N: Maximum force that can be sustained before failure.
            ultimate_strain: Maximum strain that can be sustained before failure.
            ultimate_strength_Pa: Maximum stress that can be sustained before failure.
            e_modulus_strain_1: First strain at which the E-modulus is calculated.
            e_modulus_strain_2: Second strain at which the E-modulus is calculated.
            c_Pa: Y-intercept of the linear stress-strain regression.
            e_modulus_Pa: Gradient of the linear stress-strain regression.
            e_modulus_r2: Coefficient of determination of the linear stress-strain
                regression.
            toughness_strain: Strain at which the toughness is calculated.
            toughness_Pa: Area under the stress-strain curve up to the specified strain.
        """

        ultimate_force_N: float = dataclasses.field(
            metadata={"column_name": "Ultimate force"}
        )
        ultimate_strain: float = dataclasses.field(
            metadata={"column_name": "Ultimate strain"}
        )
        ultimate_strength_Pa: float = dataclasses.field(
            metadata={"column_name": "Ultimate strength"}
        )
        e_modulus_strain_1: float = dataclasses.field(
            metadata={"column_name": "E-modulus strain 1"}
        )
        e_modulus_strain_2: float = dataclasses.field(
            metadata={"column_name": "E-modulus strain 2"}
        )
        c_Pa: float = dataclasses.field(metadata={"column_name": "c"})
        e_modulus_Pa: float = dataclasses.field(metadata={"column_name": "E-modulus"})
        e_modulus_r2: float = dataclasses.field(metadata={"column_name": "E-modulus R²"})
        toughness_strain: float = dataclasses.field(
            metadata={"column_name": "Toughness strain"}
        )
        toughness_Pa: float = dataclasses.field(metadata={"column_name": "Toughness"})

    def __init__(self, transcoder: SummaryTranscoder, id: str = "") -> None:
        super().__init__(
            pd.DataFrame(columns=list(transcoder.columns.keys())),
            transcoder,
            id,
        )

    @property
    def transcoder(self) -> SummaryTranscoder:
        return cast(SummaryTranscoder, self._transcoder)

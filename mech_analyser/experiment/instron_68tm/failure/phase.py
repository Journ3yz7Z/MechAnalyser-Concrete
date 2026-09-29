import dataclasses
import enum
import mech_analyser.experiment.instron_68tm.failure.data as ma_data
import mech_analyser.experiment.instron_68tm.phase as ma_phase
import mech_analyser.util.units as ma_units
import mech_analyser.util.utils as ma_utils
import numpy as np
import pandas as pd

from scipy.integrate import cumulative_trapezoid  # type: ignore
from scipy.optimize import curve_fit  # type: ignore
from typing import Optional, cast


@dataclasses.dataclass
class Parameters(ma_phase.Parameters):
    """
    Instron 68TM compression-to-failure experiment phase parameters.

    Args:
        cross_sectional_area_m2: The cross-sectional surface area of the sample.
        initial_length_m: The initial length of the sample.
        abort_strain_pct: The strain at which the experiment aborts even if the
            sample has not yet failed.
        toughness_strain_pct: The strain at which the toughness is calculated.
            If set to None, the failure or abort strain will be used.
        e_modulus_method: Method used to calculate the Young's modulus.
        e_modulus_fixed_strain1_pct: The strain value which defines the first
            datapoint on the stress-strain curve used to calculate the Young's
            modulus.  It is ε1 in the equation E = (σ2 - σ1) / (ε2 - ε1).
        e_modulus_fixed_strain2_pct: The strain value which defines the second
            datapoint on the stress-strain curve used to calculate the Young's
            modulus.  It is ε2 in the equation E = (σ2 - σ1) / (ε2 - ε1).
        e_modulus_anchor_point: The point used to anchor the strain range over
            which the Young's modulus is to be calculated.
        e_modulus_anchor_offset_pct: The strain offset from the specific point
            on the stress-strain curve from/to which the Young's modulus will be
            calculated.  It, in combination with the anchor point, specifies ε1
            in the equation E = (σ2 - σ1) / (ε2 - ε1).
        e_modulus_anchor_strain_width_pct: The width of the range on the
            stress-strain curve over which the Young's modulus will be
            calculated.  It, in combination with the strain offset and anchor
            point, specifies ε2 in the equation E = (σ2 - σ1) / (ε2 - ε1).
        e_modulus_find_strain_min_pct: The strain value which defines the
            minimum strain that can be used to find the best approximation of
            the linear region of the stress-strain curve.
        e_modulus_find_strain_max_pct: The strain value which defines the
            maximum strain that can be used to find the best approximation of
            the linear region of the stress-strain curve.
        e_modulus_find_strain_width_pct: The width of the strain window which
            will be used to find the best approximation of the linear region of
            the stress-strain curve for all possible regions between the minimum
            and maximum strains.
    """

    class AnchorPoint(enum.Enum):
        """
        The point used to anchor the strain range over which the Young's modulus
        is to be calculated.
        """

        START = 0
        TOE = 1
        ULTIMATE = 2
        FAILURE = 3
        END = 4

    class Method(enum.Enum):
        """The method used to calculate the Young's modulus."""

        FIXED_RANGE = 0
        ANCHOR_POINT = 1
        FIND_RANGE = 2

    abort_strain_pct: float = 95.0
    toughness_strain_pct: Optional[float] = None
    e_modulus_method: Method = Method.FIXED_RANGE
    e_modulus_fixed_strain1_pct: float = 10.0
    e_modulus_fixed_strain2_pct: float = 15.0
    e_modulus_anchor_point: AnchorPoint = AnchorPoint.ULTIMATE
    e_modulus_anchor_offset_pct: float = 5.0
    e_modulus_anchor_strain_width_pct: float = 5.0
    e_modulus_find_strain_min_pct: float = 10.0
    e_modulus_find_strain_max_pct: float = 90.0
    e_modulus_find_strain_width_pct: float = 5.0

    @property
    def abort_strain(self) -> float:
        return ma_units.convert_to_base_units(
            self.abort_strain_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_anchor_offset(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_anchor_offset_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_anchor_strain_width(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_anchor_strain_width_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_find_strain_max(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_find_strain_max_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_find_strain_min(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_find_strain_min_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_find_strain_width(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_find_strain_width_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_fixed_strain1(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_fixed_strain1_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def e_modulus_fixed_strain2(self) -> float:
        return ma_units.convert_to_base_units(
            self.e_modulus_fixed_strain2_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def toughness_strain(self) -> Optional[float]:
        if self.toughness_strain_pct is None:
            return None

        return ma_units.convert_to_base_units(
            self.toughness_strain_pct,
            ma_units.unit_registry.Unit("%"),
        )


class Phase(ma_phase.Phase):
    """
    Instron 68TM compression-to-failure experiment phase.

    Args:
        raw_data: The raw data from which the processed data is created.
        processed_transcoder: Processed data transcoder.
        id: The unique identifier for the phase. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        raw_data: ma_data.ma_data.RawData,
        processed_transcoder: ma_data.ProcessedTranscoder,
        id: str = "",
    ) -> None:
        super().__init__(
            raw_data,
            ma_data.ProcessedData(
                pd.DataFrame(columns=raw_data.frame.columns),
                processed_transcoder,
            ),
            "Toughness",
            id,
        )

        self._aborted: bool = False
        self._c_Pa: float = 0.0
        self._e_modulus_Pa: float = 0.0
        self._e_modulus_r2: float = 0.0
        self._e_modulus_strain1: float = 0.0
        self._e_modulus_strain2: float = 0.0
        self._toughness_id: int = 0
        self._ultimate_id: int = 0

    @property
    def aborted(self) -> bool:
        return self._aborted

    @property
    def c_Pa(self) -> float:
        return self._c_Pa

    @property
    def e_modulus_Pa(self) -> float:
        return self._e_modulus_Pa

    @property
    def e_modulus_r2(self) -> float:
        return self._e_modulus_r2

    @property
    def e_modulus_strain1(self) -> float:
        return self._e_modulus_strain1

    @property
    def e_modulus_strain2(self) -> float:
        return self._e_modulus_strain2

    @property
    def processed_data(self) -> ma_data.ProcessedData:
        return cast(ma_data.ProcessedData, self._processed_data)

    @processed_data.setter
    def processed_data(self, value: ma_data.ma_data.ma_data.ProcessedData) -> None:
        self._processed_data = value

    @property
    def toughness_Pa(self) -> float:
        return self.processed_data.toughness.loc[self._toughness_id]

    @property
    def toughness_strain(self) -> float:
        return self.processed_data.strain.loc[self._toughness_id]

    @property
    def toughness_strain_pct(self) -> float:
        return ma_units.convert_from_base_units(
            self.toughness_strain,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def ultimate_force_N(self) -> float:
        return self.processed_data.force.loc[self._ultimate_id]

    @property
    def ultimate_strain(self) -> float:
        return self.processed_data.strain.loc[self._ultimate_id]

    @property
    def ultimate_strength_Pa(self) -> float:
        return self.processed_data.stress.loc[self._ultimate_id]

    def process(self, parameters: ma_phase.ma_phase.Parameters) -> None:
        """
        Processes the Instron 68TM compression-to-failure experiment raw data.

        Dataset filtering:
            -

        Columns that are populated:
            - Strain: The strain at each data point (if the initial length is manually
                specified).
            - Stress: The stress at each data point (if the cross-sectional area is
                manually specified).
            - Regression stress: Stress at each strain point as calculated by
                the E-modulus regression equation of the stress.
            - Toughness: The area under the stress-strain curve up until each
                data point.

        Summary parameters that are calculated:
            - Linear regression equation parameters (E and c in
                σ = E * ε + c, where E is the Young's modulus of the sample)
            - E-modulus coefficient of determination: The R-squared value of
                the linear regression used to determine the E-modulus.
            - E-modulus strains: The strains over which the E-modulus was
                calculated.
            - Toughness strain: The measured strain closest to the strain at
                which the toughness is to be calculated.
            - Toughness: The area under the stress-strain curve up until the
                toughness strain.
            - Ultimate force: The maximum force that the material can withstand.
            - Ultimate strain: The maximum strain that the material can
                withstand.
            - Ultimate strength: The maximum stress that the material can
                withstand.

        Args:
            parameters: The parameters to use when processing the data.
        """

        phase_parameters: Parameters = cast(Parameters, parameters)

        # Ensure that either strain exists in the raw data or it can be created from it
        if (
            not self.raw_data.transcoder.get_column("Strain").input_included
            and phase_parameters.initial_length_m <= 0.0
        ):
            raise ValueError(
                "Initial length must be specified if strain is not in the raw data."
            )
        # Ensure that either strain exists in the raw data or it can be created from it
        elif (
            not self.raw_data.transcoder.get_column("Stress").input_included
            and phase_parameters.cross_sectional_area_m2 <= 0.0
        ):
            raise ValueError(
                "Cross-sectional area must be specified if stress is not in the raw data."
            )

        # Create the processed data frame
        self.processed_data = ma_data.ProcessedData(
            self.raw_data.frame,
            self.processed_data.transcoder,
            self.id,
        )

        # Add the strain column if it does not exist
        if phase_parameters.initial_length_m > 0.0:
            self.processed_data.strain = pd.Series(  # type: ignore
                self.processed_data.displacement / phase_parameters.initial_length_m
            )

        # Add the stress column if it does not exist
        if phase_parameters.cross_sectional_area_m2 > 0.0:
            self.processed_data.stress = pd.Series(  # type: ignore
                self.processed_data.force / phase_parameters.cross_sectional_area_m2
            )

        # Add the toughness column
        # NOTE: np.insert is required because the output of
        #       cumulative_trapezoid() is an array one less than the length of
        #       the data frame
        self.processed_data.toughness = pd.Series(  # type: ignore
            np.insert(
                cumulative_trapezoid(
                    self.processed_data.stress,
                    self.processed_data.strain,
                ),
                0,
                0,
            )
        )

        # NOTE: in the event that there is no strain in the raw data, the tare strain
        #       needs to be calculated from the tare displacement and the initial length
        tare_strain = 0.0
        if self.raw_data.transcoder.get_column("Strain").input_included:
            tare_strain = self.raw_data.tare_strain
        elif phase_parameters.initial_length_m > 0.0:
            tare_strain = self.raw_data.tare_displacement_m / phase_parameters.initial_length_m

        # Calculate the summary parameters
        self._ultimate_id = self.processed_data.stress.idxmax()  # type: ignore
        self._aborted = (
            self.ultimate_strain + tare_strain
        ) >= phase_parameters.abort_strain
        self._toughness_id = (
            self._ultimate_id
            if phase_parameters.toughness_strain is None
            else (self.processed_data.strain - phase_parameters.toughness_strain)
            .abs()
            .idxmin()  # type: ignore
        )

        # Calculate the parameters of the linear equation that best fits the
        # data points
        match phase_parameters.e_modulus_method:
            # Calculate the E-modulus for the fixed range
            case Parameters.Method.FIXED_RANGE:
                self._e_modulus_strain1 = phase_parameters.e_modulus_fixed_strain1
                self._e_modulus_strain2 = phase_parameters.e_modulus_fixed_strain2
                self._c_Pa, self._e_modulus_Pa, self._e_modulus_r2 = (
                    self._execute_regression(
                        self._e_modulus_strain1,
                        self._e_modulus_strain2,
                    )
                )

            # Calculate the E-modulus for the range that is anchored to a point
            case Parameters.Method.ANCHOR_POINT:
                if (
                    phase_parameters.e_modulus_anchor_point
                    == Parameters.AnchorPoint.START
                ):
                    self._e_modulus_strain1 = phase_parameters.e_modulus_anchor_offset
                    self._e_modulus_strain2 = (
                        self._e_modulus_strain1
                        + phase_parameters.e_modulus_anchor_strain_width
                    )
                elif (
                    phase_parameters.e_modulus_anchor_point
                    == Parameters.AnchorPoint.ULTIMATE
                ):
                    self._e_modulus_strain2 = (
                        self.ultimate_strain - phase_parameters.e_modulus_anchor_offset
                    )
                    self._e_modulus_strain1 = (
                        self._e_modulus_strain2
                        - phase_parameters.e_modulus_anchor_strain_width
                    )
                elif (
                    phase_parameters.e_modulus_anchor_point == Parameters.AnchorPoint.END
                ):
                    self._e_modulus_strain2 = 1 - phase_parameters.e_modulus_anchor_offset
                    self._e_modulus_strain1 = (
                        self._e_modulus_strain2
                        - phase_parameters.e_modulus_anchor_strain_width
                    )

                # Ensure that the strains are bounded between 0% and 100%
                self._e_modulus_strain1 = max(0, min(1, self._e_modulus_strain1))
                self._e_modulus_strain2 = max(0, min(1, self._e_modulus_strain2))

                # Execute the regression
                self._c_Pa, self._e_modulus_Pa, self._e_modulus_r2 = (
                    self._execute_regression(
                        self._e_modulus_strain1,
                        self._e_modulus_strain2,
                    )
                )

            # Calculate the E-modulus for all possible windows and save the one
            # with the highest R^2 value
            case Parameters.Method.FIND_RANGE:
                results: list[tuple[float, float, float, float, float]] = [
                    (
                        round(float(strain), 2),
                        round(float(strain), 2)
                        + phase_parameters.e_modulus_find_strain_width,
                        *self._execute_regression(
                            float(strain),
                            float(strain) + phase_parameters.e_modulus_find_strain_width,
                        ),
                    )
                    for strain in np.arange(
                        phase_parameters.e_modulus_find_strain_min,
                        phase_parameters.e_modulus_find_strain_max
                        - phase_parameters.e_modulus_find_strain_width
                        + 0.01,
                        0.01,
                    )
                ]
                (
                    self._e_modulus_strain1,
                    self._e_modulus_strain2,
                    self._c_Pa,
                    self._e_modulus_Pa,
                    self._e_modulus_r2,
                ) = max(results, key=lambda x: x[4])

            case _:
                self._e_modulus_strain1 = float("NaN")
                self._e_modulus_strain2 = float("NaN")
                self._c_Pa = float("NaN")
                self._e_modulus_Pa = float("NaN")
                self._e_modulus_r2 = float("NaN")

        # Add the regression stress column
        self.processed_data.regression_stress = pd.Series(
            [
                self.y(x, self.e_modulus_Pa, self.c_Pa)  # type: ignore
                for x in self.processed_data.strain  # type: ignore
            ]
        )

        # Generate the processed data plot
        self.processed_data.generate_plot(
            strain1=self.e_modulus_strain1,
            strain2=self.e_modulus_strain2,
            e_modulus_r2=self.e_modulus_r2,
        )

    def _execute_regression(
        self,
        strain1: float,
        strain2: float,
    ) -> tuple[float, float, float]:
        """
        Executes the regression to determine the E-modulus and its corresponding
        coefficient of determination.

        Args:
            strain1: The lower bound of the strain range over which to regress.
            strain2: The upper bound of the strain range over which to regress.

        Returns:
            Tuple of c and E-modulus (the linear regression equation parameters)
            and their corresponding coefficient of determination.
        """

        x: "pd.Series[float]" = (  # type: ignore
            self.processed_data.strain[
                (self.processed_data.strain > strain1)
                & (self.processed_data.strain < strain2)
            ]
        )
        y: "pd.Series[float]" = self.processed_data.stress[
            (self.processed_data.strain > strain1)
            & (self.processed_data.strain < strain2)
        ]

        # Ensure that the regression has more data points than the polynomial
        # degree
        if len(x) < 3:
            return 0.0, 0.0, 0.0

        [e_modulus_Pa, c], _ = curve_fit(self.y, x, y)  # type: ignore

        e_modulus_r2: float = ma_utils.calculate_r2(
            list(y),
            [self.y(strain, e_modulus_Pa, c) for strain in x],  # type: ignore
        )

        return c, e_modulus_Pa, e_modulus_r2  # type: ignore

    @staticmethod
    def y(x: float, E: float, c: float) -> float:
        """
        Calculates the stress according to following equation:
        y = E * x + c

        Args:
            x: Strain at which the stress is to be calculated.
            E: Young's modulus (slope of the stress-strain curve).
            c: Initial stress at zero strain of the function.

        Returns:
            Stress at strain x.
        """

        return E * x + c

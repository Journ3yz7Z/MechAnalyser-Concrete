import dataclasses
import mech_analyser.experiment.instron_68tm.stepwise.data as ma_data
import mech_analyser.experiment.instron_68tm.phase as ma_phase
import mech_analyser.util.units as ma_units
import mech_analyser.util.utils as ma_utils
import numpy as np
import pandas as pd

from scipy.optimize import curve_fit  # type: ignore
from typing import Optional, cast


@dataclasses.dataclass
class Parameters(ma_phase.Parameters):
    """
    Instron 68TM stepwise compression experiment phase parameters.

    Args:
        cross_sectional_area_m2: The cross-sectional surface area of the sample.
        initial_length_m: The initial length of the sample.
        relaxation_strain_pct: The strain at which the sample is maintained while the
            sample relaxes.
        epsilon_pct: Tolerance for the strain within which it is considered to be within
            the relaxation phase.
        regression_data_points: Maximum number of data points to be included in the
            regression analysis.
    """

    relaxation_strain_pct: float = 5.0
    epsilon_pct: float = 0.1
    regression_data_points: Optional[int] = None

    @property
    def relaxation_strain(self) -> float:
        return ma_units.convert_to_base_units(
            self.relaxation_strain_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def epsilon(self) -> float:
        return ma_units.convert_to_base_units(
            self.epsilon_pct,
            ma_units.unit_registry.Unit("%"),
        )


class Phase(ma_phase.Phase):
    """
    Instron 68TM stepwise compression experiment phase.

    Args:
        raw_data: The raw data from which the processed data is created.
        processed_transcoder: Processed data transcoder.
        id: The unique identifier for the phase.  If empty, a new identifier is generated.
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
            "Strain = ?%",
            id,
        )

        self._a_Pa: float
        self._b_Pa: float = 0.0
        self._max_id: int = 0
        self._min_id: int = 0
        self._tau_s: float = 1.0
        self._tau_r2: float = 0.0

    @property
    def a_Pa(self) -> float:
        return self._a_Pa

    @property
    def b_Pa(self) -> float:
        return self._b_Pa

    @property
    def max_force_N(self) -> float:
        return self.processed_data.force.loc[self._max_id]

    @property
    def max_stress_Pa(self) -> float:
        return self.processed_data.stress.loc[self._max_id]

    @property
    def min_force_N(self) -> float:
        return self.processed_data.force.loc[self._min_id]

    @property
    def min_stress_Pa(self) -> float:
        return self.processed_data.stress.loc[self._min_id]

    @property
    def processed_data(self) -> ma_data.ProcessedData:
        return cast(ma_data.ProcessedData, self._processed_data)

    @processed_data.setter
    def processed_data(self, value: ma_data.ma_data.ma_data.ProcessedData) -> None:
        self._processed_data = value

    @property
    def tau_s(self) -> float:
        return self._tau_s

    @property
    def tau_r2(self) -> float:
        return self._tau_r2

    def process(self, parameters: ma_phase.ma_phase.Parameters) -> None:
        """
        Process the Instron 68TM stepwise compression experiment raw data.

        Dataset filtering:
            - Relaxation phase of the sample at the specified strain.

        Columns that are populated:
            - Strain: The strain at each data point (if the initial length is manually
                specified).
            - Stress: The stress at each data point (if the cross-sectional area is
                manually specified).
            - Relative time: Time elapsed since the start of the relaxation
                phase.
            - Regression stress: Stress at each relative time point as
                calculated by the exponential decay regression equation of the
                stress.

        Summary parameters that are calculated:
            - Exponential decay regression equation parameters (a, b, and tau in
                y = a * exp(-t / tau) + b)
            - Maximum and minimum force and stress values within the dataset.

        Args:
            parameters: The parameters to use when processing the phase.
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

        # Set the phase name
        self._name = f"Strain = {round(phase_parameters.relaxation_strain_pct, 1)}%"

        # Create the processed data frame
        filtered_raw_frame: pd.DataFrame
        if phase_parameters.initial_length_m <= 0.0:
            filtered_raw_frame = self.raw_data.frame[
                (
                    self.raw_data.strain
                    > (phase_parameters.relaxation_strain - phase_parameters.epsilon)
                )
                & (
                    self.raw_data.strain
                    < (phase_parameters.relaxation_strain + phase_parameters.epsilon)
                )
            ]
        else:
            filtered_raw_frame = self.raw_data.frame[
                (
                    (self.raw_data.displacement / phase_parameters.initial_length_m)
                    > (phase_parameters.relaxation_strain - phase_parameters.epsilon)
                )
                & (
                    (self.raw_data.displacement / phase_parameters.initial_length_m)
                    < (phase_parameters.relaxation_strain + phase_parameters.epsilon)
                )
            ]
        self.processed_data = ma_data.ProcessedData(
            filtered_raw_frame,
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

        # Add the relative time column
        self.processed_data.relative_time = (
            self.processed_data.time - self.processed_data.initial_time_s
        )

        # Calculate the parameters of the exponential decay equation that best fits the
        # data points
        self._a_Pa, self._b_Pa, self._tau_s, self._tau_r2 = self._execute_regression(
            phase_parameters.regression_data_points
        )

        # Add the regression stress column
        self.processed_data.regression_stress = pd.Series(
            [
                self.y(t, self.a_Pa, self.b_Pa, self.tau_s)  # type: ignore
                for t in self.processed_data.relative_time  # type: ignore
            ]
        )

        # Calculate the remaining summary parameters
        self._min_id = self.processed_data.force.idxmin()  # type: ignore
        self._max_id = self.processed_data.force.idxmax()  # type: ignore

        # Generate the processed data plot
        self.processed_data.generate_plot(
            regression_data_points=phase_parameters.regression_data_points,
            tau_r2=self.tau_r2,
        )

    def _calculate_regression_initial_guesses(
        self,
        x: "pd.Series[float]",
        y: "pd.Series[float]",
    ) -> tuple[float, float, float]:
        """
        Calculates initial guesses for the exponential decay regression equation
        parameters.  The parameters of interest for the equation y = a * exp(-t / tau) + b
        are a, b, and tau.
            - a: The initial amplitude of the exponential decay, i.e. y(0) - y(infinity)
            - b: The baseline value of the function, i.e. y(infinity)
            - tau: The time taken for the function to decay to 1/e of its initial value.

        Based on this, the initial guesses are chosen as follows:
            - a0 = y(0) - y(end)
            - b0 = y(end)
            - tau0 = (x(end) - x(0)) / 5

        Args:
            x: The independent variable data series.
            y: The dependent variable data series.

        Returns:
            Tuple of initial guesses for a, b, and tau.
        """

        a0: float = float(y.iloc[0] - y.iloc[-1])
        b0: float = float(y.iloc[-1])
        tau0: float = float((x.iloc[-1] - x.iloc[0]) / 5.0)

        return a0, b0, tau0

    def _calculate_regression_scaling_factor(self, y: "pd.Series[float]") -> float:
        """
        Calculates an appropriate scaling factor for regression parameters based on the
        magnitude of the variable to be regressed.

        Args:
            y: The data series to be regressed.

        Returns:
            The scaling factor such that max(y) / scaling_factor < 10.
        """

        max_value: float = cast(float, np.max(y.abs()))
        if max_value == 0:
            return 1.0

        # NOTE: target range for stability is between 1 and 1000.  Therefore, the scaling
        #       factor is calculated to bring the maximum value < 10
        exponent: int = int(np.floor(np.log10(max_value)))

        return 10**exponent

    def _execute_regression(
        self,
        regression_data_points: Optional[int],
    ) -> tuple[float, float, float, float]:
        """
        Executes the regression to determine the exponential decay regression equation
        parameters and the corresponding coefficient of determination.

        Args:
            regression_data_points: Maximum number of data points to be included in the
                regression.  If None is specified, the entire data set is included in the
                regression.

        Returns:
            Tuple of a, b, and tau (the exponential decay regression equation
            parameters) and their corresponding coefficient of determination.
        """

        # Filter the data to the specified number of data points
        x: "pd.Series[float]" = self.processed_data.relative_time.head(
            regression_data_points or self.processed_data.frame.index.size  # type: ignore
        )
        y: "pd.Series[float]" = self.processed_data.stress.head(
            regression_data_points or self.processed_data.frame.index.size  # type: ignore
        )

        # Ensure that the regression has more data points than the number of parameters to
        # be regressed
        if len(x) < 4:
            return 0.0, 0.0, 1.0, 0.0

        # Determine the initial guesses
        a0_Pa: float
        b0_Pa: float
        tau0_s: float
        a0_Pa, b0_Pa, tau0_s = self._calculate_regression_initial_guesses(x, y)

        # Calculate the scaling factor
        scaling_factor: float = self._calculate_regression_scaling_factor(y)
        y_scaled: "pd.Series[float]" = y / scaling_factor  # type: ignore
        a0_scaled: float = a0_Pa / scaling_factor
        b0_scaled: float = b0_Pa / scaling_factor

        # Regress the data
        [a_scaled, b_scaled, tau_s], _ = curve_fit(  # type: ignore
            self.y,
            x,
            y_scaled,
            p0=[a0_scaled, b0_scaled, tau0_s],
        )

        # Rescale the parameters
        a_Pa: float = cast(float, a_scaled) * scaling_factor
        b_Pa: float = cast(float, b_scaled) * scaling_factor

        # Calculate the coefficient of determination
        tau_r2: float = ma_utils.calculate_r2(
            list(y),
            [self.y(time_s, a_Pa, b_Pa, tau_s) for time_s in x],  # type: ignore
        )

        return a_Pa, b_Pa, tau_s, tau_r2  # type: ignore

    @staticmethod
    def y(t: float, a: float, b: float, tau_s: float) -> float:
        """
        Calculates the stress according to the following equation:
        y = a * exp(-t / tau) + b

        Args:
            t: Time at which the stress is to be calculated.
            a: Amplitude of the exponential decay.
            b: Baseline value of the function.
            tau_s: Time constant of the exponential decay.

        Returns:
            Stress at time t.
        """

        return a * np.exp(-t / tau_s) + b

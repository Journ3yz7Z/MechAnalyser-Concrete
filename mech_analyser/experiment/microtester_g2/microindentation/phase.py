import dataclasses
import mech_analyser.experiment.microtester_g2.microindentation.data as ma_data
import mech_analyser.experiment.microtester_g2.phase as ma_phase
import mech_analyser.util.utils as ma_utils
import numpy as np
import pandas as pd

from numpy.typing import NDArray
from scipy.optimize import curve_fit  # type: ignore
from typing import Optional, cast


@dataclasses.dataclass
class Parameters(ma_phase.Parameters):
    """
    Microtester G2 microindentation experiment phase parameters.

    Args:
        cycle: Compression/recover cycle number to which the data belongs.
        samples_to_skip: Number of samples at the beginning of the sample data to skip.
        R_m: Radius of the spherical indenter.
        v: Poisson's ratio of the sample.  See Bas, Onur, et al. "Rational design and
            fabrication of multiphasic soft network composites for tissue engineering
            articular cartilage: A numerical model-based approach." Chemical Engineering
            Journal 340 (2018): 15-23.
        delta_R_threshold: Threshold for the ratio of the indentation depth to the radius
            of the indenter.  If the ratio is greater than this value, then the Hertz
            model is not a valid approximation of the indentation response.
        use_regression_offsets: Include the indentation depth and force offsets as
            regression parameters.  They allow the model to fit the data more accurately
            for cases where the tip displacement does not equal the indentation depth and
            the measured force does not equal the indentation force.
        a_max_m: Upper bound for the tip displacement to indentation depth offset
            regression parameter.  If None, `a` can take any value.
        b_max_N: Upper bound for the measured force to indentation force offset regression
            parameter.  If None, `b` can take any value.
    """

    cycle: int = 1
    samples_to_skip: int = 0
    R_m: float = 0.0005
    v: float = 0.484
    delta_R_threshold: float = 0.1
    use_regression_offsets: bool = False
    a_max_m: Optional[float] = None
    b_max_N: Optional[float] = None


class Phase(ma_phase.Phase):
    """
    Microtester G2 microindentation experiment phase.

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
            "Cycle = ?",
            id,
        )

        self._a_m: float = 0.0
        self._b_N: float = 0.0
        self._e_modulus_Pa: float = 0.0
        self._e_modulus_r2: float = 0.0
        self._energy_dissipated_J: float = 0.0

    @property
    def a_m(self) -> float:
        return self._a_m

    @property
    def b_N(self) -> float:
        return self._b_N

    @property
    def energy_dissipated_J(self) -> float:
        return self._energy_dissipated_J

    @property
    def e_modulus_Pa(self) -> float:
        return self._e_modulus_Pa

    @property
    def e_modulus_r2(self) -> float:
        return self._e_modulus_r2

    @property
    def processed_data(self) -> ma_data.ProcessedData:
        return cast(ma_data.ProcessedData, self._processed_data)

    @processed_data.setter
    def processed_data(self, value: ma_data.ma_data.ma_data.ProcessedData) -> None:
        self._processed_data = value

    def process(self, parameters: ma_phase.ma_phase.Parameters) -> None:
        """
        Process the Microtester G2 microindentation experiment raw data.

        Dataset filtering:
            - Compression cycle number of the sample.
            - Indentation depth to indenter radius ratio below the specified threshold.

        Columns that are populated:
            - Indentation force: the force applied to indent the sample
            - Regression force: the force at each tip displacement point as calculated by
                the Hertz model regression equation of the force.
            - Indentation depth: the depth of the indentation.
            - delta/R ratio: the ratio of the indentation depth to the radius of the
                indenter.

        Summary parameters that are calculated:
            - Hertz model regression equation parameters (E, a, and b in
                F = 4/3 * E / (1 - v^2) * R^0.5 * (delta - a)^1.5 + b, where E is the
                Young's modulus of the sample)
            - Energy dissipated by the sample between the compression and
                relaxation cycles.

        Args:
            parameters: The parameters to use when processing the phase.
        """

        phase_parameters: Parameters = cast(Parameters, parameters)

        # Set the phase name
        self._name = f"Cycle = {phase_parameters.cycle}"

        # Create the processed data frame
        self.processed_data = ma_data.ProcessedData(
            self.raw_data.frame[
                # Compression cycle number of the sample
                (self.raw_data.cycle == f"{phase_parameters.cycle}-Compress")
                # Indentation depth to indenter radius ratio below the specified threshold
                & (
                    (
                        self.raw_data.tip_displacement
                        - self.raw_data.tip_displacement.min()  # type: ignore
                    )
                    / phase_parameters.R_m
                    < phase_parameters.delta_R_threshold
                )
            ].iloc[phase_parameters.samples_to_skip :],
            self.processed_data.transcoder,
            self.id,
        )

        # Calculate the parameters of the Hertz equation that best fits the data points
        self._a_m, self._b_N, self._e_modulus_Pa, self._e_modulus_r2 = (
            self._execute_regression(
                phase_parameters.R_m,
                phase_parameters.v,
                phase_parameters.use_regression_offsets,
                phase_parameters.a_max_m,
                phase_parameters.b_max_N,
            )
        )

        # Add the indentation force column
        self.processed_data.indentation_force = self.processed_data.force - self._b_N

        # Add the regression force column
        self.processed_data.regression_force = pd.Series(
            [
                self.y(
                    x,
                    phase_parameters.R_m,
                    phase_parameters.v,
                    self._e_modulus_Pa,
                    self._a_m,
                    self._b_N,
                ).real  # NOTE: ignore imaginary part due to numerical errors
                for x in self.processed_data.tip_displacement
            ]
        )

        # Add the indentation depth column
        self.processed_data.indentation_depth = (
            self.processed_data.tip_displacement - self._a_m
        )

        # Add the delta/R ratio column
        self.processed_data.delta_R = (
            self.processed_data.indentation_depth / phase_parameters.R_m  # type: ignore
        )

        # Calculate the remaining summary parameters
        self._energy_dissipated_J = self._calculate_energy_dissipated_J(
            phase_parameters.cycle,
            phase_parameters.samples_to_skip,
        )

        # Generate the processed data plot
        self.processed_data.generate_plot(e_modulus_r2=self._e_modulus_r2)

    def _calculate_energy_dissipated_J(self, cycle: int, samples_to_skip: int) -> float:
        """
        Calculates the energy dissipated by the sample between the compression
        and relaxation cycles, which is the area between the force-tip
        displacement curve.  It is calculated using the shoelace formula (Gauss'
        area formula), which is as follows:

        A = 0.5 * abs(
            x0*y1 + x1*y2 + ... + x_{n-1}*y0
            - y0*x1 - y1*x2 - ... - y_{n-1}*x0
        )

        Args:
            cycle: The cycle number for which the dissipated energy is to be
                calculated.
            samples_to_skip: Number of samples at the beginning of the sample
                data to skip.

        Returns:
            The energy dissipated by the sample between the compression and
            relaxation cycles (in uJ).
        """

        x: NDArray[np.float64] = (  # type: ignore
            self.raw_data.tip_displacement[
                (self.raw_data.cycle == f"{cycle}-Compress")
                | (self.raw_data.cycle == f"{cycle}-Recover")
            ]
            .iloc[samples_to_skip:]
            .to_numpy(dtype=np.float64)  # type: ignore
        )
        y: NDArray[np.float64] = (  # type: ignore
            self.raw_data.force[
                (self.raw_data.cycle == f"{cycle}-Compress")
                | (self.raw_data.cycle == f"{cycle}-Recover")
            ]
            .iloc[samples_to_skip:]
            .to_numpy(dtype=np.float64)  # type: ignore
        )

        # Close the curve
        if (x[0] != x[-1]) or (y[0] != y[-1]):
            x = np.append(x, x[0])
            y = np.append(y, y[0])

        # Calculate the area between the curves using the shoelace formula
        return 0.5 * np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

    def _calculate_regression_initial_guesses(
        self,
        x: "pd.Series[float]",
        y: "pd.Series[float]",
        v: float,
        R_m: float,
    ) -> tuple[float, float, float]:
        """
        Calculates initial guesses for the Hertz model equation regression equation
        parameters.  The parameters of interest for the equation
        y = 4 / 3 * E / (1 - v^2) * R^0.5 * (x - a)^1.5 + b are a, b, and E.
            - a: The offset between the tip displacement and the indentation depth.
            - b: The offset between the measured force and the indentation force.
            - E: The reduced modulus of the material.

        Based on this, the initial guesses are chosen as follows:
            - a0 = min(x)
            - b0 = min(y)
            - E0 = 3 / 4 * (1 - v^2) * (max(y) - b0) / (R^0.5 * (max(x) - a0)^1.5)

        Args:
            x: The independent variable data series.
            y: The dependent variable data series.
            v: The Poisson's ratio of the sample.
            R_m: The radius of the indenter.

        Returns:
            Tuple of initial guesses for a, b, and E.
        """

        a0: float = x.min()  # type: ignore
        b0: float = float(y.loc[x.idxmin()])  # type: ignore
        E0: float = float(
            3
            / 4
            * (1 - v**2)
            * (y.loc[x.idxmax()] - b0)  # type: ignore
            / (R_m**0.5 * (x.max() - a0) ** 1.5)  # type: ignore
        )

        return a0, b0, E0

    def _calculate_x_regression_scaling_factor(self, x: "pd.Series[float]") -> float:
        """
        Calculates an appropriate scaling factor for regression parameters based on the
        magnitude of the variable to be regressed.

        Args:
            x: The data series to be regressed.

        Returns:
            The scaling factor such that max(x) / scaling_factor < 10.
        """

        max_value: float = cast(float, np.max(x))
        if max_value <= 0:
            return 1.0

        # NOTE: target range for stability is between 1 and 1000.  Therefore, the scaling
        #       factor is calculated to bring the maximum value < 10
        exponent: int = int(np.floor(np.log10(max_value)))

        return 10**exponent

    def _calculate_y_regression_scaling_factor(self, y: "pd.Series[float]") -> float:
        """
        Calculates an appropriate scaling factor for regression parameters based on the
        magnitude of the variable to be regressed.

        Args:
            y: The data series to be regressed.

        Returns:
            The scaling factor such that max(y) / scaling_factor < 10.
        """

        max_value: float = cast(float, np.max(y))
        if max_value <= 0:
            return 1.0

        # NOTE: target range for stability is between 1 and 1000.  Therefore, the scaling
        #       factor is calculated to bring the maximum value < 10
        exponent: int = int(np.floor(np.log10(max_value)))

        return 10**exponent

    def _calculate_e_modulus_regression_scaling_factor(
        self,
        x_scaling_factor: float,
        y_scaling_factor: float,
    ) -> float:
        """
        Calculates an appropriate scaling factor for regression parameters based on the
        magnitude of the variable to be regressed.

        Args:
            x_scaling_factor: The scaling factor for the independent variable.
            y_scaling_factor: The scaling factor for the dependent variable.

        Returns:
            The scaling factor for the E-modulus regression parameter.
        """

        return y_scaling_factor / x_scaling_factor**1.5

    def _execute_regression(
        self,
        R_m: float,
        v: float,
        use_regression_offsets: bool,
        a_max_m: Optional[float],
        b_max_N: Optional[float],
    ) -> tuple[float, float, float, float]:
        """
        Executes the regression to determine the Hertz model equation parameters and the
        corresponding coefficient of determination.

        Args:
            R_m: The radius of the indenter.
            v: The Poisson's ratio of the sample.
            use_regression_offsets: Include the indentation depth and force offsets as
                regression parameters.  They allow the model to fit the data more
                accurately for cases where the tip displacement does not equal the
                indentation depth and the measured force does not equal the indentation
                force.
            a_max_m: Upper bound for the tip displacement to indentation depth offset
                regression parameter.  If None, `a` can take any value.
            b_max_N: Upper bound for the measured force to indentation force offset
                regression parameter.  If None, `b` can take any value.

        Returns:
            Tuple of a, b, and E-modulus (the Hertz model regression equation
            parameters) and their corresponding coefficient of determination.
        """

        # Filter the regression data to only start from the minimum force
        x: "pd.Series[float]" = self.processed_data.tip_displacement.loc[
            self.processed_data.force.idxmin() :  # type: ignore
        ]
        y: "pd.Series[float]" = self.processed_data.force.loc[
            self.processed_data.force.idxmin() :  # type: ignore
        ]

        # Ensure that the regression has more data points than the number of parameters to
        # be regressed
        if len(x) < 4:
            return 0.0, 0.0, 1.0, 0.0

        # Determine the initial guesses
        a0_m: float
        b0_N: float
        e0_modulus_Pa: float
        a0_m, b0_N, e0_modulus_Pa = self._calculate_regression_initial_guesses(
            x,
            y,
            v,
            R_m,
        )

        # Determine the parameter bounds
        a_range_m: tuple[float, float] = (
            -a_max_m if a_max_m is not None else -np.inf,
            x.min(),  # type: ignore
        )
        b_range_N: tuple[float, float] = (
            -b_max_N if b_max_N is not None else -np.inf,
            y.min(),  # type: ignore
        )
        e_modulus_range_Pa: tuple[float, float] = (0.0, np.inf)

        # Calculate the scaling factor
        #   - x
        x_scaling_factor: float = self._calculate_x_regression_scaling_factor(x)
        x_scaled: "pd.Series[float]" = x / x_scaling_factor  # type: ignore
        a0_scaled: float = a0_m / x_scaling_factor
        a_range_scaled: tuple[float, float] = (
            a_range_m[0] / x_scaling_factor,
            a_range_m[1] / x_scaling_factor,
        )
        #   - y
        y_scaling_factor: float = self._calculate_y_regression_scaling_factor(y)
        y_scaled: "pd.Series[float]" = y / y_scaling_factor  # type: ignore
        b0_scaled: float = b0_N / y_scaling_factor
        b_range_scaled: tuple[float, float] = (
            b_range_N[0] / y_scaling_factor,
            b_range_N[1] / y_scaling_factor,
        )
        #   - E-modulus
        e_modulus_scaling_factor: float = (
            self._calculate_e_modulus_regression_scaling_factor(
                x_scaling_factor,
                y_scaling_factor,
            )
        )
        e0_modulus_scaled: float = e0_modulus_Pa / e_modulus_scaling_factor
        e_modulus_range_scaled: tuple[float, float] = (
            e_modulus_range_Pa[0] / e_modulus_scaling_factor,
            e_modulus_range_Pa[1] / e_modulus_scaling_factor,
        )

        a_scaled: float
        b_scaled: float
        e_modulus_scaled: float
        e_modulus_r2: float

        # Regress the data
        try:
            # Include offsets in the regression analysis
            if use_regression_offsets:
                [e_modulus_scaled, a_scaled, b_scaled], _ = curve_fit(  # type: ignore
                    lambda _x, e, a, b: self.y(_x, R_m, v, e, a, b),  # type: ignore
                    x_scaled,
                    y_scaled,
                    p0=[e0_modulus_scaled, a0_scaled, b0_scaled],
                    bounds=(
                        (e_modulus_range_scaled[0], a_range_scaled[0], b_range_scaled[0]),
                        (e_modulus_range_scaled[1], a_range_scaled[1], b_range_scaled[1]),
                    ),
                    maxfev=20000,
                )
            # Fix offsets at the minimum tip displacement
            else:
                a_scaled = a0_scaled
                b_scaled = b0_scaled

                [e_modulus_scaled], _ = curve_fit(  # type: ignore
                    lambda _x, e: self.y(_x, R_m, v, e, a_scaled, b_scaled),  # type: ignore
                    x_scaled,
                    y_scaled,
                    p0=[e0_modulus_scaled],
                    bounds=[
                        (e_modulus_range_scaled[0],),
                        (e_modulus_range_scaled[1],),
                    ],
                    maxfev=20000,
                )

        except:
            # Solution could not converge
            print("Solution could not converge")
            return float("nan"), float("nan"), float("nan"), float("nan")

        # Rescale the parameters
        a_m: float = cast(float, a_scaled) * x_scaling_factor
        b_N: float = cast(float, b_scaled) * y_scaling_factor
        e_modulus_Pa: float = cast(float, e_modulus_scaled) * e_modulus_scaling_factor

        # Calculate the coefficient of determination
        e_modulus_r2 = ma_utils.calculate_r2(
            list(y),
            [self.y(i, R_m, v, e_modulus_Pa, a_m, b_N).real for i in x],  # type: ignore
        )

        return [a_m, b_N, e_modulus_Pa, e_modulus_r2]  # type: ignore

    @staticmethod
    def y(x: float, R: float, v: float, e: float, a: float, b: float) -> float:
        """
        Calculates the force according to the following equation:
        y = 4/3 * e / (1 - v^2) * R^0.5 * x^1.5

        Args:
            x: The tip displacement.
            R: The radius of the indenter.
            v: The Poisson's ratio of the sample.
            e: The Young's modulus of the sample.
            a: The tip displacement to indentation depth offset.
            b: The measured force to indentation force offset.

        Returns:
            The force at tip displacement x.
        """

        return 4 / 3 * e / (1 - v**2) * (R**0.5) * ((x - a) ** 1.5) + b

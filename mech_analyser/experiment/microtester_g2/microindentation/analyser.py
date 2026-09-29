import dataclasses
import mech_analyser.experiment.microtester_g2.analyser as ma_analyser
import mech_analyser.experiment.microtester_g2.microindentation.data as ma_data
import mech_analyser.experiment.microtester_g2.microindentation.phase as ma_phase
import mech_analyser.util.units as ma_units

from pathlib import Path
from typing import Optional, cast


@dataclasses.dataclass
class Parameters(ma_analyser.Parameters):
    """
    Parameters of the Microtester G2 microindentation experiment analyser.

    Args:
        cycles: Number of compression/recover cycles in the experiment.
        samples_to_skip: Number of samples at the beginning of the sample data to skip.
        R_um: Radius of the spherical indenter.
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
        a_max_um: Upper bound for the tip displacement to indentation depth offset
            regression parameter.  If None, `a` can take any value.
        b_max_um: Upper bound for the measured force to indentation force offset
            regression parameter.  If None, `b` can take any value.
    """

    cycles: int = 1
    samples_to_skip: int = 0
    R_um: float = 1000.0
    v: float = 0.5
    delta_R_threshold: float = 0.1
    use_regression_offsets: bool = False
    a_max_um: Optional[float] = None
    b_max_uN: Optional[float] = None

    @property
    def a_max_m(self) -> Optional[float]:
        if self.a_max_um is None:
            return None

        return ma_units.convert_to_base_units(
            self.a_max_um,
            ma_units.unit_registry.Unit("um"),
        )

    @property
    def b_max_N(self) -> Optional[float]:
        if self.b_max_uN is None:
            return None

        return ma_units.convert_to_base_units(
            self.b_max_uN,
            ma_units.unit_registry.Unit("uN"),
        )

    @property
    def R_m(self) -> float:
        return ma_units.convert_to_base_units(
            self.R_um,
            ma_units.unit_registry.Unit("um"),
        )


class Analyser(ma_analyser.Analyser):
    """
    Microtester G2 microindentation experiment analyser.

    Args:
        input_file: The path to the input file containing the output of the Microtester G2
            experiment.
        parameters: The parameters to use when analysing the experiment.
        raw_transcoder: The raw experiment data file transcoder.
        processed_transcoder: The processed experiment data file transcoder.
        summary_transcoder: The experiment summary data file transcoder.
        summary_data: The summary of the analysis.
        phases: The phases of the experiment.
        id: The unique identifier for the analyser.  If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        input_file: Path,
        parameters: Parameters,
        raw_transcoder: ma_data.ma_data.RawTranscoder,
        processed_transcoder: ma_data.ProcessedTranscoder,
        summary_transcoder: ma_data.SummaryTranscoder,
        phases: list[ma_phase.Phase] = [],
        id: str = "",
    ) -> None:
        super().__init__(
            input_file,
            parameters,
            raw_transcoder,
            ma_data.SummaryData(summary_transcoder),
            [phase for phase in phases],
            id,
        )

        # Cache for creating new phases as necessary
        self._processed_transcoder: ma_data.ProcessedTranscoder = processed_transcoder

        # Create the phases if they do not exist
        if not self.phases:
            for _ in range(parameters.cycles):
                self.phases.append(ma_phase.Phase(self.raw_data, processed_transcoder))

    @property
    def parameters(self) -> Parameters:
        return cast(Parameters, self._parameters)

    @property
    def phases(self) -> list[ma_phase.Phase]:  # type: ignore
        return cast(list[ma_phase.Phase], self._phases)

    @property
    def summary_data(self) -> ma_data.SummaryData:
        return cast(ma_data.SummaryData, self._summary_data)

    def analyse(self) -> None:
        """
        Analyses the output of the Microtester G2 microindentation experiment.
        """

        # Resize the processed data based on the number of relaxation intervals
        if len(self.phases) > self.parameters.cycles:
            del self.phases[self.parameters.cycles :]
        else:
            self.phases.extend(
                [
                    ma_phase.Phase(self.raw_data, self._processed_transcoder)
                    for _ in range(self.parameters.cycles - len(self.phases))
                ]
            )

        self.summary_data.clear_all_rows()

        for i in range(len(self.phases)):
            parameters = ma_phase.Parameters(
                cycle=i + 1,
                samples_to_skip=self.parameters.samples_to_skip,
                R_m=self.parameters.R_m,
                v=self.parameters.v,
                delta_R_threshold=self.parameters.delta_R_threshold,
                use_regression_offsets=self.parameters.use_regression_offsets,
                a_max_m=self.parameters.a_max_m,
                b_max_N=self.parameters.b_max_N,
            )
            self.phases[i].process(parameters)

            row = ma_data.SummaryData.Row(
                cycle=i + 1,
                a_m=self.phases[i].a_m,
                b_N=self.phases[i].b_N,
                e_modulus_Pa=self.phases[i].e_modulus_Pa,
                e_modulus_r2=self.phases[i].e_modulus_r2,
                energy_dissipated_J=self.phases[i].energy_dissipated_J,
            )
            self.summary_data.append_row(row)

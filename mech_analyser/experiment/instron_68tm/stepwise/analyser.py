import dataclasses
import mech_analyser.experiment.instron_68tm.analyser as ma_analyser
import mech_analyser.experiment.instron_68tm.stepwise.data as ma_data
import mech_analyser.experiment.instron_68tm.stepwise.phase as ma_phase
import mech_analyser.util.units as ma_units

from pathlib import Path
from typing import Optional, cast


@dataclasses.dataclass
class Parameters(ma_analyser.Parameters):
    """
    Parameters of the Instron 68TM stepwise compression experiment analyser.

    Args:
        tare_force_N: The force which will be used to tare the experiment.  All
            raw data points with force less than the tare force will be
            discarded, and all data points with force greater than the tare
            force will be offset accordingly.
        properties_file: The path to the properties file containing the cross-sectional
            area and initial length of the sample.
        read_cross_sectional_area: Whether to read the cross-sectional area from the
            properties file.
        read_initial_length: Whether to read the initial length from the properties
            file.
        cross_sectional_area_m2: The cross-sectional surface area of the sample.
        initial_length_m: The initial length of the sample.
        relaxation_strain_intervals: The number of intervals at which the sample has been
            configured to relax.  This in combination with the first strain gives the
            relaxation strains.  For instance, if the first strain is 5%, and the number
            of intervals is 6, then the experiment will relax the sample at 5%, 10%, 15%,
            20%, 25%, 30%.
        relaxation_strain_start_pct: The first strain at which the sample has been
            configured to relax.  This in combination with the number of intervals gives
            the relaxation strains.  For instance, if the first strain is 5%, and the
            number of intervals is 6, then the experiment will relax the sample at 5%,
            10%, 15%, 20%, 25%, 30%.
        epsilon_pct: Tolerance for the strain within which it is considered to be within
            the relaxation phase.
        regression_data_points: Maximum number of data points to be included in the
            regression analysis.
    """

    relaxation_strain_intervals: int = 1
    relaxation_strain_start_pct: float = 5.0
    epsilon_pct: float = 0.1
    regression_data_points: Optional[int] = None

    @property
    def epsilon(self) -> float:
        return ma_units.convert_to_base_units(
            self.epsilon_pct,
            ma_units.unit_registry.Unit("%"),
        )

    @property
    def relaxation_strain_start(self) -> float:
        return ma_units.convert_to_base_units(
            self.relaxation_strain_start_pct,
            ma_units.unit_registry.Unit("%"),
        )


class Analyser(ma_analyser.Analyser):
    """
    Instron 68TM stepwise compression experiment analyser.

    Args:
        input_file: The path to the input file containing the output of the Instron 68TM
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
            for _ in range(parameters.relaxation_strain_intervals):
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
        Analyses the output of the Instron 68TM stepwise compression experiment.
        """

        # Resize the processed data based on the number of relaxation intervals
        if len(self.phases) > self.parameters.relaxation_strain_intervals:
            del self.phases[self.parameters.relaxation_strain_intervals :]
        else:
            self.phases.extend(
                [
                    ma_phase.Phase(self.raw_data, self._processed_transcoder)
                    for _ in range(
                        self.parameters.relaxation_strain_intervals - len(self.phases)
                    )
                ]
            )

        self.summary_data.clear_all_rows()

        for i in range(len(self.phases)):
            parameters = ma_phase.Parameters(
                cross_sectional_area_m2=self.parameters.cross_sectional_area_m2,
                initial_length_m=self.parameters.initial_length_m,
                relaxation_strain_pct=self.parameters.relaxation_strain_start_pct
                * (i + 1),
                epsilon_pct=self.parameters.epsilon_pct,
                regression_data_points=self.parameters.regression_data_points,
            )
            self.phases[i].process(parameters)

            row = ma_data.SummaryData.Row(
                strain_Pa=parameters.relaxation_strain,
                min_stress_Pa=self.phases[i].min_stress_Pa,
                max_stress_Pa=self.phases[i].max_stress_Pa,
                min_force_Pa=self.phases[i].min_force_N,
                max_force_Pa=self.phases[i].max_force_N,
                a_Pa=self.phases[i].a_Pa,
                b_Pa=self.phases[i].b_Pa,
                tau_s=self.phases[i].tau_s,
                tau_r2=self.phases[i].tau_r2,
            )
            self.summary_data.append_row(row)

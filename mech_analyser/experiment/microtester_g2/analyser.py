import dataclasses
import mech_analyser.experiment.analyser as ma_analyser
import mech_analyser.experiment.microtester_g2.data as ma_data
import mech_analyser.experiment.microtester_g2.phase as ma_phase

from pathlib import Path
from typing import cast


@dataclasses.dataclass
class Parameters(ma_analyser.Parameters):
    """
    Parameters of the Microtester G2 experiment analyser.
    """

    pass


class Analyser(ma_analyser.Analyser):
    """
    Base class for all Microtester G2 analysers.

    Args:
        input_file: The path to the input file containing the output of the Microtester G2
            experiment.
        parameters: The parameters to use when analysing the experiment.
        raw_transcoder: The raw experiment data file transcoder.
        summary_data: The summary of the analysis.
        phases: The phases of the experiment.
        id: The unique identifier for the analyser.  If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        input_file: Path,
        parameters: Parameters,
        raw_transcoder: ma_data.RawTranscoder,
        summary_data: ma_data.SummaryData,
        phases: list[ma_phase.Phase] = [],
        id: str = "",
    ) -> None:
        super().__init__(
            parameters,
            ma_data.RawData.load(input_file, raw_transcoder),
            summary_data,
            [phase for phase in phases],
            id,
        )

    @property
    def parameters(self) -> Parameters:
        return cast(Parameters, self._parameters)

    @property
    def phases(self) -> list[ma_phase.Phase]:  # type: ignore
        return cast(list[ma_phase.Phase], self._phases)

    @property
    def raw_data(self) -> ma_data.RawData:
        return cast(ma_data.RawData, self._raw_data)

    @property
    def summary_data(self) -> ma_data.SummaryData:
        return cast(ma_data.SummaryData, self._summary_data)

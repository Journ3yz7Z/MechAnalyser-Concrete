import dataclasses
import mech_analyser.experiment.instron_68tm.data as ma_data
import mech_analyser.experiment.phase as ma_phase

from typing import cast


@dataclasses.dataclass
class Parameters(ma_phase.Parameters):
    """
    Base class for all Instron 68TM phase parameters.

    Args:
        cross_sectional_area_m2: The cross-sectional surface area of the sample.
        initial_length_m: The initial length of the sample.
    """

    cross_sectional_area_m2: float = 0.0
    initial_length_m: float = 0.0


class Phase(ma_phase.Phase):
    """
    Base class for all Instron 68TM phases.

    Args:
        raw_data: The raw data from which the processed data is created.
        processed_data: The processed data.
        name: The name of the phase.
        id: The unique identifier for the phase. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        raw_data: ma_data.RawData,
        processed_data: ma_data.ProcessedData,
        name: str = "Phase",
        id: str = "",
    ) -> None:
        super().__init__(raw_data, processed_data, name, id)

    @property
    def raw_data(self) -> ma_data.RawData:
        return cast(ma_data.RawData, self._raw_data)

    @property
    def processed_data(self) -> ma_data.ProcessedData:
        return cast(ma_data.ProcessedData, self._processed_data)

    @processed_data.setter
    def processed_data(self, value: ma_data.ma_data.ProcessedData) -> None:
        self._processed_data = value

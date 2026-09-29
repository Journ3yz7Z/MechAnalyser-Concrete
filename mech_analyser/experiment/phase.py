import dataclasses
from mech_analyser.experiment.data import (
    ProcessedData,
    RawData,
    RawTranscoder,
    SerialisedData,
)
from mech_analyser.util.serialiser import SerialisedObject, Serialiser
import pandas as pd
from typing import Any, Mapping, Self, Union, cast

# Serialised type aliases
SerialisedPhase = Mapping[str, Union[str, SerialisedData]]


@dataclasses.dataclass
class Parameters:
    """
    Base class for all phase parameters.
    """

    def copy(self) -> Self:
        """
        Returns a copy of the column.

        Returns:
            Self: A copy of the column.
        """
        return type(self)(**dataclasses.asdict(self))


class Phase(Serialiser):
    """
    Base class for all phases.

    Args:
        raw_data: The raw data from which the processed data is created.
        processed_data: The processed data.
        name: The name of the phase.
        id: The unique identifier for the phase. If empty, a new identifier is generated.
    """

    def __init__(
        self,
        raw_data: RawData,
        processed_data: ProcessedData,
        name: str = "Phase",
        id: str = "",
    ) -> None:
        super().__init__(id)

        self._raw_data: RawData = raw_data
        self._processed_data: ProcessedData = processed_data
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def raw_data(self) -> RawData:
        return self._raw_data

    @property
    def processed_data(self) -> ProcessedData:
        return self._processed_data

    @processed_data.setter
    def processed_data(self, value: ProcessedData) -> None:
        self._processed_data = value

    def process(self, parameters: Parameters) -> None:
        """
        Processes the raw data.  This could include populating additional columns or
        calculating summary parameters of the dataset.

        NOTE: this is an abstract method that will be overwritten in the child classes.

        Args:
            parameters: The parameters to use when processing the data.
        """

        raise NotImplementedError

    def serialise(self) -> SerialisedPhase:
        """
        Serialises the phase.

        Returns:
            SerialisedPhase: The serialised phase.
        """

        return {
            **super().serialise(),
            "name": self.name,
            "processed_data": self.processed_data.serialise(),
        }

    @classmethod
    def deserialise(cls, serialised_object: SerialisedPhase, **kwargs: Any) -> Self:
        """
        Deserialises the phase.

        Args:
            serialised_object: The serialised phase.
            raw_data: The raw data from which the processed data was created.

        Raises:
            ValueError: If the serialised processed data cannot be found or is of the
                wrong type.

        Returns:
            Phase: The deserialised phase.
        """

        raw_data: RawData = kwargs.get(
            "raw_data",
            RawData(pd.DataFrame(), RawTranscoder()),
        )
        del kwargs["raw_data"]
        id: str = cls._deserialise_id(serialised_object)
        processed_data: ProcessedData = cls._deserialise_processed_data(serialised_object)
        name: str = cls._deserialise_name(serialised_object)

        return cls._deserialise(
            id,
            serialised_object,
            raw_data,
            processed_data,
            name,
            **kwargs,
        )

    @classmethod
    def _deserialise(
        cls,
        id: str,
        serialised_phase: SerialisedPhase,
        raw_data: RawData,
        processed_data: ProcessedData,
        name: str,
        **kwargs: Any,
    ) -> Self:
        """
        Deserialises the phase.

        NOTE: this is an abstract method that will be overwritten in the child classes.

        Args:
            id: The unique identifier for the phase.
            serialised_phase: The serialised phase.
            raw_data: The raw data from which the processed data was created.
            processed_data: The processed data.
            name: The name of the phase.

        Returns:
            Phase: The deserialised phase.
        """

        return cls(raw_data, processed_data, name, id)

    @classmethod
    def _deserialise_name(cls, serialised_phase: SerialisedPhase) -> str:
        """
        Deserialises the name of the phase.

        Args:
            serialised_phase: The serialised phase.

        Raises:
            ValueError: If the name cannot be found or is not a string.

        Returns:
            The name of the phase.
        """

        if not isinstance(serialised_phase.get("name"), str):
            raise ValueError("Invalid phase name")

        return str(serialised_phase.get("name"))

    @classmethod
    def _deserialise_processed_data(
        cls,
        serialised_phase: SerialisedPhase,
    ) -> ProcessedData:
        """
        Deserialises the processed data.

        Args:
            serialised_phase: The serialised phase.

        Raises:
            ValueError: If the serialised processed data cannot be found or is of the
                wrong type.

        Returns:
            ProcessedData: The deserialised processed data.
        """

        if not isinstance(serialised_phase.get("processed_data"), dict) or not all(
            isinstance(i, str)
            for i in cast(dict[Any, Any], serialised_phase.get("processed_data")).keys()
        ):
            raise ValueError("Invalid processed data")

        return cast(
            ProcessedData,
            Serialiser.deserialise(
                cast(SerialisedObject, serialised_phase.get("processed_data"))
            ),
        )

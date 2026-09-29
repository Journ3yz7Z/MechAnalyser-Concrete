import dataclasses
from mech_analyser.experiment.data import RawData, SummaryData, SerialisedData
from mech_analyser.experiment.phase import Phase, SerialisedPhase
from mech_analyser.util.serialiser import SerialisedObject, Serialiser
from pathlib import Path
from typing import Any, Mapping, Self, Union, cast

# Serialised type aliases
SerialisedParameters = Mapping[str, Union[float, int, str, None]]
SerialisedAnalyser = Mapping[
    str,
    Union[str, SerialisedParameters, SerialisedData, list[SerialisedPhase]],
]


@dataclasses.dataclass
class Parameters(Serialiser):
    """
    Base class for all analyser parameters.
    """

    def copy(self) -> Self:
        """
        Returns a copy of the column.

        Returns:
            Self: A copy of the column.
        """
        return type(self)(**dataclasses.asdict(self))

    def serialise(self) -> SerialisedParameters:
        """
        Serialises the parameters.

        Returns:
            SerialisedParameters: The serialised parameters.
        """

        return {
            **super().serialise(),
            **dataclasses.asdict(self),
        }

    @classmethod
    def deserialise(cls, serialised_object: SerialisedParameters, **kwargs: Any) -> Self:
        """
        Deserialises the parameters.

        Args:
            serialised_object: The serialised parameters.

        Returns:
            Parameters: The deserialised parameters.
        """

        # NOTE: need to remove the custom module and class keys
        serialised_parameters: SerialisedParameters = dict(serialised_object)
        del serialised_parameters["module"]
        del serialised_parameters["class"]

        return cls(**serialised_parameters)  # type: ignore (subclasses will have different parameters)


class Analyser(Serialiser):
    """
    Base class for all analysers.

    Args:
        parameters: The parameters to use when analysing the experiment.
        raw_data: The raw experiment data.
        summary_data: The summary of the analysis.
        phases: The phases of the experiment.
        id: The unique identifier for the analyser. If empty, a new identifier is
            generated.
    """

    def __init__(
        self,
        parameters: Parameters,
        raw_data: RawData,
        summary_data: SummaryData,
        phases: list[Phase] = [],
        id: str = "",
    ) -> None:
        assert isinstance(phases, list), f"Phases must be a list, not {type(phases)}"
        assert all(
            isinstance(phase, Phase) for phase in phases
        ), "All phases must be of type Phase"

        super().__init__(id)

        self._parameters: Parameters = parameters
        self._phases: list[Phase] = phases
        self._raw_data: RawData = raw_data
        self._summary_data: SummaryData = summary_data

    @property
    def parameters(self) -> Parameters:
        return self._parameters

    @property
    def phases(self) -> list[Phase]:
        return self._phases

    @property
    def raw_data(self) -> RawData:
        return self._raw_data

    @property
    def summary_data(self) -> SummaryData:
        return self._summary_data

    def analyse(self) -> None:
        """
        Analyses the output of the experiment.

        NOTE: this is an abstract method that will be overwritten in the child classes.
        """

        raise NotImplementedError

    def save(self, output_file: Path, **kwargs: Any) -> None:
        """
        Saves the analysis to a file.  This includes the raw data, analysis summary, and
        all processed data.

        Args:
            output_file: The path to the output file which will contain the analysis
                results.
        """

        # Delete the file if it already exists
        if output_file.exists():
            output_file.unlink()

        # Save the file
        self._raw_data.save(output_file, **kwargs)
        self._summary_data.save(output_file, **kwargs)
        for phase in self._phases:
            phase.processed_data.save(
                output_file,
                phase.name,
                **kwargs,
            )

    def serialise(self) -> SerialisedAnalyser:
        """
        Serialises the analyser.

        Returns:
            SerialisedAnalyser: The serialised analyser.
        """

        return {
            **super().serialise(),
            "parameters": self._parameters.serialise(),
            "raw_data": self._raw_data.serialise(),
            "summary_data": self._summary_data.serialise(),
            "phases": [phase.serialise() for phase in self._phases],
        }

    @classmethod
    def deserialise(cls, serialised_object: SerialisedAnalyser, **kwargs: Any) -> Self:
        """
        Deserialises the analyser.

        Args:
            serialised_object: The serialised analyser.

        Raises:
            ValueError: If the serialised parameter cannot be found or is of the wrong
                type.

        Returns:
            Analyser: The deserialised analyser.
        """

        id: str = cls._deserialise_id(serialised_object)
        parameters: Parameters = cls._deserialise_parameters(serialised_object)
        raw_data: RawData = cls._deserialise_raw_data(serialised_object)
        summary_data: SummaryData = cls._deserialise_summary_data(serialised_object)
        phases: list[Phase] = cls._deserialise_phases(serialised_object, raw_data)

        return cls._deserialise(
            id, serialised_object, parameters, raw_data, summary_data, phases, **kwargs
        )

    @classmethod
    def _deserialise(
        cls,
        id: str,
        serialised_analyser: SerialisedAnalyser,
        parameters: Parameters,
        raw_data: RawData,
        summary_data: SummaryData,
        phases: list[Phase],
        **kwargs: Any,
    ) -> Self:
        """
        Deserialises the analyser.

        NOTE: this is an abstract method that will be overwritten in the child classes.

        Args:
            id: The unique identifier for the analyser.
            serialised_analyser: The serialised analyser.
            parameters: The deserialised parameters.
            raw_data: The deserialised raw data.
            summary_data: The deserialised summary data.
            phases: The deserialised phases.

        Returns:
            Analyser: The deserialised analyser.
        """

        return cls(parameters, raw_data, summary_data, phases, id)

    @classmethod
    def _deserialise_parameters(
        cls, serialised_analyser: SerialisedAnalyser
    ) -> Parameters:
        """
        Deserialises the parameters.

        Args:
            serialised_analyser: The serialised analyser.

        Raises:
            ValueError: If the serialised parameter cannot be found or is of the wrong
                type.

        Returns:
            Parameters: The deserialised parameters.
        """

        if not isinstance(serialised_analyser.get("parameters"), dict) or not all(
            isinstance(i, str)
            for i in cast(dict[Any, Any], serialised_analyser.get("parameters")).keys()
        ):
            raise ValueError("Invalid parameters")

        return cast(
            Parameters,
            Serialiser.deserialise(
                cast(SerialisedObject, serialised_analyser.get("parameters"))
            ),
        )

    @classmethod
    def _deserialise_raw_data(cls, serialised_analyser: SerialisedAnalyser) -> RawData:
        """
        Deserialises the raw data.

        Args:
            serialised_analyser: The serialised analyser.

        Raises:
            ValueError: If the serialised raw data cannot be found or is of the wrong
                type.

        Returns:
            RawData: The deserialised raw data.
        """

        if not isinstance(serialised_analyser.get("raw_data"), dict) or not all(
            isinstance(i, str)
            for i in cast(dict[Any, Any], serialised_analyser.get("raw_data")).keys()
        ):
            raise ValueError("Invalid raw data")

        return cast(
            RawData,
            Serialiser.deserialise(
                cast(SerialisedObject, serialised_analyser.get("raw_data"))
            ),
        )

    @classmethod
    def _deserialise_summary_data(
        cls, serialised_analyser: SerialisedAnalyser
    ) -> SummaryData:
        """
        Deserialises the summary data.

        Args:
            serialised_analyser: The serialised analyser.

        Raises:
            ValueError: If the serialised summary data cannot be found or is of the wrong
                type.

        Returns:
            SummaryData: The deserialised summary data.
        """

        if not isinstance(serialised_analyser.get("summary_data"), dict) or not all(
            isinstance(i, str)
            for i in cast(dict[Any, Any], serialised_analyser.get("summary_data")).keys()
        ):
            raise ValueError("Invalid summary data")

        return cast(
            SummaryData,
            Serialiser.deserialise(
                cast(SerialisedObject, serialised_analyser.get("summary_data"))
            ),
        )

    @classmethod
    def _deserialise_phases(
        cls,
        serialised_analyser: SerialisedAnalyser,
        raw_data: RawData,
    ) -> list[Phase]:
        """
        Deserialises the phases.

        Args:
            serialised_analyser: The serialised analyser.
            raw_data: The raw data associated with the phases.

        Raises:
            ValueError: If the serialised phases cannot be found or are of the wrong type.

        Returns:
            list[Phase]: The deserialised phases.
        """

        if (
            not isinstance(serialised_analyser.get("phases"), list)
            or not all(
                isinstance(i, dict)
                for i in cast(list[Any], serialised_analyser.get("phases"))
            )
            or not all(
                all(isinstance(j, str) for j in cast(dict[Any, Any], i).keys())
                for i in cast(list[Any], serialised_analyser.get("phases"))
            )
        ):
            raise ValueError("Invalid phases")

        return [
            cast(
                Phase,
                Serialiser.deserialise(cast(SerialisedObject, phase), raw_data=raw_data),
            )
            for phase in cast(list[SerialisedPhase], serialised_analyser.get("phases"))
        ]

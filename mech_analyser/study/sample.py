import dataclasses
from mech_analyser.experiment.analyser import Analyser, SerialisedAnalyser
from mech_analyser.util.serialiser import Serialiser
from pathlib import Path
from typing import Any, Mapping, Optional, Union

# Serialised type aliases
SerialisedBase = Mapping[str, Any]
SerialisedCategoryBase = dict[str, str]
SerialisedSample = dict[str, Union[str, SerialisedAnalyser]]


@dataclasses.dataclass
class Base(Serialiser):
    """
    A base class for all objects in the study.

    Args:
        id: The unique identifier for the object.  If empty, a new identifier is
            generated.
        name: The name of the object.
        description: A description of the object.
    """

    name: str = dataclasses.field(default="")
    description: str = dataclasses.field(default="")

    def __post_init__(self) -> None:
        super().__post_init__()

        assert isinstance(self.name, str), f"Name must be a string, not {type(self.name)}"
        assert isinstance(
            self.description, str
        ), f"Description must be a string, not {type(self.description)}"

    def serialise(self) -> SerialisedBase:
        """
        Serialises the object.

        Returns:
            SerialisedBase: The serialised object.
        """

        return {
            **super().serialise(),
            **dataclasses.asdict(self),
        }


@dataclasses.dataclass
class CategoryBase(Base):
    """
    A base class for all categories of a sample.

    Args:
        id: The unique identifier for the object.  If empty, a new identifier is
            generated.
        name: The name of the object.
        description: A description of the object.
    """

    def serialise(self) -> SerialisedCategoryBase:
        """
        Serialises the object.

        Returns:
            SerialisedCategoryBase: The serialised object.
        """

        return {
            **super().serialise(),
            **dataclasses.asdict(self),
        }


@dataclasses.dataclass
class Experiment(CategoryBase):
    """
    A class to represent an experiment.

    Args:
        id: The unique identifier for the experiment.  If empty, a new
            identifier is generated.
        name: The name of the experiment.
        description: A description of the experiment.
    """

    pass


@dataclasses.dataclass
class Group(CategoryBase):
    """
    A class defining the broadest manner in which a collection of samples can be
    related.  This is a high-level grouping of samples, and is analogous to a
    species in a biological sample or a material in a mechanical sample.

    Args:
        id: The unique identifier for the group.  If empty, a new identifier is
            generated.
        name: The name of the group.
        description: A description of the group.
    """

    pass


@dataclasses.dataclass
class Specimen(CategoryBase):
    """
    A class defining a more specific manner in which a collection of sample can
    be related than a Group.  This is a mid-level grouping of samples, and is
    analogous to a specimen in a biological and mechanical sample.

    Args:
        id: The unique identifier for the specimen.  If empty, a new identifier
            is generated.
        name: The name of the specimen.
        description: A description of the specimen.
    """

    pass


@dataclasses.dataclass
class Region(CategoryBase):
    """
    A class defining a more specific manner in which a collection of sample can
    be related than a Specimen.  This is a low-level grouping of samples, and is
    analogous to an organ or region from which a biological sample is taken or a
    region or area from which a mechanical sample is taken.

    Args:
        id: The unique identifier for the region.  If empty, a new identifier is
            generated.
        name: The name of the region.
        description: A description of the region.
    """

    pass


@dataclasses.dataclass
class Sample(Base):
    """
    A class to represent a sample.

    Args:
        id: The unique identifier for the sample.  If empty, a new identifier is
            generated.
        name: The name of the sample.
        description: A description of the sample.
        experiment: The experiment to which the sample belongs.  If None, the
            sample is not (yet) part of an experiment.
        group: The group to which the sample belongs.  If None, the sample is
            not part of a group.
        specimen: The specimen to which the sample belongs.  If None, the sample
            is not part of a specimen.
        region: The region to which the sample belongs.  If None, the sample is
            not part of a region.
    """

    experiment: Optional[Experiment] = None
    group: Optional[Group] = None
    specimen: Optional[Specimen] = None
    region: Optional[Region] = None
    analyser: Optional[Analyser] = None

    # TODO: remove paths if not needed
    input_file: Path = Path("")
    output_file: Path = Path("")

    def serialise(self) -> SerialisedSample:
        """
        Serialises the sample.

        Returns:
            SerialisedSample: The serialised sample.
        """

        return {
            **super().serialise(),
            "experiment": self.experiment.id if self.experiment else "",
            "group": self.group.id if self.group else "",
            "specimen": self.specimen.id if self.specimen else "",
            "region": self.region.id if self.region else "",
            "analyser": self.analyser.serialise() if self.analyser else "",
        }

from mech_analyser.study.sample import (
    Experiment,
    Group,
    Specimen,
    Region,
    Sample,
    SerialisedCategoryBase,
    SerialisedSample,
)
from mech_analyser.util.serialiser import SerialisedObject, Serialiser
from typing import Any, Mapping, Optional, Self, Union, cast


# Serialised type aliases
SerialisedStudy = Mapping[
    str,
    Union[
        str,
        list[Union[SerialisedCategoryBase, SerialisedSample]],
    ],
]


class Study(Serialiser):
    """
    Represents a study containing experiments, groups, specimens, regions, and samples.

    Args:
        id: The unique identifier for the study. If empty, a new identifier is
            generated.
        name: The name of the study.
        description: A description of the study.
    """

    def __init__(self, id: str = "", name: str = "", description: str = "") -> None:
        assert isinstance(name, str), f"Name must be a string, not {type(name)}"
        assert isinstance(
            description, str
        ), f"Description must be a string, not {type(description)}"

        super().__init__(id)

        self.name: str = name
        self.description: str = description

        self._experiments: list[Experiment] = []
        self._groups: list[Group] = []
        self._specimens: list[Specimen] = []
        self._regions: list[Region] = []
        self._samples: list[Sample] = []

    @property
    def experiments(self) -> list[Experiment]:
        return self._experiments

    @property
    def groups(self) -> list[Group]:
        return self._groups

    @property
    def specimens(self) -> list[Specimen]:
        return self._specimens

    @property
    def regions(self) -> list[Region]:
        return self._regions

    @property
    def samples(self) -> list[Sample]:
        return self._samples

    def add_experiment(self, experiment: Experiment) -> None:
        """
        Adds an experiment to the study.

        Args:
            experiment: The experiment to add to the study.
        """

        if experiment not in self._experiments:
            self._experiments.append(experiment)
            self._experiments.sort(key=lambda e: e.name)

    def remove_experiment(self, experiment: Experiment) -> None:
        """
        Removes an experiment from the study.

        Args:
            experiment: The experiment to remove from the study.
        """

        if experiment in self._experiments:
            self._experiments.remove(experiment)
            self._experiments.sort(key=lambda e: e.name)

    def get_experiment(self, id: str) -> Optional[Experiment]:
        """
        Obtains an experiment from the study by its ID.

        Args:
            id: The ID of the experiment to obtain.

        Returns:
            The experiment with the given ID, or None if not found.
        """

        assert isinstance(id, str), "Experiment ID must be a string"

        for experiment in self._experiments:
            if experiment.id == id:
                return experiment

        return None

    def add_group(self, group: Group) -> None:
        """
        Adds a group to the study.

        Args:
            group: The group to add to the study.
        """

        if group not in self._groups:
            self._groups.append(group)
            self._groups.sort(key=lambda g: g.name)

    def remove_group(self, group: Group) -> None:
        """
        Removes a group from the study.

        Args:
            group: The group to remove from the study.
        """

        if group in self._groups:
            self._groups.remove(group)
            self._groups.sort(key=lambda g: g.name)

    def get_group(self, id: str) -> Optional[Group]:
        """
        Obtains a group from the study by its ID.

        Args:
            id: The ID of the group to obtain.

        Returns:
            The group with the given ID, or None if not found.
        """

        assert isinstance(id, str), "Group ID must be a string"

        for group in self._groups:
            if group.id == id:
                return group

        return None

    def add_specimen(self, specimen: Specimen) -> None:
        """
        Adds a specimen to the study.

        Args:
            specimen: The specimen to add to the study.
        """

        if specimen not in self._specimens:
            self._specimens.append(specimen)
            self._specimens.sort(key=lambda s: s.name)

    def remove_specimen(self, specimen: Specimen) -> None:
        """
        Removes a specimen from the study.

        Args:
            specimen: The specimen to remove from the study.
        """

        if specimen in self._specimens:
            self._specimens.remove(specimen)
            self._specimens.sort(key=lambda s: s.name)

    def get_specimen(self, id: str) -> Optional[Specimen]:
        """
        Obtains a specimen from the study by its ID.

        Args:
            id: The ID of the specimen to obtain.

        Returns:
            The specimen with the given ID, or None if not found.
        """

        assert isinstance(id, str), "Specimen ID must be a string"

        for specimen in self._specimens:
            if specimen.id == id:
                return specimen

        return None

    def add_region(self, region: Region) -> None:
        """
        Adds a region to the study.

        Args:
            region: The region to add to the study.
        """

        if region not in self._regions:
            self._regions.append(region)
            self._regions.sort(key=lambda r: r.name)

    def remove_region(self, region: Region) -> None:
        """
        Removes a region from the study.

        Args:
            region: The region to remove from the study.
        """

        if region in self._regions:
            self._regions.remove(region)
            self._regions.sort(key=lambda r: r.name)

    def get_region(self, id: str) -> Optional[Region]:
        """
        Obtains a region from the study by its ID.

        Args:
            id: The ID of the region to obtain.

        Returns:
            The region with the given ID, or None if not found.
        """

        assert isinstance(id, str), "Region ID must be a string"

        for region in self._regions:
            if region.id == id:
                return region

        return None

    def add_sample(self, sample: Sample) -> None:
        """
        Adds a sample to the study.

        Args:
            sample: The sample to add to the study.
        """

        if sample not in self._samples:
            self._samples.append(sample)
            self._samples.sort(key=lambda s: s.name)

            if sample.experiment is not None:
                self.add_experiment(sample.experiment)
            if sample.group is not None:
                self.add_group(sample.group)
            if sample.specimen is not None:
                self.add_specimen(sample.specimen)
            if sample.region is not None:
                self.add_region(sample.region)

    def remove_sample(self, sample: Sample) -> None:
        """
        Removes a sample from the study.

        Args:
            sample: The sample to remove from the study.
        """

        if sample in self._samples:
            self._samples.remove(sample)
            self._samples.sort(key=lambda s: s.name)

    def get_sample(self, id: str) -> Optional[Sample]:
        """
        Obtains a sample from the study by its ID.

        Args:
            id: The ID of the sample to obtain.

        Returns:
            The sample with the given ID, or None if not found.
        """

        assert isinstance(id, str), "Sample ID must be a string"

        for sample in self._samples:
            if sample.id == id:
                return sample

        return None

    def get_samples(
        self,
        experiments: Optional[list[Experiment]] = None,
        groups: Optional[list[Group]] = None,
        specimens: Optional[list[Specimen]] = None,
        regions: Optional[list[Region]] = None,
    ) -> list[Sample]:
        """
        Obtains all samples in the study that match the experiment, group,
        specimen, and region filters.

        Args:
            experiments: The experiments by which to filter the samples. If
                None, filtering by experiment is ignored.
            groups: The groups by which to filter the samples. If None,
                filtering by group is ignored.
            specimens: The specimens by which to filter the samples. If None,
                filtering by specimen is ignored.
            regions: The regions by which to filter the samples. If None, all
                regions are included.

        Returns:
            A list of samples that match the given filters.
        """

        # If no filter is provided for a given parameter, use the full list of
        # said parameter
        experiments_filter: list[Experiment] = (
            experiments if experiments is not None else self._experiments
        )
        groups_filter: list[Group] = groups if groups is not None else self._groups
        specimens_filter: list[Specimen] = (
            specimens if specimens is not None else self._specimens
        )
        regions_filter: list[Region] = regions if regions is not None else self._regions

        return [
            sample
            for sample in self._samples
            if sample.experiment in experiments_filter
            and sample.group in groups_filter
            and sample.specimen in specimens_filter
            and sample.region in regions_filter
        ]

    def serialise(self) -> SerialisedStudy:
        """
        Serialises the study.

        Returns:
            The serialised study.
        """

        return {
            **super().serialise(),
            "name": self.name,
            "description": self.description,
            "experiments": [experiment.serialise() for experiment in self._experiments],
            "groups": [group.serialise() for group in self._groups],
            "specimens": [specimen.serialise() for specimen in self._specimens],
            "regions": [region.serialise() for region in self._regions],
            "samples": [sample.serialise() for sample in self._samples],
        }

    @classmethod
    def deserialise(cls, serialised_object: SerialisedObject, **kwargs: Any) -> Self:
        """
        Deserialises the study.

        Args:
            serialised_object: The serialised study.

        Returns:
            Study: The deserialised study.
        """

        # Deserialise the study
        study: Study = cls(
            id=cls._deserialise_id(serialised_object),
            name=cls._deserialise_name(serialised_object),
            description=cls._deserialise_description(serialised_object),
        )

        # Deserialise the study experiments, groups, specimens, regions, and samples and
        # add them to the study
        for experiment in cls._deserialise_experiments(serialised_object):
            study.add_experiment(experiment)
        for group in cls._deserialise_groups(serialised_object):
            study.add_group(group)
        for specimen in cls._deserialise_specimens(serialised_object):
            study.add_specimen(specimen)
        for region in cls._deserialise_regions(serialised_object):
            study.add_region(region)
        for sample in cls._deserialise_samples(serialised_object, study):
            study.add_sample(sample)

        return study

    @classmethod
    def _deserialise_name(cls, serialised_study: SerialisedStudy) -> str:
        """
        Deserialises the name of the study from the serialised study.

        Args:
            serialised_study: The serialised study.

        Raises:
            ValueError: If the name cannot be found or is not a string.

        Returns:
            The name of the study.
        """

        if not isinstance(serialised_study.get("name"), str):
            raise ValueError("Invalid study name")

        return str(serialised_study.get("name"))

    @classmethod
    def _deserialise_description(cls, serialised_study: SerialisedStudy) -> str:
        """
        Deserialises the description of the study from the serialised study.

        Args:
            serialised_study: The serialised study.

        Raises:
            ValueError: If the description cannot be found or is not a string.

        Returns:
            The description of the study.
        """

        if not isinstance(serialised_study.get("description"), str):
            raise ValueError("Invalid study description")

        return str(serialised_study.get("description"))

    @classmethod
    def _deserialise_experiments(
        cls,
        serialised_study: SerialisedStudy,
    ) -> list[Experiment]:
        """
        Deserialises the experiments of the study from the serialised study.

        Args:
            serialised_study: The serialised study.

        Raises:
            ValueError: If the experiments cannot be found, are not a list of
                dictionaries, or are missing required fields.

        Returns:
            The experiments of the study.
        """

        if not isinstance(serialised_study.get("experiments"), list) or not all(
            isinstance(experiment, dict)
            for experiment in serialised_study.get("experiments", [])
        ):
            raise ValueError("Invalid study experiments")

        try:
            return [
                Experiment(
                    **{
                        k: v
                        for k, v in cast(SerialisedCategoryBase, experiment).items()
                        if k not in ["class", "module"]
                    }
                )
                for experiment in serialised_study.get("experiments", [])
                if isinstance(experiment, dict)
            ]
        except (TypeError, AssertionError):
            raise ValueError("Invalid study experiment")

    @classmethod
    def _deserialise_groups(cls, serialised_study: SerialisedStudy) -> list[Group]:
        """
        Deserialises the groups of the study from the serialised study.

        Args:
            serialised_study: The serialised study.

        Raises:
            ValueError: If the groups cannot be found, are not a list of
                dictionaries, or are missing required fields.

        Returns:
            The groups of the study.
        """

        if not isinstance(serialised_study.get("groups"), list) or not all(
            isinstance(group, dict) for group in serialised_study.get("groups", [])
        ):
            raise ValueError("Invalid study groups")

        try:
            return [
                Group(
                    **{
                        k: v
                        for k, v in cast(SerialisedCategoryBase, group).items()
                        if k not in ["class", "module"]
                    }
                )
                for group in serialised_study.get("groups", [])
                if isinstance(group, dict)
            ]
        except (TypeError, AssertionError):
            raise ValueError("Invalid study group")

    @classmethod
    def _deserialise_specimens(cls, serialised_study: SerialisedStudy) -> list[Specimen]:
        """
        Deserialises the specimens of the study from the serialised study.

        Args:
            serialised_study: The serialised study.

        Raises:
            ValueError: If the specimens cannot be found, are not a list of
                dictionaries, or are missing required fields.

        Returns:
            The specimens of the study.
        """

        if not isinstance(serialised_study.get("specimens"), list) or not all(
            isinstance(specimen, dict)
            for specimen in serialised_study.get("specimens", [])
        ):
            raise ValueError("Invalid study specimens")

        try:
            return [
                Specimen(
                    **{
                        k: v
                        for k, v in cast(SerialisedCategoryBase, specimen).items()
                        if k not in ["class", "module"]
                    }
                )
                for specimen in serialised_study.get("specimens", [])
                if isinstance(specimen, dict)
            ]
        except (TypeError, AssertionError):
            raise ValueError("Invalid study specimen")

    @classmethod
    def _deserialise_regions(cls, serialised_study: SerialisedStudy) -> list[Region]:
        """
        Deserialises the regions of the study from the serialised study.

        Args:
            serialised_study: The serialised study.

        Raises:
            ValueError: If the regions cannot be found, are not a list of
                dictionaries, or are missing required fields.

        Returns:
            The regions of the study.
        """

        if not isinstance(serialised_study.get("regions"), list) or not all(
            isinstance(region, dict) for region in serialised_study.get("regions", [])
        ):
            raise ValueError("Invalid study regions")

        try:
            return [
                Region(
                    **{
                        k: v
                        for k, v in cast(SerialisedCategoryBase, region).items()
                        if k not in ["class", "module"]
                    }
                )
                for region in serialised_study.get("regions", [])
                if isinstance(region, dict)
            ]
        except (TypeError, AssertionError):
            raise ValueError("Invalid study region")

    @classmethod
    def _deserialise_samples(
        cls,
        serialised_study: SerialisedStudy,
        study: Self,
    ) -> list[Sample]:
        """
        Deserialises the samples of the study from the serialised study.

        Args:
            serialised_study: The serialised study.
            study: The study to which the samples belong.

        Raises:
            ValueError: If the samples cannot be found, are not a list of
                dictionaries, or are missing required fields.

        Returns:
            The samples of the study.
        """

        if not isinstance(serialised_study.get("samples"), list) or not all(
            isinstance(sample, dict) for sample in serialised_study.get("samples", [])
        ):
            raise ValueError("Invalid study samples")

        try:
            return [
                Sample(
                    id=cast(dict[Any, Any], sample)["id"],
                    name=cast(dict[Any, Any], sample)["name"],
                    description=cast(dict[Any, Any], sample)["description"],
                    experiment=study.get_experiment(
                        cast(dict[Any, Any], sample)["experiment"]
                    ),
                    group=study.get_group(cast(dict[Any, Any], sample)["group"]),
                    specimen=study.get_specimen(cast(dict[Any, Any], sample)["specimen"]),
                    region=study.get_region(cast(dict[Any, Any], sample)["region"]),
                )
                for sample in serialised_study.get("samples", [])
                if isinstance(sample, dict)
            ]
        except (KeyError, AssertionError):
            raise ValueError("Invalid study sample")

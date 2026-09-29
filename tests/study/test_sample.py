import unittest
from mech_analyser.study.sample import (
    Base,
    Experiment,
    Group,
    SerialisedSample,
    Specimen,
    Region,
    Sample,
    SerialisedBase,
)


class TestBase(unittest.TestCase):
    """
    Unit tests for the Base class.
    """

    def test_base_initialization(self) -> None:
        """
        Test that the Base class initializes correctly with valid inputs.
        """

        base = Base(name="Test Base", description="A test base object")
        self.assertNotEqual(base.id, "")
        self.assertEqual(base.name, "Test Base")
        self.assertEqual(base.description, "A test base object")

    def test_base_serialisation(self) -> None:
        """
        Test that the Base class serialises correctly into a dictionary.
        """

        base = Base(name="Test Base", description="A test base object")
        serialised: SerialisedBase = base.serialise()
        self.assertEqual(serialised["id"], base.id)
        self.assertEqual(serialised["name"], base.name)
        self.assertEqual(serialised["description"], base.description)


class TestExperiment(unittest.TestCase):
    """
    Unit tests for the Experiment class.
    """

    def test_experiment_initialization(self) -> None:
        """
        Test that the Experiment class initializes correctly with valid inputs.
        """

        experiment = Experiment(name="Test Experiment", description="A test experiment")
        self.assertEqual(experiment.name, "Test Experiment")
        self.assertEqual(experiment.description, "A test experiment")


class TestGroup(unittest.TestCase):
    """
    Unit tests for the Group class.
    """

    def test_group_initialization(self) -> None:
        """
        Test that the Group class initializes correctly with valid inputs.
        """

        group = Group(name="Test Group", description="A test group")
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.description, "A test group")


class TestSpecimen(unittest.TestCase):
    """
    Unit tests for the Specimen class.
    """

    def test_specimen_initialization(self) -> None:
        """
        Test that the Specimen class initializes correctly with valid inputs.
        """

        specimen = Specimen(name="Test Specimen", description="A test specimen")
        self.assertEqual(specimen.name, "Test Specimen")
        self.assertEqual(specimen.description, "A test specimen")


class TestRegion(unittest.TestCase):
    """
    Unit tests for the Region class.
    """

    def test_region_initialization(self) -> None:
        """
        Test that the Region class initializes correctly with valid inputs.
        """

        region = Region(name="Test Region", description="A test region")
        self.assertEqual(region.name, "Test Region")
        self.assertEqual(region.description, "A test region")


class TestSample(unittest.TestCase):
    """
    Unit tests for the Sample class.
    """

    def test_sample_initialization(self) -> None:
        """
        Test that the Sample class initializes correctly with valid inputs.
        """

        experiment = Experiment(name="Experiment 1", description="Description 1")
        group = Group(name="Group 1", description="Description 2")
        specimen = Specimen(name="Specimen 1", description="Description 3")
        region = Region(name="Region 1", description="Description 4")

        sample = Sample(
            name="Sample 1",
            description="A test sample",
            experiment=experiment,
            group=group,
            specimen=specimen,
            region=region,
        )

        self.assertEqual(sample.name, "Sample 1")
        self.assertEqual(sample.description, "A test sample")
        self.assertEqual(sample.experiment, experiment)
        self.assertEqual(sample.group, group)
        self.assertEqual(sample.specimen, specimen)
        self.assertEqual(sample.region, region)

    def test_sample_serialisation(self) -> None:
        """
        Test that the Sample class serialises correctly into a dictionary.
        """

        experiment = Experiment(name="Experiment 1", description="Description 1")
        group = Group(name="Group 1", description="Description 2")
        specimen = Specimen(name="Specimen 1", description="Description 3")
        region = Region(name="Region 1", description="Description 4")

        sample = Sample(
            name="Sample 1",
            description="A test sample",
            experiment=experiment,
            group=group,
            specimen=specimen,
            region=region,
        )

        serialised: SerialisedSample = sample.serialise()
        self.assertEqual(serialised["name"], "Sample 1")
        self.assertEqual(serialised["description"], "A test sample")
        self.assertEqual(serialised["experiment"], experiment.id)
        self.assertEqual(serialised["group"], group.id)
        self.assertEqual(serialised["specimen"], specimen.id)
        self.assertEqual(serialised["region"], region.id)


if __name__ == "__main__":
    unittest.main()

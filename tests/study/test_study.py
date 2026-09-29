import unittest
from mech_analyser.study.study import Study, SerialisedStudy
from mech_analyser.study.sample import Experiment, Group, Specimen, Region, Sample


class TestStudy(unittest.TestCase):
    """
    Unit tests for the Study class.
    """

    def setUp(self) -> None:
        """
        Set up a Study instance and related objects for testing.
        """

        self.study = Study(name="Test Study", description="A test study")

        # Create experiments
        self.experiment1 = Experiment(name="Experiment 1", description="Description 1")
        self.experiment2 = Experiment(name="Experiment 2", description="Description 2")

        # Create groups
        self.group1 = Group(name="Group 1", description="Description 1")
        self.group2 = Group(name="Group 2", description="Description 2")

        # Create specimens
        self.specimen1 = Specimen(name="Specimen 1", description="Description 1")
        self.specimen2 = Specimen(name="Specimen 2", description="Description 2")

        # Create regions
        self.region1 = Region(name="Region 1", description="Description 1")
        self.region2 = Region(name="Region 2", description="Description 2")

        # Create samples
        self.sample1 = Sample(
            name="Sample 1",
            description="A test sample",
            experiment=self.experiment1,
            group=self.group1,
            specimen=self.specimen1,
            region=self.region1,
        )
        self.sample2 = Sample(
            name="Sample 2",
            description="Another test sample",
            experiment=self.experiment2,
            group=self.group2,
            specimen=self.specimen2,
            region=self.region2,
        )
        self.sample3 = Sample(
            name="Sample 3",
            description="Yet another test sample",
            experiment=self.experiment1,
            group=self.group2,
            specimen=self.specimen1,
            region=self.region2,
        )

    def test_study_initialization(self) -> None:
        """
        Test that the Study class initializes correctly with valid inputs.
        """

        self.assertEqual(self.study.name, "Test Study")
        self.assertEqual(self.study.description, "A test study")
        self.assertEqual(len(self.study.experiments), 0)
        self.assertEqual(len(self.study.groups), 0)
        self.assertEqual(len(self.study.specimens), 0)
        self.assertEqual(len(self.study.regions), 0)
        self.assertEqual(len(self.study.samples), 0)

    def test_add_experiment(self) -> None:
        """
        Test adding an experiment to the study.
        """

        self.study.add_experiment(self.experiment1)
        self.assertIn(self.experiment1, self.study.experiments)

    def test_remove_experiment(self) -> None:
        """
        Test removing an experiment from the study.
        """

        self.study.add_experiment(self.experiment1)
        self.assertIn(self.experiment1, self.study.experiments)

        self.study.remove_experiment(self.experiment1)
        self.assertNotIn(self.experiment1, self.study.experiments)

    def test_get_experiment(self) -> None:
        """
        Test getting an experiment by ID.
        """

        self.study.add_experiment(self.experiment1)
        self.assertEqual(self.study.get_experiment(self.experiment1.id), self.experiment1)

    def test_add_group(self) -> None:
        """
        Test adding a group to the study.
        """

        self.study.add_group(self.group1)
        self.assertIn(self.group1, self.study.groups)

    def test_remove_group(self) -> None:
        """
        Test removing a group from the study.
        """

        self.study.add_group(self.group1)
        self.assertIn(self.group1, self.study.groups)

        self.study.remove_group(self.group1)
        self.assertNotIn(self.group1, self.study.groups)

    def test_get_group(self) -> None:
        """
        Test getting a group by ID.
        """

        self.study.add_group(self.group1)
        self.assertEqual(self.study.get_group(self.group1.id), self.group1)

    def test_add_specimen(self) -> None:
        """
        Test adding a specimen to the study.
        """

        self.study.add_specimen(self.specimen1)
        self.assertIn(self.specimen1, self.study.specimens)

    def test_remove_specimen(self) -> None:
        """
        Test removing a specimen from the study.
        """

        self.study.add_specimen(self.specimen1)
        self.assertIn(self.specimen1, self.study.specimens)

        self.study.remove_specimen(self.specimen1)
        self.assertNotIn(self.specimen1, self.study.specimens)

    def test_get_specimen(self) -> None:
        """
        Test getting a specimen by ID.
        """

        self.study.add_specimen(self.specimen1)
        self.assertEqual(self.study.get_specimen(self.specimen1.id), self.specimen1)

    def test_add_region(self) -> None:
        """
        Test adding a region to the study.
        """

        self.study.add_region(self.region1)
        self.assertIn(self.region1, self.study.regions)

    def test_remove_region(self) -> None:
        """
        Test removing a region from the study.
        """

        self.study.add_region(self.region1)
        self.assertIn(self.region1, self.study.regions)

        self.study.remove_region(self.region1)
        self.assertNotIn(self.region1, self.study.regions)

    def test_get_region(self) -> None:
        """
        Test getting a region by ID.
        """

        self.study.add_region(self.region1)
        self.assertEqual(self.study.get_region(self.region1.id), self.region1)

    def test_add_sample(self) -> None:
        """
        Test adding a sample to the study.
        """

        self.study.add_sample(self.sample1)
        self.assertIn(self.sample1, self.study.samples)
        self.assertIn(self.experiment1, self.study.experiments)
        self.assertIn(self.group1, self.study.groups)
        self.assertIn(self.specimen1, self.study.specimens)
        self.assertIn(self.region1, self.study.regions)

    def test_remove_sample(self) -> None:
        """
        Test removing a sample from the study.
        """

        self.study.add_sample(self.sample1)
        self.study.remove_sample(self.sample1)
        self.assertNotIn(self.sample1, self.study.samples)

    def test_get_sample(self) -> None:
        """
        Test getting a sample by ID.
        """

        self.study.add_sample(self.sample1)
        self.assertEqual(self.study.get_sample(self.sample1.id), self.sample1)

    def test_serialise(self) -> None:
        """
        Test serialisation of all objects.
        """

        self.study.add_experiment(self.experiment1)
        self.study.add_experiment(self.experiment2)
        self.study.add_group(self.group1)
        self.study.add_group(self.group2)
        self.study.add_specimen(self.specimen1)
        self.study.add_specimen(self.specimen2)
        self.study.add_region(self.region1)
        self.study.add_region(self.region2)
        self.study.add_sample(self.sample1)
        self.study.add_sample(self.sample2)
        self.study.add_sample(self.sample3)

        serialised: SerialisedStudy = self.study.serialise()

        self.assertEqual(serialised["id"], self.study.id)
        self.assertEqual(serialised["name"], self.study.name)
        self.assertEqual(serialised["description"], self.study.description)

        self.assertEqual(len(serialised["experiments"]), 2)
        self.assertIn(self.experiment1.serialise(), serialised["experiments"])
        self.assertIn(self.experiment2.serialise(), serialised["experiments"])

        self.assertEqual(len(serialised["groups"]), 2)
        self.assertIn(self.group1.serialise(), serialised["groups"])
        self.assertIn(self.group2.serialise(), serialised["groups"])

        self.assertEqual(len(serialised["specimens"]), 2)
        self.assertIn(self.specimen1.serialise(), serialised["specimens"])
        self.assertIn(self.specimen2.serialise(), serialised["specimens"])

        self.assertEqual(len(serialised["regions"]), 2)
        self.assertIn(self.region1.serialise(), serialised["regions"])
        self.assertIn(self.region2.serialise(), serialised["regions"])

        self.assertEqual(len(serialised["samples"]), 3)
        self.assertIn(self.sample1.serialise(), serialised["samples"])
        self.assertIn(self.sample2.serialise(), serialised["samples"])
        self.assertIn(self.sample3.serialise(), serialised["samples"])

    def test_deserialisation(self) -> None:
        """
        Test deserialisation of a study.
        """

        self.study.add_experiment(self.experiment1)
        self.study.add_group(self.group1)
        self.study.add_specimen(self.specimen1)
        self.study.add_region(self.region1)
        self.study.add_sample(self.sample1)

        serialised: SerialisedStudy = self.study.serialise()
        deserialised_study: Study = Study.deserialise(serialised)

        self.assertEqual(deserialised_study.id, self.study.id)
        self.assertEqual(deserialised_study.name, self.study.name)
        self.assertEqual(deserialised_study.description, self.study.description)

        self.assertEqual(len(deserialised_study.experiments), 1)
        self.assertEqual(deserialised_study.experiments[0], self.study.experiments[0])

        self.assertEqual(len(deserialised_study.groups), 1)
        self.assertEqual(deserialised_study.groups[0], self.study.groups[0])

        self.assertEqual(len(deserialised_study.specimens), 1)
        self.assertEqual(deserialised_study.specimens[0], self.study.specimens[0])

        self.assertEqual(len(deserialised_study.regions), 1)
        self.assertEqual(deserialised_study.regions[0], self.study.regions[0])

        self.assertEqual(len(deserialised_study.samples), 1)
        self.assertEqual(deserialised_study.samples[0], self.study.samples[0])


if __name__ == "__main__":
    unittest.main()

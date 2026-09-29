import unittest
from mech_analyser.util.serialiser import Serialiser, SerialisedObject
from typing import Any, Self, cast


class SerialiserChild(Serialiser):
    """
    Test instance of the Serialiser.

    Args:
        id: The unique identifier for the object.  If empty, a new identifier is
            generated.
    """

    @classmethod
    def deserialise(cls, serialised_object: SerialisedObject, **kwargs: Any) -> Self:
        """
        Deserialises the data.

        Args:
            serialised_object: The serialised data.

        Raises:
            ValueError: If the serialised parameter cannot be found or is of the wrong
                type.

        Returns:
            Data: The deserialised data.
        """

        return cls(serialised_object.get("id", ""))


class TestSerialiser(unittest.TestCase):
    """
    Unit tests for the Serialiser class.
    """

    def test_serialiser_initialization(self) -> None:
        """
        Test that the Serialiser class initializes correctly with a valid ID.
        """

        serialiser = SerialiserChild(id="1234")
        self.assertEqual(serialiser.id, "1234")

    def test_serialiser_initialization_with_empty_id(self) -> None:
        """
        Test that the Serialiser class generates a new ID when initialized with an empty ID.
        """

        serialiser = SerialiserChild()
        self.assertNotEqual(serialiser.id, "")

    def test_serialise(self) -> None:
        """
        Test that the Serialiser class serialises correctly into a dictionary.
        """

        serialiser = SerialiserChild(id="1234")
        serialised: SerialisedObject = serialiser.serialise()
        self.assertEqual(serialised["id"], "1234")
        self.assertEqual(serialised["module"], "tests.util.test_serialiser")
        self.assertEqual(serialised["class"], "SerialiserChild")

    def test_deserialise(self) -> None:
        """
        Test that the Serialiser class deserialises correctly from a dictionary.
        """
        serialised: SerialisedObject = {
            "id": "1234",
            "module": "tests.util.test_serialiser",
            "class": "SerialiserChild",
        }
        deserialised: SerialiserChild = cast(
            SerialiserChild,
            Serialiser.deserialise(serialised),
        )
        self.assertEqual(deserialised.id, "1234")

    def test_deserialise_invalid_module(self) -> None:
        """
        Test that deserialising with an invalid module raises a ValueError.
        """

        serialised: SerialisedObject = {
            "id": "1234",
            "module": "invalid.module",
            "class": "SerialiserChild",
        }
        with self.assertRaises(ImportError):
            Serialiser.deserialise(serialised)

    def test_deserialise_invalid_class(self) -> None:
        """
        Test that deserialising with an invalid class raises a ValueError.
        """

        serialised: SerialisedObject = {
            "id": "1234",
            "module": "tests.util.test_serialiser",
            "class": "InvalidClass",
        }
        with self.assertRaises(AttributeError):
            Serialiser.deserialise(serialised)

    def test_deserialise_invalid_id(self) -> None:
        """
        Test that deserialising with an invalid ID raises a AssertionError.
        """

        serialised: SerialisedObject = {
            "id": 1234,  # Invalid type
            "module": "tests.util.test_serialiser",
            "class": "SerialiserChild",
        }
        with self.assertRaises(AssertionError):
            Serialiser.deserialise(serialised)

    def test_deserialise_missing_keys(self) -> None:
        """
        Test that deserialising with missing keys raises a ValueError.
        """

        serialised: SerialisedObject = {
            "id": "1234",
            "module": "tests.util.test_serialiser",
        }  # Missing "class" key
        with self.assertRaises(ValueError):
            Serialiser.deserialise(serialised)


if __name__ == "__main__":
    unittest.main()

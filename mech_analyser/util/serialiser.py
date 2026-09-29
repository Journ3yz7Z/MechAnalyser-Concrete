import dataclasses
from typing import Any, Mapping, Self, Type
import uuid

# Serialised type aliases
SerialisedObject = Mapping[str, Any]


@dataclasses.dataclass
class Serialiser:
    """
    Base class for all serialisers.

    Args:
        id: The unique identifier for the object.  If empty, a new identifier is
            generated.
    """

    id: str = dataclasses.field(default="")

    def __post_init__(self) -> None:
        assert isinstance(self.id, str), f"ID must be a string, not {type(self.id)}"

        if self.id == "":
            self.id = str(uuid.uuid4())

    def serialise(self) -> SerialisedObject:
        """
        Serialises the object.

        Returns:
            SerialisedObject: The serialised object.
        """

        return {
            "module": self.__class__.__module__,
            "class": self.__class__.__name__,
            "id": self.id,
        }

    @classmethod
    def deserialise(cls, serialised_object: SerialisedObject, **kwargs: Any) -> Self:
        """
        Deserialises the object.

        Args:
            serialised_object: The serialised object.

        Returns:
            Serialiser: The deserialised object.
        """

        module_name: str = cls._deserialise_module(serialised_object)
        class_name: str = cls._deserialise_class(serialised_object)
        class_type: Type[Self] = getattr(
            __import__(module_name, fromlist=[class_name]),
            class_name,
        )

        # NOTE: need to deserialise using the specific class type to ensure that the
        #       correct class is created
        return class_type.deserialise(serialised_object, **kwargs)

    @classmethod
    def _deserialise_module(cls, serialised_object: SerialisedObject) -> str:
        """
        Deserialises the module name.

        Args:
            serialised_object: The serialised object.

        Raises:
            ValueError: If the module name cannot be found or is not a string.

        Returns:
            str: The deserialised module name.
        """

        if not isinstance(serialised_object.get("module"), str):
            raise ValueError("Invalid module name")

        return str(serialised_object.get("module", ""))

    @classmethod
    def _deserialise_class(cls, serialised_object: SerialisedObject) -> str:
        """
        Deserialises the class name.

        Args:
            serialised_object: The serialised object.

        Raises:
            ValueError: If the class name cannot be found or is not a string.

        Returns:
            str: The deserialised class name.
        """

        if not isinstance(serialised_object.get("class"), str):
            raise ValueError("Invalid class name")

        return str(serialised_object.get("class", ""))

    @classmethod
    def _deserialise_id(cls, serialised_object: SerialisedObject) -> str:
        """
        Deserialises the ID of the object.

        Args:
            serialised_object: The serialised object.

        Raises:
            ValueError: If the ID cannot be found or is not a string.

        Returns:
            The ID of the object.
        """

        if not isinstance(serialised_object.get("id"), str):
            raise ValueError("Invalid object ID")

        return str(serialised_object.get("id"))

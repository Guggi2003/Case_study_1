import os
from tinydb import TinyDB
from tinydb.storages import JSONStorage


class Entity:
    """Base class for entities that can be persisted to the database."""
    
    def __init__(self) -> None:
        pass

    def store_data(self) -> None:
        """Insert or update this entity in the database."""
        raise NotImplementedError("Subclasses must implement store_data()")

    def delete(self) -> None:
        """Delete this entity from the database."""
        raise NotImplementedError("Subclasses must implement delete()")

    def __str__(self) -> str:
        raise NotImplementedError("Subclasses must implement __str__()")

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def find_all(cls) -> list:
        """Find all entities in the database."""
        raise NotImplementedError("Subclasses must implement find_all()")

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return: int = 1):
        """Find entity/entities by attribute in the database."""
        raise NotImplementedError("Subclasses must implement find_by_attribute()")

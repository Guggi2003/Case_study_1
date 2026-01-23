import os
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from database import DatabaseConnector
from abc import ABC, abstractmethod
from datetime import datetime



class Entity(ABC):
    """Base class for entities that can be persisted to the database."""
    
    def __init__(self) -> None:
        self.created_at = datetime.now()

    @abstractmethod
    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    @abstractmethod
    def get_table_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_key_field(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        pass

    def store_data(self) -> None:
        """Insert or update this entity in the database."""
        db = DatabaseConnector().get_table(self.__class__.get_table_name())
        q = Query()
        key_field = self.__class__.get_key_field()
        existing = db.search(q[key_field] == getattr(self, key_field))
        if existing:
            db.update(self.__dict__, doc_ids=[existing[0].doc_id])
        else:
            db.insert(self.__dict__)

    def delete(self) -> None:
        """Delete this entity from the database."""
        db = DatabaseConnector().get_table(self.__class__.get_table_name())
        q = Query()
        key_field = self.__class__.get_key_field()
        existing = db.search(q[key_field] == getattr(self, key_field))
        if existing:
            db.remove(doc_ids=[existing[0].doc_id])

    @classmethod
    def find_all(cls) -> list:
        """Find all entities in the database."""
        db = DatabaseConnector().get_table(cls.get_table_name())
        items = []
        for data in db.all():
            try:
                items.append(cls.from_dict(data))
            except (KeyError, ValueError):
                # Skip invalid data entries
                continue
        return items

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return: int = 1):
        """Find entity/entities by attribute in the database."""
        db = DatabaseConnector().get_table(cls.get_table_name())
        q = Query()
        result = db.search(q[by_attribute] == attribute_value)
        if not result:
            return [] if num_to_return > 1 else None
        items = []
        for d in result[:num_to_return]:
            try:
                items.append(cls.from_dict(d))
            except (KeyError, ValueError):
                continue
        return items if num_to_return > 1 else (items[0] if items else None)

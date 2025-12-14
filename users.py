import os
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage


class User:
    # Shared DB table for all User instances
    db_connector = TinyDB(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json"),
        storage=JSONStorage
    ).table("users")

    def __init__(self, id: str, name: str) -> None:
        """Create a new user based on the given name and id"""
        self.id = id
        self.name = name

    def store_data(self) -> None:
        """Insert or update this user in the database (by id)."""
        q = Query()
        existing = self.db_connector.search(q.id == self.id)

        if existing:
            # update existing doc
            self.db_connector.update(self.__dict__, doc_ids=[existing[0].doc_id])
        else:
            # insert new doc
            self.db_connector.insert(self.__dict__)

    def delete(self) -> None:
        """Delete this user from the database (by id)."""
        q = Query()
        existing = self.db_connector.search(q.id == self.id)

        if existing:
            self.db_connector.remove(doc_ids=[existing[0].doc_id])

    def __str__(self) -> str:
        return f"User {self.id} - {self.name}"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def find_all(cls) -> list["User"]:
        """Find all users in the database."""
        users = []
        for user_data in cls.db_connector.all():
            users.append(cls(user_data["id"], user_data["name"]))
        return users

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return: int = 1):
        """Find user(s) by attribute in the database."""
        q = Query()
        result = cls.db_connector.search(q[by_attribute] == attribute_value)

        if not result:
            return None if num_to_return == 1 else []

        data = result[:num_to_return]
        users = [cls(d["id"], d["name"]) for d in data]
        return users[0] if num_to_return == 1 else users

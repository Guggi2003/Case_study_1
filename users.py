from entity import Entity
from datetime import datetime


class User(Entity):
    """User class - represents a user in the business logic."""

    def __init__(self, id: str, name: str) -> None:
        """Create a new user based on the given name and id."""
        super().__init__()
        self.id = id
        self.name = name

    def __str__(self) -> str:
        return f"User {self.id} - {self.name}"

    @classmethod
    def get_table_name(cls) -> str:
        return "users"

    @classmethod
    def get_key_field(cls) -> str:
        return "id"

    @classmethod
    def from_dict(cls, data: dict):
        user = User(data["id"], data["name"])
        if "created_at" in data:
            user.created_at = data["created_at"]
        return user
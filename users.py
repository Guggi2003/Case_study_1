from entity import Entity


class User(Entity):
    """User class - represents a user in the business logic."""

    def __init__(self, id: str, name: str) -> None:
        """Create a new user based on the given name and id."""
        super().__init__()
        self.id = id
        self.name = name

    def store_data(self) -> None:
        """Store this user - should be called through UserRepository."""
        raise NotImplementedError("Use UserRepository.save_user() instead")

    def delete(self) -> None:
        """Delete this user - should be called through UserRepository."""
        raise NotImplementedError("Use UserRepository.delete_user() instead")

    def __str__(self) -> str:
        return f"User {self.id} - {self.name}"

    @classmethod
    def find_all(cls) -> list["User"]:
        """Find all users - should be called through UserRepository."""
        raise NotImplementedError("Use UserRepository.get_all_users() instead")

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return: int = 1):
        """Find users by attribute - should be called through UserRepository."""
        raise NotImplementedError("Use UserRepository.find_users_by_attribute() instead")
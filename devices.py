from entity import Entity
from datetime import datetime


class Device(Entity):
    """Device class - represents a device in the business logic."""

    def __init__(self, device_name: str, managed_by_user_id: str):
        """Create a new device."""
        super().__init__()
        self.device_name = device_name
        # The user id of the user that manages the device
        # We don't store the user object itself, but only the id (as a key)
        self.managed_by_user_id = managed_by_user_id
        self.is_active = True

    def __str__(self):
        return f'Device (Object) {self.device_name} ({self.managed_by_user_id})'

    def set_managed_by_user_id(self, managed_by_user_id: str):
        """Set the user ID that manages this device."""
        self.managed_by_user_id = managed_by_user_id

    @classmethod
    def get_table_name(cls) -> str:
        return "devices"

    @classmethod
    def get_key_field(cls) -> str:
        return "device_name"

    @classmethod
    def from_dict(cls, data: dict):
        if "device_name" not in data or "managed_by_user_id" not in data:
            raise ValueError(f"Invalid data for Device: {data}")
        device = Device(data["device_name"], data["managed_by_user_id"])
        if "is_active" in data:
            device.is_active = data["is_active"]
        if "created_at" in data:
            device.created_at = data["created_at"]
        return device

    
from entity import Entity
from datetime import datetime
from enum import Enum


class DeviceState(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


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
        self.state = DeviceState.AVAILABLE

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
        if "state" in data:
            device.state = DeviceState(data["state"])
        return device

    def reserve(self):
        """Reserve the device."""
        if self.state == DeviceState.AVAILABLE:
            self.state = DeviceState.RESERVED
        else:
            raise ValueError(f"Cannot reserve device in state {self.state}")

    def release(self):
        """Release the device."""
        if self.state == DeviceState.RESERVED:
            self.state = DeviceState.AVAILABLE
        else:
            raise ValueError(f"Cannot release device in state {self.state}")

    def start_maintenance(self):
        """Start maintenance on the device."""
        if self.state in [DeviceState.AVAILABLE, DeviceState.RESERVED]:
            self.state = DeviceState.MAINTENANCE
        else:
            raise ValueError(f"Cannot start maintenance on device in state {self.state}")

    def end_maintenance(self):
        """End maintenance on the device."""
        if self.state == DeviceState.MAINTENANCE:
            self.state = DeviceState.AVAILABLE
        else:
            raise ValueError(f"Cannot end maintenance on device in state {self.state}")

    def deactivate(self):
        """Deactivate the device."""
        self.state = DeviceState.INACTIVE

    def activate(self):
        """Activate the device."""
        if self.state == DeviceState.INACTIVE:
            self.state = DeviceState.AVAILABLE
        else:
            raise ValueError(f"Cannot activate device in state {self.state}")
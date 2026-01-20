import os
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from users import User
from devices import Device


class Repository:
    """Base repository class for database operations."""
    
    def __init__(self, table_name: str):
        self.db_connector = TinyDB(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json"),
            storage=JSONStorage
        ).table(table_name)
    
    def save(self, obj_dict: dict, query_field: str, query_value: str) -> None:
        """Save (insert or update) an object in the database."""
        q = Query()
        existing = self.db_connector.search(q[query_field] == query_value)
        
        if existing:
            self.db_connector.update(obj_dict, doc_ids=[existing[0].doc_id])
        else:
            self.db_connector.insert(obj_dict)
    
    def delete_by_field(self, field: str, value: str) -> bool:
        """Delete an object by field."""
        q = Query()
        existing = self.db_connector.search(q[field] == value)
        
        if existing:
            self.db_connector.remove(doc_ids=[existing[0].doc_id])
            return True
        return False
    
    def find_all(self) -> list[dict]:
        """Find all objects in the database."""
        return self.db_connector.all()
    
    def find_by_attribute(self, attribute: str, value: str, num_to_return: int = 1) -> list[dict]:
        """Find objects by attribute."""
        q = Query()
        result = self.db_connector.search(q[attribute] == value)
        
        if not result:
            return [] if num_to_return > 1 else None
        
        return result[:num_to_return]


class UserRepository(Repository):
    """Repository for User objects."""
    
    def __init__(self):
        super().__init__("users")
    
    def save_user(self, user: User) -> None:
        """Save a user to the database."""
        self.save(user.__dict__, "id", user.id)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID."""
        return self.delete_by_field("id", user_id)
    
    def get_all_users(self) -> list[User]:
        """Get all users from the database."""
        users = []
        for user_data in self.find_all():
            users.append(User(user_data["id"], user_data["name"]))
        return users
    
    def find_user_by_id(self, user_id: str) -> User:
        """Find a user by ID."""
        result = self.find_by_attribute("id", user_id, num_to_return=1)
        if result:
            data = result[0]
            return User(data["id"], data["name"])
        return None
    
    def find_users_by_attribute(self, attribute: str, value: str, num_to_return: int = 1) -> list[User]:
        """Find users by any attribute."""
        result = self.find_by_attribute(attribute, value, num_to_return)
        if not result:
            return [] if num_to_return > 1 else None
        
        users = [User(d["id"], d["name"]) for d in result]
        return users if num_to_return > 1 else users[0]


class DeviceRepository(Repository):
    """Repository for Device objects."""
    
    def __init__(self):
        super().__init__("devices")
    
    def save_device(self, device: Device) -> None:
        """Save a device to the database."""
        self.save(device.__dict__, "device_name", device.device_name)
    
    def delete_device(self, device_name: str) -> bool:
        """Delete a device by name."""
        return self.delete_by_field("device_name", device_name)
    
    def get_all_devices(self) -> list[Device]:
        """Get all devices from the database."""
        devices = []
        for device_data in self.find_all():
            devices.append(Device(device_data["device_name"], device_data["managed_by_user_id"]))
        return devices
    
    def find_device_by_name(self, device_name: str) -> Device:
        """Find a device by name."""
        result = self.find_by_attribute("device_name", device_name, num_to_return=1)
        if result:
            data = result[0]
            return Device(data["device_name"], data["managed_by_user_id"])
        return None
    
    def find_devices_by_attribute(self, attribute: str, value: str, num_to_return: int = 1) -> list[Device]:
        """Find devices by any attribute."""
        result = self.find_by_attribute(attribute, value, num_to_return)
        if not result:
            return [] if num_to_return > 1 else None
        
        devices = [Device(d["device_name"], d["managed_by_user_id"]) for d in result]
        return devices if num_to_return > 1 else devices[0]

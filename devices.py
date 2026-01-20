from entity import Entity


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

    def store_data(self):
        """Store this device - should be called through DeviceRepository."""
        raise NotImplementedError("Use DeviceRepository.save_device() instead")

    def delete(self):
        """Delete this device - should be called through DeviceRepository."""
        raise NotImplementedError("Use DeviceRepository.delete_device() instead")

    def set_managed_by_user_id(self, managed_by_user_id: str):
        """Set the user ID that manages this device."""
        self.managed_by_user_id = managed_by_user_id

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str, num_to_return=1):
        """Find devices by attribute - should be called through DeviceRepository."""
        raise NotImplementedError("Use DeviceRepository.find_devices_by_attribute() instead")

    @classmethod
    def find_all(cls) -> list:
        """Find all devices - should be called through DeviceRepository."""
        raise NotImplementedError("Use DeviceRepository.get_all_devices() instead")



    

if __name__ == "__main__":
    # Create a device
    device1 = Device("Device1", "one@mci.edu")
    device2 = Device("Device2", "two@mci.edu") 
    device3 = Device("Device3", "two@mci.edu") 
    device4 = Device("Device4", "two@mci.edu") 
    device1.store_data()
    device2.store_data()
    device3.store_data()
    device4.store_data()
    device5 = Device("Device3", "four@mci.edu") 
    device5.store_data()

    #loaded_device = Device.find_by_attribute("device_name", "Device2")
    loaded_device = Device.find_by_attribute("managed_by_user_id", "two@mci.edu")
    if loaded_device:
        print(f"Loaded Device: {loaded_device}")
    else:
        print("Device not found.")

    devices = Device.find_all()
    print("All devices:")
    for device in devices:
        print(device)

    
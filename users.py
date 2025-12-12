import os

from tinydb import TinyDB, Query
import serializer

class User:

    db_connector_user = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'), storage=serializer).table('user')

    def __init__(self, user_id, user_name) -> None:
        """Create a new user based on the given name and id"""
        self.name = user_name
        self.id = user_id

    def store_data(self)-> None:
        """Save the user to the database"""
        print("Storing data...")

        # Check if the device already exists in the database
        UserQuery = Query()

        result = self.db_connector_user.search(UserQuery.user_name == self.user_name)
        
        if result:
            # Update the existing record with the current instance's data
            result = self.db_connector_user.update(self.__dict__, doc_ids=[result[0].doc_id])
            print("Data updated.")
        else:
            # If the device doesn't exist, insert a new record
            self.db_connector_user.insert(self.__dict__)
            print("Data inserted.")

    def delete(self) -> None:
        """Delete the user from the database"""
        print("Deleting data...")
        # Check if the device exists in the database
        UserQuery = Query()
        result = self.db_connector.search(UserQuery.user_name == self.user_name)
        if result:
            # Delete the record from the database
            self.db_connector_user.remove(doc_ids=[result[0].doc_id])
            print("Data deleted.")
        else:
            print("Data not found.")
    
    def __str__(self):
        return f"User {self.id} - {self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def find_all(cls) -> list:
        """Find all users in the database"""
        user_list = []
        for user_data in User.db_connector_user.all():
            user_list.append(User(user_data['device_name'], user_data['managed_by_user_id']))
        return user_list

    @classmethod
    def find_by_attribute(cls, by_attribute : str, attribute_value : str) -> 'User':
        """From the matches in the database, select the user with the given attribute value"""
        # Load data from the database and create an instance of the Device class
        UserQuery = Query()
        result = cls.db_connector_user.search(UserQuery[by_attribute] == attribute_value)

        if result:
            data = result[:num_to_return]
            device_results = [cls(d['device_name'], d['managed_by_user_id']) for d in data]
            return device_results if num_to_return > 1 else device_results[0]
        else:
            return None

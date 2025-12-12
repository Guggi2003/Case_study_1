import os

from tinydb import TinyDB, Query
from serializer import serializer

class User:


    db_connector_user = TinyDB(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json"),
        storage=serializer
    ).table("user")


    def __init__(self, user_id, user_name) -> None:
        """Create a new user based on the given name and id"""
        self.name = user_name
        self.id = user_id

    def store_data(self)-> None:
        """Save the user to the database"""
        print("Storing data...")

        # Check if the device already exists in the database
        UserQuery = Query()

        result = self.db_connector_user.search(UserQuery.id == self.id)
        
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
        result = self.db_connector_user.search(UserQuery.id == self.id)
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
    
    @classmethod
    def find_all(cls) -> list:
        """Find all users in the database"""
        users = []
        for user_data in cls.db_connector_user.all():
            users.append(cls(user_data["id"], user_data["name"]))
        return users


    @classmethod
    def find_by_attribute(cls, by_attribute : str, attribute_value : str, num_to_return: int = 1) -> 'User':
        """From the matches in the database, select the user with the given attribute value"""
        # Load data from the database and create an instance of the Device class
        UserQuery = Query()
        result = cls.db_connector_user.search(UserQuery[by_attribute] == attribute_value)

        if result:
            data = result[:num_to_return]
            user_results = [cls(d['id'], d['name']) for d in data]
            return user_results if num_to_return > 1 else user_results[0]
        else:
            return None

   

if __name__ == "__main__":
    # Create a user
    user1 = User("one@mci.edu", "Otto O-Ring")
    user2 = User("two@mci.edu", "Hans Zahnrad") 
    user1.store_data()
    user2.store_data()
    user3 = User("three@mci.edu", "Walter Welle") 
    user3.store_data()

    #loaded_user = User.find_by_attribute("device_name", "Device2")
    loaded_user = User.find_by_attribute("id", "one@mci.edu")
    if loaded_user:
        print(f"Loaded user {loaded_user}")
    else:
        print("User not found.")

    users = User.find_all()
    print("All users:")
    for user in users:
        print(user)
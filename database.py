import os
from tinydb import TinyDB
from tinydb.table import Table
from tinydb.storages import JSONStorage
from serializer import serializer

class DatabaseConnector:
    """
    Usage: DatabaseConnector().get_table(<table_name>)
    The information about the actual database file path and the serializer objects has been abstracted away into this class
    """
    # Turns the class into a naive singleton
    # --> not thread safe and doesn't handle inheritance particularly well
    __instance = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')

        return cls.__instance
    
    def get_table(self, table_name: str) -> Table:
        return TinyDB(self.__instance.path, storage=serializer).table(table_name)
from .db_manager import DatabaseManager
import os

class Config:
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    def get_current_database(self):
        return self.db_manager.get_current_database()
        
    def set_current_database(self, db_name):
        return self.db_manager.set_current_database(db_name)
        
    def create_database(self, db_name):
        return self.db_manager.create_database(db_name)
        
    def list_databases(self):
        return self.db_manager.list_databases()
        
    def initialize_default_database(self):
        return self.db_manager.initialize_default_database()
        
    def save(self):
        # Salva as configurações atuais
        pass
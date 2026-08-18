from .db_manager import DatabaseManager
import os

class Config:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.config_path = "config.json"
        self.ensure_config_file()

    def ensure_config_file(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as f:
                json.dump({
                    'current_database': None,
                    'databases': []
                }, f)

    def get_current_database(self):
        with open(self.config_path, 'r') as f:
            return json.load(f).get('current_database')

    def set_current_database(self, db_name):
        with open(self.config_path, 'r+') as f:
            data = json.load(f)
            data['current_database'] = db_name
            f.seek(0)
            json.dump(data, f)
            return True

    def create_database(self, db_name):
        # Check if database already exists
        if db_name in self.list_databases():
            return False, "Database already exists"
        try:
            # Create database file
            with open(db_name + '.db', 'w') as f:
                pass  # Create empty file
            self.add_database_to_config(db_name)
            return True, ""
        except Exception as e:
            return False, str(e)

    def add_database_to_config(self, db_name):
        with open(self.config_path, 'r+') as f:
            data = json.load(f)
            if db_name not in data['databases']:
                data['databases'].append(db_name)
                f.seek(0)
                json.dump(data, f)

    def list_databases(self):
        with open(self.config_path, 'r') as f:
            return json.load(f).get('databases', [])

    def initialize_default_database(self):
        # Create default database if none exists
        if not self.list_databases():
            success, msg = self.create_database('default_db')
            if success:
                self.set_current_database('default_db')

    def save(self):
        # Salva as configurações atuais
        with open('config.json', 'w') as f:
            json.dump({
                'current_database': self.get_current_database(),
                'databases': self.list_databases()
            }, f)
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
                # Salva as configurações atuais
        with open('config.json', 'w') as f:
            json.dump({
                'current_database': self.get_current_database(),
                'databases': self.list_databases()
            }, f)
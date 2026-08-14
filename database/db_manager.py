# database/db_manager.py
import os
import sqlite3
from dataclasses import dataclass

class Database:
    def __init__(self, name):
        self.name = name
        self.path = f'databases/{name}.sqlite'
        
    @property
    def exists(self):
        return os.path.exists(self.path)
        
@dataclass
class DatabaseManager:
    DB_DIR = 'databases'
    
    def __init__(self):
        if not os.path.exists(self.DB_DIR):
            os.makedirs(self.DB_DIR)
        
    def list_databases(self):
        if not os.path.exists(self.DB_DIR):
            return []
        
        db_files = [f for f in os.listdir(self.DB_DIR) if f.endswith('.sqlite')]
        return [Database(name=f) for f in db_files]
        
    def create_database(self, db_name):
        try:
            db = Database(db_name)
            if db.exists():
                return False, f'Banco {db_name} já existe'
            
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(db.path), exist_ok=True)
            
            # Cria o banco de dados e as tabelas básicas
            with sqlite3.connect(db.path) as conn:
                cursor = conn.cursor()
                
                # Exemplo de criação de tabela
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
                
                conn.commit()
            
            return True, f'Banco {db_name} criado com sucesso'
        except Exception as e:
            return False, f'Erro ao criar banco de dados: {str(e)}'
        
    def set_current_database(self, db_name):
        try:
            # Salva o banco de dados atual em um arquivo de configuração
            config_path = 'current_db.txt'
            with open(config_path, 'w') as f:
                f.write(db_name)
            
            return True, f'Banco {db_name} definido como atual'
        except Exception as e:
            return False, f'Erro ao definir banco de dados: {str(e)}'
        
    def get_current_database(self):
        try:
            config_path = 'current_db.txt'
            if not os.path.exists(config_path):
                return None, 'Nenhum banco de dados selecionado'
            
            with open(config_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            return None, f'Erro ao ler banco de dados atual: {str(e)}'
        
    def initialize_default_database(self):
        # Cria um banco de dados padrão se nenhum existir
        if not any(os.path.exists(os.path.join(self.DB_DIR, f)) for f in os.listdir(self.DB_DIR) if f.endswith('.sqlite')):
            success, message = self.create_database('default_db')
            if success:
                return True, message
        
        return False, 'Não foi possível criar o banco de dados padrão'

from .config import Config
import sqlite3

class Database:
    def __init__(self):
        self.config = Config()
        self.connection = None
        
    def connect(self):
        db_name = self.config.get_current_database()
        if not db_name:
            raise ValueError('Nenhum banco de dados selecionado')
        
        try:
            self.connection = sqlite3.connect(db_name)
            return True
        except sqlite3.Error as e:
            print(f'Erro ao conectar ao banco de dados: {e}')
            return False
        
    def execute(self, query, params=None):
        if not self.connection:
            if not self.connect():
                return False, 'Falha na conexão com o banco de dados'
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return True, cursor
        except sqlite3.Error as e:
            print(f'Erro na execução da query: {e}')
            return False, str(e)
        
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
# app/database/db.py
import sqlite3
import os
import atexit
import logging
import threading

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path if db_path else self._get_db_path()
            # Map of thread_id -> sqlite3.Connection
            self._connections = {}
            self._conn_lock = threading.Lock()
            self.connection = None
            self.initialize_database()
            atexit.register(self.close_connection)
            self.initialized = True

    @classmethod
    def reset_instance(cls):
        if cls._instance:
            try:
                cls._instance.close_connection()
            except Exception:
                pass
        cls._instance = None

    def _get_db_path(self):
        # Build a path relative to the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        return os.path.join(project_root, "Dados", "DADOS.DB")

    def initialize_database(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        main_tid = threading.get_ident()
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        with self._conn_lock:
            self.connection = conn
            self._connections[main_tid] = conn

        # Use the main thread connection to initialize schema/migrations
        self._create_tables()
        self._run_migrations()
        self.connection.commit()
        logging.info(f"Banco de dados inicializado em: {self.db_path}")

    def get_connection(self):
        tid = threading.get_ident()
        with self._conn_lock:
            conn = self._connections.get(tid)
            if conn:
                return conn
            # create a new connection for this thread
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._connections[tid] = conn
            return conn

    def close_connection(self):
        # Close all thread-specific connections
        with self._conn_lock:
            for conn in list(self._connections.values()):
                try:
                    conn.close()
                except Exception:
                    pass
            self._connections.clear()
            self.connection = None
            logging.info("Conexões com o banco de dados fechadas.")

    def _create_tables(self):
        cursor = self.connection.cursor()
        # Define all CREATE TABLE statements
        tables = {
            "UNIDADE": '''CREATE TABLE IF NOT EXISTS UNIDADE (
                            ID INTEGER PRIMARY KEY AUTOINCREMENT, NOME TEXT NOT NULL UNIQUE, SIGLA TEXT NOT NULL UNIQUE )''',
            "ITEM": '''CREATE TABLE IF NOT EXISTS ITEM (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT, CODIGO_INTERNO TEXT, DESCRICAO TEXT NOT NULL UNIQUE,
                        TIPO_ITEM TEXT NOT NULL CHECK(TIPO_ITEM IN ('Insumo', 'Produto', 'Ambos')), ID_UNIDADE INTEGER NOT NULL,
                        ID_FORNECEDOR_PADRAO INTEGER, SALDO_ESTOQUE REAL NOT NULL DEFAULT 0, CUSTO_MEDIO REAL NOT NULL DEFAULT 0,
                        NAO_ESTOCAVEL INTEGER NOT NULL DEFAULT 0,
                        FOREIGN KEY (ID_UNIDADE) REFERENCES UNIDADE (ID) ON DELETE RESTRICT,
                        FOREIGN KEY (ID_FORNECEDOR_PADRAO) REFERENCES FORNECEDOR (ID) ON DELETE RESTRICT )''',
            "FORNECEDOR": '''CREATE TABLE IF NOT EXISTS FORNECEDOR (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT, RAZAO_SOCIAL TEXT NOT NULL UNIQUE, NOME_FANTASIA TEXT,
                                CNPJ TEXT UNIQUE, STATUS TEXT NOT NULL DEFAULT 'Ativo', TELEFONE TEXT, EMAIL TEXT,
                                LOGRADOURO TEXT, NUMERO TEXT, COMPLEMENTO TEXT, BAIRRO TEXT, CIDADE TEXT, UF TEXT, CEP TEXT )''',
            "ENTRADANOTA": '''CREATE TABLE IF NOT EXISTS ENTRADANOTA (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT, DATA_ENTRADA TEXT NOT NULL, DATA_DIGITACAO TEXT,
                                NUMERO_NOTA TEXT, VALOR_TOTAL REAL, OBSERVACAO TEXT,
                                STATUS TEXT NOT NULL CHECK(STATUS IN ('Em Aberto', 'Finalizada')) )''',
            "COMPOSICAO": '''CREATE TABLE IF NOT EXISTS COMPOSICAO (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_PRODUTO INTEGER NOT NULL, ID_INSUMO INTEGER NOT NULL,
                                QUANTIDADE REAL NOT NULL, FOREIGN KEY (ID_PRODUTO) REFERENCES ITEM (ID) ON DELETE RESTRICT,
                                FOREIGN KEY (ID_INSUMO) REFERENCES ITEM (ID) ON DELETE RESTRICT, UNIQUE (ID_PRODUTO, ID_INSUMO) )''',
            "ORDEMPRODUCAO": '''CREATE TABLE IF NOT EXISTS ORDEMPRODUCAO (
                                    ID INTEGER PRIMARY KEY AUTOINCREMENT, NUMERO TEXT, DATA_CRIACAO TEXT NOT NULL,
                                    DATA_PREVISTA TEXT, STATUS TEXT NOT NULL CHECK(STATUS IN ('Em Andamento', 'Concluída', 'Cancelada')),
                                    QUANTIDADE_PRODUZIDA REAL, CUSTO_TOTAL REAL, ID_LINHA_PRODUCAO INTEGER,
                                    FOREIGN KEY (ID_LINHA_PRODUCAO) REFERENCES LINHAPRODUCAO(ID) ON DELETE SET NULL)''',
            "ORDEMPRODUCAO_ITENS": '''CREATE TABLE IF NOT EXISTS ORDEMPRODUCAO_ITENS (
                                        ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_ORDEM_PRODUCAO INTEGER NOT NULL,
                                        ID_PRODUTO INTEGER NOT NULL, QUANTIDADE_PRODUZIR REAL NOT NULL,
                                        FOREIGN KEY (ID_ORDEM_PRODUCAO) REFERENCES ORDEMPRODUCAO (ID) ON DELETE RESTRICT,
                                        FOREIGN KEY (ID_PRODUTO) REFERENCES ITEM (ID) ON DELETE RESTRICT,
                                        UNIQUE (ID_ORDEM_PRODUCAO, ID_PRODUTO) )''',
            "MOVIMENTO": '''CREATE TABLE IF NOT EXISTS MOVIMENTO (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_ITEM INTEGER NOT NULL, TIPO_MOVIMENTO TEXT NOT NULL,
                                QUANTIDADE REAL NOT NULL, VALOR_UNITARIO REAL, ID_ORDEM_PRODUCAO INTEGER, DATA_MOVIMENTO TEXT NOT NULL,
                                FOREIGN KEY (ID_ITEM) REFERENCES ITEM (ID) ON DELETE RESTRICT,
                                FOREIGN KEY (ID_ORDEM_PRODUCAO) REFERENCES ORDEMPRODUCAO (ID) ON DELETE RESTRICT )''',
            "ENTRADANOTA_ITENS": '''CREATE TABLE IF NOT EXISTS ENTRADANOTA_ITENS (
                                    ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_ENTRADA INTEGER NOT NULL, ID_INSUMO INTEGER NOT NULL,
                                    ID_FORNECEDOR INTEGER NOT NULL, QUANTIDADE REAL NOT NULL, VALOR_UNITARIO REAL NOT NULL,
                                    FOREIGN KEY (ID_ENTRADA) REFERENCES ENTRADANOTA (ID) ON DELETE RESTRICT,
                                    FOREIGN KEY (ID_INSUMO) REFERENCES ITEM (ID) ON DELETE RESTRICT,
                                    FOREIGN KEY (ID_FORNECEDOR) REFERENCES FORNECEDOR (ID) ON DELETE RESTRICT,
                                    UNIQUE (ID_ENTRADA, ID_INSUMO) )''',
            "SAIDA": '''CREATE TABLE IF NOT EXISTS SAIDA (
                            ID INTEGER PRIMARY KEY AUTOINCREMENT, DATA_SAIDA TEXT NOT NULL, VALOR_TOTAL REAL,
                            OBSERVACAO TEXT, STATUS TEXT NOT NULL CHECK(STATUS IN ('Em Aberto', 'Finalizada')) )''',
            "SAIDA_ITENS": '''CREATE TABLE IF NOT EXISTS SAIDA_ITENS (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_SAIDA INTEGER NOT NULL, ID_PRODUTO INTEGER NOT NULL,
                                QUANTIDADE REAL NOT NULL, VALOR_UNITARIO REAL NOT NULL,
                                FOREIGN KEY (ID_SAIDA) REFERENCES SAIDA (ID) ON DELETE RESTRICT,
                                FOREIGN KEY (ID_PRODUTO) REFERENCES ITEM (ID) ON DELETE RESTRICT,
                                UNIQUE (ID_SAIDA, ID_PRODUTO) )''',
            "LINHAPRODUCAO": '''CREATE TABLE IF NOT EXISTS LINHAPRODUCAO (
                                        ID INTEGER PRIMARY KEY AUTOINCREMENT, NOME TEXT NOT NULL UNIQUE,
                                        DESCRICAO TEXT, STATUS TEXT NOT NULL DEFAULT 'Ativa' CHECK(STATUS IN ('Ativa', 'Inativa')) )''',
            "LINHAPRODUCAO_ITEMS": '''CREATE TABLE IF NOT EXISTS LINHAPRODUCAO_ITEMS (
                                        ID INTEGER PRIMARY KEY AUTOINCREMENT, ID_LINHA_PRODUCAO INTEGER NOT NULL,
                                        ID_PRODUTO INTEGER NOT NULL, QUANTIDADE REAL NOT NULL,
                                        FOREIGN KEY (ID_LINHA_PRODUCAO) REFERENCES LINHAPRODUCAO (ID) ON DELETE CASCADE,
                                        FOREIGN KEY (ID_PRODUTO) REFERENCES ITEM (ID) ON DELETE RESTRICT,
                                        UNIQUE (ID_LINHA_PRODUCAO, ID_PRODUTO) )'''
        }
        for table_sql in tables.values():
            cursor.execute(table_sql)
        # Seed initial data (common units used in Brazil)
        unidades = [
            ('Grama', 'g'),
            ('Quilograma', 'kg'),
            ('Miligrama', 'mg'),
            ('Mililitro', 'ml'),
            ('Litro', 'L'),
            ('Metro', 'm'),
            ('Centímetro', 'cm'),
            ('Unidade', 'un'),
            ('Caixa', 'cx'),
            ('Pacote', 'pct'),
            ('Par', 'par')
        ]
        for nome, sigla in unidades:
            cursor.execute("SELECT ID FROM UNIDADE WHERE NOME = ?", (nome,))
            if cursor.fetchone() is None:
                # Ensure abbreviation is stored in uppercase
                cursor.execute("INSERT INTO UNIDADE (NOME, SIGLA) VALUES (?, ?)", (nome, sigla.upper() if isinstance(sigla, str) else sigla))

    def _run_migrations(self):
        cursor = self.connection.cursor()
        # Migration versioning
        cursor.execute("PRAGMA user_version")
        db_version = cursor.fetchone()[0]

        if db_version < 1:
            self._migrate_v1(cursor)
            cursor.execute("PRAGMA user_version = 1")
        
        if db_version < 2:
            self._migrate_v2(cursor)
            cursor.execute("PRAGMA user_version = 2")

        if db_version < 3:
            self._migrate_v3(cursor)
            cursor.execute("PRAGMA user_version = 3")

        if db_version < 4:
            self._migrate_v4(cursor)
            cursor.execute("PRAGMA user_version = 4")

        self.connection.commit()

    def _migrate_v1(self, cursor):
        """Migrations for version 1 of the database."""
        # Fix table renames from old schema
        table_rename_map = {
            "TUNIDADE": "UNIDADE", "TITEM": "ITEM", "TFORNECEDOR": "FORNECEDOR",
            "TENTRADANOTA": "ENTRADANOTA", "TCOMPOSICAO": "COMPOSICAO",
            "TORDEMPRODUCAO": "ORDEMPRODUCAO", "TORDEMPRODUCAO_ITENS": "ORDEMPRODUCAO_ITENS",
            "TMOVIMENTO": "MOVIMENTO", "TENTRADANOTA_ITENS": "ENTRADANOTA_ITENS"
        }
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        for old_name, new_name in table_rename_map.items():
            if old_name in tables and new_name not in tables:
                cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")

        # Fix supplier table columns
        cursor.execute("PRAGMA table_info(FORNECEDOR)")
        supplier_columns = {col[1] for col in cursor.fetchall()}
        if 'NOME' in supplier_columns and 'RAZAO_SOCIAL' not in supplier_columns:
            cursor.execute('ALTER TABLE FORNECEDOR RENAME COLUMN NOME TO RAZAO_SOCIAL')
        address_columns = ['LOGRADOURO', 'NUMERO', 'COMPLEMENTO', 'BAIRRO', 'CIDADE', 'UF', 'CEP']
        for col in address_columns:
            if col not in supplier_columns:
                cursor.execute(f'ALTER TABLE FORNECEDOR ADD COLUMN {col} TEXT')

        # Fix entry items table
        cursor.execute("PRAGMA table_info(ENTRADANOTA_ITENS)")
        entry_items_columns = {col[1] for col in cursor.fetchall()}
        if 'ID_FORNECEDOR' not in entry_items_columns:
            cursor.execute('ALTER TABLE ENTRADANOTA_ITENS ADD COLUMN ID_FORNECEDOR INTEGER REFERENCES FORNECEDOR(ID)')
            if self._column_exists(cursor, 'ENTRADANOTA', 'ID_FORNECEDOR'):
                cursor.execute("""
                    UPDATE ENTRADANOTA_ITENS SET ID_FORNECEDOR = (
                        SELECT ID_FORNECEDOR FROM ENTRADANota WHERE ENTRADANOTA.ID = ENTRADANOTA_ITENS.ID_ENTRADA)
                """)
        
        # Non-destructive migration for ENTRADANOTA
        self._migrate_entradanota_table(cursor)
        # Non-destructive migration for ITEM
        self._migrate_item_table(cursor)

    def _migrate_v2(self, cursor):
        """Migrations for version 2 of the database."""
        # Recriar a tabela ORDEMPRODUCAO para atualizar a restrição CHECK e adicionar colunas
        temp_table = "ORDEMPRODUCAO_temp_migration"
        cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")
        cursor.execute(f"ALTER TABLE ORDEMPRODUCAO RENAME TO {temp_table}")

        # Recriar a tabela com a nova estrutura
        self._create_tables()

        # Copiar os dados da tabela temporária para a nova tabela
        cursor.execute(f"""
            INSERT INTO ORDEMPRODUCAO (ID, NUMERO, DATA_CRIACAO, DATA_PREVISTA, STATUS)
            SELECT ID, NUMERO, DATA_CRIACAO, DATA_PREVISTA,
                   CASE
                       WHEN STATUS = 'Planejada' THEN 'Em Andamento'
                       WHEN STATUS = 'Concluída' THEN 'Concluída'
                       ELSE STATUS
                   END
            FROM {temp_table}
        """)
        cursor.execute(f"DROP TABLE {temp_table}")

    def _migrate_v3(self, cursor):
        """Migrations for version 3 of the database."""
        # Adicionar a coluna ID_LINHA_PRODUCAO na tabela ORDEMPRODUCAO
        if not self._column_exists(cursor, 'ORDEMPRODUCAO', 'ID_LINHA_PRODUCAO'):
            cursor.execute('''
                ALTER TABLE ORDEMPRODUCAO
                ADD COLUMN ID_LINHA_PRODUCAO INTEGER REFERENCES LINHAPRODUCAO(ID) ON DELETE SET NULL
            ''')

    def _migrate_v4(self, cursor):
        """Adicionar flag de controle para itens não estocáveis."""
        if not self._column_exists(cursor, 'ITEM', 'NAO_ESTOCAVEL'):
            cursor.execute('''
                ALTER TABLE ITEM
                ADD COLUMN NAO_ESTOCAVEL INTEGER NOT NULL DEFAULT 0
            ''')

    def _column_exists(self, cursor, table_name, column_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        return any(column[1] == column_name for column in cursor.fetchall())

    def _migrate_entradanota_table(self, cursor):
        if self._column_exists(cursor, 'ENTRADANOTA', 'ID_FORNECEDOR'):
            temp_table = "ENTRADANOTA_temp_migration"
            cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")
            cursor.execute(f"ALTER TABLE ENTRADANOTA RENAME TO {temp_table}")
            
            # Recreate with correct schema
            self._create_tables() 
            
            # Copy data
            cursor.execute(f"""
                INSERT INTO ENTRADANOTA (ID, DATA_ENTRADA, DATA_DIGITACAO, NUMERO_NOTA, VALOR_TOTAL, OBSERVACAO, STATUS)
                SELECT ID, DATA_ENTRADA, DATA_DIGITACAO, NUMERO_NOTA, VALOR_TOTAL, OBSERVACAO, STATUS FROM {temp_table}
            """)
            cursor.execute(f"DROP TABLE {temp_table}")

    def _migrate_item_table(self, cursor):
        # This migration is to remove the UNIQUE constraint from CODIGO_INTERNO.
        # It's complex to check for a constraint directly, so we rebuild the table.
        temp_table = "ITEM_temp_migration"
        cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")
        cursor.execute(f"ALTER TABLE ITEM RENAME TO {temp_table}")

        # Recreate with correct schema
        self._create_tables()

        # Copy data
        cursor.execute(f"""
            INSERT INTO ITEM (ID, CODIGO_INTERNO, DESCRICAO, TIPO_ITEM, ID_UNIDADE, ID_FORNECEDOR_PADRAO, SALDO_ESTOQUE, CUSTO_MEDIO)
            SELECT ID, CODIGO_INTERNO, DESCRICAO, TIPO_ITEM, ID_UNIDADE, ID_FORNECEDOR_PADRAO, SALDO_ESTOQUE, CUSTO_MEDIO FROM {temp_table}
        """)
        cursor.execute(f"DROP TABLE {temp_table}")

    def get_stock_entries(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                en.ID,
                en.NUMERO_NOTA as numero,
                f.RAZAO_SOCIAL as fornecedor,
                en.DATA_ENTRADA as data,
                en.VALOR_TOTAL as total
            FROM ENTRADANOTA en
            LEFT JOIN ENTRADANOTA_ITENS eni ON en.ID = eni.ID_ENTRADA
            LEFT JOIN FORNECEDOR f ON eni.ID_FORNECEDOR = f.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("numero_de"):
            where_clauses.append("en.NUMERO_NOTA >= ?")
            params.append(filters["numero_de"])
            
        if filters.get("numero_ate"):
            where_clauses.append("en.NUMERO_NOTA <= ?")
            params.append(filters["numero_ate"])
        
        if filters.get("fornecedor"):
            where_clauses.append("f.RAZAO_SOCIAL LIKE ?")
            params.append(f'%{filters["fornecedor"]}%')
            
        if filters.get("data_inicial"):
            where_clauses.append("en.DATA_ENTRADA >= ?")
            params.append(filters["data_inicial"])
            
        if filters.get("data_final"):
            where_clauses.append("en.DATA_ENTRADA <= ?")
            params.append(filters["data_final"])
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " GROUP BY en.ID"
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_product_cost_report(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                i.DESCRICAO as produto,
                i.CUSTO_MEDIO as custo_medio
            FROM ITEM i
            WHERE i.TIPO_ITEM = 'Produto' OR i.TIPO_ITEM = 'Ambos'
        """
        
        where_clauses = []
        params = []
        
        if filters.get("produto_de"):
            where_clauses.append("i.DESCRICAO >= ?")
            params.append(filters["produto_de"])
            
        if filters.get("produto_ate"):
            where_clauses.append("i.DESCRICAO <= ?")
            params.append(filters["produto_ate"])

        if where_clauses:
            query += " AND " + " AND ".join(where_clauses)
            
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_entry_items_report(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                eni.ID_ENTRADA as nota,
                i.DESCRICAO as insumo,
                eni.QUANTIDADE as quantidade,
                eni.VALOR_UNITARIO as valor_unitario,
                (eni.QUANTIDADE * eni.VALOR_UNITARIO) as valor_total
            FROM ENTRADANOTA_ITENS eni
            JOIN ITEM i ON eni.ID_INSUMO = i.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("nota_de"):
            where_clauses.append("eni.ID_ENTRADA >= ?")
            params.append(filters["nota_de"])

        if filters.get("nota_ate"):
            where_clauses.append("eni.ID_ENTRADA <= ?")
            params.append(filters["nota_ate"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_stock_movements(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                i.DESCRICAO as item,
                m.TIPO_MOVIMENTO as tipo_movimento,
                m.QUANTIDADE as quantidade,
                m.VALOR_UNITARIO as valor_unitario,
                m.DATA_MOVIMENTO as data_movimento
            FROM MOVIMENTO m
            LEFT JOIN ITEM i ON m.ID_ITEM = i.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("item_de"):
            where_clauses.append("i.DESCRICAO >= ?")
            params.append(filters["item_de"])
            
        if filters.get("item_ate"):
            where_clauses.append("i.DESCRICAO <= ?")
            params.append(filters["item_ate"])
            
        if filters.get("periodo_de"):
            where_clauses.append("m.DATA_MOVIMENTO >= ?")
            params.append(filters["periodo_de"])
            
        if filters.get("periodo_ate"):
            where_clauses.append("m.DATA_MOVIMENTO <= ?")
            params.append(filters["periodo_ate"])
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_current_stock(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT DESCRICAO, SALDO_ESTOQUE, CUSTO_MEDIO FROM ITEM"
        
        cursor.execute(query)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_production_orders(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                op.ID as id,
                i.DESCRICAO as produto,
                op.STATUS as status,
                op.DATA_CRIACAO as data_criacao,
                opi.QUANTIDADE_PRODUZIR as quantidade
            FROM ORDEMPRODUCAO op
            LEFT JOIN ORDEMPRODUCAO_ITENS opi ON op.ID = opi.ID_ORDEM_PRODUCAO
            LEFT JOIN ITEM i ON opi.ID_PRODUTO = i.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("id_de"):
            where_clauses.append("op.ID >= ?")
            params.append(filters["id_de"])
            
        if filters.get("id_ate"):
            where_clauses.append("op.ID <= ?")
            params.append(filters["id_ate"])
        
        if filters.get("produto_de"):
            where_clauses.append("i.DESCRICAO >= ?")
            params.append(filters["produto_de"])
            
        if filters.get("produto_ate"):
            where_clauses.append("i.DESCRICAO <= ?")
            params.append(filters["produto_ate"])
            
        if filters.get("status"):
            where_clauses.append("op.STATUS LIKE ?")
            params.append(f'%{filters["status"]}%')
            
        if filters.get("periodo_de"):
            where_clauses.append("op.DATA_CRIACAO >= ?")
            params.append(filters["periodo_de"])

        if filters.get("periodo_ate"):
            where_clauses.append("op.DATA_CRIACAO <= ?")
            params.append(filters["periodo_ate"])
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_production_by_period(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                i.DESCRICAO as produto,
                SUM(opi.QUANTIDADE_PRODUZIR) as quantidade_produzida,
                op.DATA_CRIACAO as data_producao
            FROM ORDEMPRODUCAO op
            JOIN ORDEMPRODUCAO_ITENS opi ON op.ID = opi.ID_ORDEM_PRODUCAO
            JOIN ITEM i ON opi.ID_PRODUTO = i.ID
        """
        
        where_clauses = []
        params = []
        if filters.get("periodo_de"):
            where_clauses.append("op.DATA_CRIACAO >= ?")
            params.append(filters["periodo_de"])
            
        if filters.get("periodo_ate"):
            where_clauses.append("op.DATA_CRIACAO <= ?")
            params.append(filters["periodo_ate"])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " GROUP BY i.ID"
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_production_by_line(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                lpm.NOME as linha,
                i.DESCRICAO as produto,
                SUM(opi.QUANTIDADE_PRODUZIR) as quantidade
            FROM ORDEMPRODUCAO op
            LEFT JOIN ORDEMPRODUCAO_ITENS opi ON op.ID = opi.ID_ORDEM_PRODUCAO
            LEFT JOIN ITEM i ON opi.ID_PRODUTO = i.ID
            LEFT JOIN LINHAPRODUCAO lpm ON op.ID_LINHA_PRODUCAO = lpm.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("linha_de"):
            where_clauses.append("lpm.NOME >= ?")
            params.append(filters["linha_de"])
            
        if filters.get("linha_ate"):
            where_clauses.append("lpm.NOME <= ?")
            params.append(filters["linha_ate"])
            
        if filters.get("periodo_de"):
            where_clauses.append("op.DATA_CRIACAO >= ?")
            params.append(filters["periodo_de"])
            
        if filters.get("periodo_ate"):
            where_clauses.append("op.DATA_CRIACAO <= ?")
            params.append(filters["periodo_ate"])
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " GROUP BY lpm.ID, i.ID"
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_product_composition(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                i_produto.DESCRICAO as produto,
                i_insumo.DESCRICAO as insumo,
                c.QUANTIDADE as quantidade,
                u.SIGLA as unidade
            FROM COMPOSICAO c
            LEFT JOIN ITEM i_produto ON c.ID_PRODUTO = i_produto.ID
            LEFT JOIN ITEM i_insumo ON c.ID_INSUMO = i_insumo.ID
            LEFT JOIN UNIDADE u ON i_insumo.ID_UNIDADE = u.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("produto_de"):
            where_clauses.append("i_produto.DESCRICAO >= ?")
            params.append(filters["produto_de"])
            
        if filters.get("produto_ate"):
            where_clauses.append("i_produto.DESCRICAO <= ?")
            params.append(filters["produto_ate"])
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_suppliers_report(self, filters=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT ID, RAZAO_SOCIAL, NOME_FANTASIA, CNPJ, STATUS FROM FORNECEDOR"
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_items_report(self, filters=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT i.ID, i.CODIGO_INTERNO, i.DESCRICAO, i.TIPO_ITEM, u.SIGLA as unidade, i.SALDO_ESTOQUE, i.CUSTO_MEDIO FROM ITEM i JOIN UNIDADE u ON i.ID_UNIDADE = u.ID"
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_low_stock_report(self, threshold=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT DESCRICAO, SALDO_ESTOQUE, CUSTO_MEDIO FROM ITEM WHERE SALDO_ESTOQUE < ?"
        cursor.execute(query, (threshold,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_yield_report(self, filters=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                op.ID, 
                op.NUMERO, 
                op.DATA_CRIACAO, 
                SUM(opi.QUANTIDADE_PRODUZIR) as qtd_planejada, 
                op.QUANTIDADE_PRODUZIDA as qtd_produzida,
                CASE WHEN SUM(opi.QUANTIDADE_PRODUZIR) > 0 
                     THEN (op.QUANTIDADE_PRODUZIDA / SUM(opi.QUANTIDADE_PRODUZIR)) * 100 
                     ELSE 0 END as rendimento
            FROM ORDEMPRODUCAO op
            JOIN ORDEMPRODUCAO_ITENS opi ON op.ID = opi.ID_ORDEM_PRODUCAO
            WHERE op.STATUS = 'Concluída'
            GROUP BY op.ID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_material_requirements_report(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                i_insumo.DESCRICAO as insumo,
                u.SIGLA as unidade,
                SUM(opi.QUANTIDADE_PRODUZIR * c.QUANTIDADE) as qtd_necessaria,
                i_insumo.SALDO_ESTOQUE as qtd_estoque,
                CASE WHEN SUM(opi.QUANTIDADE_PRODUZIR * c.QUANTIDADE) > i_insumo.SALDO_ESTOQUE 
                     THEN SUM(opi.QUANTIDADE_PRODUZIR * c.QUANTIDADE) - i_insumo.SALDO_ESTOQUE 
                     ELSE 0 END as falta
            FROM ORDEMPRODUCAO op
            JOIN ORDEMPRODUCAO_ITENS opi ON op.ID = opi.ID_ORDEM_PRODUCAO
            JOIN COMPOSICAO c ON opi.ID_PRODUTO = c.ID_PRODUTO
            JOIN ITEM i_insumo ON c.ID_INSUMO = i_insumo.ID
            JOIN UNIDADE u ON i_insumo.ID_UNIDADE = u.ID
            WHERE op.STATUS = 'Em Andamento'
            GROUP BY i_insumo.ID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_abc_curve_report(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                DESCRICAO,
                SALDO_ESTOQUE,
                CUSTO_MEDIO,
                (SALDO_ESTOQUE * CUSTO_MEDIO) as valor_total
            FROM ITEM
            ORDER BY valor_total DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_inactive_items_report(self, days=30):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                i.DESCRICAO,
                i.SALDO_ESTOQUE,
                MAX(m.DATA_MOVIMENTO) as ultima_movimentacao
            FROM ITEM i
            LEFT JOIN MOVIMENTO m ON i.ID = m.ID_ITEM
            GROUP BY i.ID
            HAVING ultima_movimentacao < date('now', '-' || ? || ' days') OR ultima_movimentacao IS NULL
        """
        cursor.execute(query, (days,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_profit_by_product(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                i.DESCRICAO as produto,
                i.CUSTO_MEDIO as custo_unitario,
                si.VALOR_UNITARIO as preco_venda,
                SUM(si.QUANTIDADE) as quantidade_vendida,
                (si.VALOR_UNITARIO - i.CUSTO_MEDIO) as lucro_unitario,
                SUM(si.QUANTIDADE) * (si.VALOR_UNITARIO - i.CUSTO_MEDIO) as lucro_total
            FROM SAIDA_ITENS si
            LEFT JOIN ITEM i ON si.ID_PRODUTO = i.ID
            LEFT JOIN SAIDA s ON si.ID_SAIDA = s.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("produto_de"):
            where_clauses.append("i.DESCRICAO >= ?")
            params.append(filters["produto_de"])
            
        if filters.get("produto_ate"):
            where_clauses.append("i.DESCRICAO <= ?")
            params.append(filters["produto_ate"])
            
        if filters.get("periodo_de"):
            where_clauses.append("s.DATA_SAIDA >= ?")
            params.append(filters["periodo_de"])
            
        if filters.get("periodo_ate"):
            where_clauses.append("s.DATA_SAIDA <= ?")
            params.append(filters["periodo_ate"])
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " GROUP BY i.ID"
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_profit_by_period(self, filters):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                SUM(s.VALOR_TOTAL) as total_vendas,
                SUM(i.CUSTO_MEDIO * si.QUANTIDADE) as custo_total,
                (SUM(s.VALOR_TOTAL) - SUM(i.CUSTO_MEDIO * si.QUANTIDADE)) as lucro_final
            FROM SAIDA s
            LEFT JOIN SAIDA_ITENS si ON s.ID = si.ID_SAIDA
            LEFT JOIN ITEM i ON si.ID_PRODUTO = i.ID
        """
        
        where_clauses = []
        params = []
        
        if filters.get("data_inicial"):
            where_clauses.append("s.DATA_SAIDA >= ?")
            params.append(filters["data_inicial"])
            
        if filters.get("data_final"):
            where_clauses.append("s.DATA_SAIDA <= ?")
            params.append(filters["data_final"])
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        cursor.execute(query, params)
        
        row = cursor.fetchone()
        if row:
            column_names = [description[0] for description in cursor.description]
            return dict(zip(column_names, row))
        return {"total_vendas": 0, "custo_total": 0, "lucro_final": 0}

def get_db_manager(db_path=None, reset=False):
    # When tests request a reset without a custom path, use an in-memory DB
    # to ensure isolation and avoid polluting the on-disk database.
    if reset or db_path:
        DatabaseManager.reset_instance()
    if reset and not db_path:
        return DatabaseManager(db_path=':memory:')
    return DatabaseManager(db_path=db_path) if db_path else DatabaseManager()

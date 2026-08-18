import sqlite3
# app/item/item_repository.py
from app.database.db import get_db_manager

class ItemRepository:
    def __init__(self):
        self.db_manager = get_db_manager()
        self.connection = self.db_manager.get_connection()

    def add(self, codigo_interno, description, item_type, unit_id, id_fornecedor_padrao, nao_estocavel=False):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO ITEM (CODIGO_INTERNO, DESCRICAO, TIPO_ITEM, ID_UNIDADE, ID_FORNECEDOR_PADRAO, NAO_ESTOCAVEL) VALUES (?, ?, ?, ?, ?, ?)",
                (codigo_interno, description, item_type, unit_id, id_fornecedor_padrao, 1 if nao_estocavel else 0)
            )
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            self.connection.rollback()
            return None

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT i.ID, i.CODIGO_INTERNO, i.DESCRICAO, i.TIPO_ITEM, u.SIGLA, i.SALDO_ESTOQUE, i.CUSTO_MEDIO, i.ID_FORNECEDOR_PADRAO, i.NAO_ESTOCAVEL
            FROM ITEM i
            JOIN UNIDADE u ON i.ID_UNIDADE = u.ID
            ORDER BY i.DESCRICAO
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ITEM WHERE ID = ?", (item_id,))
        item = cursor.fetchone()
        return dict(item) if item is not None else None

    def update(self, item_id, codigo_interno, description, item_type, unit_id, id_fornecedor_padrao, nao_estocavel=False):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE ITEM SET CODIGO_INTERNO = ?, DESCRICAO = ?, TIPO_ITEM = ?, ID_UNIDADE = ?, ID_FORNECEDOR_PADRAO = ?, NAO_ESTOCAVEL = ? WHERE ID = ?",
                (codigo_interno, description, item_type, unit_id, id_fornecedor_padrao, 1 if nao_estocavel else 0, item_id)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            self.connection.rollback()
            return False

    def delete(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM ITEM WHERE ID = ?", (item_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def is_item_in_composition(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM COMPOSICAO WHERE ID_INSUMO = ?", (item_id,))
        return cursor.fetchone() is not None

    def is_item_in_production_order(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM ORDEMPRODUCAO_ITENS WHERE ID_PRODUTO = ?", (item_id,))
        return cursor.fetchone() is not None

    def has_stock_movement(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM MOVIMENTO WHERE ID_ITEM = ?", (item_id,))
        return cursor.fetchone() is not None

    def has_composition(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM COMPOSICAO WHERE ID_PRODUTO = ?", (item_id,))
        return cursor.fetchone() is not None

    def search(self, search_type, search_text):
        cursor = self.connection.cursor()
        query = "SELECT i.ID, i.CODIGO_INTERNO, i.DESCRICAO, i.TIPO_ITEM, u.SIGLA, i.SALDO_ESTOQUE, i.CUSTO_MEDIO, i.ID_FORNECEDOR_PADRAO, i.NAO_ESTOCAVEL FROM ITEM i JOIN UNIDADE u ON i.ID_UNIDADE = u.ID"
        
        allowed_types = {
            "ID": "i.ID",
            "CODIGO_INTERNO": "i.CODIGO_INTERNO",
            "DESCRICAO": "i.DESCRICAO"
        }
        
        column = allowed_types.get(search_type)
        if not column:
            return [] # Ou raise ValueError

        if search_type == "ID":
            query += f" WHERE {column} = ?"
            params = (search_text,)
        else:
            query += f" WHERE {column} LIKE ?"
            params = (f"%{search_text}%",)
            
        query += " ORDER BY i.DESCRICAO"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def update_stock_and_cost(self, item_id, new_balance, new_average_cost):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE ITEM SET SALDO_ESTOQUE = ?, CUSTO_MEDIO = ? WHERE ID = ?", (new_balance, new_average_cost, item_id))
        self.connection.commit()

    def add_stock_movement(self, item_id, movement_type, quantity, unit_value):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO MOVIMENTO (ID_ITEM, TIPO_MOVIMENTO, QUANTIDADE, VALOR_UNITARIO, DATA_MOVIMENTO) VALUES (?, ?, ?, ?, date('now'))", (item_id, movement_type, quantity, unit_value))
        self.connection.commit()

    def get_movements(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT QUANTIDADE, VALOR_UNITARIO FROM MOVIMENTO WHERE ID_ITEM = ? ORDER BY DATA_MOVIMENTO", (item_id,))
        return [dict(row) for row in cursor.fetchall()]

    def compute_average_from_movements(self, item_id):
        """
        Recalculates the weighted average unit cost of an item based SOLELY on entry movements (TIPO_MOVIMENTO = 'entrada').
        """
        item = self.get_by_id(item_id)
        if not item:
            return 0.0, 0.0
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT SUM(QUANTIDADE * VALOR_UNITARIO) / SUM(QUANTIDADE)
            FROM MOVIMENTO
            WHERE ID_ITEM = ?
              AND TIPO_MOVIMENTO = 'entrada'
        """, (item_id,))
        
        result = cursor.fetchone()
        if result and result[0] is not None:
            return result[0], item.get('SALDO_ESTOQUE', 0) or 0.0
        
        return 0.0, item.get('SALDO_ESTOQUE', 0) or 0.0

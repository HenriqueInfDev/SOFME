from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QHBoxLayout, QFrame, QApplication,
    QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QCheckBox, QFileDialog, QDialog, QDialogButtonBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread, Signal
from app.auth.service import AuthService
from app.utils.ui_utils import LoadingOverlay, show_warning_message, show_success_message, show_error_message
from app.utils.local_settings import load_local_params, save_local_params
from app.styles.windows_style import window_style, LIGHT
from app.styles.input_styles import input_style, DEFAULTINPUT
from app.styles.buttons_styles import button_style, BLUE, GREEN, RED
from app.database.config import (
    load_database_configs,
    get_selected_database_config,
    add_database_config,
    set_selected_database,
    remove_database_config,
)
import os


class LoginWindow(QWidget):
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success
        self.auth_service = None
        self.database_settings_file = 'database_params.txt'
        self.selected_database = None
        self.setWindowTitle('Login - SOFME')
        self.setGeometry(300, 200, 540, 420)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setObjectName('loginWindowRoot')
        self.setStyleSheet(window_style(LIGHT) + " #loginWindowRoot { background-color: #d1d5db; }")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setObjectName('loginTabBar')
        self.tab_widget.tabBar().setExpanding(True)
        self.tab_widget.tabBar().setDrawBase(False)
        self.tab_widget.setStyleSheet('''
            QTabBar#loginTabBar::tab {
                background: #f8fafc;
                border: 1px solid #d1d9e6;
                border-bottom: none;
                border-radius: 0px;
                padding: 12px 24px;
                margin: 0;
            }
            QTabBar#loginTabBar::tab:selected {
                background: #ffffff;
                color: #0f172a;
                font-weight: 700;
                border-bottom: 2px solid #2563eb;
            }
            QTabBar#loginTabBar::tab:!selected {
                color: #475569;
            }
            QTabBar#loginTabBar::tab:hover {
                background: #eff4ff;
            }
            QTabWidget::pane {
                margin: 0;
                padding: 0;
            }
        ''')
        self.tab_widget.addTab(self.create_login_tab(), 'Login')
        self.tab_widget.addTab(self.create_database_tab(), 'Banco de Dados')

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        self.refresh_database_list()

    def create_login_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        panel = QFrame()
        panel.setObjectName('loginPanel')
        panel.setStyleSheet('#loginPanel { background: white; border-radius: 8px; padding: 18px; }')
        panel.setFixedWidth(420)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(12)

        title = QLabel('Acesso ao sistema')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 22px; font-weight: 700; color: #0F172A;')
        panel_layout.addWidget(title)

        self.current_db_label = QLabel('Banco de dados selecionado: ---')
        self.current_db_label.setStyleSheet('font-size: 13px; color: #475569;')
        self.current_db_label.setWordWrap(True)
        panel_layout.addWidget(self.current_db_label)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setHorizontalSpacing(12)

        self.login_input = QLineEdit()
        self.login_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.login_input.setPlaceholderText('Digite o login')
        self.login_input.setFixedHeight(36)

        try:
            params = load_local_params()
            last_login = params.get('auth.last_login')
            if last_login:
                self.login_input.setText(last_login)
        except Exception:
            pass

        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.password_input.setPlaceholderText('Digite a senha')
        self.password_input.setFixedHeight(36)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)

        login_label = QLabel('Login')
        login_label.setStyleSheet('font-weight: 700; color: #0F172A; font-size: 15px;')
        login_label.setFixedHeight(36)
        login_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        senha_label = QLabel('Senha')
        senha_label.setStyleSheet('font-weight: 700; color: #0F172A; font-size: 15px;')
        senha_label.setFixedHeight(36)
        senha_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        form.setVerticalSpacing(16)
        form.addRow(login_label, self.login_input)
        form.addRow(senha_label, self.password_input)
        panel_layout.addLayout(form)

        self.login_button = QPushButton('Entrar')
        self.login_button.setStyleSheet(button_style(BLUE))
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setFixedHeight(40)
        self.login_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        panel_layout.addWidget(self.login_button)

        layout.addStretch(1)
        wrapper = QHBoxLayout()
        wrapper.addStretch(1)
        wrapper.addWidget(panel)
        wrapper.addStretch(1)
        layout.addLayout(wrapper)
        layout.addStretch(1)

        return tab

    def create_database_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(14, 14, 14, 0)

        title = QLabel('Selecionar Base de Dados')
        title.setStyleSheet('font-size: 16px; font-weight: 700; color: #0F172A;')
        layout.addWidget(title)

        self.db_table = QTableWidget(0, 3)
        self.db_table.setHorizontalHeaderLabels(['Descrição', 'Pasta', 'Caminho da Base'])
        self.db_table.verticalHeader().setVisible(False)
        self.db_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.db_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.db_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.db_table.setFocusPolicy(Qt.NoFocus)
        self.db_table.setAlternatingRowColors(True)
        self.db_table.setShowGrid(True)
        self.db_table.setStyleSheet(
            'QTableWidget { background: #ffffff; border: 1px solid #d1d9e6; font-size: 13px; }'
            'QTableWidget::item:selected { background: #e2e8f0; color: #0f172a; }'
            'QHeaderView::section { background: #eef2ff; border: 1px solid #d1d9e6; padding: 10px; font-weight: 700; }'
            'QTableCornerButton::section { background: #eef2ff; border: 1px solid #d1d9e6; }'
        )
        self.db_table.horizontalHeader().setStretchLastSection(True)
        self.db_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.db_table.horizontalHeader().setStyleSheet(
            'QHeaderView::section { background: #eef2ff; border: 1px solid #d1d9e6; padding: 10px; font-weight: 700; }'
        )
        self.db_table.setMinimumHeight(260)
        self.db_table.itemSelectionChanged.connect(self.update_database_details)

        action_layout = QVBoxLayout()
        action_layout.setSpacing(10)
        action_layout.setContentsMargins(0, 0, 0, 0)

        self.select_button = QPushButton('Selecionar')
        self.select_button.setStyleSheet(button_style(BLUE))
        self.select_button.clicked.connect(self.handle_select_database)
        self.select_button.setEnabled(False)
        self.select_button.setFixedHeight(38)
        self.select_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.new_button = QPushButton('Novo')
        self.new_button.setStyleSheet(button_style(GREEN))
        self.new_button.clicked.connect(self.handle_new_database)
        self.new_button.setFixedHeight(38)
        self.new_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.delete_button = QPushButton('Excluir')
        self.delete_button.setStyleSheet(button_style(RED))
        self.delete_button.clicked.connect(self.handle_remove_database)
        self.delete_button.setEnabled(False)
        self.delete_button.setFixedHeight(38)
        self.delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        action_layout.addWidget(self.select_button)
        action_layout.addWidget(self.new_button)
        action_layout.addWidget(self.delete_button)
        action_layout.addStretch(1)

        right_panel = QFrame()
        right_panel.setObjectName('buttonPanel')
        right_panel.setLayout(action_layout)
        right_panel.setFixedWidth(150)
        right_panel.setStyleSheet('QFrame#buttonPanel { background: #ffffff; border: 1px solid #d1d9e6; border-radius: 8px; }')

        content_frame = QFrame()
        content_frame.setObjectName('databasePanel')
        content_frame.setStyleSheet('QFrame#databasePanel { background: #f8fafc; border: 1px solid #d1d9e6; border-radius: 10px; }')
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(14, 14, 14, 14)
        content_layout.setSpacing(12)
        content_layout.addWidget(self.db_table)
        content_layout.addWidget(right_panel)

        detail_frame = QFrame()
        detail_frame.setStyleSheet('QFrame { background: #ffffff; border: 1px solid #d1d9e6; border-radius: 8px; }')
        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(8)

        self.db_name_label = QLabel('Nome: ---')
        self.db_directory_label = QLabel('Pasta: ---')
        self.db_filename_label = QLabel('Arquivo: ---')
        self.db_path_label = QLabel('Caminho completo: ---')
        for label in [self.db_name_label, self.db_directory_label, self.db_filename_label, self.db_path_label]:
            label.setWordWrap(True)
            label.setStyleSheet('color: #0F172A; font-size: 13px;')
            detail_layout.addWidget(label)

        layout.addWidget(content_frame)
        layout.addWidget(detail_frame)

        self.auto_select_checkbox = QCheckBox('Selecionar base ao iniciar o sistema ?')
        self.auto_select_checkbox.setStyleSheet(
            'QCheckBox { font-size: 13px; color: #0F172A; padding: 10px 0 10px 4px; background: transparent; }'
            'QCheckBox::indicator { width: 18px; height: 18px; margin-right: 10px; border: 1px solid #000000; border-radius: 4px; background: #ffffff; }'
            'QCheckBox::indicator:checked { background: #000000; }'
        )
        footer = QFrame()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addWidget(self.auto_select_checkbox)
        footer_layout.addStretch(1)
        layout.addWidget(footer)

        return tab

    def refresh_database_list(self):
        self.db_table.clearContents()
        self.db_table.setRowCount(0)
        self.databases = load_database_configs(self.database_settings_file)
        self.selected_database = get_selected_database_config(self.database_settings_file)

        for row, database in enumerate(self.databases):
            self.db_table.insertRow(row)
            description_item = QTableWidgetItem(database.name)
            description_item.setData(Qt.UserRole, database)
            description_item.setFlags(description_item.flags() & ~Qt.ItemIsEditable)
            directory_item = QTableWidgetItem(database.directory)
            directory_item.setFlags(directory_item.flags() & ~Qt.ItemIsEditable)
            path_item = QTableWidgetItem(database.full_path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)

            self.db_table.setItem(row, 0, description_item)
            self.db_table.setItem(row, 1, directory_item)
            self.db_table.setItem(row, 2, path_item)

            if self.selected_database and database.key == self.selected_database.key:
                self.db_table.selectRow(row)

        if self.selected_database is None and self.db_table.rowCount() > 0:
            self.db_table.selectRow(0)

        self.update_database_details()
        self.update_current_db_label()

    def update_current_db_label(self):
        if self.selected_database:
            self.current_db_label.setText(
                f'Banco de dados selecionado: {self.selected_database.name} ({self.selected_database.full_path})'
            )
        else:
            self.current_db_label.setText('Banco de dados selecionado: ---')

    def update_database_details(self):
        current_row = self.db_table.currentRow()
        if current_row >= 0:
            item = self.db_table.item(current_row, 0)
            database = item.data(Qt.UserRole)
            self.db_name_label.setText(f'Nome: {database.name}')
            self.db_directory_label.setText(f'Pasta: {database.directory}')
            self.db_filename_label.setText(f'Arquivo: {database.filename}')
            self.db_path_label.setText(f'Caminho completo: {database.full_path}')
            self.select_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.db_name_label.setText('Nome: ---')
            self.db_directory_label.setText('Pasta: ---')
            self.db_filename_label.setText('Arquivo: ---')
            self.db_path_label.setText('Caminho completo: ---')
            self.select_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def handle_select_database(self):
        current_row = self.db_table.currentRow()
        if current_row < 0:
            show_warning_message(self, 'Seleção de banco', 'Selecione um banco de dados primeiro.')
            return
        item = self.db_table.item(current_row, 0)
        database = item.data(Qt.UserRole)
        set_selected_database(database.key, self.database_settings_file)
        os.environ['SOFME_DATA_DIR'] = database.full_path
        self.selected_database = database
        self.update_current_db_label()
        show_success_message(self, 'Selecionado', f'O banco de dados "{database.name}" foi selecionado.')

    def handle_new_database(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Novo banco de dados')
        dialog.setModal(True)

        form_layout = QFormLayout(dialog)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setHorizontalSpacing(12)

        name_input = QLineEdit()
        directory_input = QLineEdit()
        filename_input = QLineEdit()
        filename_input.setPlaceholderText('Ex: DADOS.DB')

        browse_button = QPushButton('...')
        browse_button.setFixedWidth(32)
        browse_button.clicked.connect(lambda: self.on_browse_database_directory(directory_input))

        directory_container = QFrame()
        directory_container.setLayout(QHBoxLayout())
        directory_container.layout().setContentsMargins(0, 0, 0, 0)
        directory_container.layout().addWidget(directory_input)
        directory_container.layout().addWidget(browse_button)

        form_layout.addRow('Nome', name_input)
        form_layout.addRow('Pasta', directory_container)
        form_layout.addRow('Arquivo', filename_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form_layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        name = name_input.text().strip()
        directory = directory_input.text().strip()
        filename = filename_input.text().strip()

        if not name or not directory or not filename:
            show_warning_message(self, 'Dados incompletos', 'Preencha nome, pasta e arquivo do banco de dados.')
            return

        try:
            config = add_database_config(name, directory, filename, self.database_settings_file)
            set_selected_database(config.key, self.database_settings_file)
            os.environ['SOFME_DATA_DIR'] = config.full_path
            self.refresh_database_list()
            show_success_message(self, 'Banco criado', f'Banco de dados "{config.name}" criado e selecionado.')
        except Exception as exc:
            show_error_message(self, 'Falha ao criar', str(exc))

    def on_browse_database_directory(self, directory_input):
        directory = QFileDialog.getExistingDirectory(self, 'Selecionar pasta de banco de dados')
        if directory:
            directory_input.setText(directory)

    def handle_remove_database(self):
        current_row = self.db_table.currentRow()
        if current_row < 0:
            show_warning_message(self, 'Excluir banco', 'Selecione um banco de dados para excluir.')
            return
        item = self.db_table.item(current_row, 0)
        database = item.data(Qt.UserRole)
        answer = QMessageBox.question(
            self,
            'Excluir banco de dados',
            f'Tem certeza que deseja remover a configuração "{database.name}"? O arquivo não será excluído.',
            QMessageBox.Yes | QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        remove_database_config(database.key, self.database_settings_file)
        self.refresh_database_list()
        show_success_message(self, 'Removido', f'A configuração "{database.name}" foi removida.')

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not hasattr(self, 'loading_overlay'):
            self.loading_overlay = LoadingOverlay(self, message='Autenticando...')
        self.loading_overlay.setMessage('Autenticando...')
        self.loading_overlay.show()
        self.loading_overlay.raise_()
        QApplication.processEvents()

        class AuthThread(QThread):
            finished_signal = Signal(dict)
            def __init__(self, login, password):
                super().__init__()
                self.login = login
                self.password = password
            def run(self):
                try:
                    service = AuthService()
                    res = service.authenticate_user(self.login, self.password)
                except Exception as e:
                    res = {'success': False, 'message': str(e)}
                self.finished_signal.emit(res)

        self.auth_thread = AuthThread(login, password)

        def on_auth_finished(result):
            self.loading_overlay.hide()
            if result.get('success'):
                try:
                    params = load_local_params()
                    params['auth.last_login'] = login
                    save_local_params(params)
                except Exception:
                    pass
                if self.on_success:
                    self.on_success(result['data'])
                self.close()
            else:
                QMessageBox.critical(self, 'Erro de login', result.get('message', 'Erro'))

        self.auth_thread.finished_signal.connect(on_auth_finished)
        self.auth_thread.finished_signal.connect(lambda _: self.auth_thread.deleteLater())
        self.auth_thread.start()

    def open_register_window(self):
        pass


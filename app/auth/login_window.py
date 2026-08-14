from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QHBoxLayout, QFrame, QApplication,
    QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QCheckBox, QFileDialog, QDialog, QDialogButtonBox, QSizePolicy
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from PySide6.QtCore import QThread, Signal
from app.auth.service import AuthService
from app.utils.ui_utils import LoadingOverlay, show_warning_message, show_success_message, show_error_message
from app.utils.local_settings import load_local_params, save_local_params
from app.styles.login_styles import (
    login_window_style,
    login_panel_style,
    login_title_style,
    login_subtitle_style,
    login_field_label_style,
    login_input_style,
    login_button_style,
)
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
        self.password_visible = False
        self.setWindowTitle('Login - SOFME')
        self.setGeometry(100, 100, 1200, 820)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setObjectName('loginWindowRoot')
        self.setStyleSheet(login_window_style())
        self.setup_ui()

    def _icon_path(self, relative_name):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'images', 'icons', relative_name)

    def _set_icon_for_label(self, label, icon_path, size=22):
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled = pixmap.scaled(QSize(size, size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('background: transparent;')
        else:
            label.setText('')

    def _toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        self.password_input.setEchoMode(QLineEdit.Normal if self.password_visible else QLineEdit.Password)
        self.password_toggle_button.setIcon(QIcon(self._icon_path('visible_password_on.ico' if self.password_visible else 'visible_password_off.ico')))
        self.password_toggle_button.setToolTip('Mostrar senha' if not self.password_visible else 'Ocultar senha')

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignCenter)

        # Gray background container
        gray_container = QFrame()
        gray_container.setObjectName('grayContainer')
        gray_container.setStyleSheet('QFrame#grayContainer { background: #dfe5eb; }')
        gray_layout = QVBoxLayout(gray_container)
        gray_layout.setContentsMargins(0, 0, 0, 0)
        gray_layout.setSpacing(0)
        gray_layout.setAlignment(Qt.AlignCenter)

        # Main panel (white card)
        main_panel = QFrame()
        main_panel.setObjectName('mainPanel')
        main_panel.setFixedWidth(440)
        main_panel.setStyleSheet('''
            QFrame#mainPanel {
                background: #f7f7f7;
                border: 1px solid #ebeff5;
                border-radius: 12px;
            }
        ''')
        panel_layout = QVBoxLayout(main_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        # Tab bar inside the panel
        tab_bar_widget = QFrame()
        tab_bar_widget.setObjectName('tabBarWidget')
        tab_bar_widget.setStyleSheet('''
            QFrame#tabBarWidget {
                background: #f7f7f7;
                border-bottom: 1px solid #ebeff5;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        ''')
        tab_bar_widget.setFixedHeight(48)
        tab_bar_layout = QHBoxLayout(tab_bar_widget)
        tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        tab_bar_layout.setSpacing(0)

        self.login_tab_button = QPushButton('Login')
        self.login_tab_button.setObjectName('tabButton')
        self.login_tab_button.clicked.connect(lambda: self.switch_tab(0))
        self.login_tab_button.setStyleSheet('''
            QPushButton#tabButton {
                background: #f7f7f7;
                border: none;
                border-bottom: 2px solid #1f6fe5;
                color: #0f172a;
                font-size: 13px;
                font-weight: 700;
                padding: 12px 24px;
                margin: 0;
            }
        ''')

        self.database_tab_button = QPushButton('Banco de Dados')
        self.database_tab_button.setObjectName('tabButton')
        self.database_tab_button.clicked.connect(lambda: self.switch_tab(1))
        self.database_tab_button.setStyleSheet('''
            QPushButton#tabButton {
                background: #f7f7f7;
                border: none;
                border-bottom: 2px solid transparent;
                color: #5a6e82;
                font-size: 13px;
                font-weight: 700;
                padding: 12px 24px;
                margin: 0;
            }
            QPushButton#tabButton:hover {
                color: #0f172a;
            }
        ''')

        tab_bar_layout.addWidget(self.login_tab_button)
        tab_bar_layout.addWidget(self.database_tab_button)
        tab_bar_layout.addStretch(1)

        panel_layout.addWidget(tab_bar_widget)

        # Content container inside panel
        self.content_container = QFrame()
        self.content_container.setObjectName('contentContainer')
        self.content_container.setStyleSheet('QFrame#contentContainer { background: #f7f7f7; }')
        self.content_container_layout = QVBoxLayout(self.content_container)
        self.content_container_layout.setContentsMargins(0, 0, 0, 0)
        self.content_container_layout.setSpacing(0)

        # Create tab contents
        self.login_tab = self.create_login_tab()
        self.database_tab = self.create_database_tab()

        self.content_container_layout.addWidget(self.login_tab, 1)

        panel_layout.addWidget(self.content_container, 1)

        # Add main panel to gray container
        gray_layout.addWidget(main_panel, 0, Qt.AlignCenter)

        main_layout.addWidget(gray_container, 1)
        self.setLayout(main_layout)
        self.refresh_database_list()

    def switch_tab(self, tab_index):
        # Clear current content
        while self.content_container_layout.count():
            widget = self.content_container_layout.takeAt(0).widget()
            if widget:
                widget.setParent(None)

        # Update button styles
        if tab_index == 0:
            self.login_tab_button.setStyleSheet('''
                QPushButton#tabButton {
                    background: #f7f7f7;
                    border: none;
                    border-bottom: 2px solid #1f6fe5;
                    color: #0f172a;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 12px 24px;
                    margin: 0;
                }
            ''')
            self.database_tab_button.setStyleSheet('''
                QPushButton#tabButton {
                    background: #f7f7f7;
                    border: none;
                    border-bottom: 2px solid transparent;
                    color: #5a6e82;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 12px 24px;
                    margin: 0;
                }
                QPushButton#tabButton:hover {
                    color: #0f172a;
                }
            ''')
            self.content_container_layout.addWidget(self.login_tab, 1)
        else:
            self.database_tab_button.setStyleSheet('''
                QPushButton#tabButton {
                    background: #f7f7f7;
                    border: none;
                    border-bottom: 2px solid #1f6fe5;
                    color: #0f172a;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 12px 24px;
                    margin: 0;
                }
            ''')
            self.login_tab_button.setStyleSheet('''
                QPushButton#tabButton {
                    background: #f7f7f7;
                    border: none;
                    border-bottom: 2px solid transparent;
                    color: #5a6e82;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 12px 24px;
                    margin: 0;
                }
                QPushButton#tabButton:hover {
                    color: #0f172a;
                }
            ''')
            self.content_container_layout.addWidget(self.database_tab, 1)

    def create_login_tab(self):
        tab = QWidget()
        tab.setObjectName('loginTabPage')
        tab.setStyleSheet('QWidget#loginTabPage { background: #f7f7f7; }')
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        icon_wrapper = QFrame()
        icon_wrapper.setFixedSize(88, 88)
        icon_wrapper.setStyleSheet('''
            QFrame {
                background: #eaf1ff;
                border-radius: 44px;
            }
        ''')
        icon_wrapper_layout = QVBoxLayout(icon_wrapper)
        icon_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        icon_wrapper_layout.setAlignment(Qt.AlignCenter)

        logo_icon = QLabel()
        self._set_icon_for_label(logo_icon, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images', 'system_logo.ico'), 52)
        icon_wrapper_layout.addWidget(logo_icon)

        wrapper_h = QHBoxLayout()
        wrapper_h.addStretch(1)
        wrapper_h.addWidget(icon_wrapper)
        wrapper_h.addStretch(1)
        layout.addLayout(wrapper_h)

        title = QLabel('Acesso ao sistema')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(login_title_style())
        layout.addWidget(title)

        subtitle = QLabel('Faça login para acessar sua conta')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(login_subtitle_style())
        layout.addWidget(subtitle)

        self.current_db_label = QLabel('Banco de dados selecionado: ---')
        self.current_db_label.setStyleSheet(
            'font-size: 12px; color: #475569; background: #e7edf5; border-radius: 6px; padding: 8px 10px;'
        )
        self.current_db_label.setWordWrap(True)
        self.current_db_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_db_label)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(8)

        login_label = QLabel('Login')
        login_label.setStyleSheet(login_field_label_style())
        login_label.setAlignment(Qt.AlignLeft)
        form_layout.addWidget(login_label)

        self.login_input = QLineEdit()
        self.login_input.setStyleSheet(login_input_style())
        self.login_input.setPlaceholderText('Digite o usuário')
        self.login_input.setFixedHeight(42)

        login_icon = QLabel()
        self._set_icon_for_label(login_icon, self._icon_path('login_icon.ico'), 18)
        login_wrapper = QHBoxLayout()
        login_wrapper.setContentsMargins(0, 0, 0, 0)
        login_wrapper.setSpacing(8)
        login_wrapper.addWidget(login_icon)
        login_wrapper.addWidget(self.login_input)
        form_layout.addLayout(login_wrapper)

        form_layout.addSpacing(6)

        senha_label = QLabel('Senha')
        senha_label.setStyleSheet(login_field_label_style())
        senha_label.setAlignment(Qt.AlignLeft)
        form_layout.addWidget(senha_label)

        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(login_input_style())
        self.password_input.setPlaceholderText('Digite a senha')
        self.password_input.setFixedHeight(42)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)

        password_icon = QLabel()
        self._set_icon_for_label(password_icon, self._icon_path('password_ico.ico'), 18)
        self.password_toggle_button = QPushButton()
        self.password_toggle_button.setIcon(QIcon(self._icon_path('visible_password_off.ico')))
        self.password_toggle_button.setIconSize(QSize(18, 18))
        self.password_toggle_button.setFixedSize(26, 26)
        self.password_toggle_button.setFlat(True)
        self.password_toggle_button.setCursor(Qt.PointingHandCursor)
        self.password_toggle_button.setToolTip('Mostrar senha')
        self.password_toggle_button.clicked.connect(self._toggle_password_visibility)
        self.password_toggle_button.setStyleSheet('''
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
            }
        ''')

        password_wrapper = QHBoxLayout()
        password_wrapper.setContentsMargins(0, 0, 0, 0)
        password_wrapper.setSpacing(8)
        password_wrapper.addWidget(password_icon)
        password_wrapper.addWidget(self.password_input)
        password_wrapper.addWidget(self.password_toggle_button)
        form_layout.addLayout(password_wrapper)

        layout.addLayout(form_layout)

        self.login_button = QPushButton('↳ Entrar')
        self.login_button.setStyleSheet(login_button_style())
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setFixedHeight(46)
        self.login_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.login_button)

        layout.addStretch(1)

        return tab

    def create_database_tab(self):
        tab = QWidget()
        tab.setStyleSheet('background-color: #f7f7f7;')
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel('Selecionar Base de Dados')
        title.setStyleSheet('font-size: 16px; font-weight: 700; color: #0F172A;')
        layout.addWidget(title)

        self.db_table = QTableWidget(0, 1)
        self.db_table.setHorizontalHeaderLabels(['Descrição'])
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
        self.db_table.setColumnWidth(0, 250)
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
            self.db_table.setItem(row, 0, description_item)

            if self.selected_database and database.key == self.selected_database.key:
                self.db_table.selectRow(row)

        if self.selected_database is None and self.db_table.rowCount() > 0:
            self.db_table.selectRow(0)

        self.update_database_details()
        self.update_current_db_label()

    def update_current_db_label(self):
        if self.selected_database:
            self.current_db_label.setText(f'Banco de dados selecionado: {self.selected_database.name}')
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


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QHBoxLayout, QFrame, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QPixmap
from app.auth.service import AuthService
from PySide6.QtCore import QThread, Signal, QObject
from app.utils.ui_utils import LoadingOverlay
from app.utils.local_settings import load_local_params, save_local_params
from app.styles.windows_style import window_style, LIGHT
from app.styles.input_styles import input_style, DEFAULTINPUT
from app.styles.buttons_styles import button_style, BLUE


class LoginWindow(QWidget):
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success
        self.auth_service = None
        self.setWindowTitle('Login - SOFME')
        self.setGeometry(300, 200, 420, 320)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        # Use the app window style but force a gray background for the login window
        self.setObjectName('loginWindowRoot')
        self.setStyleSheet(window_style(LIGHT) + " #loginWindowRoot { background-color: #d1d5db; }")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Central panel to mimic a centered login layout
        panel = QFrame()
        panel.setObjectName('loginPanel')
        panel.setStyleSheet('#loginPanel { background: white; border-radius: 8px; padding: 18px; }')
        panel.setFixedWidth(360)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(12)

        # Title inside the panel so the panel is fully centered
        title = QLabel('Acesso ao sistema')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 22px; font-weight: 700; color: #0F172A;')
        panel_layout.addWidget(title)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setHorizontalSpacing(12)

        self.login_input = QLineEdit()
        self.login_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.login_input.setPlaceholderText('Digite o login')
        self.login_input.setFixedHeight(36)

        # Load last login from local params file
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

        # Make the login button full-width to align with inputs
        self.login_button = QPushButton('Entrar')
        self.login_button.setStyleSheet(button_style(BLUE))
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setFixedHeight(40)
        self.login_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        panel_layout.addWidget(self.login_button)

        # Center the panel
        # Add a top stretch so the panel is vertically centered
        layout.addStretch(1)

        wrapper = QHBoxLayout()
        wrapper.addStretch(1)
        wrapper.addWidget(panel)
        wrapper.addStretch(1)
        layout.addLayout(wrapper)
        layout.addStretch(1)

        self.setLayout(layout)

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        # Show loading overlay
        if not hasattr(self, 'loading_overlay'):
            self.loading_overlay = LoadingOverlay(self, message='Autenticando...')
        self.loading_overlay.setMessage('Autenticando...')
        self.loading_overlay.show()
        self.loading_overlay.raise_()
        QApplication.processEvents()

        # Use a QThread subclass to avoid cross-thread parenting issues
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
                # Save last successful login to local params
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
        # Registration removed from UI per request.
        pass


LOGIN_BG = "#dfe5eb"
LOGIN_PAGE_BG = "#dfe5eb"
LOGIN_PANEL_BG = "#f7f7f7"
LOGIN_INPUT_BG = "#f4f6f8"
LOGIN_SOFT_BG = "#e8edf3"
LOGIN_TEXT = "#0f172a"
LOGIN_MUTED = "#5a6e82"
LOGIN_BORDER = "#d9e0e7"
LOGIN_ACCENT = "#1f6fe5"
LOGIN_ACCENT_DARK = "#165ed0"
LOGIN_FIELD_BORDER = "#d1d9e5"


def login_window_style():
    return f"""
        QWidget {{
            background-color: {LOGIN_PAGE_BG};
            color: {LOGIN_TEXT};
            font-family: "Segoe UI", Arial, sans-serif;
        }}
        #loginWindowRoot {{
            background-color: {LOGIN_PAGE_BG};
        }}
        QTabWidget {{
            background: transparent;
        }}
    """


def login_tab_style():
    return f"""
        QTabBar#loginTabBar {{
            background: transparent;
            border: none;
            margin: 0;
            padding: 0;
        }}
        QTabBar#loginTabBar::tab {{
            background: {LOGIN_SOFT_BG};
            border: none;
            border-radius: 0px;
            padding: 12px 26px 10px 26px;
            margin: 0;
            color: {LOGIN_MUTED};
            min-width: 120px;
        }}
        QTabBar#loginTabBar::tab:selected {{
            background: {LOGIN_SOFT_BG};
            color: {LOGIN_TEXT};
            font-weight: 700;
            border-bottom: 3px solid {LOGIN_ACCENT};
        }}
        QTabBar#loginTabBar::tab:hover {{
            background: #e4ebf4;
        }}
        QTabWidget::pane {{
            border: none;
            margin: 0;
            padding: 0;
            background: transparent;
        }}
    """


def login_panel_style():
    return f"""
        #loginPanel {{
            background: {LOGIN_PANEL_BG};
            border: 1px solid #ebeff5;
            border-radius: 12px;
        }}
    """


def login_title_style():
    return f"""
        QLabel {{
            color: {LOGIN_TEXT};
            font-size: 25px;
            font-weight: 700;
            background: transparent;
        }}
    """


def login_subtitle_style():
    return f"""
        QLabel {{
            color: {LOGIN_MUTED};
            font-size: 14px;
            background: transparent;
        }}
    """


def login_field_label_style():
    return f"""
        QLabel {{
            color: {LOGIN_TEXT};
            font-size: 13px;
            font-weight: 600;
            background: transparent;
        }}
    """


def login_input_style():
    return f"""
        QLineEdit {{
            background: {LOGIN_INPUT_BG};
            border: 1px solid {LOGIN_FIELD_BORDER};
            border-radius: 7px;
            padding: 10px 12px;
            font-size: 14px;
            color: {LOGIN_TEXT};
            min-height: 40px;
        }}
        QLineEdit:focus {{
            border: 1px solid {LOGIN_ACCENT};
            background: #f1f6ff;
        }}
        QLineEdit::placeholder {{
            color: #8fa0b5;
        }}
    """


def login_button_style():
    return f"""
        QPushButton {{
            background: {LOGIN_ACCENT};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            font-size: 16px;
            font-weight: 700;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background: {LOGIN_ACCENT_DARK};
        }}
        QPushButton:pressed {{
            background: #144fae;
        }}
    """

import os

# ======================================================
# INPUT PADRÃO
# ======================================================

DEFAULTINPUT = {
    "border-radius": "14px",
    "padding": "10px 14px",
    "font-weight": "600",
    "border-color": "#D1D9E6",
}


def _get_icon_path(icon_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.normpath(os.path.join(current_dir, "..", "images", "icons", icon_name))
    return icon_path.replace("\\", "/")


# ======================================================
# QLINEEDIT / QTEXTEDIT
# ==================================================

def input_style(color):
    """Retorna QSS padrão para inputs de texto"""
    return f"""
    QLineEdit, QTextEdit {{
        border-radius: {color['border-radius']};
        padding: {color['padding']};
        font-weight: {color['font-weight']};
        font-size: 14px;
        border: 1px solid {color['border-color']};
        background-color: #FFFFFF;
        color: #0F172A;
        min-height: 34px;
    }}

    QLineEdit:hover, QTextEdit:hover {{
        border-color: #A3BFFA;
    }}

    QLineEdit:focus, QTextEdit:focus {{
        border-color: #2563EB;
    }}
    """


def table_editor_style(color):
    """Retorna QSS compacto para editores embutidos em células de tabela."""
    return f"""
    QLineEdit {{
        border-radius: 4px;
        padding: 2px 6px;
        font-weight: {color['font-weight']};
        font-size: 13px;
        border: 1px solid {color['border-color']};
        background-color: #FFFFFF;
        color: #0F172A;
        min-height: 0px;
    }}

    QLineEdit:focus {{
        border-color: #2563EB;
    }}
    """


# ======================================================
# QDOUBLESPINBOX
# ======================================================

def doublespinbox_style(color):
    return f"""
    QDoubleSpinBox {{
        border-radius: {color['border-radius']};
        padding: {color['padding']};
        font-weight: {color['font-weight']};
        font-size: 14px;
        padding-right: 20px; /* espaço para os botões */
    }}

    /* Caixa dos botões */
    QDoubleSpinBox::up-button,
    QDoubleSpinBox::down-button {{
        background: transparent;
        border: none;
        width: 16px;
    }}

    /* Botão de subir */
    QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
    }}

    /* Botão de descer */
    QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
    }}

    /* Seta de subir */
    QDoubleSpinBox::up-arrow {{
        image: url({_get_icon_path('doublespin-up-arrow.svg')});
        width: 10px;
        height: 10px;
    }}

    /* Seta de descer */
    QDoubleSpinBox::down-arrow {{
        image: url({_get_icon_path('doublespin-down-arrow.svg')});
        width: 10px;
        height: 10px;
    }}

    /* Hover opcional */
    QDoubleSpinBox::up-button:hover,
    QDoubleSpinBox::down-button:hover {{
        background-color: rgba(255, 255, 255, 0.05);
    }}
    """


# ======================================================
# QDATEEDIT / QDATETIMEEDIT + CALENDÁRIO
# ======================================================

def input_date_style(color):
    return f"""
    /* ===== INPUT DE DATA / DATA+HORA ===== */
    QDateEdit, QDateTimeEdit {{
        border: 1px solid {color['border-color']};
        border-radius: {color['border-radius']};
        padding: {color['padding']};
        font-weight: {color['font-weight']};
        font-size: 14px;
        background-color: white;
        color: #333333;
    }}

    QDateEdit:hover, QDateTimeEdit:hover {{
        border-color: #999999;
    }}

    QDateEdit, QDateTimeEdit {{
        min-height: 34px;
    }}

    QDateEdit:focus, QDateTimeEdit:focus {{
        border-color: #7A7A7A;
    }}

    /* ===== BOTÃO DO CALENDÁRIO ===== */
    QDateEdit::drop-down, QDateTimeEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: right center;
        width: 30px;
        border-left: 1px solid {color['border-color']};
        background-color: #F5F5F5;
    }}

    QDateEdit::down-arrow, QDateTimeEdit::down-arrow {{
        image: url({_get_icon_path('calendar.svg')});
        width: 14px;
        height: 14px;
    }}

    /* ===== CALENDÁRIO ===== */
    QCalendarWidget {{
        background-color: white;
        border: 1px solid {color['border-color']};
        border-radius: 8px;
        min-width: 280px;
        min-height: 260px;
    }}

    /* ===== BARRA DE NAVEGAÇÃO (MÊS / ANO) ===== */
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: #F2F2F2;
        border-bottom: 1px solid #DDDDDD;
    }}

    /* Botões de navegação */
    QCalendarWidget QToolButton {{
        color: #333333;
        font-weight: 600;
        background: transparent;
        padding: 6px 10px;
        margin: 2px;
    }}

    QCalendarWidget QToolButton:hover {{
        background-color: #E0E0E0;
        border-radius: 4px;
    }}

    /* Remove seta dropdown do mês */
    QCalendarWidget QToolButton::menu-indicator {{
        image: none;
        width: 0px;
    }}

    /* ===== DIAS DA SEMANA ===== */
    QCalendarWidget QHeaderView::section {{
        background-color: #FAFAFA;
        color: #666666;
        padding: 6px;
        font-weight: 600;
        border: none;
    }}

    /* ===== GRADE ===== */
    QCalendarWidget QAbstractItemView {{
        gridline-color: #E6E6E6;
        selection-background-color: #198754;
        selection-color: white;
        outline: none;
        font-size: 13px;
    }}

    /* ===== DIAS ===== */
    QCalendarWidget QAbstractItemView::item {{
        background-color: white;
        color: #333333;
        min-width: 36px;
        min-height: 32px;
        padding: 6px;
        border-radius: 6px;
    }}

    QCalendarWidget QAbstractItemView::item:hover {{
        background-color: #EAEAEA;
    }}

    /* ===== DIAS FORA DO MÊS ===== */
    QCalendarWidget QAbstractItemView::item:disabled {{
        background-color: #F3F3F3;
        color: #B5B5B5;
    }}

    /* ===== DIA SELECIONADO ===== */
    QCalendarWidget QAbstractItemView::item:selected {{
        background-color: #198754;
        color: white;
        font-weight: 600;
    }}
    """

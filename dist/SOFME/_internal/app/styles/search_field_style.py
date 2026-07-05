# ======================================================
# SEARCH FIELD / COMBOBOX
# ======================================================
import os

DEFAULT = {
    "border-radius": "14px",
    "padding": "10px 14px",
    "font-weight": "600",
    "border-color": "#D1D9E6",
}


def _get_icon_path(icon_name):
    """Resolve o caminho absoluto de um ícone"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.normpath(os.path.join(current_dir, "..", "images", "icons", icon_name))
    # Converter para caminho com forward slashes para o QSS
    return icon_path.replace("\\", "/")


def search_field_style(c):
    arrow_icon_path = _get_icon_path("search_field_arrow_down.svg")
    return f"""
    /* ===== COMBOBOX ===== */
    QComboBox {{
        padding: {c['padding']};
        font-weight: {c['font-weight']};
        border: 1px solid {c['border-color']};
        border-radius: {c['border-radius']};
        background-color: white;
        color: #0F172A;
        min-height: 34px;
    }}

    QComboBox:hover {{
        border-color: #A3BFFA;
    }}

    QComboBox:focus {{
        border-color: #2563EB;
    }}

    /* ===== BOTÃO DROPDOWN ===== */
    QComboBox::drop-down {{
        background: transparent;
        border: none;
        width: 34px;
    }}

    QComboBox::down-arrow {{
        image: url({arrow_icon_path});
        width: 14px;
        height: 14px;
    }}

    /* ===== LISTA SUSPENSA ===== */
    QComboBox QAbstractItemView {{
        background-color: white;
        border: 1px solid #D1D9E6;
        selection-background-color: #E8F0FF;
        selection-color: #0F172A;
        outline: 0;
    }}

    QComboBox QAbstractItemView::item:hover {{
        background-color: #EFF4FF;
    }}

    QComboBox QAbstractItemView::item:selected {{
        background-color: #DCE8FF;
        color: #0F172A;
    }}
    """

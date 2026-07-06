# ======================================================
# PALETA DE CORES
# ======================================================

GREEN = {
    "default": "#16A34A",
    "hover": "#15803D",
    "pressed": "#166534",
    "disabled": "#A7F3D0",
    "text": "white",
}

BLUE = {
    "default": "#2563EB",
    "hover": "#1D4ED8",
    "pressed": "#1E40AF",
    "disabled": "#93C5FD",
    "text": "white",
}

GRAY = {
    "default": "#475569",
    "hover": "#334155",
    "pressed": "#1E293B",
    "disabled": "#CBD5E1",
    "text": "white",
}

RED = {
    "default": "#DC2626",
    "hover": "#B91C1C",
    "pressed": "#991B1B",
    "disabled": "#FCA5A5",
    "text": "white",
}

YELLOW = {
    "default": "#F59E0B",
    "hover": "#D97706",
    "pressed": "#B45309",
    "disabled": "#FCD34D",
    "text": "#0F172A",
}

# ======================================================
# FUNÇÕES DE ESTILO
# ======================================================

def button_style(color):
    """Retorna QSS padrão para botões"""
    return f"""
    QPushButton {{
        background-color: {color['default']};
        color: {color.get('text', 'white')};
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 14px;
        min-height: 34px;
        border: none;
    }}

    QPushButton:hover {{
        background-color: {color['hover']};
    }}

    QPushButton:pressed {{
        background-color: {color['pressed']};
    }}

    QPushButton:disabled {{
        background-color: {color['disabled']};
        color: #94A3B8;
    }}
    """

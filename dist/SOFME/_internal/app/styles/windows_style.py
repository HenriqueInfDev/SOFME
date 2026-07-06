import os

# ======================================================
# PALETA – TEMA CLARO CORPORATIVO
# ======================================================

LIGHT = {
    "background": "#F5F8FF",
    "background-menu": "#FFFFFF",
    "surface": "#FFFFFF",
    "surface-alt": "#F8FAFF",
    "border": "#D1D9E6",
    "text-color": "#0F172A",
    "text-muted": "#475569",
    "accent": "#2563EB",
    "accent-soft": "#E8F1FF",
    "hover": "#EFF4FF",
    "focus": "#2563EB",
}


def _get_icon_path(icon_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.normpath(os.path.join(current_dir, "..", "images", "icons", icon_name))
    return icon_path.replace("\\", "/")


# ======================================================
# WINDOW STYLE
# ======================================================

def window_style(color):
    return f"""
    /* ==================================================
       BASE
       ================================================== */

    QWidget {{
        background-color: {color['background']};
        color: {color['text-color']};
        font-family: "Inter", "Segoe UI", "Arial", sans-serif;
    }}

    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QDateEdit,
    QDateTimeEdit,
    QTextEdit,
    QTableWidget,
    QTableView,
    QMenuBar,
    QMenu,
    QGroupBox,
    QTabBar::tab,
    QHeaderView::section {{
        font-size: 14px;
    }}

    QLabel {{
        color: {color['text-color']};
        background-color: transparent;
    }}

    /* ==================================================
       MAIN WINDOW
       ================================================== */

    QMainWindow {{
        background-color: {color['background']};
    }}

    QToolBar {{
        background-color: {color['background-menu']};
        border-bottom: 1px solid {color['border']};
        padding: 6px 10px;
    }}

    QToolButton {{
        background: transparent;
        border: none;
        border-radius: 12px;
        padding: 9px 14px;
        color: {color['text-color']};
    }}

    QToolButton:hover {{
        background-color: {color['hover']};
    }}

    QToolButton:checked {{
        background-color: {color['accent-soft']};
        color: {color['accent']};
    }}

    /* ==================================================
       MENU BAR / MENU
       ================================================== */

    QMenuBar {{
        background-color: {color['background-menu']};
        color: {color['text-color']};
        font: 14px "Inter", "Segoe UI", "Arial";
        font-weight: 600;
        padding: 0 16px;
        border-bottom: 1px solid {color['border']};
    }}

    QMenuBar::item {{
        padding: 8px 12px;
        margin: 0 6px;
        border-radius: 10px;
    }}

    QMenuBar::item:selected,
    QMenuBar::item:pressed {{
        background-color: {color['accent-soft']};
        color: {color['accent']};
    }}

    QMenu {{
        background-color: {color['surface']};
        color: {color['text-color']};
        border: 1px solid {color['border']};
        border-radius: 16px;
        padding: 2px 2px;
    }}

    QMenu::item {{
        padding: 6px 24px 6px 16px;
        border-radius: 8px;
        margin: 0;
        min-height: 28px;
    }}

    QMenu::icon {{
        width: 16px;
        height: 16px;
        margin: 0 8px 0 4px;
    }}

    QMenu::right-arrow {{
        width: 10px;
        height: 10px;
        subcontrol-position: right center;
        margin: 0 8px 0 8pxpx;
    }}

    QMenu::separator {{
        height: 1px;
        background: #E5E7EB;
        margin: 4px 0;
    }}

    QMenu::item:selected {{
        background-color: {color['accent-soft']};
        color: {color['text-color']};
    }}

    /* ==================================================
       GROUP BOX
       ================================================== */

    QGroupBox {{
        border: 1px solid {color['border']};
        border-radius: 16px;
        margin-top: 18px;
        padding: 16px;
        background-color: {color['surface']};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        color: {color['text-color']};
        font-weight: 700;
    }}

    /* ==================================================
       INPUTS
       ================================================== */

    QLineEdit,
    QComboBox,    QComboBox,    QDoubleSpinBox,
    QTextEdit,
    QDateEdit,
    QDateTimeEdit {{
        background-color: {color['surface']};
        border: 1px solid {color['border']};
        border-radius: 14px;
        padding: 12px 14px;
        color: {color['text-color']};
        min-height: 34px;
    }}

    QDateEdit::drop-down,
    QDateTimeEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: right center;
        width: 28px;
        border-left: 1px solid {color['border']};
        background-color: #F5F5F5;
    }}

    QDateEdit::down-arrow,
    QDateTimeEdit::down-arrow {{
        image: url({_get_icon_path('calendar.ico')});
        width: 14px;
        height: 14px;
    }}

    QLineEdit:hover,
    QDoubleSpinBox:hover,
    QTextEdit:hover,
    QDateEdit:hover,
    QDateTimeEdit:hover {{
        border-color: {color['focus']};
    }}

    QLineEdit:focus,
    QDoubleSpinBox:focus,
    QTextEdit:focus,
    QDateEdit:focus,
    QDateTimeEdit:focus {{
        border-color: {color['accent']};
        outline: none;
    }}

    QFormLayout QLabel {{
        padding-right: 10px;
        color: {color['text-muted']};
        font-weight: 600;
    }}

    /* ==================================================
       TABS
       ================================================== */

    QTabWidget::pane {{
        border: 1px solid {color['border']};
        border-radius: 18px;
        background: {color['surface']};
    }}

    QTabWidget::pane QWidget {{
        background-color: {color['surface']};
    }}

    QTabBar::tab {{
        background: {color['surface-alt']};
        padding: 10px 18px;
        border: 1px solid {color['border']};
        border-radius: 14px;
        margin-right: 8px;
    }}

    QTabBar::tab:selected {{
        background: {color['surface']};
        font-weight: 700;
        color: {color['accent']};
    }}

    QTabBar::tab:!selected {{
        margin-top: 2px;
    }}

    /* ==================================================
       TABLES (QTableView / QTableWidget)
       ================================================== */

    QTableView,
    QTableWidget {{
        background-color: {color['surface']};
        alternate-background-color: {color['surface-alt']};
        border: 1px solid {color['border']};
        gridline-color: {color['border']};
        outline: 0;
    }}

    QTableView::item,
    QTableWidget::item {{
        padding: 12px 14px;
        color: {color['text-color']};
        border-bottom: 1px solid {color['border']};
    }}

    QTableView::item:hover,
    QTableWidget::item:hover {{
        background-color: {color['hover']};
    }}

    QTableView::item:selected,
    QTableWidget::item:selected {{
        background-color: {color['accent-soft']};
        color: {color['text-color']};
    }}

    QTableView::item:selected:!active,
    QTableWidget::item:selected:!active {{
        background-color: {color['accent-soft']};
    }}

    /* ==================================================
       SCROLLBARS
       ================================================== */

    QScrollBar:vertical,
    QScrollBar:horizontal {{
        background: {color['accent-soft']};
        border-radius: 10px;
        margin: 4px 0;
        padding: 0;
    }}

    QScrollBar::handle:vertical,
    QScrollBar::handle:horizontal {{
        background: {color['accent']};
        border-radius: 10px;
        min-height: 24px;
        min-width: 24px;
    }}

    QScrollBar::handle:vertical:hover,
    QScrollBar::handle:horizontal:hover {{
        background: {color['focus']};
    }}

    QScrollBar::add-line,
    QScrollBar::sub-line {{
        background: transparent;
        border: none;
        width: 0;
        height: 0;
    }}

    QScrollBar::add-page,
    QScrollBar::sub-page {{
        background: {color['accent-soft']};
        border-radius: 10px;
    }}

    QHeaderView::section {{
        background-color: {color['accent-soft']};
        padding: 10px 14px;
        border: none;
        color: {color['accent']};
        font-weight: 700;
    }}

    QTableCornerButton::section {{
        background-color: {color['accent-soft']};
        border: none;
    }}
    """

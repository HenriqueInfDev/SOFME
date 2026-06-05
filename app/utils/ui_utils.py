# app/utils/ui_utils.py
import re
from decimal import Decimal, InvalidOperation
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog, QDateEdit, QLineEdit, QPushButton, QCalendarWidget, QHBoxLayout, QWidget, QDialog, QVBoxLayout
from PySide6.QtCore import Qt, QDate, QEvent
from PySide6.QtGui import QFontMetrics, QIcon
from app.styles.buttons_styles import button_style, GREEN, RED, YELLOW
from app.styles.input_styles import _get_icon_path


def configure_table_columns(table_view, total_width=None, padding=36):
    """Configura larguras iniciais de colunas para exibir o cabeçalho completo.

    A largura mínima de cada coluna fica baseada no tamanho do texto do cabeçalho,
    e a largura total é distribuída proporcionalmente no espaço disponível.
    """
    model = table_view.model()
    if model is None or model.columnCount() == 0:
        return

    fm = QFontMetrics(table_view.font())
    header = table_view.horizontalHeader()
    column_count = model.columnCount()
    min_widths = []
    for column in range(column_count):
        header_label = model.headerData(column, Qt.Horizontal) or ""
        label_width = fm.horizontalAdvance(str(header_label))
        min_widths.append(max(label_width + padding, header.minimumSectionSize()))

    if total_width is None or total_width <= 0:
        total_width = max(table_view.viewport().width(), table_view.width())

    total_width = max(total_width, sum(min_widths))
    total_min = sum(min_widths)
    widths = []

    if total_min == 0:
        widths = [max(100, total_width // column_count)] * column_count
    else:
        for min_width in min_widths:
            widths.append(max(min_width, int(total_width * min_width / total_min)))

    for index, width in enumerate(widths):
        table_view.setColumnWidth(index, width)


def show_warning_message(parent, title, message):
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)
    ok_button.setStyleSheet(button_style(YELLOW))
    msg_box.exec()

def show_error_message(parent, title, message):
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)
    ok_button.setStyleSheet(button_style(RED))
    msg_box.exec()

def show_success_message(parent, title, message):
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)
    ok_button.setStyleSheet(button_style(GREEN))
    msg_box.exec()

def show_confirmation_message(parent, title, message):
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    yes_button = msg_box.addButton("Sim", QMessageBox.YesRole)
    no_button = msg_box.addButton("Não", QMessageBox.NoRole)
    
    yes_button.setStyleSheet(button_style(GREEN))
    no_button.setStyleSheet(button_style(RED))
    
    msg_box.exec()
    
    if msg_box.clickedButton() == yes_button:
        return QMessageBox.Yes
    return QMessageBox.No

def show_custom_confirmation(parent, title, message, buttons_config):
    """
    buttons_config: list of dicts {'text': '...', 'role': ..., 'style': ..., 'result': ...}
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    button_widgets = {}
    for cfg in buttons_config:
        btn = msg_box.addButton(cfg['text'], cfg['role'])
        btn.setStyleSheet(button_style(cfg['style']))
        button_widgets[btn] = cfg['result']
        
    msg_box.exec()
    return button_widgets.get(msg_box.clickedButton())


def configure_blank_date_edit(date_edit, display_format="dd/MM/yyyy"):
    min_date = QDate(1752, 1, 1)
    date_edit.setCalendarPopup(True)
    date_edit.setDisplayFormat(display_format)
    date_edit.setMinimumDate(min_date)
    date_edit.setSpecialValueText(" ")
    date_edit.setDate(min_date)
    date_edit.clear()


def get_required_date_value(date_edit):
    if not getattr(date_edit, "text", lambda: "")().strip():
        return None

    if not hasattr(date_edit, "date"):
        return None

    date = date_edit.date()
    if not date.isValid():
        return None

    if hasattr(date_edit, "minimumDate") and date == date_edit.minimumDate():
        return None

    return date.toString("yyyy-MM-dd")

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except (ValueError, TypeError):
            return super().__lt__(other)


class CalendarTextField(QWidget):
    def __init__(self, display_format="dd/MM/yyyy", parent=None):
        super().__init__(parent)
        self.display_format = display_format
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("DD/MM/AAAA")
        self.line_edit.setMaxLength(10)
        self.line_edit.textChanged.connect(self._on_text_changed)

        self.button = QPushButton(self)
        icon_path = _get_icon_path("calendar.svg")
        self.button.setIcon(QIcon(icon_path))
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setFlat(True)
        self.button.setFixedWidth(36)
        self.button.clicked.connect(self.open_calendar)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

    def _format_text(self, text):
        digits = re.sub(r"\D", "", text)[:8]
        parts = []
        if digits:
            parts.append(digits[:2])
            if len(digits) > 2:
                parts.append(digits[2:4])
                if len(digits) > 4:
                    parts.append(digits[4:8])
        return "/".join(parts)

    def _on_text_changed(self, text):
        formatted = self._format_text(text)
        if text != formatted:
            cursor = self.line_edit.cursorPosition()
            self.line_edit.blockSignals(True)
            self.line_edit.setText(formatted)
            self.line_edit.blockSignals(False)
            self.line_edit.setCursorPosition(min(cursor, len(formatted)))

    def open_calendar(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar data")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background-color: white; }")
        calendar = QCalendarWidget(dialog)
        calendar.setGridVisible(True)
        if self.date().isValid():
            calendar.setSelectedDate(self.date())
        else:
            calendar.setSelectedDate(QDate.currentDate())
        calendar.clicked.connect(lambda date: self._select_date(date, dialog))
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(calendar)
        dialog.exec()

    def _select_date(self, date, dialog):
        self.line_edit.blockSignals(True)
        self.line_edit.setText(date.toString(self.display_format))
        self.line_edit.blockSignals(False)
        dialog.accept()

    def text(self):
        return self.line_edit.text()

    def clear(self):
        self.line_edit.clear()

    def date(self):
        text = self.line_edit.text()
        if len(text) != 10:
            return QDate()
        parts = text.split("/")
        if len(parts) != 3:
            return QDate()
        day, month, year = parts
        if not (day.isdigit() and month.isdigit() and year.isdigit()):
            return QDate()
        return QDate(int(year), int(month), int(day))

    def setText(self, value):
        self.line_edit.setText(value)


def format_decimal_text(value, min_decimals=2):
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return str(value)

    if dec == dec.to_integral():
        return f"{dec:.2f}"

    normalized = dec.normalize()
    text = format(normalized, 'f')
    if '.' in text:
        integer, fraction = text.split('.')
        if len(fraction) < min_decimals:
            fraction = fraction.ljust(min_decimals, '0')
        return f"{integer}.{fraction}"
    return f"{text}.{'0' * min_decimals}"


def get_save_filename(parent, caption, filter):
    """
    Abre um diálogo para salvar arquivo.
    Retorna o caminho do arquivo selecionado e o filtro de tipo de arquivo.
    """
    filename, selected_filter = QFileDialog.getSaveFileName(parent, caption, filter=filter)
    return filename, selected_filter

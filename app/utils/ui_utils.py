# app/utils/ui_utils.py
import os
import re
from decimal import Decimal, InvalidOperation
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog, QDateEdit, QLineEdit, QPushButton, QCalendarWidget, QHBoxLayout, QWidget, QDialog, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QDate, QEvent
from PySide6.QtGui import QFontMetrics, QIcon
from app.styles.buttons_styles import button_style, GREEN, RED, YELLOW
from app.styles.input_styles import _get_icon_path
from app.utils.local_settings import load_table_column_widths, save_table_column_widths
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QPainter, QColor, QPen


def configure_table_columns(table_view, total_width=None, padding=36, table_name=None):
    """Configura larguras iniciais de colunas para exibir o cabeçalho completo.

    Se `table_name` for fornecido, tentamos carregar larguras salvas em
    `local_params.txt` antes de calcular larguras automáticas.
    """
    model = table_view.model()
    if model is None or model.columnCount() == 0:
        return

    column_count = model.columnCount()
    if table_name:
        saved_widths = load_table_column_widths(table_name)
        if saved_widths:
            for index, width in enumerate(saved_widths[:column_count]):
                table_view.setColumnWidth(index, width)
            if len(saved_widths) >= column_count:
                return

    fm = QFontMetrics(table_view.font())
    header = table_view.horizontalHeader()
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
        for index, min_width in enumerate(min_widths):
            if table_name and index < len(saved_widths):
                widths.append(saved_widths[index])
            else:
                widths.append(max(min_width, int(total_width * min_width / total_min)))

    for index, width in enumerate(widths):
        table_view.setColumnWidth(index, width)


def save_table_columns(table_view, table_name):
    model = table_view.model()
    if model is None or model.columnCount() == 0:
        return

    widths = [table_view.columnWidth(i) for i in range(model.columnCount())]
    save_table_column_widths(table_name, widths)


def center_widget_on_screen(widget):
    if widget is None:
        return
    screen = widget.screen()
    if screen is None:
        screen = QApplication.primaryScreen()
    if screen is None:
        return
    geometry = screen.availableGeometry()
    widget.setGeometry(
        geometry.center().x() - widget.width() // 2,
        geometry.center().y() - widget.height() // 2,
        widget.width(),
        widget.height()
    )


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


class Spinner(QWidget):
    """Simple animated spinner widget."""
    def __init__(self, parent=None, line_count=12, line_length=8, line_width=3, inner_radius=10, color=QColor(66,133,244)):
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timeout)
        self._timer.start(80)
        self.line_count = line_count
        self.line_length = line_length
        self.line_width = line_width
        self.inner_radius = inner_radius
        self.color = color
        self.setFixedSize(inner_radius * 4, inner_radius * 4)

    def _on_timeout(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2
        painter.translate(cx, cy)
        for i in range(self.line_count):
            angle = (360.0 * i) / self.line_count
            painter.save()
            painter.rotate(angle + self._angle)
            alpha = int(255 * (i + 1) / self.line_count)
            pen = QPen(self.color)
            pen.setWidth(self.line_width)
            col = QColor(self.color)
            col.setAlpha(alpha)
            pen.setColor(col)
            painter.setPen(pen)
            painter.drawLine(self.inner_radius, 0, self.inner_radius + self.line_length, 0)
            painter.restore()


class LoadingOverlay(QWidget):
    """Semi-transparent full-window overlay with centered spinner and optional message."""
    def __init__(self, parent=None, message="Carregando..."):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        self.message = message
        self.spinner = Spinner(self)
        self.label = QLabel(message, self)
        self.label.setStyleSheet('color: white; font-weight: 600;')
        self.label.setAlignment(Qt.AlignCenter)
        self.hide()

    def showEvent(self, event):
        self.resize_overlay()
        super().showEvent(event)

    def resize_overlay(self):
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        # center spinner + label
        cx = self.width() / 2
        cy = self.height() / 2
        self.spinner.move(int(cx - self.spinner.width() / 2), int(cy - self.spinner.height() / 2 - 12))
        self.label.move(int(cx - 100), int(cy + self.spinner.height() / 2 - 6))
        self.label.resize(200, 24)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

    def show(self):
        self.resize_overlay()
        super().show()

    def setMessage(self, msg):
        self.message = msg
        self.label.setText(msg)

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

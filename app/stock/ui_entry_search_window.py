# app/stock/ui_entry_search_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QComboBox, QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from app.stock.service import StockService
from app.utils.ui_utils import show_error_message, configure_table_columns, save_table_columns
from app.stock.ui_entry_edit_window import EntryEditWindow
from app.utils.date_utils import format_date_for_display

from app.styles.buttons_styles import (
    button_style, GREEN, BLUE
)
from app.styles.windows_style import (
    window_style, LIGHT
)
from app.styles.search_field_style import (
    search_field_style, DEFAULT
)
from app.styles.input_styles import (
    input_style, DEFAULTINPUT
)

class EntrySearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.stock_service = StockService()
        self.edit_window = None
        self.setWindowTitle("Pesquisa de Entradas de Insumo")
        self.setGeometry(200, 200, 900, 700)
        self.setStyleSheet(window_style(LIGHT))
        self.setup_ui()
        self.table_model.removeRows(0, self.table_model.rowCount())

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout()
        self.search_field = QComboBox()
        self.search_field.setStyleSheet(search_field_style(DEFAULT))
        self.search_field.addItems(["ID", "Nº Nota", "Data Entrada", "Valor Total", "Status"])
        self.search_field.currentTextChanged.connect(self.update_search_placeholder)
        self.search_term = QLineEdit()
        self.search_term.setStyleSheet(input_style(DEFAULTINPUT))
        self.search_term.returnPressed.connect(self.load_entries)
        self.update_search_placeholder(self.search_field.currentText())
        search_button = QPushButton("Buscar")
        search_button.setStyleSheet(button_style(BLUE))
        search_button.clicked.connect(self.load_entries)
        new_button = QPushButton("Nova Entrada")
        new_button.setStyleSheet(button_style(GREEN))
        new_button.clicked.connect(self.open_new_entry_window)
        
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_term, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(new_button)
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()
        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID", "Data Entrada", "Nº Nota", "Valor Total", "Status"])
        self.table_view.setModel(self.table_model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)
        
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSortingEnabled(True)
        self.table_view.doubleClicked.connect(self.open_edit_entry_window)
        
        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

    def showEvent(self, event):
        super().showEvent(event)
        configure_table_columns(self.table_view, total_width=self.table_view.viewport().width(), table_name='entry_search')

    def closeEvent(self, event):
        save_table_columns(self.table_view, 'entry_search')
        super().closeEvent(event)

    def load_entries(self):
        self.table_model.removeRows(0, self.table_model.rowCount())
        search_term = self.search_term.text()
        search_field = self.search_field.currentText()
        response = self.stock_service.list_entries(search_term, search_field)
        
        if response["success"]:
            for entry in response["data"]:
                row = [
                    QStandardItem(str(entry['ID'])),
                    QStandardItem(format_date_for_display(entry.get('DATA_ENTRADA', ''))),
                    QStandardItem(entry.get('NUMERO_NOTA', '')),
                    QStandardItem(f"{entry.get('VALOR_TOTAL', 0):.2f}" if entry.get('VALOR_TOTAL') is not None else "N/A"),
                    QStandardItem(entry.get('STATUS', ''))
                ]
                self.table_model.appendRow(row)
        else:
            show_error_message(self, "Error", response["message"])

    def open_new_entry_window(self):
        self.show_edit_window(entry_id=None)

    def open_edit_entry_window(self, model_index):
        entry_id = int(self.table_model.item(model_index.row(), 0).text())
        self.show_edit_window(entry_id=entry_id)

    def show_edit_window(self, entry_id):
        if self.edit_window is not None:
            if self.edit_window.isVisible():
                self.edit_window.activateWindow()
                self.edit_window.raise_()
                return
            self.edit_window.deleteLater()
            self.edit_window = None

        self.edit_window = EntryEditWindow(entry_id=entry_id)
        self.edit_window.setAttribute(Qt.WA_DeleteOnClose)
        self.edit_window.destroyed.connect(self.on_edit_window_closed)
        self.edit_window.show()

    def on_edit_window_closed(self):
        self.edit_window = None
        self.load_entries()

    def update_search_placeholder(self, field):
        placeholders = {
            "Data Entrada": "Pesquisar por data (DD-MM-AAAA)...",
            "Valor Total": "Pesquisar por valor (ex: 50.25)...",
            "ID": "Pesquisar por ID...",
            "Nº Nota": "Pesquisar por número da nota...",
            "Status": "Pesquisar por status (Em Aberto, Finalizada)..."
        }
        self.search_term.setPlaceholderText(placeholders.get(field, "Digite para pesquisar..."))

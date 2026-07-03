# app/sales/ui_sale_search_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QComboBox, QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from app.sales.sale_service import SaleService
from app.utils.ui_utils import show_error_message, configure_table_columns, save_table_columns
from app.sales.ui_sale_edit_window import SaleEditWindow
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

class SaleSearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.sale_service = SaleService()
        self.edit_window = None
        self.setWindowTitle("Pesquisa de Saídas de Produto")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet(window_style(LIGHT))
        self.setup_ui()
        self.load_sales()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout()
        self.search_field = QComboBox()
        self.search_field.setStyleSheet(search_field_style(DEFAULT))
        self.search_field.addItems(["ID", "Status"])
        self.search_term = QLineEdit()
        self.search_term.setStyleSheet(input_style(DEFAULTINPUT))
        self.search_term.returnPressed.connect(self.load_sales)
        search_button = QPushButton("Buscar")
        search_button.setStyleSheet(button_style(BLUE))
        search_button.clicked.connect(self.load_sales)
        new_button = QPushButton("Nova Saída")
        new_button.setStyleSheet(button_style(GREEN))
        new_button.clicked.connect(self.open_new_sale_window)
        
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
        self.table_model.setHorizontalHeaderLabels(["ID", "Data Saída", "Valor Total", "Status"])
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
        self.table_view.doubleClicked.connect(self.open_edit_sale_window)
        
        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

    def showEvent(self, event):
        super().showEvent(event)
        configure_table_columns(self.table_view, total_width=self.table_view.viewport().width(), table_name='sale_search')

    def closeEvent(self, event):
        save_table_columns(self.table_view, 'sale_search')
        super().closeEvent(event)

    def load_sales(self):
        self.table_model.removeRows(0, self.table_model.rowCount())
        search_term = self.search_term.text()
        search_field = self.search_field.currentText().lower()
        response = self.sale_service.list_sales(search_term, search_field)
        
        if response["success"]:
            for sale in response["data"]:
                row = [
                    QStandardItem(str(sale['ID'])),
                    QStandardItem(format_date_for_display(sale.get('DATA_SAIDA', ''))),
                    QStandardItem(f"{sale.get('VALOR_TOTAL', 0):.2f}" if sale.get('VALOR_TOTAL') is not None else "N/A"),
                    QStandardItem(sale.get('STATUS', ''))
                ]
                self.table_model.appendRow(row)
        else:
            show_error_message(self, "Error", response["message"])

    def open_new_sale_window(self):
        self.show_edit_window(sale_id=None)

    def open_edit_sale_window(self, model_index):
        sale_id = int(self.table_model.item(model_index.row(), 0).text())
        self.show_edit_window(sale_id=sale_id)

    def show_edit_window(self, sale_id):
        if self.edit_window is not None:
            if self.edit_window.isVisible():
                self.edit_window.activateWindow()
                self.edit_window.raise_()
                return
            self.edit_window.deleteLater()
            self.edit_window = None

        self.edit_window = SaleEditWindow(sale_id=sale_id)
        self.edit_window.setAttribute(Qt.WA_DeleteOnClose)
        self.edit_window.destroyed.connect(self.on_edit_window_closed)
        self.edit_window.show()

    def on_edit_window_closed(self):
        self.edit_window = None
        self.load_sales()

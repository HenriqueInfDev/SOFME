# app/item/ui_search_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit,
    QComboBox, QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from decimal import Decimal, InvalidOperation
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from app.item.service import ItemService
from app.utils.ui_utils import show_error_message, configure_table_columns, save_table_columns

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

from app.styles.buttons_styles import (
    button_style, GREEN, BLUE
)
from app.styles.input_styles import (
    input_style, DEFAULTINPUT
)
from app.styles.search_field_style import (
    search_field_style, DEFAULT
)

from app.styles.windows_style import (
    window_style, LIGHT
)
 
class ItemSearchWindow(QWidget):
    # Sinal que emitirá os dados do item selecionado
    item_selected = Signal(dict)
    
    def __init__(self, selection_mode=False, item_type_filter=None):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.item_service = ItemService()
        self.edit_window = None # Para manter referência da janela de edição
        self.selection_mode = selection_mode
        self.item_type_filter = item_type_filter # Lista de tipos de item a exibir
        
        title = "Selecionar Insumo" if selection_mode else "Pesquisa de Produto"
        self.setWindowTitle(title)
        self.setGeometry(150, 150, 800, 600)
        self.setStyleSheet(window_style(LIGHT))

        # Layout Principal
        self.main_layout = QVBoxLayout(self)

        # --- Grupo de Pesquisa ---
        self.create_search_group()

        # --- Grupo de Resultados ---
        self.create_results_group()
        
        # A tela começa vazia e só carrega quando o usuário clicar em Buscar.
        self.table_model.removeRows(0, self.table_model.rowCount())

    def create_search_group(self):
        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout()

        self.search_field_combo = QComboBox()
        self.search_field_combo.setStyleSheet(search_field_style(DEFAULT))
        self.search_field_combo.addItems(["Descrição", "Código Interno", "Tipo", "ID"])
        
        self.search_text = QLineEdit()
        self.search_text.setStyleSheet(input_style(DEFAULTINPUT))
        self.search_text.returnPressed.connect(self.load_items) # Busca ao pressionar Enter

        search_button = QPushButton("Buscar")
        search_button.setStyleSheet(button_style(BLUE))
        search_button.clicked.connect(self.load_items)
        
        new_button = QPushButton("Novo Item")
        new_button.setStyleSheet(button_style(GREEN))
        new_button.clicked.connect(self.open_new_item_window)

        search_layout.addWidget(self.search_field_combo)
        search_layout.addWidget(self.search_text, 1) # O campo de texto se expande
        search_layout.addWidget(search_button)
        search_layout.addWidget(new_button)
        search_group.setLayout(search_layout)
        
        self.main_layout.addWidget(search_group)

    def create_results_group(self):
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()

        self.table_view = QTableView()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["ID", "Descrição", "Código Interno", "Tipo", "Un.", "Quantidade", "Custo Unit."])
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
        self.table_view.doubleClicked.connect(self.handle_double_click)

        results_layout.addWidget(self.table_view)
        results_group.setLayout(results_layout)
        self.main_layout.addWidget(results_group)

    def showEvent(self, event):
        super().showEvent(event)
        configure_table_columns(self.table_view, total_width=self.table_view.viewport().width(), table_name='item_search')

    def closeEvent(self, event):
        save_table_columns(self.table_view, 'item_search')
        super().closeEvent(event)

    def load_items(self):
        """Carrega os itens na tabela, usando o ItemService."""
        search_type_text = self.search_field_combo.currentText()
        search_content = self.search_text.text()
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        if search_content:
            search_type_map = {
                "Descrição": "DESCRICAO",
                "Código Interno": "CODIGO_INTERNO",
                "Tipo": "TIPO_ITEM",
                "ID": "ID"
            }
            search_type = search_type_map.get(search_type_text, "DESCRICAO")
            response = self.item_service.search_items(search_type, search_content)
        else:
            response = self.item_service.get_all_items()

        if not response["success"]:
            show_error_message(self, "Error", response["message"])
            return

        # Aplica o filtro de tipo de item, se existir
        items = response["data"]
        if self.item_type_filter:
            items = [item for item in items if item['TIPO_ITEM'] in self.item_type_filter]
            
        for item in items:
            # Convert sqlite3.Row to dict if needed
            item_dict = dict(item) if hasattr(item, 'keys') else item
            
            id_item = QStandardItem(str(item_dict['ID']))
            id_item.setData(item_dict['ID'], Qt.DisplayRole)

            qty_item = QStandardItem(format_decimal_text(item_dict['SALDO_ESTOQUE']) if item_dict['SALDO_ESTOQUE'] is not None else "")
            cost_item = QStandardItem(format_decimal_text(item_dict['CUSTO_MEDIO']) if item_dict['CUSTO_MEDIO'] is not None else "")

            row = [
                id_item,
                QStandardItem(item_dict['DESCRICAO']),
                QStandardItem(item_dict['CODIGO_INTERNO'] or ""),
                QStandardItem(item_dict['TIPO_ITEM']),
                QStandardItem(item_dict['SIGLA'].upper()),
                qty_item,
                cost_item
            ]
            self.table_model.appendRow(row)

            full_item_data = {
                'ID': item_dict['ID'],
                'DESCRICAO': item_dict['DESCRICAO'],
                'CODIGO_INTERNO': item_dict['CODIGO_INTERNO'],
                'TIPO_ITEM': item_dict['TIPO_ITEM'],
                'SIGLA': item_dict['SIGLA'],
                'SALDO_ESTOQUE': item_dict['SALDO_ESTOQUE'],
                'CUSTO_MEDIO': item_dict['CUSTO_MEDIO']
            }
            self.table_model.item(self.table_model.rowCount() - 1, 0).setData(full_item_data, Qt.UserRole)

    def handle_double_click(self, model_index):
        if self.selection_mode:
            item_data = self.table_model.item(model_index.row(), 0).data(Qt.UserRole)
            self.item_selected.emit(item_data)
            self.close()
        else:
            self.open_edit_item_window(model_index)
            
    def open_new_item_window(self):
        # Passa None para indicar que é um novo item
        self.show_edit_window(item_id=None)

    def open_edit_item_window(self, model_index):
        # Pega o ID do item da tabela e passa para a janela de edição
        item_data = self.table_model.item(model_index.row(), 0).data(Qt.UserRole)
        self.show_edit_window(item_id=item_data['ID'])

    def show_edit_window(self, item_id):
        """Abre a janela de edição, garantindo que apenas uma instância exista e limpando a referência quando fechada."""
        from .ui_form_window import ItemFormWindow

        if self.edit_window is not None:
            if self.edit_window.isVisible():
                self.edit_window.activateWindow()
                self.edit_window.raise_()
                return
            self.edit_window.deleteLater()
            self.edit_window = None

        self.edit_window = ItemFormWindow(item_id=item_id)
        self.edit_window.setAttribute(Qt.WA_DeleteOnClose)
        self.edit_window.destroyed.connect(self.on_edit_window_closed)
        self.edit_window.show()

    def on_edit_window_closed(self):
        """Slot para limpar a referência da janela de edição e recarregar os itens."""
        self.edit_window = None
        self.load_items()

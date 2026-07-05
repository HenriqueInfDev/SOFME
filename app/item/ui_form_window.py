# app/item/ui_form_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QHeaderView, QTabWidget,
    QTableWidget, QTableWidgetItem, QLabel, QDoubleSpinBox, QAbstractItemView, QCheckBox
)
from decimal import Decimal, InvalidOperation
from PySide6.QtCore import Qt, QTimer
from app.item.service import ItemService
from app.production import composition_operations
from app.utils.ui_utils import (
    NumericTableWidgetItem, show_error_message, show_success_message, 
    show_confirmation_message, show_warning_message, show_custom_confirmation,
    center_widget_on_screen
)

from app.styles.buttons_styles import (
    button_style, GREEN, BLUE, RED, GRAY, YELLOW
)

from app.styles.windows_style import (
    window_style, LIGHT
)

from app.styles.search_field_style import (
    search_field_style, DEFAULT
) 

from app.styles.input_styles import (
    input_style, doublespinbox_style, DEFAULTINPUT
)

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

class ItemFormWindow(QWidget):
    def __init__(self, item_id=None, copy_from=None):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.item_service = ItemService()
        self.current_item_id = item_id
        self.has_unsaved_changes = False
        self.copy_from = copy_from

        self.setWindowTitle(f"Editando Item #{item_id}" if item_id else "Novo Item")
        self.setStyleSheet(window_style(LIGHT))
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.resize(700, 600)
        center_widget_on_screen(self)

        # Layout Principal
        self.main_layout = QVBoxLayout(self)

        # --- Cabeçalho com Botões ---
        self.create_header_buttons()

        # --- Sistema de Abas ---
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # --- Aba Principal ---
        self.create_main_tab()

        # --- Aba Composição ---
        self.create_composition_tab()

        # --- Aba Reajuste de Estoque ---
        self.create_stock_adjustment_tab()

        # Carregar dados
        self.populate_units_combobox()
        self.load_item_data()
        if self.copy_from:
            self._apply_copy_data(self.copy_from)
        
        # Conectar sinal da ComboBox de tipo
        self.type_combo.currentTextChanged.connect(self.toggle_composition_tab)
        
        self.search_window = None # Para manter a referência da janela de busca
        self.search_supplier_window = None # Para manter a referência da janela de busca de fornecedor
        self.selected_supplier_id = None # Para armazenar o ID do fornecedor selecionado
        
        # Conectar o botão de busca de fornecedor
        self.search_supplier_button.clicked.connect(self.open_supplier_search)
        self.clear_supplier_button.clicked.connect(self.clear_selected_supplier)
        
        # Conectar sinais para detectar alterações
        self.code_internal_input.textChanged.connect(self._set_unsaved_changes)
        self.description_input.textChanged.connect(self._set_unsaved_changes)
        self.type_combo.currentIndexChanged.connect(self._set_unsaved_changes)
        self.unit_combo.currentIndexChanged.connect(self._set_unsaved_changes)
        self.non_stock_checkbox.toggled.connect(self._set_unsaved_changes)
        # A alteração da composição será tratada nos métodos add/remove

    def _set_unsaved_changes(self):
        """Marca o estado como 'não salvo' e atualiza o título da janela."""
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.setWindowTitle(self.windowTitle().rstrip('*') + "*")

    def closeEvent(self, event):
        """Sobrescreve o evento de fechar a janela para verificar alterações."""
        if self.has_unsaved_changes:
            buttons_config = [
                {'text': 'Salvar', 'role': QMessageBox.AcceptRole, 'style': GREEN, 'result': QMessageBox.Save},
                {'text': 'Descartar', 'role': QMessageBox.DestructiveRole, 'style': RED, 'result': QMessageBox.Discard},
                {'text': 'Cancelar', 'role': QMessageBox.RejectRole, 'style': GRAY, 'result': QMessageBox.Cancel}
            ]
            reply = show_custom_confirmation(
                self,
                'Alterações Não Salvas',
                'Você tem alterações não salvas. Deseja salvá-las antes de sair?',
                buttons_config
            )

            if reply == QMessageBox.Save:
                self.save_item()
                # Se o save_item falhar (por exemplo, validação), não devemos fechar
                if self.has_unsaved_changes: # O save_item reseta o flag se for bem sucedido
                    event.ignore()
                else:
                    event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else: # Cancel
                event.ignore()
        else:
            event.accept()

    def create_header_buttons(self):
        header_layout = QHBoxLayout()
        
        new_button = QPushButton("Novo")
        new_button.setStyleSheet(button_style(GREEN))
        new_button.clicked.connect(self.new_item)
        
        save_button = QPushButton("Salvar")
        save_button.setStyleSheet(button_style(GREEN))
        save_button.clicked.connect(self.save_item)

        copy_button = QPushButton("Copiar Produto")
        copy_button.setStyleSheet(button_style(YELLOW))
        copy_button.clicked.connect(self.copy_item)

        delete_button = QPushButton("Excluir")
        delete_button.setStyleSheet(button_style(RED))
        delete_button.clicked.connect(self.delete_item)
        
        close_button = QPushButton("Fechar")
        close_button.setStyleSheet(button_style(GRAY))
        close_button.clicked.connect(self.close)

        header_layout.addStretch()
        header_layout.addWidget(new_button)
        header_layout.addWidget(save_button)
        header_layout.addWidget(copy_button)
        header_layout.addWidget(delete_button)
        header_layout.addWidget(close_button)
        
        self.main_layout.addLayout(header_layout)

    def create_main_tab(self):
        main_widget = QWidget()
        layout = QFormLayout(main_widget)

        self.code_internal_input = QLineEdit()
        self.code_internal_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.description_input = QLineEdit()
        self.description_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.type_combo = QComboBox()
        self.type_combo.setStyleSheet(search_field_style(DEFAULT))
        self.type_combo.addItems(["Insumo", "Produto", "Ambos"])
        self.unit_combo = QComboBox()
        self.unit_combo.setStyleSheet(search_field_style(DEFAULT))
        self.non_stock_checkbox = QCheckBox("Produto não estocável")
        self.non_stock_checkbox.toggled.connect(self.toggle_stock_adjustment_tab)
        self.non_stock_checkbox.setStyleSheet(
            "QCheckBox { spacing: 8px; padding: 4px 6px; }"
            "QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #000000; border-radius: 3px; background-color: #FFFFFF; }"
            "QCheckBox::indicator:checked { background-color: #2563EB; }"
        )

        # Novo layout para o fornecedor
        supplier_layout = QHBoxLayout()
        self.supplier_display = QLineEdit()
        self.supplier_display.setReadOnly(True)
        self.supplier_display.setPlaceholderText("Selecione um fornecedor")
        self.supplier_display.setStyleSheet(input_style(DEFAULTINPUT))
        self.search_supplier_button = QPushButton("Buscar")
        self.search_supplier_button.setStyleSheet(button_style(BLUE))
        self.clear_supplier_button = QPushButton("Limpar") # Novo botão
        self.clear_supplier_button.setStyleSheet(button_style(RED))
        supplier_layout.addWidget(self.supplier_display)
        supplier_layout.addWidget(self.search_supplier_button)
        supplier_layout.addWidget(self.clear_supplier_button) # Adiciona ao layout

        layout.addRow("Código Interno:", self.code_internal_input)
        layout.addRow("Descrição:", self.description_input)
        layout.addRow("Tipo de Item:", self.type_combo)
        layout.addRow("Unidade:", self.unit_combo)
        layout.addRow("Fornecedor Padrão:", supplier_layout)
        layout.addRow("", self.non_stock_checkbox)

        self.tab_widget.addTab(main_widget, "Principal")

    def create_composition_tab(self):
        self.composition_widget = QWidget()
        layout = QVBoxLayout(self.composition_widget)
        self.selected_material = None # Para armazenar os dados do insumo selecionado

        # --- Formulário de Edição/Adição ---
        edit_group = QGroupBox("Insumo")
        edit_group_layout = QVBoxLayout(edit_group) # Layout principal do grupo

        # Layout horizontal para os campos de entrada
        input_layout = QHBoxLayout()
        
        # Campo de Descrição (Insumo)
        self.material_display = QLineEdit()
        self.material_display.setPlaceholderText("Selecione um insumo...")
        self.material_display.setReadOnly(True)
        self.material_display.setStyleSheet(input_style(DEFAULTINPUT))
        input_layout.addWidget(self.material_display, 6) # Proporção 6

        # Campo de Quantidade
        self.quantity_spinbox = QDoubleSpinBox()
        self.quantity_spinbox.setStyleSheet(doublespinbox_style(DEFAULTINPUT))
        self.quantity_spinbox.setRange(0.0, 99999.99)
        self.quantity_spinbox.setDecimals(4)
        input_layout.addWidget(self.quantity_spinbox, 2) # Proporção 2

        # Label da Unidade
        self.unit_label = QLabel("Un.")
        self.unit_label.setStyleSheet("background-color: transparent")
        self.unit_label.setFixedWidth(40) # Largura fixa para alinhar
        input_layout.addWidget(self.unit_label)

        # Botão de Busca
        search_button = QPushButton("Buscar")
        search_button.setStyleSheet(button_style(BLUE))
        search_button.clicked.connect(self.open_material_search)
        input_layout.addWidget(search_button)
        
        edit_group_layout.addLayout(input_layout)

        # Botão de Adicionar/Atualizar em uma linha separada
        self.add_update_button = QPushButton("Adicionar Insumo")
        self.add_update_button.setStyleSheet(button_style(GREEN))
        self.add_update_button.clicked.connect(self.add_update_composition_item)
        
        # O botão agora ocupa toda a largura
        edit_group_layout.addWidget(self.add_update_button)
        
        layout.addWidget(edit_group)

        # --- Grid de Composição e Botões de Ação ---
        self.composition_table = QTableWidget()
        self.composition_table.setColumnCount(6)
        self.composition_table.setHorizontalHeaderLabels(["ID Insumo", "Descrição", "Qtd", "Un.", "Custo Unit.", "Custo Total"])
        self.composition_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.composition_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.composition_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.composition_table.setColumnHidden(0, True)
        self.composition_table.verticalHeader().setVisible(False)
        self.composition_table.setSortingEnabled(True)
        self.composition_table.setAlternatingRowColors(True)
        layout.addWidget(self.composition_table)

        # --- Barra de Ações da Composição ---
        action_bar_layout = QHBoxLayout()
        self.edit_selected_button = QPushButton("Editar Selecionado")
        self.edit_selected_button.setStyleSheet(button_style(YELLOW))
        self.edit_selected_button.clicked.connect(self.load_selected_for_edit)
        self.remove_selected_button = QPushButton("Remover Selecionado")
        self.remove_selected_button.setStyleSheet(button_style(RED))
        self.remove_selected_button.clicked.connect(self.remove_selected_composition_item)

        action_bar_layout.addStretch()
        action_bar_layout.addWidget(self.edit_selected_button)
        action_bar_layout.addWidget(self.remove_selected_button)
        layout.addLayout(action_bar_layout)

        # --- Custo Total ---
        self.total_cost_label = QLabel("Custo Total da Composição: R$ 0.00")
        layout.addWidget(self.total_cost_label, 0, Qt.AlignRight)

        self.tab_widget.addTab(self.composition_widget, "Composição")

    def showEvent(self, event):
        super().showEvent(event)
        center_widget_on_screen(self)

    def create_stock_adjustment_tab(self):
        self.stock_adjustment_widget = QWidget()
        layout = QVBoxLayout(self.stock_adjustment_widget)
        layout.setSpacing(12)

        self.current_stock_label = QLabel("Estoque atual: --")
        self.current_stock_label.setStyleSheet("font-size: 15px; font-weight: 600;")
        self.current_stock_unit_label = QLabel("Unidade: --")

        form_layout = QHBoxLayout()
        self.new_stock_input = QLineEdit()
        self.new_stock_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.new_stock_input.setPlaceholderText("Novo estoque")
        self.update_stock_button = QPushButton("Atualizar estoque")
        self.update_stock_button.setStyleSheet(button_style(BLUE))
        self.update_stock_button.clicked.connect(self.update_stock_quantity)
        form_layout.addWidget(self.new_stock_input)
        form_layout.addWidget(self.update_stock_button)

        layout.addWidget(self.current_stock_label)
        layout.addWidget(self.current_stock_unit_label)
        layout.addLayout(form_layout)
        layout.addStretch()

        self.tab_widget.addTab(self.stock_adjustment_widget, "Reajuste de estoque")

    def populate_units_combobox(self):
        response = self.item_service.list_units()
        if response["success"]:
            for unit in response["data"]:
                self.unit_combo.addItem(f"{unit['NOME']} ({unit['SIGLA']})", userData=unit['ID'])
        else:
            show_error_message(self, "Error", response["message"])

    def _ensure_mapping(self, item_data):
        if hasattr(item_data, 'keys'):
            return {key: item_data[key] for key in item_data.keys()}
        return dict(item_data or {})

    def _apply_copy_data(self, item_data):
        self.current_item_id = None
        self.setWindowTitle("Novo Item")
        item_data = self._ensure_mapping(item_data)
        self.code_internal_input.setText(item_data.get('CODIGO_INTERNO') or '')
        self.description_input.setText(f"{item_data.get('DESCRICAO') or ''} (Cópia)")
        self.type_combo.setCurrentText(item_data.get('TIPO_ITEM') or 'Insumo')
        self.non_stock_checkbox.setChecked(bool(item_data.get('NAO_ESTOCAVEL')))
        self.selected_supplier_id = item_data.get('ID_FORNECEDOR_PADRAO')
        if self.selected_supplier_id:
            from app.supplier.service import SupplierService
            supplier_service = SupplierService()
            supplier_response = supplier_service.get_supplier_by_id(self.selected_supplier_id)
            if supplier_response['success']:
                supplier = supplier_response['data']
                self.supplier_display.setText(supplier.get('NOME_FANTASIA') or supplier.get('RAZAO_SOCIAL') or '')
        self.composition_table.setRowCount(0)
        self.update_total_cost()
        self.toggle_composition_tab()
        self.toggle_stock_adjustment_tab()
        self._set_unsaved_changes()

    def load_item_data(self):
        if self.current_item_id:
            response = self.item_service.get_item_by_id(self.current_item_id)
            if response["success"]:
                item = self._ensure_mapping(response["data"])
                self.code_internal_input.setText(item.get('CODIGO_INTERNO') or '')
                self.description_input.setText(item.get('DESCRICAO') or '')
                self.type_combo.setCurrentText(item.get('TIPO_ITEM') or 'Insumo')
                self.non_stock_checkbox.setChecked(bool(item.get('NAO_ESTOCAVEL')))
                
                unit_index = self.unit_combo.findData(item.get('ID_UNIDADE'))
                if unit_index != -1:
                    self.unit_combo.setCurrentIndex(unit_index)

                self.selected_supplier_id = item.get('ID_FORNECEDOR_PADRAO')
                self._refresh_stock_adjustment_tab(item)
                if self.selected_supplier_id:
                    from app.supplier.service import SupplierService
                    supplier_service = SupplierService()
                    supplier_response = supplier_service.get_supplier_by_id(self.selected_supplier_id)
                    if supplier_response["success"]:
                        supplier = supplier_response["data"]
                        self.supplier_display.setText(supplier.get('NOME_FANTASIA') or supplier.get('RAZAO_SOCIAL') or '')
                
                self.load_composition_data()
        
        self.toggle_composition_tab()

    def load_composition_data(self):
        self.composition_table.setRowCount(0)
        if self.current_item_id:
            composition = composition_operations.get_bom(self.current_item_id)
            for comp_item in composition:
                self.add_row_to_composition_grid(
                    comp_item['ID_INSUMO'], 
                    comp_item['DESCRICAO'],
                    comp_item['QUANTIDADE'],
                    comp_item['CUSTO_MEDIO'],
                    comp_item['SIGLA']
                )
            self.update_total_cost()

    def toggle_composition_tab(self):
        item_type = self.type_combo.currentText()
        composition_tab_index = self.tab_widget.indexOf(self.composition_widget)
        is_visible = item_type in ("Produto", "Ambos")
        self.tab_widget.setTabVisible(composition_tab_index, is_visible)

    def toggle_stock_adjustment_tab(self):
        stock_tab_index = self.tab_widget.indexOf(self.stock_adjustment_widget)
        is_non_stock = self.non_stock_checkbox.isChecked()
        self.tab_widget.setTabVisible(stock_tab_index, not is_non_stock)

    def _refresh_stock_adjustment_tab(self, item):
        if not hasattr(self, 'current_stock_label'):
            return
        self.current_stock_label.setText(f"Estoque atual: {format_decimal_text(item.get('SALDO_ESTOQUE', 0))}")
        self.current_stock_unit_label.setText(f"Unidade: {item.get('SIGLA', '') or '--'}")

    def update_stock_quantity(self):
        if self.current_item_id is None:
            show_warning_message(self, 'Atenção', 'Salve o item antes de ajustar o estoque.')
            return
        try:
            new_quantity = Decimal(self.new_stock_input.text().replace(',', '.'))
        except Exception:
            show_warning_message(self, 'Atenção', 'Informe uma quantidade válida.')
            return
        response = self.item_service.adjust_stock_quantity(self.current_item_id, float(new_quantity))
        if response['success']:
            show_success_message(self, 'Sucesso', response['message'])
            self.current_stock_label.setText(f"Estoque atual: {format_decimal_text(new_quantity)}")
            self.new_stock_input.clear()
        else:
            show_error_message(self, 'Erro', response['message'])

    def open_material_search(self):
        """Abre a janela de busca de itens em modo de seleção."""
        from .ui_search_window import ItemSearchWindow
        if self.search_window is not None:
            if self.search_window.isVisible():
                self.search_window.activateWindow()
                self.search_window.raise_()
                return
            self.search_window.deleteLater()
            self.search_window = None

        self.search_window = ItemSearchWindow(selection_mode=True, item_type_filter=['Insumo', 'Ambos'])
        self.search_window.setAttribute(Qt.WA_DeleteOnClose)
        self.search_window.item_selected.connect(self.set_selected_material)
        self.search_window.destroyed.connect(lambda: setattr(self, 'search_window', None))
        self.search_window.show()

    def set_selected_material(self, item_data):
        """Recebe o item selecionado da janela de busca e preenche o formulário."""
        self.selected_material = item_data
        self.material_display.setText(item_data['DESCRICAO'])
        self.unit_label.setText(item_data['SIGLA'].upper())
        self.quantity_spinbox.setFocus() # Move o foco para a quantidade

    def add_update_composition_item(self):
        """Adiciona ou atualiza um item na tabela de composição."""
        if not self.selected_material:
            show_warning_message(self, "Atenção", "Nenhum insumo selecionado.")
            return

        quantity = Decimal(str(self.quantity_spinbox.value()))
        if quantity <= 0:
            show_warning_message(self, "Atenção", "A quantidade deve ser maior que zero.")
            return

        material_id = self.selected_material['ID']

        # VALIDAÇÃO: Movida para o módulo de operações
        is_valid, error_message = composition_operations.validate_bom_item(
            self.current_item_id, material_id
        )
        if not is_valid:
            show_warning_message(self, "Erro de Validação", error_message)
            return
            
        # Verifica se o item já está na tabela (para atualização)
        for row in range(self.composition_table.rowCount()):
            if int(self.composition_table.item(row, 0).text()) == material_id:
                # Atualiza a quantidade
                self.composition_table.item(row, 2).setText(format_decimal_text(quantity))
                # Recalcula o custo total da linha
                unit_cost = Decimal(str(self.composition_table.item(row, 4).text().replace(',', '.')))
                total_cost = quantity * unit_cost
                self.composition_table.item(row, 5).setText(format_decimal_text(total_cost))
                self.update_total_cost()
                self._clear_material_form()
                return

        # Se não encontrou, adiciona uma nova linha
        response = self.item_service.get_item_by_id(material_id)
        unit_cost = response["data"]['CUSTO_MEDIO'] if response["success"] else 0
        
        self.add_row_to_composition_grid(
            material_id,
            self.selected_material['DESCRICAO'],
            quantity,
            unit_cost,
            self.selected_material['SIGLA']
        )
        self.update_total_cost()
        self._clear_material_form()
        self._set_unsaved_changes()

    def load_selected_for_edit(self):
        """Carrega um item da tabela de volta no formulário para edição."""
        selected_rows = self.composition_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning_message(self, "Atenção", "Selecione um item na tabela para editar.")
            return
            
        selected_row = selected_rows[0].row()
        
        # Recria o dicionário `selected_material` com os dados da tabela
        self.selected_material = {
            'ID': int(self.composition_table.item(selected_row, 0).text()),
            'DESCRICAO': self.composition_table.item(selected_row, 1).text(),
            'SIGLA': self.composition_table.item(selected_row, 3).text()
        }
        
        # Preenche o formulário
        self.material_display.setText(self.selected_material['DESCRICAO'])
        self.unit_label.setText(self.selected_material['SIGLA'].upper())
        self.quantity_spinbox.setValue(float(self.composition_table.item(selected_row, 2).text()))
        
        self.add_update_button.setText("Atualizar Insumo")

    def remove_selected_composition_item(self):
        """Remove o item selecionado da tabela de composição."""
        selected_rows = self.composition_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning_message(self, "Atenção", "Selecione um item na tabela para remover.")
            return
            
        # Remove em ordem reversa para não bagunçar os índices
        for index in sorted([idx.row() for idx in selected_rows], reverse=True):
            self.composition_table.removeRow(index)
            
        self.update_total_cost()
        self._set_unsaved_changes()

    def _clear_material_form(self):
        """Limpa o formulário de adição/edição de insumo."""
        self.selected_material = None
        self.material_display.clear()
        self.quantity_spinbox.setValue(0.0)
        self.unit_label.clear()
        self.add_update_button.setText("Adicionar")
        self.composition_table.clearSelection()

    def add_row_to_composition_grid(self, material_id, description, quantity, unit_cost, unit):
        row_position = self.composition_table.rowCount()
        self.composition_table.insertRow(row_position)
        
        total_cost = Decimal(str(quantity)) * Decimal(str(unit_cost))
        
        self.composition_table.setItem(row_position, 0, NumericTableWidgetItem(str(material_id)))
        self.composition_table.setItem(row_position, 1, QTableWidgetItem(description))
        self.composition_table.setItem(row_position, 2, NumericTableWidgetItem(format_decimal_text(quantity)))
        self.composition_table.setItem(row_position, 3, QTableWidgetItem(unit.upper()))
        self.composition_table.setItem(row_position, 4, NumericTableWidgetItem(format_decimal_text(unit_cost)))
        self.composition_table.setItem(row_position, 5, NumericTableWidgetItem(format_decimal_text(total_cost)))

    def update_total_cost(self):
        total = Decimal('0')
        for row in range(self.composition_table.rowCount()):
            total += Decimal(str(self.composition_table.item(row, 5).text().replace(',', '.')))
        self.total_cost_label.setText(f"Custo Total da Composição: R$ {format_decimal_text(total)}")

    def open_supplier_search(self):
        """Abre a janela de busca de fornecedores em modo de seleção."""
        from app.supplier.ui_search_window import SupplierSearchWindow
        if self.search_supplier_window is not None:
            if self.search_supplier_window.isVisible():
                self.search_supplier_window.activateWindow()
                self.search_supplier_window.raise_()
                return
            self.search_supplier_window.deleteLater()
            self.search_supplier_window = None

        self.search_supplier_window = SupplierSearchWindow(selection_mode=True)
        self.search_supplier_window.setAttribute(Qt.WA_DeleteOnClose)
        self.search_supplier_window.supplier_selected.connect(self.set_selected_supplier)
        self.search_supplier_window.destroyed.connect(lambda: setattr(self, 'search_supplier_window', None))
        self.search_supplier_window.show()

    def set_selected_supplier(self, supplier_data):
        """Recebe o fornecedor selecionado e atualiza a UI."""
        self.selected_supplier_id = supplier_data['ID']
        self.supplier_display.setText(supplier_data['NOME_FANTASIA'] or supplier_data['RAZAO_SOCIAL'])
        self._set_unsaved_changes()

    def clear_selected_supplier(self):
        """Limpa o fornecedor padrão selecionado."""
        self.selected_supplier_id = None
        self.supplier_display.clear()
        self._set_unsaved_changes()

    def _confirm_unsaved_changes(self, action_message):
        if not self.has_unsaved_changes:
            return True

        buttons_config = [
            {'text': 'Salvar', 'role': QMessageBox.AcceptRole, 'style': GREEN, 'result': QMessageBox.Save},
            {'text': 'Descartar', 'role': QMessageBox.DestructiveRole, 'style': RED, 'result': QMessageBox.Discard},
            {'text': 'Cancelar', 'role': QMessageBox.RejectRole, 'style': GRAY, 'result': QMessageBox.Cancel}
        ]
        reply = show_custom_confirmation(
            self,
            'Alterações Não Salvas',
            action_message,
            buttons_config
        )
        if reply == QMessageBox.Save:
            self.save_item()
            return not self.has_unsaved_changes
        if reply == QMessageBox.Cancel:
            return False
        return True

    def new_item(self):
        if not self._confirm_unsaved_changes('Deseja salvar as alterações antes de criar um novo produto?'):
            return

        self.current_item_id = None
        self.setWindowTitle("Novo Item")
        self.code_internal_input.clear()
        self.description_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.unit_combo.setCurrentIndex(0)
        self.supplier_display.clear()
        self.selected_supplier_id = None
        self.non_stock_checkbox.setChecked(False)
        self.composition_table.setRowCount(0)
        self.update_total_cost()
        self.toggle_composition_tab()
        self.toggle_stock_adjustment_tab()
        self.description_input.setFocus()
        self._clear_material_form()

        self.has_unsaved_changes = False
        self.setWindowTitle("Novo Item")


    def copy_item(self):
        if not self._confirm_unsaved_changes('Deseja salvar as alterações antes de copiar este produto?'):
            return

        if not self.current_item_id:
            show_warning_message(self, 'Atenção', 'Selecione ou salve um produto antes de copiar.')
            return

        response = self.item_service.get_item_by_id(self.current_item_id)
        if not response['success']:
            show_error_message(self, 'Erro', response['message'])
            return

        self.current_item_id = None
        self.has_unsaved_changes = False
        self.setWindowTitle('Novo Item')
        self._apply_copy_data(response['data'])

    def save_item(self):
        # Coleta dados da aba Principal
        codigo_interno = self.code_internal_input.text()
        description = self.description_input.text()
        item_type = self.type_combo.currentText()
        unit_id = self.unit_combo.currentData()
        supplier_id = self.selected_supplier_id

        if not description or unit_id is None:
            show_warning_message(self, "Atenção", "Descrição e Unidade são obrigatórios.")
            return

        # Salva o item principal
        nao_estocavel = self.non_stock_checkbox.isChecked()

        if self.current_item_id is None:  # Novo item
            response = self.item_service.add_item(codigo_interno, description, item_type, unit_id, supplier_id, nao_estocavel)
            if response["success"]:
                self.current_item_id = response["data"]
            else:
                show_error_message(self, "Error", response["message"])
                return
        else:  # Item existente
            response = self.item_service.update_item(self.current_item_id, codigo_interno, description, item_type, unit_id, supplier_id, nao_estocavel)
            if not response["success"]:
                show_error_message(self, "Error", response["message"])
                return

        # Salva a composição se a aba estiver visível
        if self.tab_widget.isTabVisible(self.tab_widget.indexOf(self.composition_widget)):
            new_composition = []
            for row in range(self.composition_table.rowCount()):
                material_id = int(self.composition_table.item(row, 0).text())
                quantity = float(self.composition_table.item(row, 2).text())
                new_composition.append({'id_insumo': material_id, 'quantidade': quantity})
            
            composition_operations.update_composition(self.current_item_id, new_composition)
        
        show_success_message(self, "Sucesso", "Item salvo com sucesso!")
        self.setWindowTitle(f"Editando Item #{self.current_item_id}")
        self.has_unsaved_changes = False

    def delete_item(self):
        """Lida com a exclusão do item atual."""
        if self.current_item_id is None:
            show_warning_message(self, "Atenção", "Nenhum item carregado para excluir.")
            return

        reply = show_confirmation_message(
            self,
            'Confirmar Exclusão',
            f"Você tem certeza que deseja excluir o item #{self.current_item_id}?\nEsta ação não pode ser desfeita."
        )

        if reply == QMessageBox.Yes:
            response = self.item_service.delete_item(self.current_item_id)
            if response["success"]:
                show_success_message(self, "Sucesso", response["message"])
                self.has_unsaved_changes = False # Para evitar o prompt de salvar ao fechar
                self.close()
            else:
                show_error_message(self, "Error", response["message"])

# app/stock/ui_entry_edit_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QHeaderView, QTableWidget, QTableWidgetItem,
    QLabel, QDateEdit, QAbstractItemView, QDateTimeEdit
)
from decimal import Decimal, InvalidOperation
from PySide6.QtCore import QDate, Qt, QDateTime, QEvent, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from app.stock.service import StockService
from app.supplier.service import SupplierService
from app.utils.date_utils import BRAZILIAN_DATE_FORMAT, format_qdate_for_db, format_qdatetime_for_db
from app.item.ui_search_window import ItemSearchWindow
from app.supplier.ui_search_window import SupplierSearchWindow
from app.utils.ui_utils import (
    NumericTableWidgetItem, show_error_message, show_success_message, 
    show_confirmation_message, show_warning_message, configure_table_columns,
    center_widget_on_screen
)
from PySide6.QtWidgets import QStyledItemDelegate

from app.styles.buttons_styles import (
    button_style, GREEN, BLUE, RED, YELLOW
)
from app.styles.windows_style import (
    window_style, LIGHT
)
from app.styles.input_styles import (
    input_style, input_date_style, table_editor_style, DEFAULTINPUT
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

class NumericDelegate(QStyledItemDelegate):
    """Delegate para editar valores numéricos diretamente na tabela."""
    def __init__(self, parent=None, decimals=10):
        super().__init__(parent)
        self.decimals = decimals

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        regex = QRegularExpression(r"^\d{0,12}([.,]\d{0,%d})?$" % self.decimals)
        validator = QRegularExpressionValidator(regex, editor)
        editor.setValidator(validator)
        editor.setStyleSheet(table_editor_style(DEFAULTINPUT))
        editor.setAlignment(Qt.AlignRight)
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)
        if text is None:
            text = ""
        editor.setText(str(text))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class SupplierDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Impede a criação de um editor padrão (como um QLineEdit)
        return None

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.Type.MouseButtonDblClick:
            parent_window = self.parent().parent().parent()
            parent_window.open_supplier_search_for_item(index.row())
            return True
        return super().editorEvent(event, model, option, index)

class EntryEditWindow(QWidget):
    def __init__(self, entry_id=None):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.stock_service = StockService()
        self.supplier_service = SupplierService()
        self.current_entry_id = entry_id
        self.selected_supplier_id = None
        self.search_item_window = None
        self.search_supplier_window = None
        
        title = f"Editando Entrada #{entry_id}" if entry_id else "Nova Entrada de Insumo"
        self.setWindowTitle(title)
        self.setGeometry(250, 250, 800, 700)
        self.setStyleSheet(window_style(LIGHT))
        center_widget_on_screen(self)
        self.setup_ui()

        if self.current_entry_id:
            self.load_entry_data()
        else:
            self.new_entry()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.setStyleSheet(button_style(GREEN))
        self.save_button.clicked.connect(self.save_entry)
        self.finalize_button = QPushButton("Finalizar Entrada")
        self.finalize_button.setStyleSheet(button_style(BLUE))
        self.finalize_button.clicked.connect(self.finalize_entry)
        self.reopen_button = QPushButton("Reabrir Entrada")
        self.reopen_button.setStyleSheet(button_style(YELLOW))
        self.reopen_button.clicked.connect(self.reopen_entry)
        self.reopen_button.setObjectName("reopen_button")
        self.delete_button = QPushButton("Excluir")
        self.delete_button.setStyleSheet(button_style(RED))
        self.delete_button.clicked.connect(self.delete_entry)
        self.delete_button.setObjectName("delete_button")
        header_layout.addStretch()
        header_layout.addWidget(self.delete_button)
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.finalize_button)
        header_layout.addWidget(self.reopen_button)
        self.main_layout.addLayout(header_layout)

        form_group = QGroupBox("Dados da Nota de Entrada")
        form = QFormLayout()
        self.entry_id_display = QLabel("(Nova)")
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setStyleSheet(input_date_style(DEFAULTINPUT))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat(BRAZILIAN_DATE_FORMAT)
        self.date_input.setDate(QDate.currentDate())
        self.typing_date_input = QDateTimeEdit()
        self.typing_date_input.setStyleSheet(input_date_style(DEFAULTINPUT))
        self.typing_date_input.setCalendarPopup(True)
        self.typing_date_input.setDisplayFormat(BRAZILIAN_DATE_FORMAT + " HH:mm:ss")
        self.typing_date_input.setDateTime(QDateTime.currentDateTime())
        self.typing_date_input.setCalendarPopup(True)
        
        self.note_number_input = QLineEdit()
        self.note_number_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.observacao_input = QLineEdit()
        self.observacao_input.setStyleSheet(input_style(DEFAULTINPUT))
        self.status_display = QLabel("Em Aberto")

        form.addRow("ID da Entrada:", self.entry_id_display)
        form.addRow("Data da Entrada:", self.date_input)
        form.addRow("Data de Digitação:", self.typing_date_input)
        form.addRow("Número da Nota:", self.note_number_input)
        form.addRow("Observação:", self.observacao_input)
        form.addRow("Status:", self.status_display)
        form_group.setLayout(form)
        self.main_layout.addWidget(form_group)

        items_group = QGroupBox("Insumos da Nota")
        items_layout = QVBoxLayout()
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels(["ID Insumo", "Descrição", "Fornecedor", "Quantidade", "Un.", "Valor Unit.", "Valor Total"])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.items_table.setColumnHidden(0, True)
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)

        self.supplier_delegate = SupplierDelegate(self.items_table)
        self.items_table.setItemDelegateForColumn(2, self.supplier_delegate)
        
        # Usar delegate numérico para as colunas editáveis de quantidade e valores
        self.numeric_delegate = NumericDelegate(self.items_table)
        self.items_table.setItemDelegateForColumn(3, self.numeric_delegate)  # Quantidade
        self.items_table.setItemDelegateForColumn(5, self.numeric_delegate)  # Valor Unit.
        self.items_table.setItemDelegateForColumn(6, self.numeric_delegate)  # Valor Total
        
        self.items_table.cellChanged.connect(self.on_cell_changed)
        items_layout.addWidget(self.items_table)

        buttons_layout = QHBoxLayout()
        self.total_label = QLabel("Valor Total da Nota: R$ 0.00")
        buttons_layout.addWidget(self.total_label)
        buttons_layout.addStretch()
        self.add_item_button = QPushButton("Adicionar Insumo")
        self.add_item_button.setStyleSheet(button_style(GREEN))
        self.add_item_button.setObjectName("add_item_button")
        self.add_item_button.clicked.connect(self.open_item_search)
        self.remove_item_button = QPushButton("Remover Insumo")
        self.remove_item_button.setStyleSheet(button_style(RED))
        self.remove_item_button.setObjectName("remove_item_button")
        self.remove_item_button.clicked.connect(self.remove_item)
        buttons_layout.addWidget(self.add_item_button)
        buttons_layout.addWidget(self.remove_item_button)
        items_layout.addLayout(buttons_layout)
        
        items_group.setLayout(items_layout)
        self.main_layout.addWidget(items_group)

    def showEvent(self, event):
        super().showEvent(event)
        center_widget_on_screen(self)

    def new_entry(self):
        self.current_entry_id = None
        self.setWindowTitle("Nova Entrada de Insumo")
        self.entry_id_display.setText("(Nova)")
        self.date_input.setDate(QDate.currentDate())
        self.typing_date_input.setDateTime(QDateTime.currentDateTime())
        self.note_number_input.clear()
        self.observacao_input.clear()
        self.status_display.setText("Em Aberto")
        self.items_table.setRowCount(0)
        self.set_read_only(False)

    def save_entry(self):
        entry_date = format_qdate_for_db(self.date_input.date())
        typing_date = format_qdatetime_for_db(self.typing_date_input.dateTime())
        note_number = self.note_number_input.text()
        observacao = self.observacao_input.text()

        items = []
        for row in range(self.items_table.rowCount()):
            supplier_id = self.items_table.item(row, 2).data(Qt.UserRole)
            items.append({
                'id_insumo': int(self.items_table.item(row, 0).text()),
                'id_fornecedor': supplier_id,
                'quantidade': float(self.items_table.item(row, 3).text().replace(',', '.')),
                'valor_unitario': float(self.items_table.item(row, 5).text().replace(',', '.'))
            })

        if self.current_entry_id:
            response = self.stock_service.update_entry(self.current_entry_id, entry_date, typing_date, note_number, observacao, items)
            if response["success"]:
                show_success_message(self, "Sucesso", response["message"])
            else:
                show_error_message(self, "Error", response["message"])
        else:
            # Primeiro, cria a entrada mestre para obter um ID
            create_response = self.stock_service.create_entry(entry_date, typing_date, note_number, observacao)
            if create_response["success"]:
                self.current_entry_id = create_response["data"]
                
                # Agora, chama o update para salvar os itens e o valor total
                update_response = self.stock_service.update_entry(self.current_entry_id, entry_date, typing_date, note_number, observacao, items)
                if update_response["success"]:
                    self.setWindowTitle(f"Editando Entrada #{self.current_entry_id}")
                    self.entry_id_display.setText(str(self.current_entry_id))
                    show_success_message(self, "Sucesso", "Nota de entrada criada e salva com sucesso.")
                else:
                    # Se o update falhar, informa o utilizador. O cabeçalho foi criado.
                    show_error_message(self, "Aviso", f"O cabeçalho da nota foi criado (ID: {self.current_entry_id}), mas falhou ao salvar os itens: {update_response['message']}")
            else:
                show_error_message(self, "Error", create_response["message"])

    def load_entry_data(self):
        response = self.stock_service.get_entry_details(self.current_entry_id)
        if not response["success"]:
            show_error_message(self, "Error", response["message"])
            self.close()
            return

        details = response["data"]
        master = details['master']
        self.entry_id_display.setText(str(master['ID']))
        self.date_input.setDate(QDate.fromString(master['DATA_ENTRADA'], "yyyy-MM-dd"))
        self.typing_date_input.setDateTime(QDateTime.fromString(master['DATA_DIGITACAO'], "yyyy-MM-dd HH:mm:ss"))
        
        self.note_number_input.setText(master['NUMERO_NOTA'] if 'NUMERO_NOTA' in master else '')
        self.observacao_input.setText(master['OBSERVACAO'] if 'OBSERVACAO' in master else '')
        self.status_display.setText(master['STATUS'] if 'STATUS' in master else '')
        
        self.items_table.setRowCount(0)
        for item in details['items']:
            self.add_item_to_table(item, is_loading=True)
        
        is_finalizada = master['STATUS'] == 'Finalizada'
        self.set_read_only(is_finalizada)
        # Adjust table columns to fit content
        self.adjust_table_columns()

    def open_supplier_search_for_item(self, row):
        self.current_editing_row = row
        if self.search_supplier_window is None:
            self.search_supplier_window = SupplierSearchWindow(selection_mode=True)
            self.search_supplier_window.supplier_selected.connect(self.set_selected_supplier_for_item)
            self.search_supplier_window.destroyed.connect(lambda: setattr(self, 'search_supplier_window', None))
            self.search_supplier_window.show()
        else:
            self.search_supplier_window.activateWindow()
            self.search_supplier_window.raise_()

    def set_selected_supplier_for_item(self, supplier_data):
        item = self.items_table.item(self.current_editing_row, 2)
        item.setText(supplier_data['NOME_FANTASIA'] or supplier_data['RAZAO_SOCIAL'])
        item.setData(Qt.UserRole, supplier_data['ID'])
        self.search_supplier_window.close()

    def open_item_search(self):
        if self.search_item_window is None:
            self.search_item_window = ItemSearchWindow(selection_mode=True, item_type_filter=['Insumo', 'Ambos'])
            self.search_item_window.item_selected.connect(self.add_item_from_search)
            self.search_item_window.destroyed.connect(lambda: setattr(self, 'search_item_window', None))
            self.search_item_window.show()
        else:
            self.search_item_window.activateWindow()
            self.search_item_window.raise_()

    def add_item_from_search(self, item_data):
        for row in range(self.items_table.rowCount()):
            if int(self.items_table.item(row, 0).text()) == item_data['ID']:
                show_warning_message(self, "Atenção", "Este insumo já está na lista.")
                return

        item_details = self.stock_service.get_item_details(item_data['ID'])
        if not item_details["success"]:
            show_error_message(self, "Erro", item_details["message"])
            return
        
        item = item_details["data"]
        if bool(item.get('NAO_ESTOCAVEL')):
            show_warning_message(self, 'Atenção', f"O item '{item['DESCRICAO']}' está marcado como não estocável. Não é possivel dar entrada nele.")
            return
        
        item_to_add = { 
            'ID_INSUMO': item['ID'], 
            'DESCRICAO': item['DESCRICAO'], 
            'SIGLA': item['SIGLA'],
            'ID_FORNECEDOR': item['ID_FORNECEDOR_PADRAO'],
            'FORNECEDOR': item['NOME_FANTASIA_PADRAO'],
            'QUANTIDADE': 1.0, 
            'VALOR_UNITARIO': 0.0 
        }
        self.add_item_to_table(item_to_add)

        if not item_to_add['ID_FORNECEDOR']:
            show_success_message(self, "Atenção", f"O insumo '{item_to_add['DESCRICAO']}' não possui um fornecedor padrão. Por favor, selecione um manualmente.")

    def add_item_to_table(self, item, is_loading=False):
        self.items_table.blockSignals(True)
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        id_item = QTableWidgetItem(str(item['ID_INSUMO']))
        self.items_table.setItem(row, 0, id_item)
        
        desc_item = QTableWidgetItem(item['DESCRICAO'])
        self.items_table.setItem(row, 1, desc_item)

        supplier_item = QTableWidgetItem(item['FORNECEDOR'] if 'FORNECEDOR' in item and item['FORNECEDOR'] else '')
        supplier_item.setData(Qt.UserRole, item['ID_FORNECEDOR'] if 'ID_FORNECEDOR' in item else None)
        self.items_table.setItem(row, 2, supplier_item)

        self.items_table.setItem(row, 3, NumericTableWidgetItem(format_decimal_text(item['QUANTIDADE'])))

        unit_item = QTableWidgetItem(item['SIGLA'].upper())
        self.items_table.setItem(row, 4, unit_item)

        self.items_table.setItem(row, 5, NumericTableWidgetItem(format_decimal_text(item['VALOR_UNITARIO'])))
        total = Decimal(str(item['QUANTIDADE'])) * Decimal(str(item['VALOR_UNITARIO']))
        self.items_table.setItem(row, 6, NumericTableWidgetItem(format_decimal_text(total)))

        # Colunas não editáveis
        for col in [0, 1, 4]: # ID, Descrição, Un.
            if self.items_table.item(row, col):
                 self.items_table.item(row, col).setFlags(self.items_table.item(row, col).flags() & ~Qt.ItemIsEditable)
        
        self.items_table.blockSignals(False)
        self.update_total_value()

    def remove_item(self):
        rows = self.items_table.selectionModel().selectedRows()
        if not rows:
            show_warning_message(self, "Atenção", "Selecione um insumo para remover.")
            return
        for index in sorted([r.row() for r in rows], reverse=True):
            self.items_table.removeRow(index)
        self.update_total_value()

    def update_total_value(self):
        total = 0.0
        for row in range(self.items_table.rowCount()):
            total_item = self.items_table.item(row, 6)
            if total_item and total_item.text():
                try:
                    total += float(total_item.text().replace(',', '.'))
                except ValueError:
                    pass  # Ignora valores que não podem ser convertidos para float
        self.total_label.setText(f"Valor Total da Nota: R$ {total:.2f}")

    def on_cell_changed(self, row, column):
        # Quantidade(3), Valor Unit.(5), Valor Total(6)
        if column not in [3, 5, 6]:
            return
        
        qty_item = self.items_table.item(row, 3)
        unit_price_item = self.items_table.item(row, 5)
        total_price_item = self.items_table.item(row, 6)

        if not all([qty_item, unit_price_item, total_price_item]):
            return

        self.items_table.blockSignals(True)
        try:
            qty = Decimal(str(qty_item.text().replace(',', '.'))) if qty_item and qty_item.text() else Decimal('0')
            unit_price = Decimal(str(unit_price_item.text().replace(',', '.'))) if unit_price_item and unit_price_item.text() else Decimal('0')
            
            if column == 3 or column == 5: # Quantidade ou Valor Unitário
                new_total = qty * unit_price
                total_price_item.setText(format_decimal_text(new_total))
            elif column == 6: # Valor Total
                total_price = Decimal(str(total_price_item.text().replace(',', '.'))) if total_price_item and total_price_item.text() else Decimal('0')
                if qty != 0:
                    new_unit_price = total_price / qty
                    unit_price_item.setText(format_decimal_text(new_unit_price))
                else:
                    unit_price_item.setText("0.00")
        except (ValueError, TypeError, ZeroDivisionError) as e:
            print(f"Error in on_cell_changed: {e}")
        finally:
            self.items_table.blockSignals(False)
        
        self.update_total_value()

    def set_read_only(self, read_only):
        self.date_input.setReadOnly(read_only)
        self.typing_date_input.setReadOnly(read_only)

        self.note_number_input.setReadOnly(read_only)
        self.items_table.setEditTriggers(QAbstractItemView.NoEditTriggers if read_only else QAbstractItemView.AllEditTriggers)
        # Controla a visibilidade dos botões baseado no status
        self.save_button.setVisible(not read_only)
        self.finalize_button.setVisible(not read_only)
        self.add_item_button.setVisible(not read_only)
        self.remove_item_button.setVisible(not read_only)
        self.reopen_button.setVisible(read_only)
        # O botão de excluir só aparece se a nota não for nova e estiver aberta
        self.delete_button.setVisible(not read_only and self.current_entry_id is not None)

    def delete_entry(self):
        if not self.current_entry_id:
            return

        reply = show_confirmation_message(
            self, "Confirmar Exclusão", 
            "Você tem certeza que deseja excluir esta nota de entrada?\n\n"
            "Esta ação não pode ser desfeita."
        )

        if reply == QMessageBox.Yes:
            response = self.stock_service.delete_entry(self.current_entry_id)
            if response["success"]:
                show_success_message(self, "Sucesso", response["message"])
                self.close()  # Fecha a janela de edição após a exclusão
            else:
                show_error_message(self, "Erro", response["message"])

    def reopen_entry(self):
        if not self.current_entry_id:
            return

        reply = show_confirmation_message(
            self, "Confirmar Reabertura", 
            "Você tem certeza que deseja reabrir esta entrada?\n\n"
            "Esta ação irá estornar o lançamento de estoque e recalcular o custo médio dos insumos.\n"
            "A nota voltará ao status 'Em Aberto' para edição."
        )

        if reply == QMessageBox.Yes:
            response = self.stock_service.reopen_entry(self.current_entry_id)
            if response["success"]:
                show_success_message(self, "Sucesso", response["message"])
                self.load_entry_data()  # Recarrega os dados para refletir o novo status
            else:
                show_error_message(self, "Erro", response["message"])
        
    def finalize_entry(self):

        if self.items_table.rowCount() == 0:
            show_error_message(self, "Erro de Validação", "Adicione pelo menos um insumo à nota antes de finalizar.")
            return

        if not self.current_entry_id:
            show_error_message(self, "Ação Necessária", "É necessário SALVAR a nota antes de finalizá-la.\n\nClique no botão 'Salvar' para que um ID seja gerado para a nota.")
            return

        # Validações dos itens
        for row in range(self.items_table.rowCount()):
            supplier_id = self.items_table.item(row, 2).data(Qt.UserRole)
            if not supplier_id:
                show_error_message(self, "Erro de Validação", f"O item '{self.items_table.item(row, 1).text()}' não possui um fornecedor definido.")
                return

            quantity = float(self.items_table.item(row, 3).text().replace(',', '.'))
            if quantity <= 0:
                show_error_message(self, "Erro de Validação", f"A quantidade do item '{self.items_table.item(row, 1).text()}' deve ser maior que zero.")
                return

            unit_price = float(self.items_table.item(row, 5).text().replace(',', '.'))
            if unit_price <= 0:
                show_error_message(self, "Erro de Validação", f"O valor unitário do item '{self.items_table.item(row, 1).text()}' deve ser maior que zero.")
                return
            
        reply = show_confirmation_message(
            self, "Confirmar Finalização", "Você tem certeza que deseja finalizar esta entrada?\nEsta ação atualizará o estoque e o custo dos insumos e não poderá ser desfeita."
        )
        
        if reply == QMessageBox.Yes:
            self.save_entry() 
            response = self.stock_service.finalize_entry(self.current_entry_id)
            if response["success"]:
                show_success_message(self, "Sucesso", response["message"])
                self.load_entry_data()
            else:
                show_error_message(self, "Error", response["message"])
    
    def adjust_table_columns(self):
        """Ajusta as larguras das colunas da tabela de itens."""
        if self.items_table.model() is None:
            return
        configure_table_columns(self.items_table, total_width=self.items_table.viewport().width())
    
    def showEvent(self, event):
        """Ajusta colunas quando a janela é exibida."""
        super().showEvent(event)
        self.adjust_table_columns()
    
    def resizeEvent(self, event):
        """Reajusta colunas quando a janela é redimensionada."""
        super().resizeEvent(event)
        self.adjust_table_columns()

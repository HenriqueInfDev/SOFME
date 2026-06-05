
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QDateEdit
from app.database.db import get_db_manager
from app.reports.export import export_to_pdf, export_to_excel
from app.utils.ui_utils import CalendarTextField, format_decimal_text, get_required_date_value, get_save_filename, show_success_message

from app.styles.buttons_styles import (
    button_style, BLUE, GREEN
)
from app.styles.windows_style import (
    window_style, LIGHT
)
from app.styles.input_styles import (
    input_style, DEFAULTINPUT
)

class StockReportWindow(QWidget):
    def __init__(self, report_type):
        super().__init__()
        self.report_type = report_type
        self.setWindowTitle(f"Relatório de {report_type}")
        self.setStyleSheet(window_style(LIGHT))
        self.layout = QVBoxLayout(self)
        self.setup_filters()
        self.setup_buttons()
        self.apply_styles_to_filters()

    def setup_filters(self):
        self.filters_layout = QFormLayout()
        self.filters = {}

        if self.report_type == "Entradas (Compras)":
            self.filters["numero_de"] = QLineEdit()
            self.filters["numero_ate"] = QLineEdit()
            self.filters["fornecedor"] = QLineEdit()
            self.filters["data_inicial"] = CalendarTextField()
            self.filters["data_final"] = CalendarTextField()
            self.filters_layout.addRow("Número (de):", self.filters["numero_de"])
            self.filters_layout.addRow("Número (até):", self.filters["numero_ate"])
            self.filters_layout.addRow("Fornecedor:", self.filters["fornecedor"])
            self.filters_layout.addRow("Data Inicial:", self.filters["data_inicial"])
            self.filters_layout.addRow("Data Final:", self.filters["data_final"])
        elif self.report_type == "Movimentação de Estoque":
            self.filters["item_de"] = QLineEdit()
            self.filters["item_ate"] = QLineEdit()
            self.filters["periodo_de"] = CalendarTextField()
            self.filters["periodo_ate"] = CalendarTextField()
            self.filters_layout.addRow("Item (de):", self.filters["item_de"])
            self.filters_layout.addRow("Item (até):", self.filters["item_ate"])
            self.filters_layout.addRow("Período (de):", self.filters["periodo_de"])
            self.filters_layout.addRow("Período (até):", self.filters["periodo_ate"])
        elif self.report_type == "Estoque Atual":
            pass # No filters for this report
        elif self.report_type == "Estoque Baixo":
            pass # No filters for this report
        elif self.report_type == "Curva ABC de Estoque":
            pass # No filters for this report
        elif self.report_type == "Itens Sem Giro":
            self.filters["dias"] = QLineEdit()
            self.filters["dias"].setPlaceholderText("Dias (padrão 30)")
            self.filters_layout.addRow("Inativo há (dias):", self.filters["dias"])
        elif self.report_type == "Itens da Nota de Entrada":
            self.filters["nota_de"] = QLineEdit()
            self.filters["nota_ate"] = QLineEdit()
            self.filters_layout.addRow("Nota (de):", self.filters["nota_de"])
            self.filters_layout.addRow("Nota (até):", self.filters["nota_ate"])

        self.layout.addLayout(self.filters_layout)

    def setup_buttons(self):
        self.generate_button = QPushButton("Gerar Relatório")
        self.generate_button.setStyleSheet(button_style(BLUE))
        self.generate_button.clicked.connect(self.generate_report)
        self.layout.addWidget(self.generate_button)

    def apply_styles_to_filters(self):
        for widget in self.filters.values():
            if isinstance(widget, CalendarTextField):
                widget.line_edit.setStyleSheet(input_style(DEFAULTINPUT))
                widget.button.setStyleSheet("border:none; background: transparent;")
            elif isinstance(widget, (QLineEdit, QDateEdit)):
                widget.setStyleSheet(input_style(DEFAULTINPUT))

    def generate_report(self):
        if self.report_type == "Entradas (Compras)":
            headers, data = self.generate_input_supplies_report()
        elif self.report_type == "Movimentação de Estoque":
            headers, data = self.generate_stock_movement_report()
        elif self.report_type == "Estoque Atual":
            headers, data = self.generate_current_stock_report()
        elif self.report_type == "Estoque Baixo":
            headers, data = self.generate_low_stock_report()
        elif self.report_type == "Curva ABC de Estoque":
            headers, data = self.generate_abc_curve_report()
        elif self.report_type == "Itens Sem Giro":
            headers, data = self.generate_inactive_items_report()
        elif self.report_type == "Itens da Nota de Entrada":
            headers, data = self.generate_entry_items_report()
        else:
            headers, data = [], []

        if data:
            self.show_preview(headers, data)
        else:
            show_success_message(self, "Relatório", "Nenhum dado encontrado para os filtros selecionados.")

    def show_preview(self, headers, data):
        dialog = QDialog(self)
        dialog.setWindowTitle("Pré-visualização do Relatório")
        dialog.setStyleSheet(window_style(LIGHT))
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(item)))
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        
        save_button = QPushButton("Salvar")
        save_button.setStyleSheet(button_style(GREEN))
        save_button.clicked.connect(lambda: self.save_report(headers, data))
        layout.addWidget(save_button)
        
        dialog.exec()

    def save_report(self, headers, data):
        filename, selected_filter = get_save_filename(self, "Salvar Relatório", "PDF (*.pdf);;Excel (*.xlsx)")
        
        if filename:
            if "pdf" in selected_filter:
                export_to_pdf(filename, data, headers)
            elif "xlsx" in selected_filter:
                export_to_excel(filename, data, headers)

    def generate_input_supplies_report(self):
        filters = {
            "numero_de": self.filters["numero_de"].text(),
            "numero_ate": self.filters["numero_ate"].text(),
            "fornecedor": self.filters["fornecedor"].text(),
            "data_inicial": get_required_date_value(self.filters["data_inicial"]),
            "data_final": get_required_date_value(self.filters["data_final"]),
        }
        
        db_manager = get_db_manager()
        entries = db_manager.get_stock_entries(filters)
        
        headers = ["Número", "Fornecedor", "Data", "Total"]
        data = [[e["numero"], e["fornecedor"], e["data"], format_decimal_text(e["total"]) ] for e in entries]
        
        return headers, data

    def generate_stock_movement_report(self):
        filters = {
            "item_de": self.filters["item_de"].text(),
            "item_ate": self.filters["item_ate"].text(),
            "periodo_de": get_required_date_value(self.filters["periodo_de"]),
            "periodo_ate": get_required_date_value(self.filters["periodo_ate"]),
        }
        
        db_manager = get_db_manager()
        movements = db_manager.get_stock_movements(filters)
        
        headers = ["Item", "Tipo de Movimento", "Quantidade", "Valor Unitário", "Data"]
        data = [[m["item"], m["tipo_movimento"], format_decimal_text(m["quantidade"]), format_decimal_text(m["valor_unitario"]), m["data_movimento"]] for m in movements]
        
        return headers, data

    def generate_current_stock_report(self):
        db_manager = get_db_manager()
        stock = db_manager.get_current_stock()
        
        headers = ["Item", "Saldo em Estoque", "Custo Médio"]
        data = [[s["DESCRICAO"], format_decimal_text(s["SALDO_ESTOQUE"]), f"R$ {format_decimal_text(s["CUSTO_MEDIO"])}"] for s in stock]
        
        return headers, data

    def generate_entry_items_report(self):
        filters = {
            "nota_de": self.filters["nota_de"].text(),
            "nota_ate": self.filters["nota_ate"].text(),
        }
        
        db_manager = get_db_manager()
        entry_items_data = db_manager.get_entry_items_report(filters)
        
        headers = ["Nota", "Insumo", "Quantidade", "Valor Unitário", "Valor Total"]
        data = [[i["nota"], i["insumo"], format_decimal_text(i["quantidade"]), format_decimal_text(i["valor_unitario"]), format_decimal_text(i["valor_total"]) ] for i in entry_items_data]
        
        return headers, data

    def generate_low_stock_report(self):
        db_manager = get_db_manager()
        stock = db_manager.get_low_stock_report()
        
        headers = ["Item", "Saldo em Estoque", "Custo Médio"]
        data = [[s["DESCRICAO"], format_decimal_text(s["SALDO_ESTOQUE"]), f"R$ {format_decimal_text(s['CUSTO_MEDIO'])}"] for s in stock]
        
        return headers, data

    def generate_abc_curve_report(self):
        db_manager = get_db_manager()
        stock = db_manager.get_abc_curve_report()
        
        headers = ["Item", "Saldo", "Custo Médio", "Valor Total"]
        data = [[s["DESCRICAO"], format_decimal_text(s["SALDO_ESTOQUE"]), f"R$ {format_decimal_text(s['CUSTO_MEDIO'])}", f"R$ {format_decimal_text(s['valor_total'])}"] for s in stock]
        
        return headers, data

    def generate_inactive_items_report(self):
        dias = self.filters["dias"].text()
        dias = int(dias) if dias.isdigit() else 30
        
        db_manager = get_db_manager()
        items = db_manager.get_inactive_items_report(dias)
        
        headers = ["Item", "Saldo em Estoque", "Última Movimentação"]
        data = [[i["DESCRICAO"], i["SALDO_ESTOQUE"], i["ultima_movimentacao"] or "Nenhuma"] for i in items]
        
        return headers, data

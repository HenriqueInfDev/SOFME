
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

class FinancialReportWindow(QWidget):
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

        if self.report_type == "Lucro por Produto":
            self.filters["produto_de"] = QLineEdit()
            self.filters["produto_ate"] = QLineEdit()
            self.filters["periodo_de"] = CalendarTextField()
            self.filters["periodo_ate"] = CalendarTextField()
            self.filters_layout.addRow("Produto (de):", self.filters["produto_de"])
            self.filters_layout.addRow("Produto (até):", self.filters["produto_ate"])
            self.filters_layout.addRow("Período (de):", self.filters["periodo_de"])
            self.filters_layout.addRow("Período (até):", self.filters["periodo_ate"])
        elif self.report_type == "Lucro por Período":
            self.filters["data_inicial"] = CalendarTextField()
            self.filters["data_final"] = CalendarTextField()
            self.filters_layout.addRow("Data Inicial:", self.filters["data_inicial"])
            self.filters_layout.addRow("Data Final:", self.filters["data_final"])
        elif self.report_type == "Custo do Produto":
            self.filters["produto_de"] = QLineEdit()
            self.filters["produto_ate"] = QLineEdit()
            self.filters_layout.addRow("Produto (de):", self.filters["produto_de"])
            self.filters_layout.addRow("Produto (até):", self.filters["produto_ate"])

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
        if self.report_type == "Lucro por Produto":
            headers, data = self.generate_profit_by_product_report()
        elif self.report_type == "Lucro por Período":
            headers, data = self.generate_profit_by_period_report()
        elif self.report_type == "Custo do Produto":
            headers, data = self.generate_product_cost_report()
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

    def generate_profit_by_product_report(self):
        filters = {
            "produto_de": self.filters["produto_de"].text(),
            "produto_ate": self.filters["produto_ate"].text(),
            "periodo_de": get_required_date_value(self.filters["periodo_de"]),
            "periodo_ate": get_required_date_value(self.filters["periodo_ate"]),
        }
        
        db_manager = get_db_manager()
        profit_data = db_manager.get_profit_by_product(filters)
        
        headers = ["Produto", "Custo Unit.", "Preço Venda", "Qtd Vendida", "Lucro Unit.", "Lucro Total"]
        data = [
            [
                d["produto"],
                f"R$ {format_decimal_text(d['custo_unitario'])}",
                f"R$ {format_decimal_text(d['preco_venda'])}",
                format_decimal_text(d['quantidade_vendida']),
                f"R$ {format_decimal_text(d['lucro_unitario'])}",
                f"R$ {format_decimal_text(d['lucro_total'])}",
            ]
            for d in profit_data
        ]
        
        return headers, data
        
    def generate_product_cost_report(self):
        filters = {
            "produto_de": self.filters["produto_de"].text(),
            "produto_ate": self.filters["produto_ate"].text(),
        }
        
        db_manager = get_db_manager()
        cost_data = db_manager.get_product_cost_report(filters)
        
        headers = ["Produto", "Custo Médio"]
        data = [[c["produto"], format_decimal_text(c["custo_medio"])] for c in cost_data]
        
        return headers, data

    def generate_profit_by_period_report(self):
        filters = {
            "data_inicial": get_required_date_value(self.filters["data_inicial"]),
            "data_final": get_required_date_value(self.filters["data_final"]),
        }
        
        db_manager = get_db_manager()
        profit_data = db_manager.get_profit_by_period(filters)
        
        headers = ["Total de Vendas", "Custo Total", "Lucro Final"]
        data = []
        if profit_data and profit_data["total_vendas"] is not None:
            data.append([
                f"R$ {format_decimal_text(profit_data['total_vendas'])}",
                f"R$ {format_decimal_text(profit_data['custo_total'])}",
                f"R$ {format_decimal_text(profit_data['lucro_final'])}",
            ])
        
        return headers, data

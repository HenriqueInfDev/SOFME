
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

class ProductionReportWindow(QWidget):
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

        if self.report_type == "Ordens de Produção":
            self.filters["id_de"] = QLineEdit()
            self.filters["id_ate"] = QLineEdit()
            self.filters["produto_de"] = QLineEdit()
            self.filters["produto_ate"] = QLineEdit()
            self.filters["status"] = QLineEdit()
            self.filters["periodo_de"] = CalendarTextField()
            self.filters["periodo_ate"] = CalendarTextField()
            self.filters_layout.addRow("ID (de):", self.filters["id_de"])
            self.filters_layout.addRow("ID (até):", self.filters["id_ate"])
            self.filters_layout.addRow("Produto (de):", self.filters["produto_de"])
            self.filters_layout.addRow("Produto (até):", self.filters["produto_ate"])
            self.filters_layout.addRow("Status:", self.filters["status"])
            self.filters_layout.addRow("Período (de):", self.filters["periodo_de"])
            self.filters_layout.addRow("Período (até):", self.filters["periodo_ate"])
        elif self.report_type == "Produção por Linha":
            self.filters["linha_de"] = QLineEdit()
            self.filters["linha_ate"] = QLineEdit()
            self.filters["periodo_de"] = CalendarTextField()
            self.filters["periodo_ate"] = CalendarTextField()
            self.filters_layout.addRow("Linha (de):", self.filters["linha_de"])
            self.filters_layout.addRow("Linha (até):", self.filters["linha_ate"])
            self.filters_layout.addRow("Período (de):", self.filters["periodo_de"])
            self.filters_layout.addRow("Período (até):", self.filters["periodo_ate"])
        elif self.report_type == "Produção por Período":
            self.filters["periodo_de"] = CalendarTextField()
            self.filters["periodo_ate"] = CalendarTextField()
            self.filters_layout.addRow("Período (de):", self.filters["periodo_de"])
            self.filters_layout.addRow("Período (até):", self.filters["periodo_ate"])
        elif self.report_type == "Composição / Estrutura de Produto":
            self.filters["produto_de"] = QLineEdit()
            self.filters["produto_ate"] = QLineEdit()
            self.filters_layout.addRow("Produto (de):", self.filters["produto_de"])
            self.filters_layout.addRow("Produto (até):", self.filters["produto_ate"])
        elif self.report_type == "Rendimento de OP":
            pass # No filters for now
        elif self.report_type == "Necessidade de Insumos":
            pass # No filters for now

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
        if self.report_type == "Ordens de Produção":
            headers, data = self.generate_production_orders_report()
        elif self.report_type == "Produção por Linha":
            headers, data = self.generate_production_by_line_report()
        elif self.report_type == "Composição / Estrutura de Produto":
            headers, data = self.generate_product_composition_report()
        elif self.report_type == "Produção por Período":
            headers, data = self.generate_production_by_period_report()
        elif self.report_type == "Rendimento de OP":
            headers, data = self.generate_yield_report()
        elif self.report_type == "Necessidade de Insumos":
            headers, data = self.generate_material_requirements_report()
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

    def generate_production_orders_report(self):
        filters = {
            "id_de": self.filters["id_de"].text(),
            "id_ate": self.filters["id_ate"].text(),
            "produto_de": self.filters["produto_de"].text(),
            "produto_ate": self.filters["produto_ate"].text(),
            "status": self.filters["status"].text(),
            "periodo_de": get_required_date_value(self.filters["periodo_de"]),
            "periodo_ate": get_required_date_value(self.filters["periodo_ate"]),
        }
        
        db_manager = get_db_manager()
        orders = db_manager.get_production_orders(filters)
        
        headers = ["ID", "Produto", "Status", "Data de Criação", "Quantidade"]
        data = [[o["id"], o["produto"], o["status"], o["data_criacao"], format_decimal_text(o["quantidade"]) ] for o in orders]
        
        return headers, data

    def generate_production_by_line_report(self):
        filters = {
            "linha_de": self.filters["linha_de"].text(),
            "linha_ate": self.filters["linha_ate"].text(),
            "periodo_de": get_required_date_value(self.filters["periodo_de"]),
            "periodo_ate": get_required_date_value(self.filters["periodo_ate"]),
        }
        
        db_manager = get_db_manager()
        production = db_manager.get_production_by_line(filters)
        
        headers = ["Linha de Produção", "Produto", "Quantidade Produzida"]
        data = [[p["linha"], p["produto"], format_decimal_text(p["quantidade"]) ] for p in production]
        
        return headers, data

    def generate_product_composition_report(self):
        filters = {
            "produto_de": self.filters["produto_de"].text(),
            "produto_ate": self.filters["produto_ate"].text(),
        }
        
        db_manager = get_db_manager()
        composition = db_manager.get_product_composition(filters)
        
        headers = ["Produto", "Insumo", "Quantidade", "Un."]
        data = [[c["produto"], c["insumo"], format_decimal_text(c["quantidade"]), c["unidade"]] for c in composition]
        
        return headers, data

    def generate_yield_report(self):
        db_manager = get_db_manager()
        yield_data = db_manager.get_yield_report()
        
        headers = ["ID OP", "Número", "Data Criação", "Qtd Planejada", "Qtd Produzida", "Rendimento (%)"]
        data = [[d["ID"], d["NUMERO"], d["DATA_CRIACAO"], format_decimal_text(d['qtd_planejada']), format_decimal_text(d['qtd_produzida']), f"{format_decimal_text(d['rendimento'])}%"] for d in yield_data]
        
        return headers, data

    def generate_material_requirements_report(self):
        db_manager = get_db_manager()
        reqs = db_manager.get_material_requirements_report()
        
        headers = ["Insumo", "Un.", "Qtd Necessária", "Saldo em Estoque", "Falta"]
        data = [[d["insumo"], d["unidade"], format_decimal_text(d['qtd_necessaria']), format_decimal_text(d['qtd_estoque']), format_decimal_text(d['falta'])] for d in reqs]
        
        return headers, data

    def generate_production_by_period_report(self):
        filters = {
            "periodo_de": get_required_date_value(self.filters["periodo_de"]),
            "periodo_ate": get_required_date_value(self.filters["periodo_ate"]),
        }
        
        db_manager = get_db_manager()
        production_data = db_manager.get_production_by_period(filters)
        
        headers = ["Produto", "Quantidade Produzida", "Data da Produção"]
        data = [[p["produto"], p["quantidade_produzida"], p["data_producao"]] for p in production_data]
        
        return headers, data

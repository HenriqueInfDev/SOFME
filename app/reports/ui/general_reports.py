
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog
from app.database.db import get_db_manager
from app.reports.export import export_to_pdf, export_to_excel
from app.utils.ui_utils import format_decimal_text, get_save_filename, show_success_message

from app.styles.buttons_styles import (
    button_style, BLUE, GREEN
)
from app.styles.windows_style import (
    window_style, LIGHT
)
from app.styles.input_styles import (
    input_style, DEFAULTINPUT
)

class GeneralReportWindow(QWidget):
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
        # Currently no filters for General Reports (listing all)
        self.layout.addLayout(self.filters_layout)

    def setup_buttons(self):
        self.generate_button = QPushButton("Gerar Relatório")
        self.generate_button.setStyleSheet(button_style(BLUE))
        self.generate_button.clicked.connect(self.generate_report)
        self.layout.addWidget(self.generate_button)

    def apply_styles_to_filters(self):
        for widget in self.filters.values():
            if isinstance(widget, QLineEdit):
                widget.setStyleSheet(input_style(DEFAULTINPUT))

    def generate_report(self):
        if self.report_type == "Fornecedores":
            headers, data = self.generate_suppliers_report()
        elif self.report_type == "Itens":
            headers, data = self.generate_items_report()
        else:
            headers, data = [], []

        if data:
            self.show_preview(headers, data)
        else:
            show_success_message(self, "Relatório", "Nenhum dado encontrado.")

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

    def generate_suppliers_report(self):
        db_manager = get_db_manager()
        suppliers = db_manager.get_suppliers_report()
        
        headers = ["ID", "Razão Social", "Nome Fantasia", "CNPJ", "Status"]
        data = [[s["ID"], s["RAZAO_SOCIAL"], s["NOME_FANTASIA"], s["CNPJ"], s["STATUS"]] for s in suppliers]
        
        return headers, data

    def generate_items_report(self):
        db_manager = get_db_manager()
        items = db_manager.get_items_report()
        
        headers = ["ID", "Cód. Interno", "Descrição", "Tipo", "Un.", "Saldo", "Custo Médio"]
        data = [[i["ID"], i["CODIGO_INTERNO"], i["DESCRICAO"], i["TIPO_ITEM"], i["unidade"], format_decimal_text(i['SALDO_ESTOQUE']), f"R$ {format_decimal_text(i['CUSTO_MEDIO'])}"] for i in items]
        
        return headers, data

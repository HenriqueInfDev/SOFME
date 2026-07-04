# main.py
import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QToolBar,
)
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from functools import partial

from app.styles.windows_style import (
    window_style, LIGHT
)

class MainWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.windows = {}
        self.user = user
        self.setWindowTitle("GP - MiniSis")
        self.setWindowIcon(QIcon(self._resolve_icon('home.svg')))
        self.setGeometry(100, 100, 1200, 820)
        self.setStyleSheet(window_style(LIGHT))
        self.setup_menus()
        self.setup_toolbar()
        self.setup_central_widget()
        self.statusBar().showMessage(f"Pronto - {self.user.get('LOGIN', 'Usuário') if self.user else 'Usuário'}")

    def _resolve_icon(self, icon_name):
        project_root = os.path.abspath(os.path.dirname(__file__))
        # Tenta primeiro em app/images/icons
        icon_path = os.path.join(project_root, "app", "images", "icons", icon_name)
        if not os.path.exists(icon_path):
            # Se não encontrar, tenta em app/styles/images/icons
            icon_path = os.path.join(project_root, "app", "styles", "images", "icons", icon_name)
        return icon_path

    def _load_white_icon(self, icon_name):
        """Carrega um ícone SVG e o colore de branco para a toolbar"""
        icon_path = self._resolve_icon(icon_name)
        pixmap = QPixmap(icon_path)
        # Converter para RGBA para aplicar cor
        if not pixmap.isNull():
            # Em PySide6, usamos convertToFormat da imagem ou criamos nova imagem
            image = pixmap.toImage()
            # Aplicar filtro de cor branca
            for x in range(image.width()):
                for y in range(image.height()):
                    color = image.pixelColor(x, y)
                    if color.alpha() > 0:  # Se não é totalmente transparente
                        color.setRed(255)
                        color.setGreen(255)
                        color.setBlue(255)
                        image.setPixelColor(x, y, color)
            pixmap = QPixmap.fromImage(image)
        return QIcon(pixmap)

    def setup_menus(self):
        menu_bar = self.menuBar()
        
        # Menu Cadastros
        registers_menu = menu_bar.addMenu("&Cadastros")
        
        from app.item.ui_search_window import ItemSearchWindow
        self._add_menu_action(registers_menu, "Produtos", "item_search_window", ItemSearchWindow, 'registro_produto_icon.svg', "Pesquisar e gerenciar produtos")
        
        from app.supplier.ui_search_window import SupplierSearchWindow
        self._add_menu_action(registers_menu, "Fornecedores", "supplier_search_window", SupplierSearchWindow, 'fornecedor_registro.svg', "Pesquisar e gerenciar fornecedores")
        
        registers_menu.addSeparator()
        from app.unit.ui_unit_window import UnitWindow
        self._add_menu_action(registers_menu, "Unidades de Medida", "unit_window", UnitWindow)
        registers_menu.addSeparator()
        from app.auth.ui_user_window import UserWindow
        self._add_menu_action(registers_menu, "Usuários", "user_window", UserWindow)
        
        # Menu Movimento
        movement_menu = menu_bar.addMenu("&Movimento")
        
        from app.stock.ui_entry_search_window import EntrySearchWindow
        self._add_menu_action(movement_menu, "Entrada de Insumos", "stock_entry_window", EntrySearchWindow, 'entrada_insumo.svg', "Registrar entrada de insumos")

        movement_menu.addSeparator()

        from app.production_line.ui_line_list_window import LineListWindow
        self._add_menu_action(movement_menu, "Linhas de Produção", "line_list_window", LineListWindow, 'linha_producao_icon.svg', "Gerenciar linhas de produção")
        
        from app.production.ui_op_search_window import OPSearchWindow
        self._add_menu_action(movement_menu, "Ordem de Produção", "op_search_window", OPSearchWindow, 'ordem_producao_icon.svg', "Gerenciar ordens de produção")
        
        movement_menu.addSeparator()

        from app.sales.ui_sale_search_window import SaleSearchWindow
        self._add_menu_action(movement_menu, "Saída de Produtos", "sale_search_window", SaleSearchWindow, 'saida_produtos_icon.svg', "Registrar saída de produtos")

        # Menu Relatórios
        reports_menu = menu_bar.addMenu("&Relatórios")
        
        # Submenu Cadastros
        general_reports_menu = reports_menu.addMenu("Cadastros")
        from app.reports.ui.general_reports import GeneralReportWindow
        self._add_menu_action(general_reports_menu, "Fornecedores", "suppliers_report", lambda: GeneralReportWindow("Fornecedores"))
        self._add_menu_action(general_reports_menu, "Itens", "items_report", lambda: GeneralReportWindow("Itens"))

        # Submenu Estoque
        stock_reports_menu = reports_menu.addMenu("Estoque")
        from app.reports.ui.stock_reports import StockReportWindow
        self._add_menu_action(stock_reports_menu, "Entradas (Compras)", "stock_entry_report", lambda: StockReportWindow("Entradas (Compras)"))
        self._add_menu_action(stock_reports_menu, "Itens da Nota de Entrada", "entry_items_report", lambda: StockReportWindow("Itens da Nota de Entrada"))
        self._add_menu_action(stock_reports_menu, "Movimentação de Estoque", "stock_movement_report", lambda: StockReportWindow("Movimentação de Estoque"))
        self._add_menu_action(stock_reports_menu, "Estoque Atual", "current_stock_report", lambda: StockReportWindow("Estoque Atual"))
        self._add_menu_action(stock_reports_menu, "Estoque Baixo", "low_stock_report", lambda: StockReportWindow("Estoque Baixo"))
        self._add_menu_action(stock_reports_menu, "Curva ABC de Estoque", "abc_report", lambda: StockReportWindow("Curva ABC de Estoque"))
        self._add_menu_action(stock_reports_menu, "Itens Sem Giro", "inactive_report", lambda: StockReportWindow("Itens Sem Giro"))

        # Submenu Produção
        production_reports_menu = reports_menu.addMenu("Produção")
        from app.reports.ui.production_reports import ProductionReportWindow
        self._add_menu_action(production_reports_menu, "Ordens de Produção", "production_orders_report", lambda: ProductionReportWindow("Ordens de Produção"))
        self._add_menu_action(production_reports_menu, "Produção por Período", "production_by_period_report", lambda: ProductionReportWindow("Produção por Período"))
        self._add_menu_action(production_reports_menu, "Produção por Linha", "production_by_line_report", lambda: ProductionReportWindow("Produção por Linha"))
        self._add_menu_action(production_reports_menu, "Composição de Produto", "product_composition_report", lambda: ProductionReportWindow("Composição / Estrutura de Produto"))
        self._add_menu_action(production_reports_menu, "Rendimento de OP", "yield_report", lambda: ProductionReportWindow("Rendimento de OP"))
        self._add_menu_action(production_reports_menu, "Necessidade de Insumos", "requirements_report", lambda: ProductionReportWindow("Necessidade de Insumos"))

        # Submenu Financeiro
        financial_reports_menu = reports_menu.addMenu("Financeiro")
        from app.reports.ui.financial_reports import FinancialReportWindow
        self._add_menu_action(financial_reports_menu, "Custo do Produto", "product_cost_report", lambda: FinancialReportWindow("Custo do Produto"))
        self._add_menu_action(financial_reports_menu, "Lucro por Produto", "profit_by_product_report", lambda: FinancialReportWindow("Lucro por Produto"))
        self._add_menu_action(financial_reports_menu, "Lucro por Período", "profit_by_period_report", lambda: FinancialReportWindow("Lucro por Período"))

        # Menu Configurações
        # settings_menu = menu_bar.addMenu("&Configurações")

    def _add_menu_action(self, menu, text, window_name, window_class, icon_name=None, tooltip=None):
        action = QAction(text, self)
        if icon_name:
            action.setIcon(QIcon(self._resolve_icon(icon_name)))
        if tooltip:
            action.setToolTip(tooltip)
        action.triggered.connect(partial(self._open_window, window_name, window_class))
        menu.addAction(action)

    def _open_window(self, window_name, window_class):
        # Ensure we have a live instance. If the stored instance was deleted
        # (Qt/C++ object destroyed), calling methods on it raises RuntimeError.
        # Create a new instance when needed and keep the dict entry in sync.
        instance = self.windows.get(window_name)

        def make_instance():
            return window_class() if callable(window_class) else window_class

        if instance is None:
            instance = make_instance()
            self.windows[window_name] = instance
            try:
                instance.destroyed.connect(lambda _obj=None, name=window_name: self.windows.pop(name, None))
            except Exception:
                pass

        try:
            instance.show()
            instance.raise_()
        except RuntimeError:
            # Underlying C++ object was deleted; recreate and replace it.
            instance = make_instance()
            self.windows[window_name] = instance
            # If the instance emits destroyed, remove it from registry when destroyed
            try:
                instance.destroyed.connect(lambda _obj=None, name=window_name: self.windows.pop(name, None))
            except Exception:
                pass
            instance.show()
            instance.raise_()

    def setup_toolbar(self):
        from app.item.ui_search_window import ItemSearchWindow
        from app.stock.ui_entry_search_window import EntrySearchWindow
        from app.supplier.ui_search_window import SupplierSearchWindow
        from app.production_line.ui_line_list_window import LineListWindow
        from app.production.ui_op_search_window import OPSearchWindow
        from app.sales.ui_sale_search_window import SaleSearchWindow

        toolbar = QToolBar("Ações Rápidas")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet(
            "QToolBar { background-color: #1E3A8A; border-bottom: 1px solid #1E40AF; spacing: 10px; padding: 8px; }"
            "QToolButton { background: transparent; border: none; padding: 8px 12px; border-radius: 12px; color: white; }"
            "QToolButton:hover { background-color: rgba(255, 255, 255, 0.15); }"
            "QToolButton:checked { background-color: rgba(255, 255, 255, 0.25); }"
        )

        products_action = QAction(self._load_white_icon('registro_produto_icon.svg'), "Produtos", self)
        entry_action = QAction(self._load_white_icon('entrada_insumo.svg'), "Entrada de Insumos", self)
        supplier_action = QAction(self._load_white_icon('fornecedor_registro.svg'), "Fornecedores", self)
        line_action = QAction(self._load_white_icon('linha_producao_icon.svg'), "Linhas de Produção", self)
        order_action = QAction(self._load_white_icon('ordem_producao_icon.svg'), "Ordem de Produção", self)
        sale_action = QAction(self._load_white_icon('saida_produtos_icon.svg'), "Saída de Produtos", self)

        products_action.setToolTip("PRODUTOS")
        entry_action.setToolTip("ENTRADA DE INSUMOS")
        supplier_action.setToolTip("FORNECEDORES")
        line_action.setToolTip("LINHAS DE PRODUÇÃO")
        order_action.setToolTip("ORDENS DE PRODUÇÃO")
        sale_action.setToolTip("SAÍDA DE PRODUTOS")

        products_action.triggered.connect(partial(self._open_window, "item_search_window", ItemSearchWindow))
        entry_action.triggered.connect(partial(self._open_window, "stock_entry_window", EntrySearchWindow))
        supplier_action.triggered.connect(partial(self._open_window, "supplier_search_window", SupplierSearchWindow))
        line_action.triggered.connect(partial(self._open_window, "line_list_window", LineListWindow))
        order_action.triggered.connect(partial(self._open_window, "op_search_window", OPSearchWindow))
        sale_action.triggered.connect(partial(self._open_window, "sale_search_window", SaleSearchWindow))

        toolbar.addAction(supplier_action)
        toolbar.addAction(products_action)
        toolbar.addSeparator()
        toolbar.addAction(entry_action)
        toolbar.addAction(line_action)
        toolbar.addAction(order_action)
        toolbar.addSeparator()
        toolbar.addAction(sale_action)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def show_home(self):
        self.setCentralWidget(self.central_widget)

    def setup_central_widget(self):
        self.central_widget = QWidget()
        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(24, 24, 24, 24)
        central_layout.setSpacing(20)
        central_layout.addStretch(1)

        title = QLabel("Bem-vindo ao SOFME")
        title.setStyleSheet("font-size: 32px; font-weight: 800; color: #0F172A; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel(
            "Sistema de organização financeira para microempreendedor."
        )
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #475569; line-height: 1.8;")

        central_layout.addWidget(title)
        central_layout.addWidget(subtitle)
        central_layout.addStretch(1)

        self.setCentralWidget(self.central_widget)


import logging

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

import traceback


def main():
    try:
        from app.database.db import get_db_manager
        from app.auth.login_window import LoginWindow
        get_db_manager()

        app = QApplication(sys.argv)

        login_window = None
        main_window = None

        def on_login_success(user):
            nonlocal main_window
            main_window = MainWindow(user=user)
            main_window.showMaximized()
            if login_window is not None:
                login_window.close()

        login_window = LoginWindow(on_success=on_login_success)
        # Show the login window maximized (covers the screen but keeps window borders)
        login_window.showMaximized()
        sys.exit(app.exec())

    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

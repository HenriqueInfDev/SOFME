import os
import sqlite3
import sys
import time
import unittest
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.db import get_db_manager, DatabaseManager
from app.item.service import ItemService
from app.supplier.service import SupplierService
from app.stock.service import StockService
from app.sales.sale_service import SaleService
from app.unit.unit_service import UnitService
from app.production.composition_operations import (
    validate_bom_item, add_bom_item, get_bom, update_bom_item, delete_bom_item, update_composition
)
from app.production.order_operations import (
    create_op, update_op, finalize_op, get_op_details, list_ops, cancel_op, delete_op, reopen_op, check_stock_for_production
)
from app.production_line.line_operations import (
    create_production_line, get_all_production_lines, get_production_line_details,
    update_production_line, delete_production_line
)
from app.stock.stock_repository import StockRepository
from app.sales.sale_repository import SaleRepository
from app.supplier.supplier_repository import SupplierRepository
from app.item.item_repository import ItemRepository
from app.unit.unit_repository import UnitRepository
from app.database.db import DatabaseManager


def setUpModule():
    # Ensure the module uses a fresh in-memory database
    DatabaseManager.reset_instance()


class BaseDatabaseTest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.reset_instance()
        self.db_manager = get_db_manager(db_path=':memory:')

    def tearDown(self):
        DatabaseManager.reset_instance()


class TestDatabaseInitialization(BaseDatabaseTest):
    def test_database_tables_exist(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        expected_tables = {
            'UNIDADE', 'ITEM', 'FORNECEDOR', 'ENTRADANOTA', 'COMPOSICAO', 'ORDEMPRODUCAO',
            'ORDEMPRODUCAO_ITENS', 'MOVIMENTO', 'ENTRADANOTA_ITENS', 'SAIDA', 'SAIDA_ITENS',
            'LINHAPRODUCAO', 'LINHAPRODUCAO_ITEMS'
        }
        self.assertTrue(expected_tables.issubset(tables))

    def test_frozen_app_uses_shared_data_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app_root = os.path.join(temp_dir, "SOFME")
            legacy_db_path = os.path.join(app_root, "_internal", "Dados", "DADOS.DB")
            os.makedirs(os.path.dirname(legacy_db_path), exist_ok=True)

            legacy_conn = sqlite3.connect(legacy_db_path)
            legacy_conn.execute("CREATE TABLE TEST (ID INTEGER PRIMARY KEY)")
            legacy_conn.commit()
            legacy_conn.close()

            with patch("sys.frozen", True, create=True), patch("sys.executable", os.path.join(app_root, "SOFME.exe")):
                DatabaseManager.reset_instance()
                try:
                    db_manager = DatabaseManager()
                    expected_db_path = os.path.join(app_root, "Dados", "DADOS.DB")
                    self.assertEqual(db_manager.db_path, expected_db_path)
                    self.assertTrue(os.path.exists(expected_db_path))
                finally:
                    DatabaseManager.reset_instance()

    def test_frozen_app_uses_shared_data_folder_when_executable_is_internal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app_root = os.path.join(temp_dir, "SOFME")
            internal_exe = os.path.join(app_root, "_internal", "SOFME.exe")
            legacy_db_path = os.path.join(app_root, "_internal", "Dados", "DADOS.DB")
            os.makedirs(os.path.dirname(legacy_db_path), exist_ok=True)

            legacy_conn = sqlite3.connect(legacy_db_path)
            legacy_conn.execute("CREATE TABLE TEST (ID INTEGER PRIMARY KEY)")
            legacy_conn.commit()
            legacy_conn.close()

            with patch("sys.frozen", True, create=True), patch("sys.executable", internal_exe):
                DatabaseManager.reset_instance()
                try:
                    db_manager = DatabaseManager()
                    expected_db_path = os.path.join(app_root, "Dados", "DADOS.DB")
                    self.assertEqual(db_manager.db_path, expected_db_path)
                    self.assertTrue(os.path.exists(expected_db_path))
                finally:
                    DatabaseManager.reset_instance()

    def test_existing_root_database_preferred_over_internal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app_root = os.path.join(temp_dir, "SOFME")
            os.makedirs(os.path.join(app_root, "Dados"), exist_ok=True)
            os.makedirs(os.path.join(app_root, "_internal", "Dados"), exist_ok=True)

            root_db_path = os.path.join(app_root, "Dados", "DADOS.DB")
            internal_db_path = os.path.join(app_root, "_internal", "Dados", "DADOS.DB")

            root_conn = sqlite3.connect(root_db_path)
            root_conn.execute("CREATE TABLE TEST_ROOT (ID INTEGER PRIMARY KEY)")
            root_conn.commit()
            root_conn.close()

            internal_conn = sqlite3.connect(internal_db_path)
            internal_conn.execute("CREATE TABLE TEST_INTERNAL (ID INTEGER PRIMARY KEY)")
            internal_conn.commit()
            internal_conn.close()

            with patch("sys.frozen", True, create=True), patch("sys.executable", os.path.join(app_root, "SOFME.exe")):
                DatabaseManager.reset_instance()
                try:
                    db_manager = DatabaseManager()
                    self.assertEqual(db_manager.db_path, root_db_path)
                    self.assertTrue(os.path.exists(root_db_path))
                    self.assertFalse(os.path.exists(internal_db_path))
                finally:
                    DatabaseManager.reset_instance()

    def test_stock_item_details_returns_mapping(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('Test Unit', 'TU')['data']
        item_id = item_service.add_item('codItem', 'Item Test', 'Insumo', unit_id, None)['data']

        stock_service = StockService()
        result = stock_service.get_item_details(item_id)
        self.assertTrue(result['success'])
        self.assertIsInstance(result['data'], dict)
        self.assertEqual(result['data']['ID'], item_id)


class TestUnitService(BaseDatabaseTest):
    def test_add_update_delete_unit(self):
        unit_service = UnitService()

        result = unit_service.add_unit('Test Unit', 'tu')
        self.assertTrue(result['success'])
        unit_id = result['data']

        result = unit_service.add_unit('Test Unit', 'tu')
        self.assertFalse(result['success'])

        result = unit_service.update_unit(unit_id, 'Updated Unit', 'UT')
        self.assertTrue(result['success'])

        result = unit_service.delete_unit(unit_id)
        self.assertTrue(result['success'])

    def test_delete_unit_in_use(self):
        unit_service = UnitService()
        item_service = ItemService()
        result = unit_service.add_unit('Test Unit', 'tu')
        unit_id = result['data']

        item_service.add_item('codigo1', 'Produto Teste', 'Produto', unit_id, None)
        result = unit_service.delete_unit(unit_id)
        self.assertFalse(result['success'])


class TestItemService(BaseDatabaseTest):
    def test_add_get_update_delete_item(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('Test Item Unit', 'TI')['data']

        add_result = item_service.add_item('cod1', 'Item 1', 'Insumo', unit_id, None)
        self.assertTrue(add_result['success'])
        item_id = add_result['data']

        get_result = item_service.get_item_by_id(item_id)
        self.assertTrue(get_result['success'])
        self.assertEqual(get_result['data']['ID'], item_id)

        update_result = item_service.update_item(item_id, 'cod1', 'Item 1 Updated', 'Insumo', unit_id, None)
        self.assertTrue(update_result['success'])

        delete_result = item_service.delete_item(item_id)
        self.assertTrue(delete_result['success'])

    def test_search_items(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('Search Unit', 'SU')['data']
        item_service.add_item('codA', 'Alpha', 'Produto', unit_id, None)
        item_service.add_item('codB', 'Beta', 'Produto', unit_id, None)

        find_result = item_service.search_items('DESCRICAO', 'Alpha')
        self.assertTrue(find_result['success'])
        self.assertEqual(len(find_result['data']), 1)

    def test_manual_input_material(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('Input Unit', 'IU')['data']
        item_id = item_service.add_item('codM', 'Material Teste', 'Insumo', unit_id, None)['data']

        result = item_service.manual_input_material(item_id, 10, 50)
        self.assertTrue(result['success'])
        item = item_service.get_item_by_id(item_id)['data']
        self.assertEqual(item['SALDO_ESTOQUE'], 10)
        self.assertEqual(item['CUSTO_MEDIO'], 5)

    def test_get_item_by_id_returns_mapping_for_ui(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('UI Unit', 'UI')['data']
        item_id = item_service.add_item('codUI', 'Item UI', 'Insumo', unit_id, None)['data']

        result = item_service.get_item_by_id(item_id)
        self.assertTrue(result['success'])
        self.assertTrue(hasattr(result['data'], 'get'))

    def test_manual_input_material_updates_average_cost_with_different_prices(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('Input Unit 2', 'IU')['data']
        item_id = item_service.add_item('codM2', 'Material Teste 2', 'Insumo', unit_id, None)['data']

        result1 = item_service.manual_input_material(item_id, 10, 50)
        self.assertTrue(result1['success'])

        result2 = item_service.manual_input_material(item_id, 20, 120)
        self.assertTrue(result2['success'])

        item = item_service.get_item_by_id(item_id)['data']
        self.assertEqual(item['SALDO_ESTOQUE'], 30)
        self.assertAlmostEqual(item['CUSTO_MEDIO'], 170 / 30, places=6)


class TestSupplierService(BaseDatabaseTest):
    def test_add_supplier_allows_blank_cnpj(self):
        supplier_service = SupplierService()
        supplier_data = {
            'logradouro': 'Rua A', 'numero': '1', 'complemento': '',
            'bairro': 'Bairro', 'cidade': 'Cidade', 'uf': 'SP', 'cep': '00000-000'
        }
        result = supplier_service.add_supplier('Fornecedor Sem CNPJ', 'Fantasia', '   ', '999999999', 'email@test.com', supplier_data, 'Ativo')
        self.assertTrue(result['success'])

    def test_add_get_update_delete_supplier(self):
        supplier_service = SupplierService()
        supplier_data = {
            'logradouro': 'Rua A', 'numero': '1', 'complemento': '',
            'bairro': 'Bairro', 'cidade': 'Cidade', 'uf': 'SP', 'cep': '00000-000'
        }
        result = supplier_service.add_supplier('Fornecedor Teste', 'Fantasia', '', '999999999', 'email@test.com', supplier_data, 'Ativo')
        self.assertTrue(result['success'])
        supplier_id = result['data']

        get_result = supplier_service.get_supplier_by_id(supplier_id)
        self.assertTrue(get_result['success'])
        self.assertEqual(get_result['data']['ID'], supplier_id)

        update_result = supplier_service.update_supplier(supplier_id, 'Fornecedor Teste Updated', 'Fantasia', '', '999999999', 'email@test.com', supplier_data, 'Ativo')
        self.assertTrue(update_result['success'])

        delete_result = supplier_service.delete_supplier(supplier_id)
        self.assertTrue(delete_result['success'])

    def test_add_supplier_invalid_cnpj(self):
        supplier_service = SupplierService()
        supplier_data = {
            'logradouro': 'Rua A', 'numero': '1', 'complemento': '',
            'bairro': 'Bairro', 'cidade': 'Cidade', 'uf': 'SP', 'cep': '00000-000'
        }
        result = supplier_service.add_supplier('Fornecedor Inválido', 'Fantasia', '1234', '999999999', 'email@test.com', supplier_data, 'Ativo')
        self.assertFalse(result['success'])

    def test_get_supplier_by_id_returns_mapping_for_ui(self):
        supplier_service = SupplierService()
        supplier_data = {
            'logradouro': 'Rua A', 'numero': '1', 'complemento': '',
            'bairro': 'Bairro', 'cidade': 'Cidade', 'uf': 'SP', 'cep': '00000-000'
        }
        supplier_id = supplier_service.add_supplier('Fornecedor UI', 'Fantasia UI', '', '999999999', 'email@test.com', supplier_data, 'Ativo')['data']

        result = supplier_service.get_supplier_by_id(supplier_id)
        self.assertTrue(result['success'])
        self.assertTrue(hasattr(result['data'], 'get'))


class TestStockService(BaseDatabaseTest):
    def test_create_update_finalize_reopen_delete_entry(self):
        unit_service = UnitService()
        supplier_service = SupplierService()
        item_service = ItemService()
        stock_service = StockService()

        supplier_data = {
            'logradouro': 'Rua A', 'numero': '1', 'complemento': '',
            'bairro': 'Bairro', 'cidade': 'Cidade', 'uf': 'SP', 'cep': '00000-000'
        }
        supplier_id = supplier_service.add_supplier('Fornecedor Entrada', 'Fantasia', '', '999999999', 'email@test.com', supplier_data, 'Ativo')['data']
        unit_id = unit_service.add_unit('Estoque Unit', 'EU')['data']
        item_id = item_service.add_item('codEntrada', 'Insumo Entrada', 'Insumo', unit_id, supplier_id)['data']

        entry_result = stock_service.create_entry('2024-01-01', '2024-01-02', '123', 'Observacao')
        self.assertTrue(entry_result['success'])
        entry_id = entry_result['data']

        update_result = stock_service.update_entry(entry_id, '2024-01-01', '2024-01-02', '123', 'Observacao atualizada', [{'id_insumo': item_id, 'id_fornecedor': supplier_id, 'quantidade': 5, 'valor_unitario': 10}])
        self.assertTrue(update_result['success'])

        get_result = stock_service.get_entry_details(entry_id)
        self.assertTrue(get_result['success'])
        self.assertEqual(get_result['data']['master']['NUMERO_NOTA'], '123')

        finalize_result = stock_service.finalize_entry(entry_id)
        self.assertTrue(finalize_result['success'])

        reopen_result = stock_service.reopen_entry(entry_id)
        self.assertTrue(reopen_result['success'])

        delete_result = stock_service.delete_entry(entry_id)
        self.assertTrue(delete_result['success'])

    def test_finalize_entry_updates_item_stock_and_cost(self):
        unit_service = UnitService()
        supplier_service = SupplierService()
        item_service = ItemService()
        stock_service = StockService()

        supplier_data = {
            'logradouro': 'Rua A', 'numero': '1', 'complemento': '',
            'bairro': 'Bairro', 'cidade': 'Cidade', 'uf': 'SP', 'cep': '00000-000'
        }
        supplier_id = supplier_service.add_supplier('Fornecedor Entrada 2', 'Fantasia', '', '999999999', 'email@test.com', supplier_data, 'Ativo')['data']
        unit_id = unit_service.add_unit('Estoque Unit 2', 'EU')['data']
        item_id = item_service.add_item('codEntrada2', 'Insumo Entrada 2', 'Insumo', unit_id, supplier_id)['data']

        entry_result = stock_service.create_entry('2024-01-05', '2024-01-06', '456', 'Observacao')
        self.assertTrue(entry_result['success'])
        entry_id = entry_result['data']

        update_result = stock_service.update_entry(entry_id, '2024-01-05', '2024-01-06', '456', 'Observacao atualizada', [{'id_insumo': item_id, 'id_fornecedor': supplier_id, 'quantidade': 8, 'valor_unitario': 12}])
        self.assertTrue(update_result['success'])

        finalize_result = stock_service.finalize_entry(entry_id)
        self.assertTrue(finalize_result['success'])

        item = item_service.get_item_by_id(item_id)['data']
        self.assertEqual(item['SALDO_ESTOQUE'], 8)
        self.assertEqual(item['CUSTO_MEDIO'], 12)

        reopen_result = stock_service.reopen_entry(entry_id)
        self.assertTrue(reopen_result['success'])

    def test_list_entries_search(self):
        stock_service = StockService()
        entry_result = stock_service.create_entry('2024-01-01', '2024-01-02', '321', 'Observacao')
        self.assertTrue(entry_result['success'])

        list_result = stock_service.list_entries('321', 'Nº Nota')
        self.assertTrue(list_result['success'])
        self.assertGreaterEqual(len(list_result['data']), 1)


class TestSaleService(BaseDatabaseTest):
    def test_create_update_finalize_sale(self):
        unit_service = UnitService()
        item_service = ItemService()
        sale_service = SaleService()

        unit_id = unit_service.add_unit('Sale Unit', 'SU')['data']
        product_id = item_service.add_item('codProd', 'Produto Venda', 'Produto', unit_id, None)['data']

        sale_result = sale_service.create_sale('2024-01-10', 'Observacao', [{'id_produto': product_id, 'quantidade': 2, 'valor_unitario': 15}])
        self.assertTrue(sale_result['success'])
        sale_id = sale_result['data']

        update_result = sale_service.update_sale(sale_id, '2024-01-11', 'Obs update', [{'id_produto': product_id, 'quantidade': 3, 'valor_unitario': 15}])
        self.assertTrue(update_result['success'])

        finalize_result = sale_service.finalize_sale(sale_id)
        self.assertTrue(finalize_result['success'])

        details_result = sale_service.get_sale_details(sale_id)
        self.assertTrue(details_result['success'])
        self.assertEqual(details_result['data']['master']['ID'], sale_id)

    def test_finalize_sale_reduces_stock(self):
        unit_service = UnitService()
        item_service = ItemService()
        sale_service = SaleService()

        unit_id = unit_service.add_unit('Sale Stock Unit', 'SS')['data']
        product_id = item_service.add_item('codProdStock', 'Produto Venda Stock', 'Ambos', unit_id, None)['data']

        result = item_service.manual_input_material(product_id, 20, 100)
        self.assertTrue(result['success'])

        sale_result = sale_service.create_sale('2024-01-10', 'Observacao', [{'id_produto': product_id, 'quantidade': 4, 'valor_unitario': 15}])
        self.assertTrue(sale_result['success'])
        sale_id = sale_result['data']

        finalize_result = sale_service.finalize_sale(sale_id)
        self.assertTrue(finalize_result['success'])

        item = item_service.get_item_by_id(product_id)['data']
        self.assertEqual(item['SALDO_ESTOQUE'], 16)

    def test_list_sales_search(self):
        sale_service = SaleService()
        result = sale_service.create_sale('2024-01-10', 'Observacao', [])
        self.assertTrue(result['success'])

        list_result = sale_service.list_sales('', 'id')
        self.assertTrue(list_result['success'])
        self.assertGreaterEqual(len(list_result['data']), 1)


class TestProductionLineOperations(BaseDatabaseTest):
    def test_create_get_update_delete_line(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('Line Unit', 'LU')['data']
        prod_id = item_service.add_item('codLine', 'Produto Linha', 'Produto', unit_id, None)['data']

        line_id = create_production_line('Linha 1', 'Descricao', 'Ativa', [{'id_produto': prod_id, 'quantidade': 5}])
        self.assertIsNotNone(line_id)

        all_lines = get_all_production_lines()
        self.assertGreaterEqual(len(all_lines), 1)

        details = get_production_line_details(line_id)
        self.assertIsNotNone(details)
        self.assertEqual(details['master']['NOME'], 'Linha 1')

        updated = update_production_line(line_id, 'Linha 1 Atualizada', 'Descricao', 'Ativa', [{'id_produto': prod_id, 'quantidade': 10}])
        self.assertTrue(updated)

        deleted = delete_production_line(line_id)
        self.assertTrue(deleted)


class TestProductionOperations(BaseDatabaseTest):
    def test_bom_operations(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('BOM Unit', 'BU')['data']
        prod_id = item_service.add_item('codBomProduto', 'Produto BOM', 'Produto', unit_id, None)['data']
        mat_id = item_service.add_item('codBomInsumo', 'Insumo BOM', 'Insumo', unit_id, None)['data']

        valid, message = validate_bom_item(prod_id, mat_id)
        self.assertTrue(valid)

        add_ok = add_bom_item(prod_id, mat_id, 2)
        self.assertTrue(add_ok)

        bom = get_bom(prod_id)
        self.assertEqual(len(bom), 1)

        update_bom_item(bom[0]['ID'], 5)
        bom_updated = get_bom(prod_id)
        self.assertEqual(bom_updated[0]['QUANTIDADE'], 5)

        delete_bom_item(bom[0]['ID'])
        bom_deleted = get_bom(prod_id)
        self.assertEqual(len(bom_deleted), 0)

    def test_op_create_update_finalize_cancel_delete(self):
        unit_service = UnitService()
        item_service = ItemService()
        unit_id = unit_service.add_unit('OP Unit', 'OU')['data']
        prod_id = item_service.add_item('codOpProduto', 'Produto OP', 'Produto', unit_id, None)['data']
        insumo_id = item_service.add_item('codOpInsumo', 'Insumo OP', 'Insumo', unit_id, None)['data']

        add_bom_item(prod_id, insumo_id, 1)

        op_id = create_op('OP-001', '2024-02-01', [{'id_produto': prod_id, 'quantidade': 2}])
        self.assertIsNotNone(op_id)

        op_details = get_op_details(op_id)
        self.assertIsNotNone(op_details)

        update_ok = update_op(op_id, 'OP-002', '2024-02-10', [{'id_produto': prod_id, 'quantidade': 3}])
        self.assertTrue(update_ok)

        can_produce, msg = check_stock_for_production(prod_id, 1)
        self.assertFalse(can_produce)

        result = create_op('OP-003', '2024-02-25', [{'id_produto': prod_id, 'quantidade': 1}])
        self.assertIsNotNone(result)

        cancel_ok, cancel_msg = cancel_op(op_id)
        self.assertTrue(cancel_ok)

        reopen_ok, reopen_msg = reopen_op(op_id)
        self.assertTrue(reopen_ok)

        deleted_ok, deleted_msg = delete_op(op_id)
        self.assertTrue(deleted_ok)


def get_test_description(test):
    description = test.shortDescription()
    if description:
        return description

    name = getattr(test, '_testMethodName', '')
    descriptions = {
        'test_database_tables_exist': 'Banco de dados cria todas as tabelas',
        'test_add_update_delete_unit': 'Adicionar, atualizar e excluir unidade',
        'test_delete_unit_in_use': 'Não permitir excluir unidade em uso',
        'test_add_get_update_delete_item': 'Adicionar, consultar, atualizar e excluir item',
        'test_search_items': 'Pesquisar itens',
        'test_manual_input_material': 'Entrada manual de material',
        'test_manual_input_material_updates_average_cost_with_different_prices': 'Cálculo do custo médio',
        'test_add_get_update_delete_supplier': 'Adicionar, consultar, atualizar e excluir fornecedor',
        'test_add_supplier_invalid_cnpj': 'Validar CNPJ inválido do fornecedor',
        'test_create_update_finalize_reopen_delete_entry': 'Criar, atualizar, finalizar, reabrir e excluir entrada',
        'test_finalize_entry_updates_item_stock_and_cost': 'Finalizar entrada atualiza estoque e custo',
        'test_list_entries_search': 'Listar e pesquisar entradas',
        'test_create_update_finalize_sale': 'Criar, atualizar e finalizar venda',
        'test_finalize_sale_reduces_stock': 'Finalizar venda reduz estoque',
        'test_list_sales_search': 'Listar e pesquisar vendas',
        'test_create_get_update_delete_line': 'Criar, consultar, atualizar e excluir linha de produção',
        'test_bom_operations': 'Operações de composição (BOM)',
        'test_op_create_update_finalize_cancel_delete': 'Criar, atualizar, finalizar, cancelar e excluir ordem de produção',
    }

    if name in descriptions:
        return descriptions[name]

    description = name.replace('_', ' ')
    if description.startswith('test '):
        description = description[5:]
    return description.capitalize()


class PortugueseTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.start_time = None

    def startTestRun(self):
        self.start_time = time.time()
        print('\n' + '=' * 60)
        print('EXECUTANDO TESTES DO SISTEMA')
        print('=' * 60)
        print()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        print(f'\033[32mOK\033[0m {get_test_description(test)}')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f'\033[31mERROR\033[0m {get_test_description(test)}')

    def addError(self, test, err):
        super().addError(test, err)
        print(f'\033[31mERROR\033[0m {get_test_description(test)}')

    def stopTestRun(self):
        super().stopTestRun()
        duration = time.time() - self.start_time if self.start_time else 0
        print()
        print('=' * 60)
        print('RESUMO')
        print('-' * 60)
        print(f'Total de testes : {self.testsRun}')
        print(f'Sucessos        : {self.success_count}')
        print(f'Falhas          : {len(self.failures)}')
        print(f'Erros           : {len(self.errors)}')
        print(f'Tempo           : {duration:.2f} segundos')
        print()
        if not self.failures and not self.errors:
            print('🎉 TODOS OS TESTES FORAM APROVADOS')
        else:
            print('⚠️ HOUVE FALHAS OU ERROS NOS TESTES')
        print('=' * 60)


class PortugueseTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return PortugueseTestResult(self.stream, self.descriptions, self.verbosity)


if __name__ == '__main__':
    runner = PortugueseTestRunner(verbosity=0)
    unittest.main(testRunner=runner)

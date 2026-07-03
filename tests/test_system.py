import os
import sys
import unittest
import tempfile

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
    @classmethod
    def setUpClass(cls):
        cls.temp_db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        cls.db_path = cls.temp_db_file.name
        cls.temp_db_file.close()

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(cls.db_path)
        except OSError:
            pass

    def setUp(self):
        DatabaseManager.reset_instance()
        self.db_manager = get_db_manager(db_path=self.db_path)

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


class TestSupplierService(BaseDatabaseTest):
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


if __name__ == '__main__':
    unittest.main()

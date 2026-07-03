import os
import sys
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.item.ui_search_window import ItemSearchWindow
from app.supplier.ui_search_window import SupplierSearchWindow


class TestSearchWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_item_search_window_does_not_load_all_items_on_init(self):
        with patch('app.item.ui_search_window.ItemService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_all_items.return_value = {'success': True, 'data': []}
            mock_service.search_items.return_value = {'success': True, 'data': []}

            window = ItemSearchWindow()
            self.assertEqual(window.table_model.rowCount(), 0)
            mock_service.get_all_items.assert_not_called()
            window.close()

    def test_supplier_search_window_does_not_load_all_suppliers_on_init(self):
        with patch('app.supplier.ui_search_window.SupplierService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_all_suppliers.return_value = {'success': True, 'data': []}
            mock_service.search_suppliers.return_value = {'success': True, 'data': []}

            window = SupplierSearchWindow()
            self.assertEqual(window.table_model.rowCount(), 0)
            mock_service.get_all_suppliers.assert_not_called()
            window.close()


if __name__ == '__main__':
    unittest.main()

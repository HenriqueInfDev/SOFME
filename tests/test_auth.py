import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.db import get_db_manager
from app.auth.service import AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        get_db_manager(reset=True)
        self.auth_service = AuthService()

    def test_default_user_can_login(self):
        result = self.auth_service.authenticate_user('SUPORTE', 'SP-2370')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['LOGIN'], 'SUPORTE')

    def test_can_create_new_user(self):
        result = self.auth_service.create_user('admin', '123456')
        self.assertTrue(result['success'])

        auth_result = self.auth_service.authenticate_user('admin', '123456')
        self.assertTrue(auth_result['success'])

    def test_duplicate_user_is_rejected(self):
        self.auth_service.create_user('admin', '123456')
        result = self.auth_service.create_user('admin', '654321')
        self.assertFalse(result['success'])

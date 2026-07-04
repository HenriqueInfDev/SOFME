import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.db import get_db_manager
from app.auth.service import AuthService


class TestUserEdit(unittest.TestCase):
    def setUp(self):
        get_db_manager(reset=True)
        self.svc = AuthService()

    def test_update_login_and_auth(self):
        self.svc.create_user('alice', 'pw')
        users = self.svc.list_users()
        uid = users[0]['ID']
        res = self.svc.update_user(uid, login='alice2')
        self.assertTrue(res['success'])
        self.assertTrue(self.svc.authenticate_user('alice2', 'pw')['success'])
        self.assertFalse(self.svc.authenticate_user('alice', 'pw')['success'])

    def test_update_login_duplicate_rejected(self):
        self.svc.create_user('u1', 'p1')
        self.svc.create_user('u2', 'p2')
        users = self.svc.list_users()
        u1 = users[0]['ID']
        u2 = users[1]['ID']
        # try to change u2 login to u1's login
        res = self.svc.update_user(u2, login=users[0]['LOGIN'])
        self.assertFalse(res['success'])

    def test_forbid_support_login_on_update(self):
        self.svc.create_user('bob', 'pw')
        uid = self.svc.list_users()[0]['ID']
        res = self.svc.update_user(uid, login='SUPORTE')
        self.assertFalse(res['success'])

    def test_change_password(self):
        self.svc.create_user('chris', 'old')
        uid = self.svc.list_users()[0]['ID']
        res = self.svc.update_user(uid, password='new')
        self.assertTrue(res['success'])
        self.assertFalse(self.svc.authenticate_user('chris', 'old')['success'])
        self.assertTrue(self.svc.authenticate_user('chris', 'new')['success'])

    def test_deactivate_user_blocks_login(self):
        self.svc.create_user('dave', 'pw')
        uid = self.svc.list_users()[0]['ID']
        res = self.svc.update_user(uid, ativo='Não')
        self.assertTrue(res['success'])
        self.assertFalse(self.svc.authenticate_user('dave', 'pw')['success'])

    def test_ativo_stored_as_sim(self):
        self.svc.create_user('eve', 'pw')
        users = self.svc.list_users()
        self.assertEqual(users[0]['ATIVO'], 'Sim')


if __name__ == '__main__':
    unittest.main()

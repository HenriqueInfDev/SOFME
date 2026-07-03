from app.database.db import get_db_manager
get_db_manager(reset=True)
from app.auth.service import AuthService
s = AuthService()
print('Default user exists:', any(u['LOGIN']=='SUPORTE' for u in s.list_users()))
res = s.create_user('admin','123456')
print('create_user returned:', res)
print('All users:', s.list_users())

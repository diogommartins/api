# -*- coding: utf-8 -*-
#Git ignored file
from dal_sie import SIEDB2BaseAdapter
try:
    from gluon.dal.adapters import ADAPTERS
except ImportError:
    from gluon.dal import ADAPTERS      # Necessário para manter backward compatibility de versões < 2.9.12

ADAPTERS.update({
    'db2': SIEDB2BaseAdapter
})

db = DAL('postgres://postgres:devdtic2@sistemas.unirio.br/api', migrate=False)
# db = DAL('db2://DSN=apitest', db_codec='utf-8', pool_size=5, migrate=False)
dbSie = DAL('db2://DSN=dbsmtest;UID=dbsm;PWD=htrg11sn;LONGDATACOMPAT=1;DISABLEUNICODE=1', db_codec='utf-8', pool_size=5)
# -*- coding: utf-8 -*-
#Git ignored file
from dal_sie import SIEDB2BaseAdapter
from gluon.dal.adapters import ADAPTERS

ADAPTERS.update({
    'db2': SIEDB2BaseAdapter
})

db = DAL('postgres://postgres:devdtic2@sistemas.unirio.br/api', migrate=False)
dbSie = DAL('db2://DSN=dbsmtest;UID=dbsm;PWD=htrg11sn;LONGDATACOMPAT=1;DISABLEUNICODE=1', db_codec='utf-8', pool_size=5)
# -*- coding: utf-8 -*-
#Git ignored file
from dal_sie import SIEDB2BaseAdapter
from gluon.dal import ADAPTERS

ADAPTERS.update({
    'db2': SIEDB2BaseAdapter
})

db = DAL('postgres://postgres:devdtic2@sistemas.unirio.br/api')
dbSie = DAL('db2://DSN=dbsmtest;UID=dbsm;PWD=htrg11sn', db_codec='latin1')


# -*- coding: utf-8 -*-
#Git ignored file
if request.is_local:
    db = DAL('postgres://postgres:devdtic2@sistemas.unirio.br/api', migrate=False)
    dbSie = db
else:
    db = DAL('postgres://postgres:devdtic2@sistemas.unirio.br/api')
    dbSie = DAL('db2://DSN=dbsmtest;UID=dbsm;PWD=htrg11sn', db_codec='latin1')


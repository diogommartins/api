# -*- coding: utf-8 -*-
#Git ignored file
db = DAL('postgres://postgres:devdtic2@sistemas.unirio.br/api', migrate=False)
dbSie = DAL('db2://DSN=dbsmtest;UID=dbsm;PWD=htrg11sn', db_codec='latin1')
#dbSie = DAL('db2://DSN=DB2_SIE;UID=dbsm;PWD=S1&@Ufsm@App')
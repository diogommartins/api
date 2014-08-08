# -*- coding: utf-8 -*-
def index():	
	pessoas = dbSie.executesql(""" SELECT DBSM.RETIRAACENTOS(P.NOME_PESSOA) AS name, A.SEXO
                                    FROM DBSM.ALUNOS A INNER JOIN DBSM.PESSOAS P ON A.ID_PESSOA = P.ID_PESSOA
                                    WHERE P.ID_PESSOA = """ + str(request.vars.id) + """
                                """, as_dict=True)
	return response.json(pessoas)


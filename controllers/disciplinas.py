# -*- coding: utf-8 -*-
@service.json
@service.xml
def index():
	disciplinas = dbSie.executesql(""" SELECT ID, DBSM.RETIRAACENTOS(CODIGO) AS CODIGO, DBSM.RETIRAACENTOS(NOME) AS NOME FROM DBSM.ACAD_DISCIPLINAS
									ORDER BY NOME
								""", as_dict=True)

	return disciplinas

@service.json
@service.xml
def inscritas(MATR_ALUNO):
	disciplinas = dbSie.executesql(""" SELECT RTRIM(CURSO_DO_ALUNO),
											  RTRIM(DBSM.RETIRAACENTOS(NOME_DISCIPLINA)) AS NOME_DISCIPLINA,
											  RTRIM(DBSM.RETIRAACENTOS(NOME_DOCENTE)) AS NOME_DOCENTE,
											  ANO,
											  RTRIM(PERIODO),
											  RTRIM(DBSM.RETIRAACENTOS(DESCRICAO)) AS DESCRICAO,
											  RTRIM(CURSO_DA_TURMA),
											  RTRIM(COD_TURMA),
											  HORA_INICIO_AULA,
											  HORA_FIM_AULA,
											  RTRIM(DBSM.RETIRAACENTOS(DIA_DA_AULA)) AS DIA_DA_AULA,
											  RTRIM(DBSM.RETIRAACENTOS(TIPO_DE_AULA)) AS TIPO_DE_AULA
										FROM DBSM.DIARIO_CLASSE
										WHERE MATR_ALUNO LIKE '""" + MATR_ALUNO + """%'
									ORDER BY ANO DESC, PERIODO DESC
								""", as_dict=True)
	if disciplinas:
		return disciplinas
	else:
		return False

def call():
	session.forget()
	return service()
# -*- coding: utf-8 -*-
@service.json
@service.xml
def deMatricula(MATR_ALUNO):
	result = dbSie.executesql("""  SELECT A.ID_ALUNO,
										  DBSM.RETIRAACENTOS(TRIM(A.NOME_PAI)) AS NOME_PAI,
										  DBSM.RETIRAACENTOS(A.NOME_MAE) AS NOME_MAE,
										  A.SEXO,
										  DBSM.RETIRAACENTOS(P.NOME_PESSOA) AS NOME_PESSOA,
										  CA.ANO_INGRESSO,
										  TRIM(DP.NUMERO_DOCUMENTO) AS NUMERO_DOCUMENTO,
										  DBSM.RETIRAACENTOS(TRIM(DP.ORGAO_EMISSOR)) AS ORGAO_EMISSOR,
										  TRIM(CA.MATR_ALUNO) AS MATR_ALUNO
									FROM DBSM.ALUNOS A INNER JOIN DBSM.PESSOAS P ON P.ID_PESSOA = A.ID_PESSOA
									INNER JOIN DBSM.CURSOS_ALUNOS CA ON CA.ID_ALUNO = A.ID_ALUNO
									INNER JOIN DBSM.DOC_PESSOAS DP ON DP.ID_PESSOA = P.ID_PESSOA AND DP.ID_TDOC_PESSOA = 2
									WHERE TRIM(CA.MATR_ALUNO) LIKE '""" + MATR_ALUNO + """'""", as_dict=True)
	if result:
		return result[0]

#recebe uma matrícula e 1retorna Resourse do tipo Imagem
def getAlunoFoto():
	MATR_ALUNO = request.vars.MATR_ALUNO
	result = dbSie.executesql(""" SELECT DBSM.BLOBTOVARCHAR(A.FOTO) AS FOTO
								  FROM DBSM.ALUNOS A INNER JOIN DBSM.CURSOS_ALUNOS CA ON A.ID_ALUNO = CA.ID_ALUNO
								  WHERE TRIM(CA.MATR_ALUNO) LIKE '""" + MATR_ALUNO + """'""", as_dict=True)

	if result:
		import base64
		fotoHex = result[0]['FOTO']
		response.headers['Content-Type']="image/png"
		response.body = base64.encodestring(fotoHex.decode('hex')).decode('base64')
		return response.body
	else:
		return False

def qr():
	import qrcode
	from AESCipher import *

	qr = qrcode.QRCode(
					    version=1,
					    error_correction=qrcode.constants.ERROR_CORRECT_L,
					    box_size=20,
					    border=1,
						)


	AESCipher = AESCipher()
	criptografada = AESCipher.encrypt(request.vars.MATR_ALUNO)
	qr.add_data( criptografada )
	qr.make(fit=True)

	img = qr.make_image()
	response.headers['Content-Type']="image/png"
	img.save(response.body, "PNG")
	return response.body.getvalue()

@service.json
@service.xml
def foto(MATR_ALUNO):
	result = dbSie.executesql(""" SELECT DBSM.BLOBTOVARCHAR(A.FOTO) AS FOTO
								  FROM DBSM.ALUNOS A INNER JOIN DBSM.CURSOS_ALUNOS CA ON A.ID_ALUNO = CA.ID_ALUNO
								  WHERE TRIM(CA.MATR_ALUNO) LIKE '""" + MATR_ALUNO + """'""", as_dict=True)

	if result:
		import base64
		fotoHex = result[0]['FOTO']
		return base64.encodestring(fotoHex.decode('hex')).decode('base64')
	else:
		return False

@service.json
def getAlunosComFotos():
	alunos = []
	result = dbSie.executesql("""SELECT DBSM.BLOBTOVARCHAR(A.FOTO) AS FOTO, TRIM(CA.MATR_ALUNO) AS MATR_ALUNO
								 FROM DBSM.ALUNOS A INNER JOIN DBSM.CURSOS_ALUNOS CA ON A.ID_ALUNO = CA.ID_ALUNO
								 WHERE A.FOTO IS NOT NULL
								 AND A.SEXO = 'F'
								 ORDER BY CA.MATR_ALUNO DESC """, as_dict=True)

	for entry in result:
		if entry['FOTO'].startswith("FFD8FF"):
			alunos.append( entry['MATR_ALUNO'] )

	return alunos

def call():
    session.forget()
    return service()
import base64

import pyodbc


def index():
    cnxn = pyodbc.connect('DSN=dbsmtest;UID=dbsm;PWD=htrg11sn;LONGDATACOMPAT=1;')
    cursor = cnxn.cursor()

    form = FORM(
        INPUT(_type="file", _name="arquivo"),
        INPUT(_type="submit")
    )



    if form.process().accepted:
        a = open(form.vars.arquivo.fp.name, mode="rb")
        b = base64.b64encode(a.read())
        # ID_PESSOA DIOGO = 33694
        # ID_ALUNO DIOGO =

        # dbSie.executesql("INSERT INTO ALUNOS(FOTO) VALUES(:foto) WHERE ID_ALUNO = 33694", {"foto": b})
        nome = 'TESTE TESTE TESTE'
        cursor.execute("UPDATE ALUNOS SET FOTO = ?, NOME_PAI = ? WHERE ID_ALUNO = 33694", b, nome)
        # dbSie.executesql("UPDATE ALUNOS SET FOTO = ?, NOME_PAI = ? WHERE ID_ALUNO = 33694", b, nome)

    return dict(locals())
# -*- coding: utf-8 -*-
@request.restful()
def request():
    response.view = 'generic.' + request.extension #
    def GET(*args,**vars):
        patterns = [
                    "/ALUNOS/ID-ALUNO/{ALUNOS.ID_ALUNO}",
                    "/ALUNOS/ETNIA-ITEM/{ALUNOS.ETNIA_ITEM}",
                    ':auto[CURSOS]',
                    ':auto[CURSOS_ALUNOS]',
                    ':auto[DISCIPLINAS]',
                    ':auto[TAB_ESTRUTURADA]',
                    ':auto[VERSOES_CURSOS]'
                    ]
        parser = dbSie.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)

    return locals()
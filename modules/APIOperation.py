# coding=utf-8
from gluon import current, HTTP


class APIOperation(object):
    def __init__(self, tablename):
        self.tablename = tablename
        self.table = current.dbSie[self.tablename]

    def baseResourseURI(self):
        pass


class APIInsert(APIOperation):
    def __init__(self, tablename, parameters):
        """
        Classe responsável por lidar com requisições do tipo POST, que serão transformadas
        em um INSERT no banco de dados e retornarão uma resposta HTTP adequada a criação do novo
        recurso.

        :type tablename: str
        :type parameters: dict
        :param tablename: Str relativa ao nome da tabela modela no banco dbSie
        :param parameters: dict de parâmetros que serão inseridos
        """
        super(APIInsert, self).__init__(tablename)
        self.parameters = parameters
        self.db = current.dbSie

    def execute(self):
        newId = self.db[self.tablename].insert(**self.parameters)
        if newId:
            # self.db.commit()
            raise HTTP(201, headers={
                "Location": newId
            })
# coding=utf-8
from gluon import current, HTTP
from datetime import datetime, date


class APIOperation(object):
    def __init__(self, tablename):
        """

        :type tablename: str
        :param tablename: Str relativa ao nome da tabela modela no banco dbSie
        """
        self.tablename = tablename
        self.db = current.dbSie
        self.table = current.dbSie[self.tablename]
        self.primarykeyField = self.table[self.table._primarykey[0]]
        self.primarykeyColumns = self.table._primarykey[0]

    @property
    def baseResourseURI(self):
        return current.request.env.http_host + current.request.env.PATH_INFO + "/"


class APIQuery(APIOperation):
    ENTRIES_PER_QUERY_DEFAULT = 10
    ENTRIES_PER_QUERY_MAX = 5000

    def __init__(self, tablename, fields, request_vars, return_fields=None):
        super(APIQuery, self).__init__(tablename)
        self.fields = fields['valid']
        self.special_fields = fields['special']
        self.request_vars = request_vars
        self.return_fields = return_fields

    # Gera diferentes tipos de consultas para tipos de dados diferentes
    # Return: List
    def _getQueryStatement(self):
        conditions = []
        # Consultas normais
        for field in self.fields:
            if self.table[field].type == 'integer':
                conditions.append(self.table[field] == self.request_vars[field])
            elif self.table[field].type == 'string':
                conditions.append(self.table[field].contains(self.request_vars[field], case_sensitive=False))
            elif self.table[field].type == 'date':
                conditions.append(self.table[field] == self.request_vars[field])

        # Trata condições especiais
        for special_field in self.special_fields:
            field = self.specialFieldChop(special_field)
            if field:
                if special_field.endswith('_MIN'):
                    conditions.append(self.table[field] > self.request_vars[special_field])
                elif special_field.endswith('_MAX'):
                    conditions.append(self.table[field] < self.request_vars[special_field])

        return conditions

    # Retirar essa funcao daqui e ver porque import de APIRequest nao ta funcionando
    def specialFieldChop(self, field):
        DEFAULT_SUFIX_SIZE = 4
        validSufixes = ('_MIN', '_MAX', '_BET')
        if field.endswith(validSufixes):
            return field[:-DEFAULT_SUFIX_SIZE]
        return False

    # Return: List
    def _getReturnTableFields(self):
        if len(self.return_fields) > 0:
            return [self.table[field] for field in set(self.return_fields)]
        else:
            return [self.table.ALL]


    # Retorna a tupla do limite
    # Return: Tuple
    def _getRecordsSubset(self):
        limits = {
            "min": 0,
            "max": self.ENTRIES_PER_QUERY_DEFAULT
        }
        # Caso o usário passe os parâmetros LMIN e LMAX
        if set(['LMIN', 'LMAX']).issubset(self.request_vars):
            min = int(self.request_vars['LMIN'])
            max = int(self.request_vars['LMAX'])

            entriesToLimit = self.ENTRIES_PER_QUERY_MAX - max - min
            limits['max'] = max if (entriesToLimit > 0) else (
                max + entriesToLimit)  # Se subset maior do que o estabelecido, corrige

        return ( limits['min'], limits['max'] )


    # Retorna as linhas com as colunas requisitadas
    # Return: Dict
    def execute(self):
        conditions = self._getQueryStatement()
        recordsSubset = self._getRecordsSubset()
        if conditions:
            count = current.dbSie(reduce(lambda a, b: (a & b), conditions)).count()
            ret = current.dbSie(reduce(lambda a, b: (a & b), conditions)).select(*self._getReturnTableFields(),
                                                                                 limitby=recordsSubset)
        else:
            count = current.dbSie(self.table).count()
            ret = current.dbSie(self.table).select(limitby=recordsSubset, *self._getReturnTableFields())

        if ret:
            return {"count": count, "content": ret, "subset": recordsSubset}


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

    @property
    def defaultFieldsForSIETables(self):
        """
        Campos que obrigatoriamente devem ser preenchidos em um INSERT e devem ser feitos pela API.

        :rtype : dict
        :return: Um dicionário de parãmetros padrões
        """
        pkey = self.table._primarykey[0]
        return {
            pkey: self.nextValueForSequence(),
            "CONCORRENCIA": 999,
            "DT_ALTERACAO": str(date.today()),
            "HR_ALTERACAO": datetime.now().time().strftime("%H:%M:%S"),
            "ENDERECO_FISICO": current.request.env.remote_addr,
            "COD_OPERADOR": 1                                       # DBSM.USUARIOS.ID_USUARIO
        }

    def nextValueForSequence(self):
        """
        Por uma INFELIZ particularidade do DB2 de não possuir auto increment, ao inserir algum novo conteúdo em uma
        tabela, precisamos passar manualmente qual será o valor da nossa surrogate key. O DB2 nos provê a possibilidade
        de uso de SEQUECENCE. A nomenclatura padrão é composta do prefixo `SEQ_` acrescido do nome da tabela relacionada.

        :rtype: int
        :return: Um inteiro correspondente ao próximo ID válido disponível para um INSERT
        """
        return self.db.executesql("SELECT NEXT VALUE FOR SEQ_%s FROM SYSIBM.SYSDUMMY1" % self.tablename)[0][0]

    @property
    def optionalFieldsForSIETables(self):
        return {}

    def contentWithValidParameters(self):
        """
        Retorna um dicionário contendo somente os k,v onde k são colunas válidas da tabela em que se quer inserir.
        Esse dicionário também deve conter os campos padrões como IP utilizado par alterar, data e hora...

        :rtype : dict
        """
        validContent = {column: current.request.vars[column] for column in self.parameters['valid']}
        validContent.update({k: v for k, v in self.defaultFieldsForSIETables.iteritems() if k in self.table.fields})

        return validContent

    def execute(self):
        try:
            newId = self.table.insert(**self.contentWithValidParameters())
        except Exception as e:
            self.db.rollback()
            raise HTTP(404, "Não foi possível completar a operação.")
        else:
            self.db.commit()
            headers = {
                "Location": self.baseResourseURI + "?" + self.table._primarykey[0] + "=" + str(newId[self.table._primarykey[0]]),
                "id": newId[self.table._primarykey[0]]
            }
            raise HTTP(201, "Conteúdo inserido com sucesso.", **headers)


class APIUpdate(APIOperation):
    def __init__(self, tablename, parameters):
        super(APIUpdate, self).__init__(tablename)
        self.parameters = parameters

    def execute(self):
        try:
            affectedRows = self.db(self.primarykeyField == self.parameters[self.primarykeyColumn]).update(**self.parameters)
        except SyntaxError:
            raise HTTP(204, "Nenhum conteúdo foi passado")
        except ValueError:
            raise HTTP(422, "Algum parâmetro possui tipo inválido")
        if affectedRows > 0:
            headers = {
                "Affected": affectedRows
            }
            raise HTTP(200, "Conteúdo atualizado com sucesso", **headers)

        raise HTTP(404, "Ooops... A princesa está em um castelo com outro ID.")


class APIDelete(APIOperation):
    def __init__(self, tablename, rowId):
        super(APIDelete, self).__init__(tablename)
        self.rowId = rowId

    def execute(self):
        primarykeyField = self.table[self.table._primarykey[0]]
        self.db(primarykeyField == self.rowId).delete()
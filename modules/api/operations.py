# coding=utf-8
import base64
import os
import tempfile
import subprocess
import shutil
from datetime import datetime, date
from gluon import current, HTTP
import abc
from gluon.contrib.websocket_messaging import websocket_send
from gluon.serializers import json

try:
    import httplib as http
except ImportError:
    import http.client as http

__all__ = ['APIDelete', 'APIInsert', 'APIQuery', 'APIUpdate']


class APIOperation(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, request):
        """

        :type endpoint: str
        :param endpoint: Str relativa ao nome da tabela modela no banco datasource
        """
        self.request = request
        self.endpoint = self.request.endpoint
        self.db = current.datasource
        self.table = self.db[self.endpoint]

    @property
    def baseResourseURI(self):
        return current.request.env.http_host + current.request.env.PATH_INFO + "/"

    # TODO Isso não deveria existir aqui, já que é relacionado somente ao SIE
    @property
    def defaultFieldsForSIETables(self):
        """
        Campos que obrigatoriamente devem ser preenchidos em um INSERT e devem ser feitos pela API.

        :rtype : dict
        :return: Um dicionário de parãmetros padrões
        """
        return {
            "CONCORRENCIA": 999,
            "DT_ALTERACAO": str(date.today()),
            "HR_ALTERACAO": datetime.now().time().strftime("%H:%M:%S"),
            "ENDERECO_FISICO": current.request.env.remote_addr,
            "COD_OPERADOR": 1  # TODO DBSM.USUARIOS.ID_USUARIO admin REMOVER COD_OPERADOR DAQUI.
        }

    @property
    def _uniqueIdentifierColumn(self):
        return self.table._primarykey[0]

    @abc.abstractmethod
    def execute(self):
        raise NotImplementedError("Should be implemented on subclasses")


class APIAlterOperation(APIOperation):
    __metaclass__ = abc.ABCMeta

    def __init__(self, request):
        super(APIAlterOperation, self).__init__(request)
        self.parameters = request.parameters
        try:
            self.p_key_fields = { column:self.table[column] for column in self.table._primarykey}
        except (AttributeError, IndexError):
            HTTP(http.BAD_REQUEST, "O Endpoint requisitado não possui uma chave primária válida para esta operação.")
        self.p_key_columns = self.table._primarykey # lista de colunas que sao primary keys.

    def primarykeyInParameters(self, parameters):
        """
        Método utilizado para validar se a chave primária encontra-se na lista de parâmetros

        :rtype : bool
        """
        return set(self.p_key_columns).issubset(set(parameters['valid']))

    @abc.abstractmethod
    def contentWithValidParameters(self):
        """
        :rtype : dict
        """
        raise NotImplementedError("Should be implemented on subclasses")

    def blob_fields(self, parameters):
        """
        Retorna uma tupla de fields do tipo blob que estejam na lista de parâmetros
        :type parameters: dict
        :rtype : tuple
        """
        return tuple(field for field in parameters['valid'] if self.table[field].type == 'blob')

    def blob_values(self, parameters, fields):
        """
        Retorna uma tupla de valores correpondentes aos campos blob a serem usados em um prepared statement
        :type parameters: dict
        :type fields: list or tuple
        :rtype : tuple
        """

        return tuple(base64.b64decode(parameters[k]) for k in fields)

    def notify_clients(self, message):
        websocket_send("http://%s:%s" % (self.ws['host'], self.ws['port']), json(message), self.ws['password'],
                       self.table)


class APIQuery(APIOperation):
    ENTRIES_PER_QUERY_DEFAULT = 10

    __sorting_options = ("ASC", "DESC",)

    # TODO rever documetação
    def __init__(self, request):
        """

        :type request: request.APIRequest
        :type apiKey: key.APIKey
        :param endpoint: string relativa ao nome da tabela modela no banco datasource
        :param fields: Uma lista de colunas que devem ser retornadas pela consulta
        """
        super(APIQuery, self).__init__(request)
        self.fields = self.request.parameters['valid']
        self.special_fields = self.request.parameters['special']
        self.request_vars = self.request.request.vars
        self.apiKey = self.request.apiKey
        self.return_fields = self.request.return_fields

    def _utf8_lower(self,string):
        """
        Como python não suporta a chamada .lower() de uma string, tem que se passar por este workaround.
        :param string: a string que se deseja converter.
        :return: string convertida.
        """
        return string.decode('utf-8').lower().encode('utf-8') # TODO Sim, é uma gambiarra. Só mudando para python 3.

    def _getQueryStatement(self):
        """
        O método gera diferentes tipos de consultas para tipos de dados diferentes. Cada tipo de dado gera uma
        condição diferente e própria para o seu tipo.

        :rtype : list
        :return: Uma lista de parâmetros processados de consulta
        """
        conditions = []
        # Consultas normais
        for field in self.fields:
            if self.table[field].type == 'string':
                try:
                    if isinstance(self.request_vars[field],list):
                        lower_encoded_field = map(lambda x: self._utf8_lower(x),self.request_vars[field]) # TODO PYTHON 2.x DOESN'T SUPPORT .lower() of unicode strings.
                    else:
                        lower_encoded_field = self._utf8_lower(self.request_vars[field]) # TODO PYTHON 2.x DOESN'T SUPPORT .lower() of unicode strings.
                    conditions.append(self.table[field].contains(lower_encoded_field, case_sensitive=False, all=True))
                except UnicodeDecodeError:
                    headers = {"InvalidEncoding": json(dict(campo=field))}
                    raise HTTP(http.BAD_REQUEST, "Encoding do parâmetro é inválido (tem certeza que é utf-8?)",
                               **headers)
            else:
                conditions.append(self.table[field] == self.request_vars[field])

        # Trata condições especiais
        for special_field in self.special_fields:
            field = self.request.specialFieldChop(special_field)
            if field:
                if special_field.endswith('_MIN'):
                    conditions.append(self.table[field] > self.request_vars[special_field])
                elif special_field.endswith('_MAX'):
                    conditions.append(self.table[field] < self.request_vars[special_field])
                elif special_field.endswith('_SET'):
                    conditions.append(self.table[field].belongs(self.request_vars[special_field]))

        return conditions

    def _getReturnTableFields(self):
        """
        :rtype : list
        """
        if len(self.return_fields) > 0:
            return [self.table[field] for field in set(self.return_fields)]
        else:
            return [self.table.ALL]

    def _subsetIsDefined(self):
        return {'LMIN', 'LMAX'}.issubset(self.request_vars)

    def _getRecordsSubset(self):
        """
        O método processa LMIN e LMAX ou, caso os mesmos não sejam fornecidos, gera-os de acordo com a permissão
        da chave de usuário

        :return: Uma tupla contendo o LIMIT e OFFSET da consulta
        """
        limits = {
            "min": 0,
            "max": self.ENTRIES_PER_QUERY_DEFAULT
        }
        if self._subsetIsDefined():
            min = int(self.request_vars['LMIN'])
            max = int(self.request_vars['LMAX'])

            entriesToLimit = self.apiKey.max_entries - max - min
            limits['max'] = max if entriesToLimit > 0 else max + entriesToLimit

        return limits['min'], limits['max']

    def _distinctStyle(self):
        """
        Caso o parâmetro DISTINCT seja passado, a função define como será o tratamento. Ao usar DISTINCT, não se deve
        selecionar todos os fields
        :rtype : gluon.DAL.Field
        :return: A forma
        """
        if self.request_vars["DISTINCT"]:
            return True

    def __orderby(self):
        """
        :raises HTTP: http.BAD_REQUEST
        :rtype: str
        """
        order_field = self.request_vars["ORDERBY"]
        sort_order = self.request_vars['SORT'] or 'ASC'

        if order_field:
            if order_field not in self.table.fields:
                headers = {"InvalidParameters": json(order_field)}
                raise HTTP(http.BAD_REQUEST, "%s não é um campo válido para ordenação." % order_field, **headers)
            if sort_order not in self.__sorting_options:
                headers = {"InvalidParameters": json(sort_order)}
                raise HTTP(http.BAD_REQUEST, "%s não é uma ordenacão válida." % sort_order, **headers)
            return "%s %s" % (self.table[order_field], sort_order)
        elif self.table._primarykey:
            return self.table._primarykey
        else:
            return self.table.fields[0]

    def execute(self):
        """
        O método realiza uma consulta no banco de dados, retornando HTTP Status Code 200 (OK) e um dicionário em seu
        corpo com as seguintes chaves e valores:
            `content` onde encontra-se uma lista de entradas
            `count` o total de entradas para a consulta (descartando os limites);
            `subset` uma tupla com os limites LMIN e LMAX utilizados para realizar a consulta.

        :rtype : dict
        :return: Um dicionário com o conteúdo requisitado pelo usuário
        """
        conditions = self._getQueryStatement()
        recordsSubset = self._getRecordsSubset()

        if conditions:
            rows = self.db(reduce(lambda a, b: (a & b), conditions)).select(*self._getReturnTableFields(),
                                                                            limitby=recordsSubset,
                                                                            distinct=self._distinctStyle(),
                                                                            orderby=self.__orderby())
        else:
            rows = self.db().select(*self._getReturnTableFields(),
                                    limitby=recordsSubset,
                                    distinct=self._distinctStyle(),
                                    orderby=self.__orderby())

        if rows:
            print self.db._lastsql
            return {"content": rows, "subset": recordsSubset, "fields": self.table.fields}


class APIInsert(APIAlterOperation):
    def __init__(self, request):
        """
        Classe responsável por lidar com requisições do tipo POST, que serão transformadas
        em um INSERT no banco de dados e retornarão uma resposta HTTP adequada a criação do novo
        recurso.

        :type request: APIRequest
        """
        super(APIInsert, self).__init__(request)
        if self.has_composite_primary_key() and not self.primarykeyInParameters(self.parameters):
            raise HTTP(http.BAD_REQUEST, "Não é possível inserir um conteúdo sem sua chave primária composta.")
        if not self.has_composite_primary_key() and self.primarykeyInParameters(self.parameters):
            raise HTTP(http.BAD_REQUEST, "Não é possível inserir um conteúdo com sua chave primária.")

    @property
    def defaultFieldsForSIEInsert(self):
        fields = dict(self.defaultFieldsForSIETables)

        if not self.has_composite_primary_key():
            #Se a chave não é composta, procura o próximo valor válido da sequence da pkey para popular a query.
            fields.update({self._uniqueIdentifierColumn: self.nextValueForSequence})

        return fields

    def has_composite_primary_key(self):
        return len(self.p_key_columns) > 1

    @property
    def nextValueForSequence(self):
        """
        Por uma INFELIZ particularidade do DB2 de não possuir auto increment, ao inserir algum novo conteúdo em uma
        tabela, precisamos passar manualmente qual será o valor da nossa surrogate key. O DB2 nos provê a possibilidade
        de uso de SEQUECENCE. A nomenclatura padrão é composta do prefixo `SEQ_` acrescido do nome da tabela relacionada.

        :rtype: int
        :return: Um inteiro correspondente ao próximo ID válido disponível para um INSERT
        """
        return self.db.executesql("SELECT NEXT VALUE FOR DBSM.SEQ_%s FROM SYSIBM.SYSDUMMY1" % self.endpoint)[0][0]

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
        validContent.update({k: v for k, v in self.defaultFieldsForSIEInsert.iteritems() if k in self.table.fields})

        return validContent

    def filterSpecialFieldTypes(self, content):
        for field in content.iteritems():
            if self.table[field].type == "blob":
                content[field] = self.table.store(content[field])

    def insert_blob_fields_callback(self, new_id, blobs):
        """
        Gambiarra para inserir blobs.
        #TODO Deveria funcionar como um campo qualquer, mas não driver do DB2 não funciona.
        #TODO Commits? Rollback?
        :return:
        """

        directory_name = tempfile.mkdtemp()  # cria diretório temporário para copiar arquivos

        for field, blob in blobs:
            file_path = os.path.join(directory_name, field)
            f = open(file_path, "wb")
            f.write(blob)
            f.close()

        jar_path = os.path.join(current.request.folder, "modules", "blob.jar")
        properties_path = os.path.join(current.request.folder, "properties", "1_db_conn.properties")

        # Chama java externo
        subprocess.check_call(["java", "-jar", jar_path, directory_name, str(self.table), str(new_id),
                               self._uniqueIdentifierColumn, properties_path],
                              stderr=subprocess.STDOUT)

        shutil.rmtree(directory_name)  # os.removedirs não deleta diretório que não esteja vazio.

    def execute(self):
        try:
            blob_fields = self.blob_fields(self.parameters)
            parameters = self.contentWithValidParameters()
            if not blob_fields:
                if self.has_composite_primary_key():
                    new_id = 1 # TODO O que podemos retornar no caso de sucesso que faça sentido?
                else:
                    new_id = self.table.insert(**parameters)[self._uniqueIdentifierColumn]
            else:
                if self.has_composite_primary_key():
                    raise NotImplementedError # TODO Precisa atualizar o JAR que faz inserção para lidar id composta
                stmt = self.table._insert(**parameters)
                # Essa inserção não funcionará. É necessário reinserir pelo Java.
                blob_values = self.blob_values(parameters, blob_fields)
                self.db.executesql(stmt, blob_values)
                new_id = parameters[self._uniqueIdentifierColumn]
        except Exception as e:
            print self.db._lastsql
            print e
            self.db.rollback()
            raise HTTP(http.BAD_REQUEST, "Não foi possível completar a operação.")
        else:
            self.db.commit()
            if new_id and blob_fields:
                self.insert_blob_fields_callback(new_id, zip(blob_fields, blob_values))  # Reinsere blobs pelo JAVA
            headers = {
                # "Location": self.baseResourseURI + "?" + self.table._primarykey[0] + "=" + str(
                #     newId[self.table._primarykey[0]]),
                "Location": "%s?%s=%i" % (self.baseResourseURI, self._uniqueIdentifierColumn, new_id),
                "id": new_id
            }
            raise HTTP(http.CREATED, "Conteúdo inserido com sucesso.", **headers)


class APIUpdate(APIAlterOperation):
    def __init__(self, request):
        """
        Classe responsável por lidar com requisições do tipo PUT, que serão transformadas
        em um UPDATE no banco de dados e retornarão uma resposta HTTP adequada a atualizaçao do recurso.
        :type request: APIRequest

        :raises HTTP: 400 O dicionário `parameters` deve conter obrigatoriamente a primary key da tabela `tablename`
        """
        super(APIUpdate, self).__init__(request)
        if not self.primarykeyInParameters(self.parameters):
            raise HTTP(http.BAD_REQUEST, "Não é possível atualizar um conteúdo sem sua chave primária.")

        self.identifiers_values = [ (column, request.request.vars[column]) for column in self.p_key_columns]

    def contentWithValidParameters(self):
        """
        Retorna um dicionário contendo somente os k,v onde k são colunas válidas da tabela em que se quer atualizar.
        Esse dicionário não deve conter a chave primária.

        :rtype : dict
        """
        validContent = {column: current.request.vars[column] for column in self.parameters['valid'] if
                        column not in self.p_key_columns}

        #TODO Atualizar campo CONCORRENCIA somente quando o mesmo não existir
        validContent.update({k: v for k, v in self.defaultFieldsForSIETables.iteritems() if k in self.table.fields})
        return validContent

    def execute(self):
        """
        O método realiza uma atualização de uma entrada no banco de dados e retorna HTTP Status Code 200 (OK) caso
        o conteúdo seja atualizado com sucesso. A chave primária deve estar contida na lista de parâmetros e a mesma
        é utilizada para atualização.

        :rtype : HTTP
        :raise HTTP: 204 Não é possível realizar uma atualização sem que parâmetros sejam passados
        :raise HTTP: 422 Ocorre haja incompatibilidade entre o tipo de dados da coluna e o valor passsado
        :raise HTTP: 404 A chave primária informada é inválida e nenhuma entrada foi afetada
        """
        try:
            blob_fields = self.blob_fields(self.parameters)
            conditions = [ self.p_key_fields[field] == valor for field,valor in self.identifiers_values]
            if not blob_fields:
                affectedRows = self.db(reduce(lambda a, b: (a & b), conditions)).update(
                    **self.contentWithValidParameters())
            else:
                parameters = self.contentWithValidParameters() #TODO Funciona atualização de blob?

                stmt = self.db(reduce(lambda a, b: (a & b), conditions))._update(**parameters)
                affectedRows = self.db.executesql(stmt, self.blob_values(parameters, blob_fields))
                # TODO As entradas são atualizadas corretamente, mas rowcount retorna -1 O.o
        except SyntaxError:
            self.db.rollback()
            raise HTTP(http.NO_CONTENT, "Nenhum conteúdo foi passado")
        except Exception:
            self.db.rollback()
            raise HTTP(http.UNPROCESSABLE_ENTITY, "Algum parâmetro possui tipo inválido")
        if affectedRows == 0:
            raise HTTP(http.NOT_FOUND, "Ooops... A princesa está em um castelo com outro ID.")
        else:
            self.db.commit()
            headers = {"Affected": affectedRows}
            raise HTTP(http.OK, "Conteúdo atualizado com sucesso", **headers)


class APIDelete(APIAlterOperation):
    def __init__(self, request):
        """
        Classe responsável por lidar com requisições do tipo DELETE, que serão transformadas
        em um DELETE no banco de dados e retornarão uma resposta HTTP adequada a remoção de um recurso.
        :type request: APIRequest
        """
        super(APIDelete, self).__init__(request)
        if not self.primarykeyInParameters(self.parameters):
            raise HTTP(http.BAD_REQUEST, "Não é possível remover um conteúdo sem sua chave primária.")
        self.identifiers_values = [ (column, request.request.vars[column]) for column in self.p_key_columns]

    def execute(self):
        """
        O método realiza a remoção de uma entrada no banco de dados e retorna HTTP Status Code 200 (OK) caso
        o conteúdo seja removido com sucesso. A chave primária deve estar contida na lista de parâmetros e a mesma
        é utilizada para remoção.

        :rtype : HTTP
        :raise HTTP: 422 Ocorre haja incompatibilidade entre o tipo de dados da coluna e o valor passsado
        :raise HTTP: 404 A chave primária informada é inválida e nenhuma entrada foi afetada
        :raise HTTP: 403 A linha requisitada não pode ser deletada porque possui dependências que não foram atendidas
        """
        try:
            conditions = [ self.p_key_fields[field] == valor for field,valor in self.identifiers_values]
            affectedRows = self.db(reduce(lambda a, b: (a & b), conditions)).delete()
            print self.db._lastsql
        except Exception:
            self.db.rollback()
            raise HTTP(http.INTERNAL_SERVER_ERROR, "Não foi possível deletar.")
        if affectedRows == 0:
            raise HTTP(http.NO_CONTENT, "Ooops... A princesa está em um castelo com outro ID.")
        else:
            self.db.commit()
            headers = {"Affected": affectedRows}
            raise HTTP(http.OK, "Conteúdo atualizado com sucesso", **headers)

    def contentWithValidParameters(self):
        # TODO Retirar a obrigação de implementar esse cara aqui.
        pass

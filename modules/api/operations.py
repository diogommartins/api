# coding=utf-8
import base64
import os
import tempfile
import subprocess
import shutil
from datetime import datetime, date
from gluon import current, HTTP
import abc
from gluon.serializers import json
import gambiarras

try:
    import httplib as http
except ImportError:
    import http.client as http

__all__ = ['Delete', 'Insert', 'Select', 'Update', 'AlterOperation']


class OperationObserver(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def did_finish_successfully(self, sender, parameters):
        """
        :param sender: The APIOperation that triggered the websocket notification
        :type sender: Operation
        :type parameters: dict
        """
        raise NotImplementedError

    @abc.abstractmethod
    def did_finish_with_error(self, sender, parameters, error):
        """
        :param sender: The APIOperation that triggered the websocket notification
        :type sender: Operation
        :type parameters: dict
        :type error: Exception
        """
        raise NotImplementedError


class Operation(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, request):
        """
        :type request: APIRequest
        :type endpoint: str
        :param endpoint: Str relativa ao nome da tabela modela no banco datasource
        """
        self.request = request
        self.endpoint = self.request.endpoint
        self.db = current.datasource
        self.table = self.db[self.endpoint]

    @property
    def base_endpoint_uri(self):
        return current.request.env.http_host + current.request.env.PATH_INFO + "/"

    # TODO Isso não deveria existir aqui, já que é relacionado somente ao SIE
    @property
    def default_fields_for_sie_tables(self):
        """
        Campos que obrigatoriamente devem ser preenchidos em um INSERT e devem ser feitos pela API.

        :rtype : dict
        :return: Um dicionário de parãmetros padrões
        """
        opcoes_default = {
            "concorrencia": 999,  # Pode ser qualquer valor aqui segundo consultoria feita junto à Sintese.
            "dt_alteracao": str(date.today()),
            "hr_alteracao": datetime.now().time().strftime("%H:%M:%S"),
            "endereco_fisico": current.request.env.remote_addr
        }

        if not self.request.request.post_vars.COD_OPERADOR:
            # todo: Workaround enquanto outros projetos não colocam isso via api_client
            opcoes_default["COD_OPERADOR"] = 1

        return opcoes_default

    @property
    def _unique_identifier_column(self):
        # todo: único item ou lista ? Para considerarmos composite keys....
        return self.table._primarykey[0]

    @abc.abstractmethod
    def execute(self):
        raise NotImplementedError("Should be implemented on subclasses")


class AlterOperation(Operation):
    __metaclass__ = abc.ABCMeta

    observer = None  # type: OperationObserver

    def __init__(self, request):
        super(AlterOperation, self).__init__(request)
        self.parameters = self.request.parameters
        try:
            self.p_key_fields = {column:self.table[column] for column in self.table._primarykey}
            self.p_key_columns = self.table._primarykey  # lista de colunas que sao primary keys.
        except (AttributeError, IndexError):
            # TODO IndexError = sem chave primaria. Liberar exception diferente?
            HTTP(http.BAD_REQUEST, "O Endpoint requisitado não possui uma chave primária válida para esta operação.")

        # Comentário deve ser removido quando todas as aplicações estiverem com api_client atualizados
        # if 'COD_OPERADOR' not in self.parameters['valid']:
        #     HTTP(http.BAD_REQUEST, "A requisição não possui um COD_OPERADOR")

    def primary_key_in_parameters(self, parameters):
        """
        Método utilizado para validar se a chave primária encontra-se na lista de parâmetros

        :type parameters: dict
        :rtype : bool
        """
        return set(self.p_key_columns).issubset(set(parameters['valid']))

    @abc.abstractproperty
    def content_with_valid_parameters(self):
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

    @staticmethod
    def blob_values(parameters, fields):
        """
        Retorna uma tupla de valores correpondentes aos campos blob a serem usados em um prepared statement
        :type parameters: dict
        :type fields: list or tuple
        :rtype : tuple
        """

        return tuple(base64.b64decode(parameters[k]) for k in fields)


class Select(Operation):
    ENTRIES_PER_QUERY_DEFAULT = 10

    __sorting_options = ("ASC", "DESC",)

    # TODO rever documetação
    def __init__(self, request):
        """
        :type request: request.APIRequest
        :var endpoint: string relativa ao nome da tabela modela no banco datasource
        :var fields: Uma lista de colunas que devem ser retornadas pela consulta
        """
        super(Select, self).__init__(request)
        self.fields = self.request.parameters['valid']
        self.special_fields = self.request.parameters['special']
        self.request_vars = self.request.lower_vars
        # type: key.Key
        self.api_key = self.request.api_key
        self.return_fields = self.request.return_fields

    def _utf8_lower(self, string):
        """
        Como python não suporta a chamada .lower() de uma string, tem que se passar por este workaround.
        :param string: a string que se deseja converter.
        :return: string convertida.
        """
        return string.decode('utf-8').lower().encode('utf-8')  # TODO Sim, é uma gambiarra. Só mudando para python 3.

    def _get_query_statement(self):
        """
        O método gera diferentes tipos de consultas para tipos de dados diferentes. Cada tipo de dado gera uma
        condição diferente e própria para o seu tipo.

        :rtype : list
        :return: Uma lista de parâmetros processados de consulta
        """
        conditions = []

        if not self.fields and self.request.id_from_path:
            conditions.append(self.table[self._unique_identifier_column] == self.request.id_from_path)
            return conditions

        # Consultas normais
        for field in self.fields:
            if self.table[field].type == 'string':
                try:
                    if isinstance(self.request_vars[field], list):
                        # TODO: PYTHON 2.x DOESN'T SUPPORT .lower() of unicode strings.
                        lower_encoded_field = map(lambda x: self._utf8_lower(x), self.request_vars[field])
                    else:
                        # TODO PYTHON 2.x DOESN'T SUPPORT .lower() of unicode strings.
                        lower_encoded_field = self._utf8_lower(self.request_vars[field])
                    conditions.append(self.table[field].contains(lower_encoded_field, case_sensitive=False, all=True))
                except UnicodeDecodeError:
                    headers = {"InvalidEncoding": json(dict(campo=field))}
                    raise HTTP(http.BAD_REQUEST, "Encoding do parâmetro é inválido (tem certeza que é utf-8?)",
                               **headers)
            else:
                conditions.append(self.table[field] == self.request_vars[field])

        # Trata condições especiais
        for special_field in self.special_fields:
            field = self.request.special_field_chop(special_field)
            if field:
                if special_field.endswith('_min'):
                    conditions.append(self.table[field] > self.request_vars[special_field])
                elif special_field.endswith('_max'):
                    conditions.append(self.table[field] < self.request_vars[special_field])
                elif special_field.endswith('_set'):
                    conditions.append(self.table[field].belongs(self.request_vars[special_field]))

        return conditions

    def _get_return_table_fields(self):
        """
        :rtype : list
        """
        if len(self.return_fields) > 0:
            return [self.table[field] for field in set(self.return_fields)]
        else:
            return [self.table.ALL]

    def _subset_is_defined(self):
        return {'lmin', 'lmax'}.issubset(self.request_vars)

    def _get_records_subset(self):
        """
        O método processa LMIN e LMAX ou, caso os mesmos não sejam fornecidos, gera-os de acordo com a permissão
        da chave de usuário

        :return: Uma tupla contendo o LIMIT e OFFSET da consulta
        """
        limits = {
            "min": 0,
            "max": self.ENTRIES_PER_QUERY_DEFAULT
        }
        if self._subset_is_defined():
            _min = int(self.request_vars['lmin'])
            _max = int(self.request_vars['lmax'])

            entries_to_limit = self.api_key.max_entries - _max - _min
            limits['max'] = _max if entries_to_limit > 0 else _max + entries_to_limit

        return limits['min'], limits['max']

    def _distinct_style(self):
        """
        Caso o parâmetro DISTINCT seja passado, a função define como será o tratamento. Ao usar DISTINCT, não se deve
        selecionar todos os fields
        :rtype : gluon.DAL.Field
        :return: A forma
        """
        if self.request_vars["distinct"]:
            return True

    def __orderby(self):
        """
        :raises HTTP: http.BAD_REQUEST
        :rtype: str
        """
        order_field = self.request_vars["orderby"]
        sort_order = self.request_vars['sort'] or 'ASC'

        if order_field:
            order_field = order_field.lower()  # todo: Essa é a melhor forma ?
            if order_field not in self.table.fields:
                headers = {"InvalidParameters": json(order_field)}
                raise HTTP(http.BAD_REQUEST, "%s não é um campo válido para ordenação." % order_field, **headers)
            if sort_order not in self.__sorting_options:
                headers = {"InvalidParameters": json(sort_order)}
                raise HTTP(http.BAD_REQUEST, "%s não é uma ordenacão válida." % sort_order, **headers)
            return "%s %s" % (self.table[order_field], sort_order)
        elif self.table._primarykey:
            return self.table._primarykey
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
        conditions = self._get_query_statement()
        records_subset = self._get_records_subset()

        if conditions:
            rows = self.db(reduce(lambda a, b: (a & b), conditions)).select(*self._get_return_table_fields(),
                                                                            limitby=records_subset,
                                                                            distinct=self._distinct_style(),
                                                                            orderby=self.__orderby())
        else:
            rows = self.db().select(*self._get_return_table_fields(),
                                    limitby=records_subset,
                                    distinct=self._distinct_style(),
                                    orderby=self.__orderby())

        if rows:
            print(self.db._lastsql)
            return {"content": rows, "subset": records_subset, "fields": self.table.fields}


class Insert(AlterOperation):
    def __init__(self, request):
        """
        Classe responsável por lidar com requisições do tipo POST, que serão transformadas
        em um INSERT no banco de dados e retornarão uma resposta HTTP adequada a criação do novo
        recurso.

        :type request: APIRequest
        """
        super(Insert, self).__init__(request)
        if self.has_composite_primary_key and not self.primary_key_in_parameters(self.parameters):
            raise HTTP(http.BAD_REQUEST, "Não é possível inserir um conteúdo sem sua chave primária composta.")
        if not self.has_composite_primary_key and self.primary_key_in_parameters(self.parameters):
            raise HTTP(http.BAD_REQUEST, "Não é possível inserir um conteúdo com sua chave primária.")

    @property
    def default_fields_for_sie_insert(self):
        # TODO Isso não deveria existir aqui, já que é relacionado somente ao SIE
        fields = dict(self.default_fields_for_sie_tables)

        if not self.has_composite_primary_key:
            # Se a chave não é composta, procura o próximo valor válido da sequence da pkey para popular a query.
            fields[self._unique_identifier_column] = self.next_value_for_sequence
        return fields

    @property
    def has_composite_primary_key(self):
        return len(self.p_key_columns) > 1

    @property
    def next_value_for_sequence(self):
        """
        Por uma INFELIZ particularidade do DB2 de não possuir auto increment, ao inserir algum novo conteúdo em uma
        tabela, precisamos passar manualmente qual será o valor da nossa surrogate key. O DB2 nos provê a possibilidade
        de uso de SEQUECENCE. A nomenclatura padrão é composta do prefixo `SEQ_` acrescido do nome da tabela relacionada.

        :rtype: int
        :return: Um inteiro correspondente ao próximo ID válido disponível para um INSERT
        """
        return self.db.executesql("SELECT NEXT VALUE FOR DBSM.SEQ_%s FROM SYSIBM.SYSDUMMY1" % self.endpoint)[0][0]

    @property
    def content_with_valid_parameters(self):
        """
        Retorna um dicionário contendo somente os k,v onde k são colunas válidas da tabela em que se quer inserir.
        Esse dicionário também deve conter os campos padrões como IP utilizado par alterar, data e hora...

        :rtype : dict
        """
        content = {column: self.request.lower_vars[column] for column in self.parameters['valid']}
        content.update({k: v for k, v in self.default_fields_for_sie_insert.iteritems() if k in self.table.fields})
        return content

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
                               self._unique_identifier_column, properties_path],
                              stderr=subprocess.STDOUT)

        shutil.rmtree(directory_name)  # os.removedirs não deleta diretório que não esteja vazio.

    def execute(self):
        blob_fields = self.blob_fields(self.parameters)
        parameters = self.content_with_valid_parameters
        blob_values = self.blob_values(parameters, blob_fields)
        try:
            if not blob_fields:
                if self.has_composite_primary_key:
                    self.table.insert(**parameters)
                    # TODO O que podemos retornar no caso de sucesso que faça sentido?
                    new_id = 1
                else:
                    new_id = self.table.insert(**parameters)[self._unique_identifier_column]
            else:
                if self.has_composite_primary_key:
                    raise NotImplementedError  # TODO Precisa atualizar o JAR que faz inserção para lidar id composta
                stmt = self.table._insert(**parameters)
                # Essa inserção funcionará. É necessário reinserir pelo Java pois o arquivo ficará corrompido
                self.db.executesql(stmt, blob_values)
                new_id = parameters[self._unique_identifier_column]

            if self.observer:
                self.observer.did_finish_successfully(self, parameters)
        except Exception as e:
            print(self.db._lastsql)
            print(e)

            self.db.rollback()

            if self.observer:
                self.observer.did_finish_with_error(self, parameters, e)

            raise HTTP(http.BAD_REQUEST, "Não foi possível completar a operação.")
        else:
            self.db.commit()
            if new_id and blob_fields:
                gambiarras.insert_blob(new_id, zip(blob_fields, blob_values), self.table, self._unique_identifier_column)
                # self.insert_blob_fields_callback(new_id, zip(blob_fields, blob_values))  # Reinsere blobs pelo JAVA
            headers = {
                "Location": "%s?%s=%i" % (self.base_endpoint_uri, self._unique_identifier_column, new_id),
                "id": new_id
            }
            raise HTTP(http.CREATED, "Conteúdo inserido com sucesso.", **headers)


class Update(AlterOperation):
    def __init__(self, request):
        """
        Classe responsável por lidar com requisições do tipo PUT, que serão transformadas
        em um UPDATE no banco de dados e retornarão uma resposta HTTP adequada a atualizaçao do recurso.
        :type request: APIRequest

        :raises HTTP: 400 O dicionário `parameters` deve conter obrigatoriamente a primary key da tabela `tablename`
        """
        super(Update, self).__init__(request)
        if not self.primary_key_in_parameters(self.parameters):
            raise HTTP(http.BAD_REQUEST, "Não é possível atualizar um conteúdo sem sua chave primária.")

        self.identifiers_values = [(column, request.lower_vars[column]) for column in self.p_key_columns]

    @property
    def content_with_valid_parameters(self):
        """
        Retorna um dicionário contendo somente os k,v onde k são colunas válidas da tabela em que se quer atualizar.
        Esse dicionário não deve conter a chave primária.

        :rtype : dict
        """
        content = {column: self.request.lower_vars[column] for column in self.parameters['valid'] if
                        column not in self.p_key_columns}
        content.update({k: v for k, v in self.default_fields_for_sie_tables.iteritems() if k in self.table.fields})
        return content

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
        parameters = self.content_with_valid_parameters  # TODO Funciona atualização de blob?
        blob_fields = self.blob_fields(self.parameters)
        conditions = [self.p_key_fields[field] == valor for field, valor in self.identifiers_values]
        try:
            if not blob_fields:
                affected_rows = self.db(reduce(lambda a, b: (a & b), conditions)).update(**parameters)
            else:
                stmt = self.db(reduce(lambda a, b: (a & b), conditions))._update(**parameters)
                affected_rows = self.db.executesql(stmt, self.blob_values(parameters, blob_fields))
                # TODO As entradas são atualizadas corretamente, mas rowcount retorna -1 O.o
        except Exception as e:
            if self.observer:
                self.observer.did_finish_with_error(self, parameters, e)
            self.db.rollback()
            if isinstance(e, SyntaxError):
                raise HTTP(http.NO_CONTENT, "Nenhum conteúdo foi passado")
            else:
                raise HTTP(http.UNPROCESSABLE_ENTITY, "Algum parâmetro possui tipo inválido")
        else:
            self.db.commit()

            if self.observer:
                parameters.update(self.identifiers_values)
                self.observer.did_finish_successfully(self, parameters)

            headers = {"Affected": affected_rows}
            raise HTTP(http.OK, "Conteúdo atualizado com sucesso", **headers)


class Delete(AlterOperation):
    def __init__(self, request):
        """
        Classe responsável por lidar com requisições do tipo DELETE, que serão transformadas
        em um DELETE no banco de dados e retornarão uma resposta HTTP adequada a remoção de um recurso.
        :type request: APIRequest
        """
        super(Delete, self).__init__(request)
        if not self.primary_key_in_parameters(self.parameters) and not self.request.id_from_path:
            raise HTTP(http.BAD_REQUEST, "Não é possível remover um conteúdo sem sua chave primária.")
        self.identifiers_values = [(column, self.request.lower_vars[column]) for column in self.p_key_columns]

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
            conditions = [self.p_key_fields[field] == valor for field, valor in self.identifiers_values]
            affected_rows = self.db(reduce(lambda a, b: (a & b), conditions)).delete()
            print(self.db._lastsql)
        except Exception:
            self.db.rollback()
            raise HTTP(http.INTERNAL_SERVER_ERROR, "Não foi possível deletar.")
        if affected_rows == 0:
            raise HTTP(http.NO_CONTENT, "Ooops... A princesa está em um castelo com outro ID.")
        else:
            self.db.commit()
            headers = {"Affected": affected_rows}
            raise HTTP(http.OK, "Conteúdo atualizado com sucesso", **headers)

    @property
    def content_with_valid_parameters(self):
        # TODO Retirar a obrigação de implementar esse cara aqui.
        return NotImplementedError

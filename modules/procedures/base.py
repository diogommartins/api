# coding=utf-8
import abc
from datetime import datetime, date
from gluon import current


def updates_super(func):
    """
    Invokes method with the same name from super class, that should return a dict, updates it with
    the return from the decorated method and than returns it.

    self_dict = {1:'a', 2: 'b'}
    super_dict = {3:'c'}
    decorated_return = {1:'a', 2: 'b', 3:'c'}

    :param func:
    :return: Dictionary updated with the k:v pairs from super method
    :rtype: dict
    """
    # Todo: Não funciona se encadear decorator em subclasses
    def wrapped(self):
        super_func = getattr(super(self.__class__, self), func.__name__, None)
        super_dict = super_func() if callable(super_func) else {}
        func_dict = func(self)
        func_dict.update(super_dict)
        return func_dict
    return wrapped


class ProcedureDatasetValidator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, procedure):
        """
        :type procedure: BaseProcedure
        """
        self.procedure = procedure

    def is_valid_dataset(self, dataset):
        """
        Checks if every item in the data parameter contains the required field for the requested procedure
        :raises ValueError: If a row has an incorrect set of parameters
        """
        required_fields = self.procedure.required_fields
        if required_fields <= frozenset(dataset.keys()):
            return True
        missing_fields = ','.join(required_fields - frozenset(dataset.keys()))
        raise ValueError("Dataset missing required fields: " + missing_fields)


class BaseProcedure(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, datasource):
        """

        :type datasource: gluon.dal.DAL
        """
        self.datasource = datasource

    @abc.abstractproperty
    def required_fields(self):
        """
        A frozenset of required dictionary keys

        :rtype : frozenset
        """
        raise NotImplementedError("Should be implemented on subclasses")

    @abc.abstractmethod
    def perform_work(self, dataset):
        """
        Something that should be done with dataset

        :returns A json serializable object
        :type dataset: dict
        """
        raise NotImplementedError("Should be implemented on subclasses")

    @staticmethod
    def convert_date_format(date, input_format="%d/%m/%Y", output_format="%Y-%m-%d"):
        """
        :type date: str
        :type output_format: str
        :type input_format: str
        :param date: A date to be converted
        :param input_format: Input format used at `date`
        :param output_format: Output format to be returned
        :rtype : str
        """
        # todo isso não deveria estar aqui... MESMO !
        try:
            input_date = datetime.strptime(date, input_format)
        except ValueError:
            try:
                input_date = datetime.strptime(date, output_format)  # It's already on the output format ?
            except ValueError:
                raise ValueError('"%s" is not a valid date format.' % date)  # Impossible to deal with
        return input_date.strftime(output_format)


class BaseSIEProcedure(BaseProcedure):
    # todo esta classe provavelmente não deveria estar no mesmo arquivo
    __metaclass__ = abc.ABCMeta
    cache = (current.cache.ram, 86400)

    @property
    def constants(self):
        return {
            "DT_ALTERACAO": str(date.today()),
            "HR_ALTERACAO": datetime.now().time().strftime("%H:%M:%S"),
        }

    def _next_value_for_sequence(self, table):
        """
        Por uma INFELIZ particularidade do DB2 de não possuir auto increment, ao inserir algum novo conteúdo em uma
        tabela, precisamos passar manualmente qual será o valor da nossa surrogate key. O DB2 nos provê a possibilidade
        de uso de SEQUECENCE. A nomenclatura padrão é composta do prefixo `SEQ_` acrescido do nome da tabela relacionada.

        :rtype: int
        :return: Um inteiro correspondente ao próximo ID válido disponível para um INSERT
        """
        return self.datasource.executesql("SELECT NEXT VALUE FOR DBSM.SEQ_%s FROM SYSIBM.SYSDUMMY1" % table)[0][0]

    def _dataset_for_table(self, table, dataset):
        """
        :type table: gluon.dal.Table
        :type dataset: dict
        """
        # todo Deveria estar atualizando o dataset aqui? Isso ta cheirando mal....
        dataset.update({table._primarykey[0]: self._next_value_for_sequence(table)})
        table_dataset = {k: v for k, v in dataset.iteritems() if k in table.fields}

        return table_dataset

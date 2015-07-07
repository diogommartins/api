import abc

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
        raise ValueError("Every data row passed should contain the required fields: %s" % str(required_fields))


class BaseProcedure(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, datasource, dataset):
        """

        :type datasource: object
        :type dataset: dict
        """
        self.datasource = datasource
        self.dataset = dataset

    @abc.abstractproperty
    def required_fields(self):
        """
        A frozenset of required dictionary keys

        :rtype : frozenset
        """
        raise NotImplementedError("Should be implemented on subclasses")

    @abc.abstractmethod
    def job(self):
        """
        Something that should be done by every item in self.dataset
        """
        raise NotImplementedError("Should be implemented on subclasses")


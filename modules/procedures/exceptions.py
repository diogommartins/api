class ProcedureException(Exception):
    pass


class ProcedureDatasetException(ProcedureException):
    def __init__(self, dataset, cause):
        """
        :type dataset: dict
        :type cause: Exception
        """
        self.dataset = dataset
        self.cause = cause


class InvalidDatasetException(ProcedureDatasetException):
    pass


class DateConversionException(InvalidDatasetException):
    pass


class UndefinedProcedureException(ProcedureException):
    pass

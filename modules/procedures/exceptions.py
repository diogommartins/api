class ProcedureException(Exception):
    def __init__(self, msg=None, cause=None, *args, **kwargs):
        super(ProcedureException, self).__init__(*args, **kwargs)
        self.msg = msg
        self.cause = cause


class UndefinedProcedureException(ProcedureException):
    pass


class ProcedureDatasetException(ProcedureException):
    def __init__(self, dataset, cause=None):
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




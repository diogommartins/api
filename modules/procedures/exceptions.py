class ProcedureException(Exception):
    def __init__(self, msg='', cause=None, *args, **kwargs):
        super(ProcedureException, self).__init__(*args, **kwargs)
        self.msg = msg
        self.cause = cause

    def __str__(self):
        return self.msg + "\n\tCaused by " + str(type(self.cause)) + ": " + str(self.cause) + "\n\t"


class UndefinedProcedureException(ProcedureException):
    pass


class ProcedureDatasetException(ProcedureException):
    def __init__(self, dataset, cause=None, msg='', *args, **kwargs):
        """
        :type dataset: dict
        :type cause: Exception
        """
        super(ProcedureDatasetException, self).__init__(msg, cause, *args, **kwargs)
        self.dataset = dataset


class InvalidDatasetException(ProcedureDatasetException):
    pass


class DateConversionException(InvalidDatasetException):
    pass




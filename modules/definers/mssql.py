# coding=utf-8
from .base import BaseTableDefiner


class MSSQLTableDefiner(BaseTableDefiner):
    types = {
        'bit': 'boolean',
        'char': 'string',
        'int': 'integer',
        'nchar': 'string',
        'nvarchar': 'string',
        'smallint': 'integer',
        'varchar': 'string'
    }


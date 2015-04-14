# coding=utf-8
from .base import InformationSchema


class PostgreSQLTableDefiner(InformationSchema):
    types = {
        'bigint': 'bigint',
        'bytea': 'blob',
        'character varying': 'string',
        'character': 'boolean',
        'date': 'date',
        'float': 'float',
        'float8': 'double',
        'integer': 'integer',
        'text': 'text',
        'time': 'time',
        'timestamp': 'datetime',
        'timestamp with timezone': 'datetime',
        'timestamp without time zone': 'datetime',
        'varchar': 'string'
    }
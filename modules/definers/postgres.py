# coding=utf-8
from .base import InformationSchema


class PostgreSQLTableDefiner(InformationSchema):
    types = {
        'bigint': 'bigint',
        'bytea': 'blob',
        'boolean': 'boolean',
        'character varying': 'string',
        'character': 'boolean',
        'date': 'date',
        'double precision': 'double',
        'float': 'float',
        'float8': 'double',
        'integer': 'integer',
        'numeric': 'integer',
        'text': 'text',
        'time': 'time',
        'time without time zone': 'time',
        'timestamp': 'datetime',
        'timestamp with timezone': 'datetime',
        'timestamp without time zone': 'datetime',
        'varchar': 'string'
    }
# coding=utf-8
from TableBeautify import TableBeautify


def index():
    response.title = 'API UNIRIO'

    tableBeautify = TableBeautify(datasource)

    accessPermissions = db(db.auth_group).select(db.auth_group.role,
                                                 cache=(cache.ram, 172800),
                                                 cacheable=True).as_list()

    avaiableFields = [{table: datasource[table].fields} for table in datasource.tables]

    return dict(
        accessPermissions=accessPermissions,
        avaiableData=datasource.tables,
        avaiableFields=avaiableFields,
        tabelas=tableBeautify.beautifyDatabaseTables()
    )


def user():
    return dict(form=auth())
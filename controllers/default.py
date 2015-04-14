# coding=utf-8
from TableBeautify import TableBeautify


def index():
    response.title = 'API UNIRIO'

    tableBeautify = TableBeautify(datasource)

    accessPermissions = db(db.auth_group).select(db.auth_group.role,
                                                 cache=(cache.ram, 172800),
                                                 cacheable=True).as_list()

    return dict(
        accessPermissions=accessPermissions,
        avaiableData=datasource.tables,
        tabelas=tableBeautify.beautifyDatabaseTables()
    )


def user():
    return dict(form=auth())
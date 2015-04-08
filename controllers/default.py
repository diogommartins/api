def index():
    from TableBeautify import TableBeautify

    response.title = 'API UNIRIO'

    # Todas as tabelas declaradas
    inSieDeclairedTables = reduce(lambda a, b: (a | b), [datasource.COLUMNS.TABNAME == table for table in datasource.tables])
    descriptions = datasource((datasource.COLUMNS.TABSCHEMA == 'DBSM')
                              & inSieDeclairedTables).select(datasource.COLUMNS.TABNAME,
                                                             datasource.COLUMNS.COLNAME,
                                                             datasource.COLUMNS.REMARKS,
                                                             cache=(cache.ram, 172800),
                                                             cacheable=True)

    tableBeautify = TableBeautify(datasource, descriptions)

    accessPermissions = db(db.auth_group).select(db.auth_group.role).as_list()

    avaiableFields = [{table: datasource[table].fields} for table in datasource.tables]

    return dict(
        accessPermissions=accessPermissions,
        avaiableData=datasource.tables,
        avaiableFields=avaiableFields,
        tabelas=tableBeautify.beautifyDatabaseTables()
    )


def user():
    return dict(form=auth())
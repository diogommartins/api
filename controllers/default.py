def index():
    from TableBeautify import TableBeautify

    response.title = 'API UNIRIO'

    # Todas as tabelas declaradas
    inSieDeclairedTables = reduce(lambda a, b: (a | b), [dbSie.COLUMNS.TABNAME == table for table in dbSie.tables])
    descriptions = dbSie((dbSie.COLUMNS.TABSCHEMA == 'DBSM') & (inSieDeclairedTables)).select(dbSie.COLUMNS.TABNAME,
                                                                                              dbSie.COLUMNS.COLNAME,
                                                                                              dbSie.COLUMNS.REMARKS,
                                                                                              cache=(cache.ram, 172800),
                                                                                              cacheable=True)

    tableBeautify = TableBeautify(dbSie.tables, descriptions)

    accessPermissions = db(db.auth_group).select(db.auth_group.role).as_list()
    avaiableData = dbSie.tables
    avaiableFields = []
    for table in avaiableData:
        avaiableFields.append({table: dbSie[table].fields})

    return dict(
        accessPermissions=accessPermissions,
        avaiableData=avaiableData,
        avaiableFields=avaiableFields,
        tabelas=tableBeautify.beautifyDatabaseTables()
    )

# coding=utf-8
from tables import TableBeautify


def index():
    response.title = 'API UNIRIO'

    roles = db(db.auth_group).select(db.auth_group.role, cache=(cache.ram, 172800), cacheable=True)

    return dict(
        roles=[p.role for p in roles],
        avaiable_data=datasource.tables,
        endpoints=sorted(datasource.tables)
    )


def ajax_endpoint_description():
    endpoint = request.args[0]

    return TableBeautify(datasource).table(endpoint)


def user():
    return dict(form=auth())
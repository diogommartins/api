routes_in = (
    ('/$a/appadmin/$f', '/$a/appadmin/$f'),
    ('/api/users', '/api/users'),
    ('/api/admin', '/api/admin'),
    ('/api/admin/$f', '/api/admin/$f'),
    ('/api/default/$f', '/api/default/$f'),
    ('/api/appadmin', '/api/appadmin'),
    ('/api/sandbox', '/api/sandbox'),
    ('/api/procedure/$f', '/api/procedure'),
    ('/api/log', '/api/log'),
    ('/api/$c', '/api/rest'),
    ('/api/$c/$f', '/api/rest')
)

routes_out = [(x, y) for (y, x) in routes_in]

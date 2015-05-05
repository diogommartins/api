from gluon.serializers import custom_json
try:
    import simplejson as json_parser                # try external module
except ImportError:
    try:
        import json as json_parser                  # try stdlib (Python >= 2.6)
    except:
        import gluon.contrib.simplejson as json_parser    # fallback to pure-Python module


def json(value, default=custom_json):
    value = json_parser.dumps(value, default=default, ensure_ascii=False)
    # replace JavaScript incompatible spacing
    # http://timelessrepo.com/json-isnt-a-javascript-subset
    value.replace(ur'\u2028', '\\u2028').replace(ur'\2029', '\\u2029')

    return value
from gluon.serializers import custom_json
try:
    import simplejson as json_parser                # try external module
except ImportError:
    try:
        import json as json_parser                  # try stdlib (Python >= 2.6)
    except:
        import gluon.contrib.simplejson as json_parser    # fallback to pure-Python module


def json(value, default=custom_json):
    """
    replace JavaScript incompatible spacing http://timelessrepo.com/json-isnt-a-javascript-subset
    """
    return json_parser.dumps(value, default=default, ensure_ascii=False)
import json.encoder as encoder

from gluon.serializers import custom_json


try:
    import simplejson as json_parser                # try external module
except ImportError:
    try:
        import json as json_parser                  # try stdlib (Python >= 2.6)
    except:
        import gluon.contrib.simplejson as json_parser    # fallback to pure-Python module


# Adicionado decode e rstrip a forma normal de encodar strings para json
def custom_encode_basestring_ascii(s):
    def replace(match):
        return encoder.ESCAPE_DCT[match.group(0)]
    return '"' + encoder.ESCAPE.sub(replace, s.decode('utf-8').rstrip()) + '"'

encoder.encode_basestring_ascii = custom_encode_basestring_ascii


def json(value, default=custom_json):
    # replace JavaScript incompatible spacing
    # http://timelessrepo.com/json-isnt-a-javascript-subset
    d = json_parser.dumps(value, default=default)
    return d
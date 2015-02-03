import base64
from gluon.dal.adapters import DB2Adapter


class SIEDB2BaseAdapter(DB2Adapter):
    def parse_blob(self, value, field_type):
        return base64.b64encode(str(value))

    def represent_exceptions(self, obj, fieldtype):
        if fieldtype == 'blob':
            return "BLOB('%s')" % obj
        elif fieldtype == 'datetime':
            super(SIEDB2BaseAdapter, self).represent_exceptions(obj, fieldtype)
        return None
# coding=utf-8
import base64
try:
    from gluon.dal.adapters import DB2Adapter
except ImportError:
    from gluon.dal import DB2Adapter    # Necessário para manter backward compatibility de versões < 2.9.12


class SIEDB2BaseAdapter(DB2Adapter):
    def parse_blob(self, value, field_type):
        return base64.b64encode(str(value))

    def represent_exceptions(self, obj, fieldtype):
        if fieldtype == 'blob':
            return "BLOB('%s')" % obj
        elif fieldtype == 'datetime':
            super(SIEDB2BaseAdapter, self).represent_exceptions(obj, fieldtype)
        return None
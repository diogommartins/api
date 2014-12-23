import base64

from gluon.dal import DB2Adapter


class SIEDB2BaseAdapter(DB2Adapter):
    def parse_blob(self, value, field_type):
        return base64.b64encode(str(value))
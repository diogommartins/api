import base64

from gluon.dal import DAL, BaseAdapter


class DALSIE(DAL):
    def __init__(self, **kwargs):
        super(DALSIE, self).__init__(**kwargs)
        self._adapter = SIEBaseAdapter(db=self, pool_size=0, uri='None', folder=self._folder, db_codec=self._db_codec)


class SIEBaseAdapter(BaseAdapter):
    def parse_blob(self, value, field_type):
        return base64.b64encode(str(value))
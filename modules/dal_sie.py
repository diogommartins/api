# coding=utf-8
import base64
from pydal._compat import hashlib_md5

try:
    from gluon.dal.adapters import DB2Adapter
except ImportError:
    try:
        from pydal.adapters import DB2Adapter
    except ImportError:
        from gluon.dal import DB2Adapter    # Necessário para manter backward compatibility de versões < 2.9.12


class SIEDB2BaseAdapter(DB2Adapter):
    drivers = ('ibm_db_dbi', )

    def parse_blob(self, value, field_type):
        return base64.b64encode(str(value))

    def represent_exceptions(self, obj, fieldtype):
        if fieldtype == 'blob':
            return '?'  # Adiciona placeholder
        if fieldtype == 'datetime':
            super(SIEDB2BaseAdapter, self).represent_exceptions(obj, fieldtype)
        return None

    def select(self, query, fields, attributes):
        force_unicode = attributes.get('force_unicode', False)
        if 'force_unicode' in attributes:
            del attributes['force_unicode']
        sql = self._select(query, fields, attributes)

        if force_unicode:
            sql = sql.decode('utf-8')

        cache = attributes.get('cache', None)
        if cache and attributes.get('cacheable',False):
            del attributes['cache']
            (cache_model, time_expire) = cache
            key = self.uri + '/' + sql
            key = hashlib_md5(key).hexdigest()
            args = (sql,fields,attributes)
            return cache_model(
                key,
                lambda self=self,args=args:self._select_aux(*args),
                time_expire)
        else:
            return self._select_aux(sql,fields,attributes)

    def _insert(self, table, fields):
        return super(SIEDB2BaseAdapter, self)._insert(table, fields).decode('utf-8')

    def _update(self, tablename, query, fields):
        return super(SIEDB2BaseAdapter, self)._update(tablename, query, fields).decode('utf-8')
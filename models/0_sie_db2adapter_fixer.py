# -*- coding: utf-8 -*-
from dal_sie import SIEDB2BaseAdapter

# Necessário para manter backward compatibility de versões < 2.9.12
try:
    from gluon.dal.adapters import ADAPTERS
except ImportError:
    try:
        from pydal.adapters import ADAPTERS
    except ImportError:
        from gluon.dal import ADAPTERS

ADAPTERS.update({
    'db2': SIEDB2BaseAdapter
})
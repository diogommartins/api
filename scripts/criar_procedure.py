# coding=utf-8
import os
import sys


template = """# coding=utf-8
from procedures.base import BaseSIEProcedure, as_transaction


class {cls}(BaseSIEProcedure):
    @property
    def required_fields(self):
        super_required = super({cls}, self).required_fields
        required = {{
            # me complete
        }}
        required.update(super_required)

        return required

    @property
    def constants(self):
        super_consts = super({cls}, self).constants
        consts = {{
            # me complete
        }}
        consts.update(super_consts)
        return consts

    @as_transaction
    def perform_work(self, dataset, commit=False):
        raise NotImplementedError("Precisa ser implementado")
        return dataset
"""

if __name__ == '__main__':
    try:
        cls = sys.argv[1]
    except IndexError:
        print("Você precisa passar como primeiro argumento "
              "o nome da classe(procedure) a ser criado")
        sys.exit(1)

    content = template.format(cls=cls)
    procedures_path = os.path.abspath('../modules/procedures/MUDE_ME.py')

    with open(procedures_path, 'w') as fp:
        fp.write(content)

    print("Arquivo criado em: " + procedures_path)

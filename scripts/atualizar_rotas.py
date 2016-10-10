# coding=utf-8
import shutil
import os


ROUTES_FILE = 'routes.py'
W2P_ROOT_DIR = os.path.realpath('../../../')


if __name__ == '__main__':
    """
    Script simples para automatizar o trabalho de criar as rotas necessárias
    para o correto funcionamento da aplicação
    """
    assert os.path.isfile(ROUTES_FILE)

    destination = os.path.join(W2P_ROOT_DIR, ROUTES_FILE)
    shutil.copyfile(src=ROUTES_FILE, dst=destination)

    print("Arquivo de rotas atualizado em {}".format(destination))

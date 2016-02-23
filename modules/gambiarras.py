# coding=utf-8
import os
import shutil
import subprocess
import tempfile


def insert_blob(new_id, blobs, table, unique_identifier_column):
    """
    Gambiarra para inserir blobs.
    #TODO Deveria funcionar como um campo qualquer, mas não driver do DB2 não funciona.
    #TODO Commits? Rollback?
    :return:
    """

    directory_name = tempfile.mkdtemp()  # cria diretório temporário para copiar arquivos

    def criar_arquivos_temporarios():
        """
        para cada campo blob, cria um arquivo temporário a ser utilizado pelo jar
        que terá como nome a coluna correspondente ao blob
        """
        for field, blob in blobs:
            file_path = os.path.join(directory_name, field)
            f = open(file_path, "wb")
            f.write(blob)
            f.close()

    criar_arquivos_temporarios()
    current_dir = os.path.dirname(os.path.realpath(__file__))

    jar_path = os.path.join(current_dir, "blob.jar")
    properties_path = os.path.join(current_dir, "..", "properties", "1_db_conn.properties")

    # Chama java externo
    subprocess.check_call(["java", "-jar", jar_path, directory_name, str(table), str(new_id),
                           unique_identifier_column, properties_path],
                          stderr=subprocess.STDOUT)

    shutil.rmtree(directory_name)  # os.removedirs não deleta diretório que não esteja vazio.
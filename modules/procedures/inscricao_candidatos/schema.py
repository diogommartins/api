class InscricaoCandidatoPosGraduacaoSchema(object):
    schema = {
        "type": "object",
        "properties": {
            "cpf": {"type": "string"},
            "id_concurso": {"type": "int"},
            "id_conc_edicao": {"type": "int"},
            "id_opcao": {"type": "int"},
            "id_cota_edicao": {"type": "int"},
            "nome_pessoa": {"type": "string"},
            "dt_nascimento": {"type": "date"},
            "estado_civil_item": {"type": "int"},
            "sexo": {"type": "string"},
            "nome_pai": {"type": "string"},
            "nome_mae": {"type": "string"},
            "nacionalidade_item": {"type": "int"},
            "deficiencia_item": {"type": "int"},
            "tipo_sanguineo": {"type": "string"},
            "fator_rh": {"type": "string"},
            "cor_item": {"type": "int"},
            "uf_item": {"type": "int"},
            "id_naturalidade": {"type": "int"},
            "ano_conclusao": {"type": "int"},
            "instituicao_conclusao": {"type": "string"},
            "foto": {
                "type": "string",
                "media": {
                    "binaryEncoding": "base64",
                    "type": "image/png"
                }
            },
            "conteudo_arquivo": {
                "type": "string",
                "media": {
                    "binaryEncoding": "base64"
                }
            }
        },
        "required": [
            "ano_conclusao",
            "conteudo_arquivo",
            "cor_item",
            "cpf",
            "deficiencia_item",
            "dt_nascimento",
            "estado_civil_item",
            "fator_rh",
            "foto",
            "id_conc_edicao",
            "id_concurso",
            "id_cota_edicao",
            "id_naturalidade",
            "id_opcao",
            "instituicao_conclusao",
            "nacionalidade_item",
            "nome_mae",
            "nome_pai",
            "nome_pessoa",
            "sexo",
            "tipo_sanguineo",
            "uf_item"
        ]
    }

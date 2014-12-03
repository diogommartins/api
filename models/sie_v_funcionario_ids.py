dbSie.define_table(
    "V_FUNCIONARIO_IDS",
    Field("ID_USUARIO", "integer"),
    Field("ID_PESSOA", "integer"),
    Field("ID_FUNCIONARIO", "integer"),
    Field("ID_CONTRATO_RH", "integer"),
    Field("CPF", "string"),
    Field("CPF_MASCARA", "string"),
    primarykey=["CPF"],
    migrate=False
)
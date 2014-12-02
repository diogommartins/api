dbSie.define_table(
    "V_FUNCIONARIO_IDS",
    Field("ID_USUARIO", "interger"),
    Field("ID_PESSOA", "interger"),
    Field("ID_FUNCIONARIO", "interger"),
    Field("ID_CONTRATO_RH", "interger"),
    Field("CPF", "string"),
    Field("CPF_MASCARA", "interger"),
    primarykey=["CPF"]
)
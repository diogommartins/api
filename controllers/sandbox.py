from APIOperation import APIInsert

def index():
    op = APIInsert("PROJETOS", {})
    return dict(
        foo = op.nextValueForSequence()
    )
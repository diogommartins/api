@auth.requires_membership('Desenvolvedor')
def refresh_cache():
    endpoints_definer.refresh_cache()
    load_endpoints(write_models=True)

    return dict()

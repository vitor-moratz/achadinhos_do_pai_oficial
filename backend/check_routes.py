from app import create_app
app = create_app()
routes = [r.rule for r in app.url_map.iter_rules() if '/affiliate/' in r.rule]
print('Rotas /affiliate/ registradas:', routes)

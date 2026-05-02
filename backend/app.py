import unicodedata
import re as _re
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import get_db

DEFAULT_SEGMENTS = [
    ("ferramentas", "Ferramentas & Manutencao", "\U0001f527", "Ferramentas, reparos e tudo para a oficina em casa"),
    ("automotivo",  "Automotivo",              "\U0001f697", "Acessorios e cuidados para seu veiculo"),
    ("pet-shop",    "Pet Shop",                "\U0001f43e", "O melhor para seus bichinhos"),
    ("casa",        "Casa",                    "\U0001f3e0", "Organizacao, cozinha e tudo para o lar"),
    ("eletronicos", "Eletronicos",             "\u26a1", "Gadgets e tecnologia com custo-beneficio"),
    ("esporte",     "Esporte e Lazer",         "\U0001f4aa", "Para quem curte atividade fisica e aventura"),
    ("games",       "Games e Hobbies",         "\U0001f3ae", "Entretenimento e passatempos"),
    ("moda",        "Moda",                    "\U0001f454", "Roupas, calcados e acessorios para todos os estilos"),
]

DEFAULT_CATEGORIES = {
    "ferramentas": [("Manuais","\U0001f528"),("Eletricas","\U0001f50c"),("Medicao","\U0001f4cf"),("Fixadores","\U0001f529"),("Organizacao","\U0001f5c2"),("Corte e Solda","\u2702")],
    "automotivo":  [("Limpeza","\U0001f9fd"),("Acessorios","\U0001f527"),("Eletronicos","\U0001f4e1"),("Iluminacao","\U0001f4a1"),("Som","\U0001f50a"),("Manutencao","\U0001f6e0")],
    "pet-shop":    [("Comida","\U0001f356"),("Petiscos","\U0001f9b4"),("Brinquedos","\U0001f3be"),("Higiene","\U0001f6c1"),("Cama e Descanso","\U0001f634"),("Transporte","\U0001f392")],
    "casa":        [("Cozinha","\U0001f373"),("Churrasco","\U0001f525"),("Organizacao","\U0001f4e6"),("Limpeza","\U0001f9f9"),("Jardim","\U0001f331"),("Iluminacao","\U0001f4a1"),("Decoracao","\U0001f5bc")],
    "eletronicos": [("Smartphones","\U0001f4f1"),("Audio","\U0001f3a7"),("Computadores","\U0001f4bb"),("Cameras","\U0001f4f7"),("Cabos e Carregadores","\U0001f50c"),("Smart Home","\U0001f3e0")],
    "esporte":     [("Fitness","\U0001f3cb"),("Camping","\u26fa"),("Pesca","\U0001f3a3"),("Ciclismo","\U0001f6b4"),("Futebol","\u26bd")],
    "games":       [("Controles","\U0001f3ae"),("Impressao 3D","\U0001f5a8"),("Drones","\U0001f681"),("Board Games","\U0001f3b2")],
    "moda":        [("Camisetas","\U0001f455"),("Calcados","\U0001f45f"),("Relogios","\u231a"),("Oculos","\U0001f576")],
}

DEFAULT_TAGS = [
    ("destaque","Em Destaque"),("novo","Recem Chegado"),("recomendado","Recomendado pelo Pai"),
    ("melhor_custo","Melhor Custo-Beneficio"),("mais_vendido","Mais Vendido"),
    ("queima","Queima de Estoque"),("limitado","Estoque Limitado"),("imperdivel","Imperdivel"),
]


def _slugify(text):
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    return _re.sub(r"[^a-z0-9]+", "-", ascii_str.lower()).strip("-")


def _seed_defaults():
    from pymongo.errors import DuplicateKeyError
    db = get_db()
    for slug, name, icon, desc in DEFAULT_SEGMENTS:
        db.segments.update_one({"slug": slug}, {"$setOnInsert": {"slug": slug, "name": name, "icon": icon, "description": desc}}, upsert=True)
    for seg_slug, cats in DEFAULT_CATEGORIES.items():
        for name, icon in cats:
            cat_slug = f"{seg_slug}-{_slugify(name)}"
            try:
                db.categories.update_one({"slug": cat_slug, "segment_slug": seg_slug}, {"$setOnInsert": {"name": name, "slug": cat_slug, "icon": icon, "segment_slug": seg_slug}}, upsert=True)
            except DuplicateKeyError:
                pass
    for slug, label in DEFAULT_TAGS:
        db.tags.update_one({"slug": slug}, {"$setOnInsert": {"slug": slug, "label": label, "is_custom": False}}, upsert=True)
    from routes.auth import ensure_first_user
    ensure_first_user()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    CORS(app, origins=app.config["CORS_ORIGINS"])
    JWTManager(app)

    from routes.products import products_bp
    from routes.categories import categories_bp
    from routes.tags import tags_bp
    from routes.shopee import shopee_bp
    from routes.segments import segments_bp
    from routes.auth import auth_bp

    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(shopee_bp)
    app.register_blueprint(segments_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        _seed_defaults()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)

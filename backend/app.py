from flask import Flask
from flask_cors import CORS
from config import Config
from database import get_db

DEFAULT_SEGMENTS = [
    ("ferramentas", "Ferramentas & Manutenção", "🔧", "Ferramentas, reparos e tudo para a oficina em casa"),
    ("automotivo",  "Automotivo",               "🚗", "Acessórios e cuidados para seu veículo"),
    ("pet-shop",    "Pet Shop",                 "🐾", "O melhor para seus bichinhos"),
    ("casa",        "Casa",                     "🏠", "Organização, cozinha e tudo para o lar"),
    ("eletronicos", "Eletrônicos",              "⚡", "Gadgets e tecnologia com custo-benefício"),
    ("esporte",     "Esporte e Lazer",          "💪", "Para quem curte atividade física e aventura"),
    ("games",       "Games e Hobbies",          "🎮", "Entretenimento e passatempos"),
    ("moda",        "Moda Masculina",           "👔", "Estilo e acessórios para o homem"),
]

DEFAULT_CATEGORIES = {
    "ferramentas": [("Manuais","🔨"),("Elétricas","🔌"),("Medição","📏"),("Fixadores","🔩"),("Organização","🗂️"),("Corte e Solda","✂️")],
    "automotivo":  [("Limpeza","🧽"),("Acessórios","🔧"),("Eletrônicos","📡"),("Iluminação","💡"),("Som","🔊"),("Manutenção","🛠️")],
    "pet-shop":    [("Comida","🍖"),("Petiscos","🦴"),("Brinquedos","🎾"),("Higiene","🛁"),("Cama e Descanso","😴"),("Transporte","🎒")],
    "casa":        [("Cozinha","🍳"),("Churrasco","🔥"),("Organização","📦"),("Limpeza","🧹"),("Jardim","🌱"),("Iluminação","💡"),("Decoração","🖼️")],
    "eletronicos": [("Smartphones","📱"),("Áudio","🎧"),("Computadores","💻"),("Câmeras","📷"),("Cabos e Carregadores","🔌"),("Smart Home","🏠")],
    "esporte":     [("Fitness","🏋️"),("Camping","⛺"),("Pesca","🎣"),("Ciclismo","🚴"),("Futebol","⚽")],
    "games":       [("Controles","🎮"),("Impressão 3D","🖨️"),("Drones","🚁"),("Board Games","🎲")],
    "moda":        [("Camisetas","👕"),("Calçados","👟"),("Relógios","⌚"),("Óculos","🕶️")],
}

DEFAULT_TAGS = [
    ("destaque",     "Em Destaque"),
    ("novo",         "Recém Chegado"),
    ("recomendado",  "Recomendado pelo Pai"),
    ("melhor_custo", "Melhor Custo-Benefício"),
    ("mais_vendido", "Mais Vendido"),
    ("queima",       "Queima de Estoque"),
    ("limitado",     "Estoque Limitado"),
    ("imperdivel",   "Imperdível"),
]


def _seed_defaults(db):
    from models.category import slugify

    for slug, name, icon, desc in DEFAULT_SEGMENTS:
        db.segments.update_one(
            {"slug": slug},
            {"$setOnInsert": {"slug": slug, "name": name, "icon": icon, "description": desc}},
            upsert=True,
        )

    for seg_slug, cats in DEFAULT_CATEGORIES.items():
        for name, icon in cats:
            cat_slug = f"{seg_slug}-{slugify(name)}"
            db.categories.update_one(
                {"slug": cat_slug},
                {"$setOnInsert": {"name": name, "slug": cat_slug, "icon": icon,
                                  "segment_slug": seg_slug, "is_custom": False}},
                upsert=True,
            )

    for slug, label in DEFAULT_TAGS:
        db.tags.update_one(
            {"slug": slug},
            {"$setOnInsert": {"slug": slug, "label": label, "is_custom": False}},
            upsert=True,
        )


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=app.config["CORS_ORIGINS"])

    from routes.products   import products_bp
    from routes.categories import categories_bp
    from routes.tags       import tags_bp
    from routes.shopee     import shopee_bp
    from routes.segments   import segments_bp

    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(shopee_bp)
    app.register_blueprint(segments_bp)

    with app.app_context():
        db = get_db()
        # Cria índices para performance
        db.products.create_index([("is_active", 1), ("created_at", -1)])
        db.products.create_index([("segment", 1)])
        db.products.create_index([("category", 1)])
        db.categories.create_index([("slug", 1)], unique=True)
        db.segments.create_index([("slug", 1)], unique=True)
        db.tags.create_index([("slug", 1)], unique=True)
        _seed_defaults(db)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)

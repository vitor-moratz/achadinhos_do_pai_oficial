from flask import Flask
from flask_cors import CORS
from config import Config
from database import db

# (slug, nome, ícone, descrição)
DEFAULT_SEGMENTS = [
    ("ferramentas", "Ferramentas & Manutenção", "🔧", "Ferramentas, reparos e tudo para a oficina em casa"),
    ("automotivo",  "Automotivo",              "🚗", "Acessórios e cuidados para seu veículo"),
    ("pet-shop",    "Pet Shop",                "🐾", "O melhor para seus bichinhos"),
    ("casa",        "Casa",                    "🏠", "Organização, cozinha e tudo para o lar"),
    ("eletronicos", "Eletrônicos",             "⚡", "Gadgets e tecnologia com custo-benefício"),
    ("esporte",     "Esporte e Lazer",         "💪", "Para quem curte atividade física e aventura"),
    ("games",       "Games e Hobbies",         "🎮", "Entretenimento e passatempos"),
    ("moda",        "Moda Masculina",          "👔", "Estilo e acessórios para o homem"),
]

# { segment_slug: [(nome, ícone), ...] }
DEFAULT_CATEGORIES = {
    "ferramentas": [
        ("Manuais",       "🔨"),
        ("Elétricas",     "🔌"),
        ("Medição",       "📏"),
        ("Fixadores",     "🔩"),
        ("Organização",   "🗂️"),
        ("Corte e Solda", "✂️"),
    ],
    "automotivo": [
        ("Limpeza",     "🧽"),
        ("Acessórios",  "🔧"),
        ("Eletrônicos", "📡"),
        ("Iluminação",  "💡"),
        ("Som",         "🔊"),
        ("Manutenção",  "🛠️"),
    ],
    "pet-shop": [
        ("Comida",          "🍖"),
        ("Petiscos",        "🦴"),
        ("Brinquedos",      "🎾"),
        ("Higiene",         "🛁"),
        ("Cama e Descanso", "😴"),
        ("Transporte",      "🎒"),
    ],
    "casa": [
        ("Cozinha",      "🍳"),
        ("Churrasco",    "🔥"),
        ("Organização",  "📦"),
        ("Limpeza",      "🧹"),
        ("Jardim",       "🌱"),
        ("Iluminação",   "💡"),
        ("Decoração",    "🖼️"),
    ],
    "eletronicos": [
        ("Smartphones",        "📱"),
        ("Áudio",              "🎧"),
        ("Computadores",       "💻"),
        ("Câmeras",            "📷"),
        ("Cabos e Carregadores","🔌"),
        ("Smart Home",         "🏠"),
    ],
    "esporte": [
        ("Fitness",   "🏋️"),
        ("Camping",   "⛺"),
        ("Pesca",     "🎣"),
        ("Ciclismo",  "🚴"),
        ("Futebol",   "⚽"),
    ],
    "games": [
        ("Controles",    "🎮"),
        ("Impressão 3D", "🖨️"),
        ("Drones",       "🚁"),
        ("Board Games",  "🎲"),
    ],
    "moda": [
        ("Camisetas", "👕"),
        ("Calçados",  "👟"),
        ("Relógios",  "⌚"),
        ("Óculos",    "🕶️"),
    ],
}

DEFAULT_TAGS = [
    ("destaque",    "Em Destaque"),
    ("novo",        "Recém Chegado"),
    ("recomendado", "Recomendado pelo Pai"),
    ("melhor_custo","Melhor Custo-Benefício"),
    ("mais_vendido","Mais Vendido"),
    ("queima",      "Queima de Estoque"),
    ("limitado",    "Estoque Limitado"),
    ("imperdivel",  "Imperdível"),
]


def _ensure_schema():
    """Se o banco não tem a tabela segments, recria tudo (migração inicial)."""
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    if "segments" not in inspector.get_table_names():
        db.drop_all()
        db.create_all()


def _seed_defaults():
    from models.segment import Segment
    from models.category import Category
    from models.tag import Tag

    for slug, name, icon, desc in DEFAULT_SEGMENTS:
        if not Segment.query.filter_by(slug=slug).first():
            db.session.add(Segment(slug=slug, name=name, icon=icon, description=desc))

    db.session.flush()  # garante IDs disponíveis

    for seg_slug, cats in DEFAULT_CATEGORIES.items():
        for name, icon in cats:
            if not Category.query.filter_by(name=name, segment_slug=seg_slug).first():
                db.session.add(Category(name=name, icon=icon, segment_slug=seg_slug))

    for slug, label in DEFAULT_TAGS:
        if not Tag.query.filter_by(slug=slug).first():
            db.session.add(Tag(slug=slug, label=label))

    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=app.config["CORS_ORIGINS"])
    db.init_app(app)

    from routes.products import products_bp
    from routes.categories import categories_bp
    from routes.tags import tags_bp
    from routes.shopee import shopee_bp
    from routes.segments import segments_bp

    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(shopee_bp)
    app.register_blueprint(segments_bp)

    with app.app_context():
        db.create_all()
        _ensure_schema()
        _seed_defaults()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)



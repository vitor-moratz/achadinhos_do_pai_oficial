# Achadinhos do Pai 🛒

Site de curadoria de produtos afiliados da Shopee. O objetivo é reunir os melhores achados organizados por segmento e categoria, com links de afiliado que geram comissão a cada compra.

## O que é

Um catálogo pessoal de produtos recomendados, integrado à **API de Afiliados da Shopee**. Os produtos podem ser importados diretamente da galeria de afiliados Shopee com categorização automática, ou cadastrados manualmente pelo painel admin.

## Funcionalidades

- Catálogo de produtos por segmento (Moda, Eletrônicos, Casa, Automotivo…) e categoria
- Integração com a **Galeria de Afiliados Shopee** — importação em massa com auto-categorização
- Painel administrativo com gerenciamento de produtos, categorias, segmentos, tags e usuários
- Autenticação JWT com controle de acesso (admin / membro)
- Links de afiliado com rastreamento de cliques

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 18 + Vite + React Router |
| Backend | Flask 3 + Flask-JWT-Extended |
| Banco de dados | MongoDB (PyMongo) |
| Deploy backend | Render |
| Deploy frontend | Vercel |

## Estrutura

```
achadinhos_do_pai_oficial/
├── backend/
│   ├── app.py              # entrypoint Flask
│   ├── config.py           # configurações e variáveis de ambiente
│   ├── database.py         # conexão com MongoDB
│   ├── models/             # schemas dos documentos
│   ├── routes/             # blueprints da API
│   │   ├── auth.py         # login / JWT
│   │   ├── products.py     # CRUD de produtos
│   │   ├── categories.py
│   │   ├── segments.py
│   │   ├── tags.py
│   │   ├── shopee.py       # scraping de produto por URL
│   │   └── affiliate.py    # integração galeria de afiliados Shopee
│   ├── scripts/            # utilitários avulsos (não sobem para produção)
│   │   ├── create_admin.py
│   │   ├── migrate_to_mongo.py
│   │   └── notifications.py
│   ├── requirements.txt
│   ├── Procfile
│   └── render.yaml
└── frontend/
    ├── public/
    └── src/
        ├── components/     # Header, Footer, Sidebar, ProductCard…
        ├── pages/          # HomePage, CategoryPage, AdminPage…
        ├── services/api.js # chamadas ao backend
        └── hooks/useAuth.jsx
```

## Rodando localmente

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
# Disponível em http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Disponível em http://localhost:5173
```

### Variáveis de ambiente (`backend/.env`)

```env
MONGODB_URI=mongodb+srv://...
SECRET_KEY=sua-chave-secreta
CORS_ORIGINS=http://localhost:5173

# Afiliados Shopee
SHOPEE_AFFILIATE_APP_ID=...
SHOPEE_AFFILIATE_SECRET=...
```

## Criar usuário admin

```bash
cd backend
source venv/bin/activate
python3 scripts/create_admin.py
```

## Deploy

- **Backend** → [Render](https://render.com) via `render.yaml` (configurar variáveis de ambiente no painel)
- **Frontend** → [Vercel](https://vercel.com) apontando para a pasta `frontend/`

path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/pages/AdminPage.jsx'
with open(path, 'r') as f:
    content = f.read()

# 1. Adicionar loading state após tags state
content = content.replace(
    "  const [viewMode, setViewMode]     = useState('card')\n  const [activeTab, setActiveTab]   = useState('products')",
    "  const [loading, setLoading]       = useState(true)\n  const [viewMode, setViewMode]     = useState('card')\n  const [activeTab, setActiveTab]   = useState('products')"
)

# 2. Envolver loadAll com setLoading
content = content.replace(
    """  const loadAll = useCallback(() => {
    Promise.all([getProducts(), getSegments(), getCategories(), getTags()])
      .then(([prods, segs, cats, tgs]) => {
        setProducts(prods); setSegments(segs); setCategories(cats); setTags(tgs)
      })
      .catch(() => setStatus({ type: 'error', msg: '⚠️ Erro ao conectar com o servidor.' }))
  }, [])""",
    """  const loadAll = useCallback(() => {
    setLoading(true)
    Promise.all([getProducts(), getSegments(), getCategories(), getTags()])
      .then(([prods, segs, cats, tgs]) => {
        setProducts(prods); setSegments(segs); setCategories(cats); setTags(tgs)
      })
      .catch(() => setStatus({ type: 'error', msg: '⚠️ Erro ao conectar com o servidor.' }))
      .finally(() => setLoading(false))
  }, [])"""
)

# 3. Inserir loading guard antes do bloco de produtos
content = content.replace(
    "          {filteredProducts.length === 0 ? (",
    """          {loading ? (
            <div className="admin-loading">
              <span className="admin-spinner" />
            </div>
          ) : filteredProducts.length === 0 ? ("""
)

# 4. Fechar o ternário extra — o bloco original termina em )} então precisamos
# ajustar o fim. Encontrar o fechamento do bloco e adicionar o parêntese extra.
# O bloco original era: ...} : viewMode === 'list' ? ... : filterSeg ? ... : (...)}
# Agora ficou: {loading ? ... : filteredProducts.length === 0 ? ... : viewMode ... }
# O bloco já tem o ) no final via a estrutura original. Não precisa mexer.

with open(path, 'w') as f:
    f.write(content)

print('loading state added OK')

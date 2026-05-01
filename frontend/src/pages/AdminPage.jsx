import { useState, useEffect, useCallback } from 'react'
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getCategories,
  createCategory,
  getTags,
  createTag,
  fetchShopeeProduct,
  getSegments,
} from '../services/api'
import './AdminPage.css'

const EMPTY_FORM = {
  title: '', description: '', original_price: '', promo_price: '',
  image_url: '', affiliate_link: '', segment: '', category: '', tag: '',
}

export default function AdminPage() {
  const [view, setView] = useState('list')
  const [products, setProducts] = useState([])
  const [segments, setSegments] = useState([])
  const [categories, setCategories] = useState([])
  const [tags, setTags] = useState([])
  const [editingProduct, setEditingProduct] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [shopeeUrl, setShopeeUrl] = useState('')
  const [fetchedUrl, setFetchedUrl] = useState(null)   // URL final confirmada após redirect
  const [fetching, setFetching] = useState(false)
  const [status, setStatus] = useState({ type: '', msg: '' })
  const [showAddCat, setShowAddCat] = useState(false)
  const [newCatName, setNewCatName] = useState('')
  const [newCatIcon, setNewCatIcon] = useState('📦')
  const [showAddTag, setShowAddTag] = useState(false)
  const [newTagLabel, setNewTagLabel] = useState('')

  const loadAll = useCallback(() => {
    Promise.all([getProducts(), getSegments(), getCategories(), getTags()])
      .then(([prods, segs, cats, tgs]) => {
        setProducts(prods)
        setSegments(segs)
        setCategories(cats)
        setTags(tgs)
      })
      .catch(() => {
        setStatus({ type: 'error', msg: '⚠️ Erro ao conectar com o servidor. Verifique se o backend está rodando.' })
      })
  }, [])

  useEffect(() => { loadAll() }, [loadAll])

  function handleChange(e) {
    const { name, value } = e.target
    setForm((prev) => {
      const next = { ...prev, [name]: value }
      // ao trocar segmento, limpa categoria
      if (name === 'segment') next.category = ''
      return next
    })
  }

  function openAdd() {
    setEditingProduct(null)
    setForm(EMPTY_FORM)
    setShopeeUrl('')
    setFetchedUrl(null)
    setStatus({ type: '', msg: '' })
    setShowAddCat(false)
    setShowAddTag(false)
    setView('form')
    window.scrollTo(0, 0)
  }

  function handleEdit(product) {
    setEditingProduct(product)
    setForm({
      title: product.title ?? '',
      description: product.description ?? '',
      original_price: product.original_price?.toString() ?? '',
      promo_price: product.promo_price?.toString() ?? '',
      image_url: product.image_url ?? '',
      affiliate_link: product.affiliate_link ?? '',
      segment: product.segment ?? '',
      category: product.category ?? '',
      tag: product.tag ?? '',
    })
    setShopeeUrl(product.affiliate_link ?? '')
    setFetchedUrl(null)
    setStatus({ type: '', msg: '' })
    setShowAddCat(false)
    setShowAddTag(false)
    setView('form')
    window.scrollTo(0, 0)
  }

  async function handleDelete(id) {
    if (!window.confirm('Remover este produto?')) return
    try {
      await deleteProduct(id)
      setProducts((prev) => prev.filter((p) => p.id !== id))
    } catch {
      alert('Erro ao remover produto.')
    }
  }

  async function handleFetchShopee() {
    if (!shopeeUrl.trim()) return
    setFetching(true)
    setStatus({ type: '', msg: '' })
    setFetchedUrl(null)
    try {
      const data = await fetchShopeeProduct(shopeeUrl.trim())
      setForm((prev) => ({
        ...prev,
        title: data.title || prev.title,
        description: data.description || prev.description,
        image_url: data.image_url || prev.image_url,
        promo_price: data.promo_price?.toString() || prev.promo_price,
        affiliate_link: shopeeUrl.trim(),
      }))
      if (data.final_url) setFetchedUrl(data.final_url)
      setStatus({ type: 'success', msg: '✅ Dados importados! Revise e complete as informações.' })
    } catch {
      setStatus({ type: 'warn', msg: '⚠️ Importação automática não disponível. Preencha manualmente.' })
    } finally {
      setFetching(false)
    }
  }

  async function handleAddCategory() {
    if (!newCatName.trim()) return
    try {
      const cat = await createCategory({ name: newCatName.trim(), icon: newCatIcon.trim() || '📦' })
      setCategories((prev) => [...prev, cat])
      setForm((prev) => ({ ...prev, category: cat.name }))
      setNewCatName('')
      setNewCatIcon('📦')
      setShowAddCat(false)
    } catch (err) {
      alert(err.response?.data?.error || 'Erro ao adicionar categoria')
    }
  }

  async function handleAddTag() {
    if (!newTagLabel.trim()) return
    try {
      const tag = await createTag({ label: newTagLabel.trim() })
      setTags((prev) => [...prev, tag])
      setForm((prev) => ({ ...prev, tag: tag.slug }))
      setNewTagLabel('')
      setShowAddTag(false)
    } catch (err) {
      alert(err.response?.data?.error || 'Erro ao adicionar tag')
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setStatus({ type: '', msg: '' })
    try {
      const payload = {
        ...form,
        // garante affiliate_link mesmo sem clicar em Buscar
        affiliate_link: form.affiliate_link || shopeeUrl.trim(),
        original_price: form.original_price ? parseFloat(form.original_price) : null,
        promo_price: parseFloat(form.promo_price),
      }
      let saved
      if (editingProduct) {
        saved = await updateProduct(editingProduct.id, payload)
        setProducts((prev) => prev.map((p) => (p.id === saved.id ? saved : p)))
      } else {
        saved = await createProduct(payload)
        setProducts((prev) => [saved, ...prev])
      }
      setForm(EMPTY_FORM)
      setEditingProduct(null)
      setShopeeUrl('')
      setView('list')
      setStatus({ type: 'success', msg: editingProduct ? '✅ Produto atualizado!' : '✅ Produto adicionado!' })
    } catch (err) {
      setStatus({ type: 'error', msg: err.response?.data?.error || 'Erro ao salvar produto.' })
    }
  }

  function handleCancel() {
    setForm(EMPTY_FORM)
    setEditingProduct(null)
    setShopeeUrl('')
    setFetchedUrl(null)
    setStatus({ type: '', msg: '' })
    setView('list')
  }

  const activeTagObj = tags.find((t) => t.slug === form.tag)
  const filteredCategories = form.segment
    ? categories.filter((c) => c.segment_slug === form.segment)
    : categories

  // ── LIST VIEW ────────────────────────────────────────────────
  if (view === 'list') {
    return (
      <div className="admin-page">
        <div className="admin-header">
          <h1>Painel Admin</h1>
          <button className="admin-btn-primary" onClick={openAdd}>+ Novo Produto</button>
        </div>

        {status.msg && (
          <div className={`admin-status ${status.type}`}>{status.msg}</div>
        )}

        {products.length === 0 ? (
          <div className="admin-empty">
            <p>Nenhum produto ainda.</p>
            <button className="admin-btn-primary" onClick={openAdd}>Adicionar primeiro produto</button>
          </div>
        ) : (
          <div className="admin-list">
            {products.map((p) => (
              <div key={p.id} className="admin-row">
                <div className="ar-image">
                  {p.image_url
                    ? <img src={p.image_url} alt={p.title} />
                    : <div className="ar-placeholder">🔧</div>
                  }
                </div>
                <div className="ar-info">
                  <p className="ar-title">{p.title}</p>
                  <div className="ar-meta">
                    {p.category && <span className="ar-badge">{p.category}</span>}
                    {p.tag_label && <span className="ar-badge ar-tag">{p.tag_label}</span>}
                    <span className="ar-price">R$ {p.promo_price.toFixed(2)}</span>
                  </div>
                </div>
                <div className="ar-actions">
                  <button className="ar-btn ar-edit" onClick={() => handleEdit(p)}>✏️ Editar</button>
                  <button className="ar-btn ar-del" onClick={() => handleDelete(p.id)}>🗑️</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  // ── FORM VIEW ────────────────────────────────────────────────
  return (
    <div className="admin-page">
      <div className="admin-header">
        <h1>{editingProduct ? '✏️ Editar Produto' : '+ Novo Produto'}</h1>
        <button className="admin-btn-ghost" onClick={handleCancel}>← Voltar</button>
      </div>

      {status.msg && (
        <div className={`admin-status ${status.type}`}>{status.msg}</div>
      )}

      {/* SHOPEE FETCH = AFFILIATE LINK */}
      <div className="admin-shopee-box">
        <label className="admin-label">🔗 Link do Afiliado Shopee *</label>
        <div className="shopee-row">
          <input
            className="admin-input shopee-input"
            value={shopeeUrl}
            onChange={(e) => { setShopeeUrl(e.target.value); setFetchedUrl(null) }}
            placeholder="Cole seu link de afiliado (ex: https://s.shopee.com.br/...)"
          />
          <button
            type="button"
            className="shopee-btn"
            onClick={handleFetchShopee}
            disabled={fetching}
          >
            {fetching ? 'Buscando...' : '🔍 Buscar'}
          </button>
        </div>
        <p className="shopee-hint">
          Cole o link do afiliado e clique em Buscar — o produto será aberto via <strong>seu link</strong>, garantindo sua comissão.
        </p>
        {fetchedUrl && (
          <p className="shopee-confirm">
            🔗 Produto encontrado: <a href={fetchedUrl} target="_blank" rel="noopener noreferrer">{fetchedUrl.replace(/^https?:\/\//, '').slice(0, 60)}&hellip;</a>
          </p>
        )}
      </div>

      <form className="admin-form" onSubmit={handleSubmit}>
        <label className="admin-label">
          Título *
          <input name="title" className="admin-input" value={form.title} onChange={handleChange} required placeholder="Nome do produto" />
        </label>

        <label className="admin-label">
          Descrição
          <textarea name="description" className="admin-input admin-textarea" value={form.description} onChange={handleChange} rows={3} placeholder="Breve descrição (opcional)" />
        </label>

        <div className="admin-row-2" style={{gridTemplateColumns:'1fr'}}>
          <label className="admin-label">
            Preço (R$) *
            <input name="promo_price" type="number" step="0.01" min="0" className="admin-input" value={form.promo_price} onChange={handleChange} required placeholder="Ex: 89.90" />
          </label>
        </div>

        <label className="admin-label">
          URL da imagem
          <input name="image_url" className="admin-input" value={form.image_url} onChange={handleChange} placeholder="https://..." />
          {form.image_url && <img src={form.image_url} alt="preview" className="admin-img-preview" />}
        </label>

        {/* SEGMENT */}
        <label className="admin-label">
          Segmento
          <select name="segment" className="admin-input admin-select" value={form.segment} onChange={handleChange}>
            <option value="">Selecione um segmento</option>
            {segments.map((s) => (
              <option key={s.slug} value={s.slug}>{s.icon} {s.name}</option>
            ))}
          </select>
        </label>

        {/* CATEGORY */}
        <div className="admin-field">
          <label className="admin-label">Categoria</label>
          <select name="category" className="admin-input admin-select" value={form.category} onChange={handleChange}>
            <option value="">Selecione uma categoria</option>
            {filteredCategories.map((c) => (
              <option key={c.id} value={c.name}>{c.icon} {c.name}</option>
            ))}
          </select>
          {!showAddCat ? (
            <button type="button" className="link-add" onClick={() => setShowAddCat(true)}>+ Adicionar nova categoria</button>
          ) : (
            <div className="inline-add">
              <div className="inline-add-inputs">
                <input className="admin-input" value={newCatName} onChange={(e) => setNewCatName(e.target.value)} placeholder="Nome (ex: Camping)" />
                <input className="admin-input icon-input" value={newCatIcon} onChange={(e) => setNewCatIcon(e.target.value)} placeholder="🏕️" maxLength={4} />
              </div>
              <div className="inline-add-actions">
                <button type="button" className="admin-btn-primary admin-btn-sm" onClick={handleAddCategory}>Adicionar</button>
                <button type="button" className="admin-btn-ghost admin-btn-sm" onClick={() => setShowAddCat(false)}>Cancelar</button>
              </div>
            </div>
          )}
        </div>

        {/* TAG */}
        <div className="admin-field">
          <label className="admin-label">
            Tag <small>— aparece como destaque no card do produto</small>
          </label>
          <select name="tag" className="admin-input admin-select" value={form.tag} onChange={handleChange}>
            <option value="">Sem tag</option>
            {tags.map((t) => (
              <option key={t.id} value={t.slug}>{t.label}</option>
            ))}
          </select>
          {activeTagObj && (
            <p className="tag-hint">🏷️ Exibido no card como: <strong>{activeTagObj.label}</strong></p>
          )}
          {!showAddTag ? (
            <button type="button" className="link-add" onClick={() => setShowAddTag(true)}>+ Adicionar nova tag</button>
          ) : (
            <div className="inline-add">
              <input className="admin-input" value={newTagLabel} onChange={(e) => setNewTagLabel(e.target.value)} placeholder="Ex: Super Promoção" />
              <div className="inline-add-actions">
                <button type="button" className="admin-btn-primary admin-btn-sm" onClick={handleAddTag}>Adicionar</button>
                <button type="button" className="admin-btn-ghost admin-btn-sm" onClick={() => setShowAddTag(false)}>Cancelar</button>
              </div>
            </div>
          )}
        </div>

        <div className="admin-form-actions">
          <button type="submit" className="admin-btn-primary admin-btn-lg">
            {editingProduct ? '💾 Salvar Alterações' : '✅ Adicionar Produto'}
          </button>
          <button type="button" className="admin-btn-ghost" onClick={handleCancel}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}

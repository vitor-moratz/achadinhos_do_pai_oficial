import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  getProducts, createProduct, updateProduct, deleteProduct,
  getCategories, createCategory, getTags, createTag,
  fetchShopeeProduct, getSegments,
  getUsers, createUser, deleteUser, updateUserRole,
} from '../services/api'
import { useAuth } from '../hooks/useAuth'
import { CustomSelect } from '../components/CustomSelect'
import './AdminPage.css'

const EMPTY_FORM = {
  title: '', description: '', price_from: '', price_to: '',
  image_url: '', affiliate_link: '', segment: '', category: '', tag: '',
}

function roleLabel(role) {
  return role === 'admin' ? 'Admin' : 'Membro'
}

export default function AdminPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const isAdmin = user?.role === 'admin'

  const [products, setProducts]     = useState([])
  const [segments, setSegments]     = useState([])
  const [categories, setCategories] = useState([])
  const [tags, setTags]             = useState([])
  const [loading, setLoading]       = useState(true)
  const [viewMode, setViewMode]     = useState('card')
  const [activeTab, setActiveTab]   = useState('products')

  const [filterSeg, setFilterSeg]   = useState('')
  const [filterCat, setFilterCat]   = useState('')
  const [filterTag, setFilterTag]   = useState('')
  const [filterText, setFilterText] = useState('')

  const [modalOpen, setModalOpen]           = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [form, setForm]           = useState(EMPTY_FORM)
  const [shopeeUrl, setShopeeUrl] = useState('')
  const [fetchedUrl, setFetchedUrl] = useState(null)
  const [fetching, setFetching]   = useState(false)
  const [status, setStatus]       = useState({ type: '', msg: '' })
  const [showAddCat, setShowAddCat] = useState(false)
  const [newCatName, setNewCatName] = useState('')
  const [newCatIcon, setNewCatIcon] = useState('📦')
  const [showAddTag, setShowAddTag] = useState(false)
  const [newTagLabel, setNewTagLabel] = useState('')

  const [users, setUsers]           = useState([])
  const [userForm, setUserForm]     = useState({ username: '', password: '', role: 'membro' })
  const [userStatus, setUserStatus] = useState({ type: '', msg: '' })
  const [editingUserId, setEditingUserId] = useState(null)

  const loadAll = useCallback(() => {
    setLoading(true)
    Promise.all([getProducts(), getSegments(), getCategories(), getTags()])
      .then(([prods, segs, cats, tgs]) => {
        setProducts(prods); setSegments(segs); setCategories(cats); setTags(tgs)
      })
      .catch(() => setStatus({ type: 'error', msg: '⚠️ Erro ao conectar com o servidor.' }))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { loadAll() }, [loadAll])

  useEffect(() => {
    if (activeTab === 'users' && isAdmin) getUsers().then(setUsers).catch(() => {})
  }, [activeTab, isAdmin])

  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape') closeModal() }
    if (modalOpen) document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [modalOpen])

  useEffect(() => { setFilterCat(''); setFilterTag('') }, [filterSeg])

  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      if (filterSeg  && p.segment  !== filterSeg)  return false
      if (filterCat  && p.category !== filterCat)  return false
      if (filterTag  && p.tag      !== filterTag)   return false
      if (filterText) {
        const q = filterText.toLowerCase()
        if (!p.title?.toLowerCase().includes(q)) return false
      }
      return true
    })
  }, [products, filterSeg, filterCat, filterTag, filterText])

  const availableCats = useMemo(() => {
    return filterSeg ? categories.filter((c) => c.segment_slug === filterSeg) : categories
  }, [categories, filterSeg])

  const availableTags = useMemo(() => {
    const slugsInView = new Set(filteredProducts.map((p) => p.tag).filter(Boolean))
    return tags.filter((t) => slugsInView.has(t.slug))
  }, [tags, filteredProducts])

  const groupedBySegment = useMemo(() => {
    if (filterSeg) return null
    const map = new Map()
    filteredProducts.forEach((p) => {
      const key = p.segment || '__none__'
      if (!map.has(key)) map.set(key, [])
      map.get(key).push(p)
    })
    return map
  }, [filteredProducts, filterSeg])

  const segmentMeta = useMemo(() => {
    const m = {}
    segments.forEach((s) => { m[s.slug] = s })
    return m
  }, [segments])

  const hasFilters = filterSeg || filterCat || filterTag || filterText

  function clearFilters() {
    setFilterSeg(''); setFilterCat(''); setFilterTag(''); setFilterText('')
  }

  function openAdd() {
    setEditingProduct(null); setForm(EMPTY_FORM); setShopeeUrl('')
    setFetchedUrl(null); setStatus({ type: '', msg: '' })
    setShowAddCat(false); setShowAddTag(false); setModalOpen(true)
  }

  function handleEdit(product) {
    setEditingProduct(product)
    setForm({
      title: product.title ?? '', description: product.description ?? '',
      price_from: product.price_from?.toString() ?? '',
      price_to: product.price_to?.toString() ?? '',
      image_url: product.image_url ?? '', affiliate_link: product.affiliate_link ?? '',
      segment: product.segment ?? '', category: product.category ?? '', tag: product.tag ?? '',
    })
    setShopeeUrl(product.affiliate_link ?? ''); setFetchedUrl(null)
    setStatus({ type: '', msg: '' }); setShowAddCat(false); setShowAddTag(false); setModalOpen(true)
  }

  function closeModal() {
    setModalOpen(false); setEditingProduct(null); setForm(EMPTY_FORM)
    setShopeeUrl(''); setFetchedUrl(null); setStatus({ type: '', msg: '' })
  }

  function handleChange(e) {
    const { name, value } = e.target
    setForm((prev) => {
      const next = { ...prev, [name]: value }
      if (name === 'segment') next.category = ''
      return next
    })
  }

  async function handleDelete(id) {
    if (!window.confirm('Remover este produto?')) return
    try {
      await deleteProduct(id)
      setProducts((prev) => prev.filter((p) => p.id !== id))
    } catch { alert('Erro ao remover produto.') }
  }

  async function handleFetchShopee() {
    if (!shopeeUrl.trim()) return
    setFetching(true); setStatus({ type: '', msg: '' }); setFetchedUrl(null)
    try {
      const data = await fetchShopeeProduct(shopeeUrl.trim())
      const cleanUrl = data.final_url || shopeeUrl.trim()
      setForm((prev) => ({
        ...prev,
        title: data.title || prev.title, description: data.description || prev.description,
        image_url: data.image_url || prev.image_url,
        price_from: data.promo_price?.toString() || prev.price_from,
        affiliate_link: cleanUrl, segment: data.segment || prev.segment, category: data.category || prev.category,
      }))
      if (data.final_url) setFetchedUrl(data.final_url)
      setStatus({
        type: (data.title || data.image_url) ? 'success' : 'warn',
        msg: (data.title || data.image_url)
          ? '✅ Dados importados! Revise as informações.'
          : '🔗 URL resolvida. Preencha título, preço e imagem manualmente.',
      })
    } catch {
      setStatus({ type: 'warn', msg: '⚠️ Importação automática indisponível. Preencha manualmente.' })
    } finally { setFetching(false) }
  }

  async function handleAddCategory() {
    if (!newCatName.trim()) return
    try {
      const cat = await createCategory({ name: newCatName.trim(), icon: newCatIcon.trim() || '📦' })
      setCategories((prev) => [...prev, cat])
      setForm((prev) => ({ ...prev, category: cat.name }))
      setNewCatName(''); setNewCatIcon('📦'); setShowAddCat(false)
    } catch (err) { alert(err.response?.data?.error || 'Erro ao adicionar categoria') }
  }

  async function handleAddTag() {
    if (!newTagLabel.trim()) return
    try {
      const tag = await createTag({ label: newTagLabel.trim() })
      setTags((prev) => [...prev, tag])
      setForm((prev) => ({ ...prev, tag: tag.slug }))
      setNewTagLabel(''); setShowAddTag(false)
    } catch (err) { alert(err.response?.data?.error || 'Erro ao adicionar tag') }
  }

  async function handleSubmit(e) {
    e.preventDefault(); setStatus({ type: '', msg: '' })
    try {
      const payload = {
        ...form,
        affiliate_link: form.affiliate_link || shopeeUrl.trim(),
        price_from: parseFloat(form.price_from),
        price_to: form.price_to ? parseFloat(form.price_to) : null,
      }
      let saved
      if (editingProduct) {
        saved = await updateProduct(editingProduct.id, payload)
        setProducts((prev) => prev.map((p) => (p.id === saved.id ? saved : p)))
      } else {
        saved = await createProduct(payload)
        setProducts((prev) => [saved, ...prev])
      }
      closeModal()
      setStatus({ type: 'success', msg: editingProduct ? '✅ Produto atualizado!' : '✅ Produto adicionado!' })
    } catch (err) {
      setStatus({ type: 'error', msg: err.response?.data?.error || 'Erro ao salvar produto.' })
    }
  }

  async function handleCreateUser(e) {
    e.preventDefault(); setUserStatus({ type: '', msg: '' })
    try {
      const u = await createUser(userForm)
      setUsers((prev) => [...prev, u])
      setUserForm({ username: '', password: '', role: 'membro' })
      setUserStatus({ type: 'success', msg: '✅ Usuário criado com sucesso!' })
    } catch (err) {
      setUserStatus({ type: 'error', msg: err.response?.data?.error || 'Erro ao criar usuário.' })
    }
  }

  async function handleDeleteUser(id) {
    if (!window.confirm('Remover este usuário?')) return
    try {
      await deleteUser(id)
      setUsers((prev) => prev.filter((u) => u.id !== id))
    } catch (err) { alert(err.response?.data?.error || 'Erro ao remover usuário.') }
  }

  async function handleChangeRole(id, newRole) {
    try {
      const updated = await updateUserRole(id, newRole)
      setUsers((prev) => prev.map((u) => (u.id === id ? updated : u)))
      setEditingUserId(null)
    } catch (err) { alert(err.response?.data?.error || 'Erro ao alterar role.') }
  }

  const filteredCategories = form.segment
    ? categories.filter((c) => c.segment_slug === form.segment)
    : categories

  function ProductCard({ p }) {
    return (
      <div className="ac-card">
        <div className="ac-img">
          {p.image_url ? <img src={p.image_url} alt={p.title} /> : <div className="ac-placeholder">📦</div>}
        </div>
        <div className="ac-body">
          <p className="ac-title">{p.title}</p>
          <div className="ac-meta">
            {p.category && <span className="al-badge">{p.category}</span>}
            {p.tag_label && <span className="al-badge tag">{p.tag_label}</span>}
          </div>
          <p className="ac-price">
            R$ {Number(p.price_from).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            {p.price_to && <> – R$ {Number(p.price_to).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</>}
          </p>
        </div>
        <div className="ac-actions">
          <button className="al-btn al-edit" onClick={() => handleEdit(p)}>Editar</button>
          <button className="al-btn al-del" onClick={() => handleDelete(p.id)}>Remover</button>
        </div>
      </div>
    )
  }

  function ProductRow({ p }) {
    return (
      <div className="al-row">
        <p className="al-title">{p.title}</p>
        <div className="al-actions">
          <button className="al-btn al-edit al-icon" onClick={() => handleEdit(p)} title="Editar">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button className="al-btn al-del al-icon" onClick={() => handleDelete(p.id)} title="Remover">
            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-page">
      <div className="admin-topbar">
        <div className="admin-topbar-left">
          <Link to="/" className="admin-back-btn">← Voltar à loja</Link>
          <h1 className="admin-title">Gerenciar Produtos</h1>
          {user && (
            <span className={`admin-user-badge ${user.role}`}>
              {user.username} · {roleLabel(user.role)}
            </span>
          )}
          <button className="admin-logout-btn" onClick={() => { logout(); navigate('/login') }}>
            Sair
          </button>
        </div>
      </div>

      <div className="admin-tabs">
        <button className={`admin-tab${activeTab === 'products' ? ' active' : ''}`} onClick={() => setActiveTab('products')}>
          Produtos
        </button>
        {isAdmin && (
          <button className={`admin-tab${activeTab === 'users' ? ' active' : ''}`} onClick={() => setActiveTab('users')}>
            Usuários
          </button>
        )}
      </div>

      {status.msg && !modalOpen && (
        <div className={`admin-status ${status.type}`}>{status.msg}</div>
      )}

      {activeTab === 'products' && (
        <>
          <div className="admin-toolbar">
            <button className="admin-btn-primary" onClick={openAdd}>+ Novo Produto</button>
            <div className="admin-view-toggle">
              <button className={`vt-btn${viewMode === 'card' ? ' active' : ''}`} onClick={() => setViewMode('card')} title="Vista cards">⊞</button>
              <button className={`vt-btn${viewMode === 'list' ? ' active' : ''}`} onClick={() => setViewMode('list')} title="Vista lista">☰</button>
            </div>
          </div>

          <div className="admin-filters">
            <div className="filter-field filter-field--search">
              <span className="filter-label">Buscar</span>
              <input
                className="filter-search"
                placeholder="Buscar por título..."
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
              />
            </div>
            <div className="filter-field">
              <span className="filter-label">Segmento</span>
              <CustomSelect
                className="filter-select"
                value={filterSeg}
                onChange={setFilterSeg}
                placeholder="Todos"
                options={[
                  { value: '', label: 'Todos' },
                  ...segments.map((s) => ({ value: s.slug, label: s.name })),
                ]}
              />
            </div>
            <div className="filter-field">
              <span className="filter-label">Categoria</span>
              <CustomSelect
                className="filter-select"
                value={filterCat}
                onChange={setFilterCat}
                placeholder="Todas"
                options={[
                  { value: '', label: 'Todas' },
                  ...availableCats.map((c) => ({ value: c.name, label: c.name })),
                ]}
              />
            </div>
            <div className="filter-field">
              <span className="filter-label">Tag</span>
              <CustomSelect
                className="filter-select"
                value={filterTag}
                onChange={setFilterTag}
                placeholder="Todas"
                options={[
                  { value: '', label: 'Todas' },
                  ...availableTags.map((t) => ({ value: t.slug, label: t.label })),
                ]}
              />
            </div>
            {hasFilters && (
              <div className="filter-field filter-field--clear">
                <span className="filter-label">&nbsp;</span>
                <button className="filter-clear" onClick={clearFilters}>✕ Limpar</button>
              </div>
            )}
          </div>

          <p className="admin-count">
            {filteredProducts.length} produto{filteredProducts.length !== 1 ? 's' : ''}
            {hasFilters && ` · ${products.length} total`}
          </p>

          {loading ? (
            <div className="admin-loading">
              <span className="admin-spinner" />
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="admin-empty">
              {hasFilters
                ? <><p>Nenhum produto encontrado com esses filtros.</p><button className="admin-btn-ghost" onClick={clearFilters}>Limpar filtros</button></>
                : <><p>Nenhum produto ainda.</p><button className="admin-btn-primary" onClick={openAdd}>Adicionar primeiro produto</button></>
              }
            </div>
          ) : viewMode === 'list' ? (
            filterSeg ? (
              <div className="admin-list">
                {filteredProducts.map((p) => <ProductRow key={p.id} p={p} />)}
              </div>
            ) : (
              <div className="admin-segments">
                {Array.from(groupedBySegment.entries()).map(([segSlug, prods]) => {
                  const seg = segmentMeta[segSlug]
                  return (
                    <div key={segSlug} className="segment-group">
                      <div className="segment-group-header">
                        <span className="segment-group-icon">{seg?.icon ?? '📦'}</span>
                        <h2 className="segment-group-title">{seg?.name ?? 'Sem segmento'}</h2>
                        <span className="segment-group-count">{prods.length}</span>
                      </div>
                      <div className="admin-list">
                        {prods.map((p) => <ProductRow key={p.id} p={p} />)}
                      </div>
                    </div>
                  )
                })}
              </div>
            )
          ) : filterSeg ? (
            <div className="admin-cards">
              {filteredProducts.map((p) => <ProductCard key={p.id} p={p} />)}
            </div>
          ) : (
            <div className="admin-segments">
              {Array.from(groupedBySegment.entries()).map(([segSlug, prods]) => {
                const seg = segmentMeta[segSlug]
                return (
                  <div key={segSlug} className="segment-group">
                    <div className="segment-group-header">
                      <span className="segment-group-icon">{seg?.icon ?? '📦'}</span>
                      <h2 className="segment-group-title">{seg?.name ?? 'Sem segmento'}</h2>
                      <span className="segment-group-count">{prods.length}</span>
                    </div>
                    <div className="admin-cards">
                      {prods.map((p) => <ProductCard key={p.id} p={p} />)}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}

      {activeTab === 'users' && isAdmin && (
        <div className="admin-users">
          <h2 className="admin-section-title">Usuários com acesso</h2>
          {userStatus.msg && <div className={`admin-status ${userStatus.type}`}>{userStatus.msg}</div>}
          <div className="user-list">
            {users.map((u) => (
              <div key={u.id} className="user-row">
                <div className="user-info">
                  <span className="user-name">{u.username}</span>
                  {editingUserId === u.id ? (
                    <div className="role-edit-inline">
                      <CustomSelect
                        className="role-select"
                        value={u.role}
                        onChange={(v) => handleChangeRole(u.id, v)}
                        options={[
                          { value: 'admin', label: 'Admin' },
                          { value: 'membro', label: 'Membro' },
                        ]}
                      />
                      <button className="role-cancel-btn" onClick={() => setEditingUserId(null)}>✕</button>
                    </div>
                  ) : (
                    <button
                      className={`user-role ${u.role}`}
                      onClick={() => u.id !== user?.id && setEditingUserId(u.id)}
                      title={u.id !== user?.id ? 'Clique para alterar' : ''}
                      style={{ cursor: u.id !== user?.id ? 'pointer' : 'default' }}
                    >
                      {roleLabel(u.role)}
                    </button>
                  )}
                </div>
                <div className="user-actions">
                  {u.id !== user?.id && (
                    <button className="al-btn al-del" onClick={() => handleDeleteUser(u.id)}>Remover</button>
                  )}
                </div>
              </div>
            ))}
          </div>

          <h2 className="admin-section-title" style={{ marginTop: '32px' }}>Novo usuário</h2>
          <form className="user-form" onSubmit={handleCreateUser}>
            <input className="admin-input" placeholder="Nome de usuário" value={userForm.username}
              onChange={(e) => setUserForm((p) => ({ ...p, username: e.target.value }))} required />
            <input className="admin-input" type="password" placeholder="Senha (mín. 6 caracteres)" value={userForm.password}
              onChange={(e) => setUserForm((p) => ({ ...p, password: e.target.value }))} required />
            <CustomSelect
              className="admin-form-select"
              value={userForm.role}
              onChange={(v) => setUserForm((p) => ({ ...p, role: v }))}
              options={[
                { value: 'membro', label: 'Membro (criar/editar itens)' },
                { value: 'admin', label: 'Admin (acesso total)' },
              ]}
            />
            <button className="admin-btn-primary" type="submit">Criar Usuário</button>
          </form>
        </div>
      )}

      {modalOpen && (
        <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) closeModal() }}>
          <div className="modal-box">
            <div className="modal-header">
              <h2 className="modal-title">{editingProduct ? 'Editar Produto' : 'Novo Produto'}</h2>
              <button className="modal-close" onClick={closeModal} aria-label="Fechar">×</button>
            </div>
            <div className="modal-body">
              {status.msg && <div className={`admin-status ${status.type}`}>{status.msg}</div>}
              <div className="admin-shopee-box">
                <label className="admin-label">🔗 Link do Afiliado Shopee</label>
                <div className="shopee-row">
                  <input className="admin-input shopee-input" value={shopeeUrl}
                    onChange={(e) => { setShopeeUrl(e.target.value); setFetchedUrl(null) }}
                    placeholder="https://s.shopee.com.br/..." />
                  <button type="button" className="shopee-btn" onClick={handleFetchShopee} disabled={fetching}>
                    {fetching ? '...' : '🔍 Buscar'}
                  </button>
                </div>
                {fetchedUrl && (
                  <p className="shopee-confirm">🔗 <a href={fetchedUrl} target="_blank" rel="noopener noreferrer">{fetchedUrl.replace(/^https?:\/\//, '').slice(0, 55)}…</a></p>
                )}
              </div>
              <form id="product-form" className="admin-form" onSubmit={handleSubmit}>
                <label className="admin-label">Título *
                  <input name="title" className="admin-input" value={form.title} onChange={handleChange} required placeholder="Nome do produto" />
                </label>
                <label className="admin-label">Descrição
                  <textarea name="description" className="admin-input admin-textarea" value={form.description} onChange={handleChange} rows={3} placeholder="Breve descrição (opcional)" />
                </label>
                <div className="admin-price-row">
                  <label className="admin-label">Valor Inicial (R$) *
                    <input name="price_from" type="number" step="0.01" min="0" className="admin-input" value={form.price_from} onChange={handleChange} required placeholder="Ex: 89,90" />
                  </label>
                  <label className="admin-label">Valor Final (R$)
                    <input name="price_to" type="number" step="0.01" min="0" className="admin-input" value={form.price_to} onChange={handleChange} placeholder="Ex: 129,90 (opcional)" />
                  </label>
                </div>
                <label className="admin-label">URL da imagem
                  <input name="image_url" className="admin-input" value={form.image_url} onChange={handleChange} placeholder="https://..." />
                  {form.image_url && <img src={form.image_url} alt="preview" className="admin-img-preview" />}
                </label>
                <label className="admin-label">Segmento
                  <CustomSelect
                    className="admin-form-select"
                    value={form.segment}
                    onChange={(v) => handleChange({ target: { name: 'segment', value: v } })}
                    placeholder="Selecione um segmento"
                    options={[
                      { value: '', label: 'Selecione um segmento' },
                      ...segments.map((s) => ({ value: s.slug, label: s.name })),
                    ]}
                  />
                </label>
                <div className="admin-field">
                  <label className="admin-label">Categoria</label>
                  <CustomSelect
                    className="admin-form-select"
                    value={form.category}
                    onChange={(v) => handleChange({ target: { name: 'category', value: v } })}
                    placeholder="Selecione uma categoria"
                    options={[
                      { value: '', label: 'Selecione uma categoria' },
                      ...filteredCategories.map((c) => ({ value: c.name, label: c.name })),
                    ]}
                  />
                  {!showAddCat ? (
                    <button type="button" className="link-add" onClick={() => setShowAddCat(true)}>+ Nova categoria</button>
                  ) : (
                    <div className="inline-add">
                      <div className="inline-add-inputs">
                        <input className="admin-input" value={newCatName} onChange={(e) => setNewCatName(e.target.value)} placeholder="Nome (ex: Camping)" />
                        <input className="admin-input icon-input" value={newCatIcon} onChange={(e) => setNewCatIcon(e.target.value)} placeholder="🏕️" maxLength={4} />
                      </div>
                      <div className="inline-add-btns">
                        <button type="button" className="admin-btn-primary" onClick={handleAddCategory}>Salvar</button>
                        <button type="button" className="admin-btn-ghost" onClick={() => setShowAddCat(false)}>Cancelar</button>
                      </div>
                    </div>
                  )}
                </div>
                <div className="admin-field">
                  <label className="admin-label">Tag</label>
                  <CustomSelect
                    className="admin-form-select"
                    value={form.tag}
                    onChange={(v) => handleChange({ target: { name: 'tag', value: v } })}
                    placeholder="Sem tag"
                    options={[
                      { value: '', label: 'Sem tag' },
                      ...tags.map((t) => ({ value: t.slug, label: t.label })),
                    ]}
                  />
                  {!showAddTag ? (
                    <button type="button" className="link-add" onClick={() => setShowAddTag(true)}>+ Nova tag</button>
                  ) : (
                    <div className="inline-add">
                      <input className="admin-input" value={newTagLabel} onChange={(e) => setNewTagLabel(e.target.value)} placeholder="Nome da tag" />
                      <div className="inline-add-btns">
                        <button type="button" className="admin-btn-primary" onClick={handleAddTag}>Salvar</button>
                        <button type="button" className="admin-btn-ghost" onClick={() => setShowAddTag(false)}>Cancelar</button>
                      </div>
                    </div>
                  )}
                </div>
              </form>
            </div>
            <div className="modal-footer">
              <button type="button" className="admin-btn-ghost" onClick={closeModal}>Cancelar</button>
              <button type="submit" form="product-form" className="admin-btn-primary">
                {editingProduct ? 'Salvar alterações' : 'Adicionar produto'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

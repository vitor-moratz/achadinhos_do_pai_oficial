import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getSegments, getSegmentCategories, getProducts } from '../services/api'
import ProductCard from '../components/ProductCard'
import './SegmentPage.css'

export default function SegmentPage() {
  const { slug } = useParams()
  const [segment, setSegment] = useState(null)
  const [categories, setCategories] = useState([])
  const [products, setProducts] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setActiveCategory(null)
    setSearch('')
    getSegments()
      .then((segs) => setSegment(segs.find((s) => s.slug === slug) || null))
      .catch(() => {})
    getSegmentCategories(slug)
      .then(setCategories)
      .catch(() => {})
  }, [slug])

  useEffect(() => {
    setLoading(true)
    const params = { segment: slug }
    if (activeCategory) params.category = activeCategory
    if (search) params.search = search

    getProducts(params)
      .then(setProducts)
      .catch(() => setProducts([]))
      .finally(() => setLoading(false))
  }, [slug, activeCategory, search])

  return (
    <div className="segment-page">
      <div className="seg-hero">
        <div className="container">
          {segment ? (
            <>
              <span className="seg-hero-icon">{segment.icon}</span>
              <h1 className="seg-hero-title">{segment.name}</h1>
              {segment.description && (
                <p className="seg-hero-desc">{segment.description}</p>
              )}
            </>
          ) : (
            <h1 className="seg-hero-title">Carregando...</h1>
          )}
        </div>
      </div>

      <div className="container seg-body">
        {categories.length > 0 && (
          <div className="seg-cats">
            <button
              className={`seg-cat-pill${activeCategory === null ? ' active' : ''}`}
              onClick={() => setActiveCategory(null)}
            >
              Todos
            </button>
            {categories.map((c) => (
              <button
                key={c.slug}
                className={`seg-cat-pill${activeCategory === c.slug ? ' active' : ''}`}
                onClick={() => setActiveCategory(c.slug)}
              >
                {c.icon} {c.name}
              </button>
            ))}
          </div>
        )}

        <div className="seg-toolbar">
          <p className="seg-count">
            {loading
              ? 'Carregando...'
              : `${products.length} produto${products.length !== 1 ? 's' : ''}`}
          </p>
          <input
            className="seg-search"
            type="search"
            placeholder="Buscar neste segmento..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <p className="state-text">Carregando...</p>
        ) : products.length === 0 ? (
          <p className="state-text">
            Nenhum produto nesse segmento ainda. Em breve mais achadinhos! 🔧
          </p>
        ) : (
          <div className="products-grid">
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
        </div>
        )}
      </div>
    </div>
  )
}

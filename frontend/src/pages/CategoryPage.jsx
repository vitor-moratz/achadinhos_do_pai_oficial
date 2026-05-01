import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getProducts, getCategories } from '../services/api'
import ProductCard from '../components/ProductCard'
import './CategoryPage.css'

export default function CategoryPage() {
  const { slug } = useParams()
  const [meta, setMeta] = useState({ name: slug, icon: '📦', desc: '' })
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getCategories().then((cats) => {
      const found = cats.find((c) => c.slug === slug)
      if (found) setMeta({ name: found.name, icon: found.icon, desc: '' })
    }).catch(() => {})
  }, [slug])

  useEffect(() => {
    setLoading(true)
    const params = { category: slug }
    if (search) params.search = search

    getProducts(params)
      .then(setProducts)
      .catch(() => setProducts([]))
      .finally(() => setLoading(false))
  }, [slug, search])

  return (
    <div className="category-page">
      <div className="cat-hero">
        <div className="container">
          <span className="cat-hero-icon">{meta.icon}</span>
          <h1 className="cat-hero-title">{meta.name}</h1>
        </div>
      </div>

      <div className="container cat-body">
        <div className="cat-toolbar">
          <p className="cat-count">
            {loading ? 'Carregando...' : `${products.length} produto${products.length !== 1 ? 's' : ''}`}
          </p>
          <input
            className="cat-search"
            type="search"
            placeholder="Buscar nesta categoria..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <p className="state-text">Carregando...</p>
        ) : products.length === 0 ? (
          <p className="state-text">Nenhum produto nessa categoria ainda. Em breve mais achadinhos! 🔧</p>
        ) : (
          <div className="products-grid">
            {products.map((p) => <ProductCard key={p.id} product={p} />)}
          </div>
        )}
      </div>
    </div>
  )
}

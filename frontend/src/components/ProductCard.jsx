import { Link } from 'react-router-dom'
import { registerClick } from '../services/api'
import './ProductCard.css'

export default function ProductCard({ product }) {
  // Usa tag_label vindo da API, ou formata o slug como fallback
  const tagLabel = product.tag_label
    ?? (product.tag ? product.tag.replace(/_/g, ' ') : null)

  async function handleBuy(e) {
    e.preventDefault()
    try {
      const { affiliate_link } = await registerClick(product.id)
      window.open(affiliate_link, '_blank', 'noopener,noreferrer')
    } catch {
      window.open(product.affiliate_link, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <article className="product-card">
      <div className="card-badges">
        {tagLabel && <span className="badge badge-tag">{tagLabel}</span>}
      </div>

      <Link to={`/produto/${product.id}`} className="card-image-link">
        <div className="card-image">
          {product.image_url ? (
            <img src={product.image_url} alt={product.title} loading="lazy" />
          ) : (
            <div className="card-image-placeholder" aria-hidden="true">🔧</div>
          )}
        </div>
      </Link>

      <div className="card-body">
        <Link to={`/produto/${product.id}`} className="card-title">
          {product.title}
        </Link>

        {(product.segment_name || product.category) && (
          <div className="card-meta">
            {product.segment_name && (
              <span className="card-meta-item card-meta-segment">{product.segment_name}</span>
            )}
            {product.category && (
              <span className="card-meta-item card-meta-category">{product.category}</span>
            )}
          </div>
        )}

        <div className="card-prices">
          <span className="price-promo">
            R$ {Number(product.price_from).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            {product.price_to && ` – R$ ${Number(product.price_to).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          </span>
        </div>

        <button className="btn-shopee" onClick={handleBuy}>
          Ver na Shopee
        </button>
      </div>
    </article>
  )
}

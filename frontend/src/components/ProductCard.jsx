import { Link } from 'react-router-dom'
import { registerClick } from '../services/api'
import './ProductCard.css'

export default function ProductCard({ product }) {
  const discount =
    product.original_price && product.promo_price
      ? Math.round(
          ((product.original_price - product.promo_price) / product.original_price) * 100
        )
      : null

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
        {discount && <span className="badge badge-discount">-{discount}%</span>}
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

        <div className="card-prices">
          {product.original_price && (
            <span className="price-original">R$ {product.original_price.toFixed(2)}</span>
          )}
          <span className="price-promo">R$ {product.promo_price.toFixed(2)}</span>
        </div>

        <button className="btn-shopee" onClick={handleBuy}>
          Ver na Shopee
        </button>
      </div>
    </article>
  )
}

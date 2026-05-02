import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProduct, registerClick } from '../services/api'
import './ProductPage.css'

export default function ProductPage() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getProduct(id)
      .then(setProduct)
      .catch(() => setProduct(null))
      .finally(() => setLoading(false))
  }, [id])

  async function handleBuy() {
    try {
      const { affiliate_link } = await registerClick(product.id)
      window.open(affiliate_link, '_blank', 'noopener,noreferrer')
    } catch {
      window.open(product.affiliate_link, '_blank', 'noopener,noreferrer')
    }
  }

  if (loading) return <p className="pp-state">Carregando...</p>
  if (!product) return (
    <div className="pp-state">
      <p>Produto não encontrado.</p>
      <Link to="/" className="pp-back">← Voltar ao início</Link>
    </div>
  )

  const discount = null  // modelo de desconto removido

  return (
    <div className="pp-wrapper">
      <div className="container pp-inner">
        <Link to={product.category ? `/categoria/${product.category}` : '/'} className="pp-breadcrumb">
          ← Voltar
        </Link>

        <div className="pp-layout">
          {/* IMAGE */}
          <div className="pp-image">
            {product.image_url ? (
              <img src={product.image_url} alt={product.title} />
            ) : (
              <div className="pp-image-placeholder" aria-hidden="true">🔧</div>
            )}
          </div>

          {/* DETAILS */}
          <div className="pp-details">
            {product.tag && <span className="pp-badge">{product.tag}</span>}

            <h1 className="pp-title">{product.title}</h1>

            {product.description && (
              <p className="pp-description">{product.description}</p>
            )}

            <div className="pp-prices">
              <span className="pp-promo">R$ {Number(product.price_from).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              {product.price_to && (
                <span className="pp-price-sep">–</span>
              )}
              {product.price_to && (
                <span className="pp-promo">R$ {Number(product.price_to).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              )}
            </div>

            <div className="pp-trust">
              <span>✅ Selecionado pelo Pai</span>
              <span>✅ Custo-benefício aprovado</span>
            </div>

            <button className="pp-btn" onClick={handleBuy}>
              🛒 Comprar na Shopee
            </button>

            <p className="pp-disclaimer">
              Link afiliado — você paga o mesmo preço, sem custo extra.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

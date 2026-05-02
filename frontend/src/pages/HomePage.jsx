import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getProducts, getSegments } from '../services/api'
import { WHATSAPP_URL, TELEGRAM_URL, INSTAGRAM_URL } from '../constants'
import { WhatsAppIcon, TelegramIcon, InstagramIcon } from '../components/SocialIcons'
import ProductCard from '../components/ProductCard'
import './HomePage.css'

export default function HomePage() {
  const [featured, setFeatured] = useState([])
  const [segments, setSegments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getProducts(), getSegments()])
      .then(([all, segs]) => {
        setFeatured(all.slice(0, 8))
        setSegments(segs)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="home">

      {/* ── HERO ─────────────────────────────────────────── */}
      <section className="hero">
        <div className="container hero-inner">
          <div className="hero-content">
            <span className="hero-badge">🛒 Achados reais da Shopee — testados antes de chegar aqui</span>
            <h1 className="hero-headline">
              O pai já testou —<br />
              <span className="hero-highlight">você só compra.</span>
            </h1>
            <p className="hero-sub">
              Cada achado aqui foi garimpado, comparado e aprovado.<br />
              Sem enrolação, sem produto duvidoso —{' '}
              <strong>só o que vale o seu dinheiro de verdade.</strong>
            </p>
            <div className="hero-proof">
              <span>Só produto que vale a pena</span>
              <span>Melhor preço da Shopee</span>
              <span>Novos achados toda semana</span>
            </div>
            <div className="hero-actions">
              <Link to="/segmento/ferramentas" className="btn btn-primary">Ver Achadinhos</Link>
              <a
                href={WHATSAPP_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline"
              >
                Entrar no WhatsApp
              </a>
            </div>
          </div>
          <div className="hero-visual" aria-hidden="true">
            <div className="hero-logo-card">
              <img src="/logo.png" alt="Achadinhos do Pai" className="hero-logo-img" />
            </div>
          </div>
        </div>
      </section>

      {/* ── SEGMENTS ─────────────────────────────────────── */}
      <section className="section section--white">
        <div className="container">
          <h2 className="section-title">Explore por segmento</h2>
          {segments.length === 0 ? (
            <p className="state-text" style={{ padding: '20px 0' }}>Carregando...</p>
          ) : (
            <div className="segments-grid">
              {segments.map((seg) => (
                <Link key={seg.slug} to={`/segmento/${seg.slug}`} className="segment-card">
                  <span className="seg-card-icon">{seg.icon}</span>
                  <span className="seg-card-label">{seg.name}</span>
                  {seg.description && (
                    <span className="seg-card-desc">{seg.description}</span>
                  )}
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── FEATURED PRODUCTS ────────────────────────────── */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Produtos em destaque</h2>
            <Link to="/segmento/ferramentas" className="link-see-all">Ver todos →</Link>
          </div>
          {loading ? (
            <p className="state-text">Carregando...</p>
          ) : featured.length === 0 ? (
            <p className="state-text">Em breve novos produtos. 🔧</p>
          ) : (
            <div className="products-grid">
              {featured.map((p) => <ProductCard key={p.id} product={p} />)}
            </div>
          )}
        </div>
      </section>

      {/* ── AUTHORITY ────────────────────────────────────── */}
      <section className="section authority-section">
        <div className="container">
          <div className="authority-inner">
            <div className="authority-avatar">👨‍🔧</div>
            <h2 className="authority-title">Por que confiar no Achadinhos do Pai?</h2>
            <p className="authority-sub">
              Aqui não tem produto jogado por aí. Cada item foi escolhido a dedo — só entra o que realmente vale o seu dinheiro.
            </p>
            <ul className="authority-list">
              <li><span>✅</span><span>Sem lixo, sem enrolação — só produto bom</span></li>
              <li><span>✅</span><span>Preço justo, nada superfaturado</span></li>
              <li><span>✅</span><span>Cada um escolhido na mão, um por um</span></li>
              <li><span>✅</span><span>O pai já testou. Você compra com tranquilidade.</span></li>
            </ul>
          </div>
        </div>
      </section>

      {/* ── WHATSAPP CTA ─────────────────────────────────── */}
      <section className="section whatsapp-section">
        <div className="container">
          <div className="whatsapp-box">
            <p className="wa-eyebrow">Não perde nenhum achado</p>
            <h2>Entre na comunidade e não perca nenhum achado</h2>
            <p className="wa-sub">
              Comunidade exclusiva com promoções diárias, novidades e achadinhos antes de todo mundo.
              Gratuito, sem spam.
            </p>
            <div className="wa-cta-buttons">
              <a
                href={WHATSAPP_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary btn-lg"
              >
                <WhatsAppIcon size={20} /> Grupo WhatsApp
              </a>
              {TELEGRAM_URL && (
                <a
                  href={TELEGRAM_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline btn-lg"
                >
                  <TelegramIcon size={20} /> Canal no Telegram
                </a>
              )}
              <a
                href={INSTAGRAM_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline btn-lg"
              >
                <InstagramIcon size={20} /> Instagram
              </a>
            </div>
          </div>
        </div>
      </section>

    </div>
  )
}

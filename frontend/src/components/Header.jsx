import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { WHATSAPP_URL, TELEGRAM_URL, INSTAGRAM_URL } from '../constants'
import { WhatsAppIcon, TelegramIcon, InstagramIcon } from './SocialIcons'
import './Header.css'

const SEGMENTS = [
  { to: '/segmento/automotivo',  label: 'Automotivo' },
  { to: '/segmento/casa',        label: 'Casa' },
  { to: '/segmento/eletronicos', label: 'Eletrônicos' },
  { to: '/segmento/esporte',     label: 'Esporte' },
  { to: '/segmento/ferramentas', label: 'Ferramentas' },
  { to: '/segmento/games',       label: 'Games' },
  { to: '/segmento/moda',        label: 'Moda' },
  { to: '/segmento/pet-shop',    label: 'Pet Shop' },
]

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link to="/" className="header-logo" onClick={() => setMenuOpen(false)}>
          <img src="/logo.png" alt="Achadinhos do Pai" className="logo-img" />
          <span className="logo-text">Achadinhos do Pai</span>
        </Link>

        <div className="header-social">
          {TELEGRAM_URL && (
            <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer" className="header-social-icon" title="Telegram" aria-label="Telegram">
              <TelegramIcon size={26} />
            </a>
          )}
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener noreferrer" className="header-social-icon" title="Instagram" aria-label="Instagram">
            <InstagramIcon size={26} />
          </a>
          <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className="header-cta">
            Entrar no Grupo
          </a>
        </div>

        <button
          className="hamburger"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
          aria-expanded={menuOpen}
        >
          <span /><span /><span />
        </button>
      </div>

      {menuOpen && (
        <nav className="mobile-nav">
          <p className="mobile-nav-section-label">Segmentos</p>
          <div className="mobile-nav-links">
            {SEGMENTS.map((seg) => (
              <NavLink
                key={seg.to}
                to={seg.to}
                className={({ isActive }) =>
                  isActive ? 'mobile-nav-link active' : 'mobile-nav-link'
                }
                onClick={() => setMenuOpen(false)}
              >
                {seg.label}
              </NavLink>
            ))}
          </div>

          <p className="mobile-nav-section-label">Comunidade</p>
          <div className="mobile-nav-social">
            <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className="mobile-social-link whatsapp" onClick={() => setMenuOpen(false)}>
              <WhatsAppIcon size={20} /> Grupo WhatsApp
            </a>
            {TELEGRAM_URL && (
              <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer" className="mobile-social-link telegram" onClick={() => setMenuOpen(false)}>
                <TelegramIcon size={20} /> Canal no Telegram
              </a>
            )}
            <a href={INSTAGRAM_URL} target="_blank" rel="noopener noreferrer" className="mobile-social-link instagram" onClick={() => setMenuOpen(false)}>
              <InstagramIcon size={20} /> Instagram
            </a>
          </div>
        </nav>
      )}
    </header>
  )
}

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { NavLink } from 'react-router-dom'
import { WHATSAPP_URL } from '../constants'
import './Header.css'

const SEGMENTS = [
  { to: '/segmento/ferramentas', icon: '🔧', label: 'Ferramentas' },
  { to: '/segmento/automotivo',  icon: '🚗', label: 'Automotivo' },
  { to: '/segmento/pet-shop',    icon: '🐾', label: 'Pet Shop' },
  { to: '/segmento/casa',        icon: '🏠', label: 'Casa' },
  { to: '/segmento/eletronicos', icon: '⚡', label: 'Eletrônicos' },
  { to: '/segmento/esporte',     icon: '💪', label: 'Esporte' },
  { to: '/segmento/games',       icon: '🎮', label: 'Games' },
  { to: '/segmento/moda',        icon: '👔', label: 'Moda' },
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

        <a
          href={WHATSAPP_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="header-cta"
        >
          💬 Entrar no Grupo
        </a>

        <button
          className="hamburger"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Menu"
          aria-expanded={menuOpen}
        >
          <span /><span /><span />
        </button>
      </div>

      {menuOpen && (
        <div className="mobile-nav">
          {SEGMENTS.map((seg) => (
            <NavLink
              key={seg.to}
              to={seg.to}
              className={({ isActive }) =>
                isActive ? 'mobile-nav-link active' : 'mobile-nav-link'
              }
              onClick={() => setMenuOpen(false)}
            >
              {seg.icon} {seg.label}
            </NavLink>
          ))}
          <a
            href={WHATSAPP_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="header-cta mobile-cta"
            onClick={() => setMenuOpen(false)}
          >
            💬 Entrar no Grupo
          </a>
        </div>
      )}
    </header>
  )
}

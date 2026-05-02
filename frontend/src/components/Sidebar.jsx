import { NavLink } from 'react-router-dom'
import './Sidebar.css'

const SEGMENTS = [
  { to: '/segmento/automotivo',  icon: '🚗', label: 'Automotivo' },
  { to: '/segmento/casa',        icon: '🏠', label: 'Casa' },
  { to: '/segmento/eletronicos', icon: '⚡', label: 'Eletrônicos' },
  { to: '/segmento/esporte',     icon: '💪', label: 'Esporte' },
  { to: '/segmento/ferramentas', icon: '🔧', label: 'Ferramentas' },
  { to: '/segmento/games',       icon: '🎮', label: 'Games' },
  { to: '/segmento/moda',        icon: '👔', label: 'Moda' },
  { to: '/segmento/pet-shop',    icon: '🐾', label: 'Pet Shop' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Segmentos">
      <p className="sidebar-label">Segmentos</p>
      <nav className="sidebar-nav">
        {SEGMENTS.map((seg) => (
          <NavLink
            key={seg.to}
            to={seg.to}
            className={({ isActive }) =>
              isActive ? 'sidebar-link active' : 'sidebar-link'
            }
          >
            {seg.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

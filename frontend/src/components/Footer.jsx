import { Link } from 'react-router-dom'
import { WHATSAPP_URL, TELEGRAM_URL, INSTAGRAM_URL } from '../constants'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <img src="/logo.png" alt="Achadinhos do Pai" className="footer-logo-img" />
            <span>Achadinhos do Pai</span>
          </div>
          <p>Curadoria manual de produtos que realmente valem a pena. O pai já testou — você só compra.</p>
        </div>

        <div className="footer-links">
          <h4>Categorias</h4>
          <Link to="/categoria/ferramentas">Ferramentas</Link>
          <Link to="/categoria/automotivo">Automotivo</Link>
          <Link to="/categoria/ofertas">Ofertas</Link>
          <Link to="/categoria/diversos">Diversos</Link>
        </div>

        <div className="footer-links">
          <h4>Comunidade</h4>
          <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer">💬 Grupo WhatsApp</a>
          {TELEGRAM_URL && <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer">✈️ Canal Telegram</a>}
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener noreferrer">📸 Instagram</a>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} Achadinhos do Pai</p>
        <p className="disclaimer">
          Este site contém links afiliados. Ao comprar através dos nossos links, podemos receber uma comissão sem custo adicional para você.
        </p>
      </div>
    </footer>
  )
}

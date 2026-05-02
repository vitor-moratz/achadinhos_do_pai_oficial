import { Link } from 'react-router-dom'
import { WHATSAPP_URL, TELEGRAM_URL, INSTAGRAM_URL } from '../constants'
import { WhatsAppIcon, TelegramIcon, InstagramIcon } from './SocialIcons'
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
          <p>Os melhores produtos da Shopee, garimpados a dedo. Sem enrolação, sem produto duvidoso — só o que vale o seu dinheiro de verdade.</p>
        </div>

        <div className="footer-links">
          <h4>Segmentos</h4>
          <Link to="/segmento/automotivo">Automotivo</Link>
          <Link to="/segmento/casa">Casa</Link>
          <Link to="/segmento/eletronicos">Eletrônicos</Link>
          <Link to="/segmento/esporte">Esporte</Link>
          <Link to="/segmento/ferramentas">Ferramentas</Link>
          <Link to="/segmento/games">Games</Link>
          <Link to="/segmento/moda">Moda</Link>
          <Link to="/segmento/pet-shop">Pet Shop</Link>
        </div>

        <div className="footer-links">
          <h4>Comunidade</h4>
          <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className="footer-social-link"><WhatsAppIcon /> Grupo WhatsApp</a>
          {TELEGRAM_URL && <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer" className="footer-social-link"><TelegramIcon /> Canal no Telegram</a>}
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener noreferrer" className="footer-social-link"><InstagramIcon /> Instagram</a>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} Achadinhos do Pai</p>
        <p className="disclaimer">
          Indicamos só o que realmente vale a pena. Quando você compra pelo nosso link, recebemos uma pequena comissão — sem nenhum custo extra pra você. É assim que mantemos esse trabalho vivo. Valeu pelo apoio!
        </p>
      </div>
    </footer>
  )
}

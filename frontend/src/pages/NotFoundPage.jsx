import { Link } from 'react-router-dom'
import './NotFoundPage.css'

export default function NotFoundPage() {
  return (
    <div className="nf-page">
      <div className="nf-inner">
        <span className="nf-emoji">🔍</span>
        <h1 className="nf-code">404</h1>
        <h2 className="nf-title">Página não encontrada</h2>
        <p className="nf-sub">
          O achado que você procura não existe ou foi removido.
        </p>
        <Link to="/" className="nf-btn">← Voltar à loja</Link>
      </div>
    </div>
  )
}

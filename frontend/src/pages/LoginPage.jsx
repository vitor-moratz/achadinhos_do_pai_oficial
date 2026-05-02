import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import './LoginPage.css'

export default function LoginPage() {
  const { setUser } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(form.username, form.password)
      localStorage.setItem('adp_token', data.token)
      setUser(data.user)
      navigate('/admin')
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <img src="/logo.png" alt="Achadinhos do Pai" className="login-logo" />
        <h1 className="login-title">Área Restrita</h1>
        <p className="login-sub">Acesse o painel de gerenciamento</p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="login-label">
            Usuário
            <input
              className="login-input"
              type="text"
              autoComplete="username"
              value={form.username}
              onChange={(e) => setForm((p) => ({ ...p, username: e.target.value }))}
              required
              placeholder="Digite seu usuário"
            />
          </label>
          <label className="login-label">
            Senha
            <input
              className="login-input"
              type="password"
              autoComplete="current-password"
              value={form.password}
              onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
              required
              placeholder="Digite sua senha"
            />
          </label>
          {error && <p className="login-error">{error}</p>}
          <button className="login-btn" type="submit" disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
        <Link to="/" className="login-back">← Voltar à loja</Link>
      </div>
    </div>
  )
}

header = open('/home/moratz/achadinhos_do_pai_oficial/frontend/src/components/Header.jsx').read()

# Substituir o div header-social sem ícones pelo com ícones
old = """        <div className="header-social">
          <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className="header-cta">
            Entrar no Grupo
          </a>
        </div>"""

new = """        <div className="header-social">
          {TELEGRAM_URL && (
            <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer" className="header-social-icon" title="Telegram" aria-label="Telegram">
              <TelegramIcon size={20} />
            </a>
          )}
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener noreferrer" className="header-social-icon" title="Instagram" aria-label="Instagram">
            <InstagramIcon size={20} />
          </a>
          <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className="header-cta">
            Entrar no Grupo
          </a>
        </div>"""

if old in header:
    header = header.replace(old, new)
    open('/home/moratz/achadinhos_do_pai_oficial/frontend/src/components/Header.jsx', 'w').write(header)
    print('Header.jsx atualizado')
else:
    print('ERRO: trecho nao encontrado no Header.jsx')
    print(repr(header[800:1200]))

# Corrigir App.css - remover align-items: flex-start para sidebar esticar
appcss = open('/home/moratz/achadinhos_do_pai_oficial/frontend/src/App.css').read()
old2 = """.app-body {
  flex: 1;
  display: flex;
  align-items: flex-start;
}"""
new2 = """.app-body {
  flex: 1;
  display: flex;
}"""
if old2 in appcss:
    appcss = appcss.replace(old2, new2)
    open('/home/moratz/achadinhos_do_pai_oficial/frontend/src/App.css', 'w').write(appcss)
    print('App.css atualizado')
else:
    print('ERRO: trecho nao encontrado no App.css')
    print(repr(appcss))

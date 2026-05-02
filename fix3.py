
# 1. Aumentar ícones header: size 20 → 26, padding maior no CSS
header_jsx = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/components/Header.jsx'
txt = open(header_jsx).read()
txt = txt.replace('<TelegramIcon size={20} />\n            </a>\n          )}\n          <a href={INSTAGRAM_URL}',
                  '<TelegramIcon size={26} />\n            </a>\n          )}\n          <a href={INSTAGRAM_URL}')
txt = txt.replace('<InstagramIcon size={20} />\n          </a>', '<InstagramIcon size={26} />\n          </a>')
open(header_jsx, 'w').write(txt)
print('Header.jsx: ícones 26px')

# 2. Aumentar padding do .header-social-icon no CSS
header_css = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/components/Header.css'
css = open(header_css).read()
css = css.replace('  padding: 8px;\n  border-radius: var(--radius-sm);\n  transition: background 0.2s, color 0.2s;\n  color: var(--clr-primary);\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  font-size: 1.25rem;',
                  '  padding: 10px;\n  border-radius: var(--radius-sm);\n  transition: background 0.2s, color 0.2s;\n  color: var(--clr-primary);\n  display: flex;\n  align-items: center;\n  justify-content: center;')
open(header_css, 'w').write(css)
print('Header.css: padding atualizado')

# 3. Copyright footer
footer_jsx = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/components/Footer.jsx'
txt = open(footer_jsx).read()
txt = txt.replace(
    '        <p>© {new Date().getFullYear()} Achadinhos do Pai</p>',
    '        <p>© {new Date().getFullYear()} Achadinhos do Pai · <span style={{opacity:0.6}}>Desenvolvido por Moratz Programming</span></p>'
)
open(footer_jsx, 'w').write(txt)
print('Footer.jsx: copyright atualizado')

# 4. Sidebar fixo até o fim
# sidebar.css: position fixed, top = altura do header (84px logo), bottom 0
sidebar_css = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/components/Sidebar.css'
css = open(sidebar_css).read()
# Substituir bloco .sidebar e .sidebar-sticky por versão fixed
old_sidebar = '''.sidebar {
  width: 200px;
  flex-shrink: 0;
  border-right: 1px solid var(--clr-border);
  background: var(--clr-white);
}

.sidebar-sticky {
  position: sticky;
  top: 0;
  padding: 20px 12px 24px;
  max-height: 100vh;
  overflow-y: auto;
  scrollbar-width: none;
}

.sidebar-sticky::-webkit-scrollbar {
  display: none;
}'''
new_sidebar = '''.sidebar {
  width: 200px;
  flex-shrink: 0;
  position: fixed;
  top: 104px;
  left: 0;
  bottom: 0;
  border-right: 1px solid var(--clr-border);
  background: var(--clr-white);
  z-index: 50;
  overflow-y: auto;
  scrollbar-width: none;
}

.sidebar::-webkit-scrollbar {
  display: none;
}

.sidebar-sticky {
  padding: 20px 12px 24px;
}'''
if old_sidebar in css:
    css = css.replace(old_sidebar, new_sidebar)
    open(sidebar_css, 'w').write(css)
    print('Sidebar.css: fixo até o fim')
else:
    print('ERRO Sidebar.css: trecho não encontrado')
    print(repr(css[:300]))

# 5. App.css: app-main com margin-left para compensar sidebar fixo
app_css = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/App.css'
css = open(app_css).read()
old_main = '''.app-main {
  flex: 1;
  min-width: 0;
}'''
new_main = '''.app-main {
  flex: 1;
  min-width: 0;
  margin-left: 200px;
}

@media (max-width: 768px) {
  .app-main {
    margin-left: 0;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .app-main {
    margin-left: 170px;
  }
}'''
if old_main in css:
    css = css.replace(old_main, new_main)
    open(app_css, 'w').write(css)
    print('App.css: margin-left adicionado')
else:
    print('ERRO App.css: trecho não encontrado')
    print(repr(css))

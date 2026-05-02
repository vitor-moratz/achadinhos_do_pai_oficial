import os

# 1. Adicionar .header-social-icon no Header.css
headercss_path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/components/Header.css'
headercss = open(headercss_path).read()

old = """.header-cta {
  background: var(--clr-primary);"""

new = """.header-social-icon {
  text-decoration: none;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: background 0.2s, color 0.2s;
  color: var(--clr-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.header-social-icon:hover {
  background: #FFF7ED;
  color: var(--clr-primary-dark);
}

.header-cta {
  background: var(--clr-primary);"""

if old in headercss:
    headercss = headercss.replace(old, new, 1)
    open(headercss_path, 'w').write(headercss)
    print('Header.css: .header-social-icon adicionado')
else:
    print('ERRO Header.css: trecho nao encontrado')

# 2. Sidebar até o fim: app-body com min-height
appcss_path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/App.css'
appcss = open(appcss_path).read()

old2 = """.app-body {
  flex: 1;
  display: flex;
}"""

new2 = """.app-body {
  flex: 1;
  display: flex;
  min-height: calc(100vh - 72px);
}"""

if old2 in appcss:
    appcss = appcss.replace(old2, new2, 1)
    open(appcss_path, 'w').write(appcss)
    print('App.css: min-height adicionado')
else:
    print('ERRO App.css: trecho nao encontrado')
    print(repr(appcss))

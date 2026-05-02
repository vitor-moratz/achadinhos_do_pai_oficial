path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/pages/AdminPage.css'
with open(path, 'r') as f:
    css = f.read()

# Fix 1: regra antiga .al-title remove truncate
css = css.replace(
    '''.al-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--clr-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}''',
    '''.al-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--clr-text);
}'''
)

# Fix 2: filter-field de tag — remover width:100% e usar flex-shrink:0 + width fixo
# Substituir a regra normalize para dar width explícito em vez de 100%
css = css.replace(
    '''/* ── FILTER FIELD WIDTH NORMALIZE ───────────────── */
.filter-field:not(.filter-field--search):not(.filter-field--clear) .filter-select {
  min-width: 130px;
}''',
    '''/* ── FILTER FIELD WIDTH NORMALIZE ───────────────── */
.filter-field:not(.filter-field--search):not(.filter-field--clear) {
  flex-shrink: 0;
}

.filter-field:not(.filter-field--search):not(.filter-field--clear) .filter-select {
  min-width: 130px;
  width: 130px;
}'''
)

# Fix 3: remover width:100% e box-sizing da regra geral .filter-select (não deve ser 100% para os selects)
css = css.replace(
    '  white-space: nowrap;\n  min-width: 130px;\n  width: 100%;\n  box-sizing: border-box;\n}',
    '  white-space: nowrap;\n}'
)

with open(path, 'w') as f:
    f.write(css)

print('Done')

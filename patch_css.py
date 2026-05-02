path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/pages/AdminPage.css'
with open(path, 'r') as f:
    css = f.read()

# 1. Remover bloco .admin-select (appearance/SVG) - não é mais um native select
css = css.replace(
'''.admin-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") no-repeat right 12px center;
  padding-right: 36px;
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.admin-select:focus {
  outline: none;
  border-color: var(--clr-primary);
}''',
'/* .admin-select — substituído por CustomSelect */'
)

# 2. Substituir o bloco .role-select inteiro (appearance/SVG) — agora é só um div
old_role = '''.role-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") no-repeat right 8px center;
  border: 1.5px solid var(--clr-primary);
  border-radius: var(--radius-sm);
  padding: 5px 28px 5px 10px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--clr-text);
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}'''
css = css.replace(old_role, '/* .role-select — estilos movidos para CustomSelect.css */')

# 3. Substituir o bloco .filter-select — era native select, agora é div wrapper
old_filter = '''.filter-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") no-repeat right 10px center;
  padding: 9px 32px 9px 12px;
  border: 1.5px solid var(--clr-border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-family: inherit;
  color: var(--clr-text);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}

.filter-select:hover {
  border-color: #D1D5DB;
}

.filter-select:focus {
  outline: none;
  border-color: var(--clr-primary);
}

.filter-select:not([value=""]) {
  border-color: var(--clr-primary);
  color: var(--clr-primary);
}'''

new_filter = '''/* .filter-select — wrapper sizing; visual/hover styles estão em CustomSelect.css */
.filter-select {
  /* sizing handled by filter-field CSS below */
}'''

css = css.replace(old_filter, new_filter)

# 4. No responsive, remover appearance-related rules de .filter-select
css = css.replace(
  '  .filter-select { flex: 1; min-width: 0; font-size: 0.78rem; }',
  '  .filter-select, .filter-select .cselect-trigger { flex: 1; min-width: 0; font-size: 0.78rem; }'
)

# 5. A regra de width normalização do .filter-select ainda vale para o wrapper div
# nada a mudar lá

with open(path, 'w') as f:
    f.write(css)

print('AdminPage.css patched OK')

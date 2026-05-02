path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/pages/AdminPage.css'
with open(path, 'r') as f:
    css = f.read()

# SVG arrow reutilizável (inline)
ARROW = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E\")"

# 1. Substituir .admin-select (só tinha cursor: pointer)
css = css.replace(
    '.admin-select { cursor: pointer; }',
    '''.admin-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) ''' + ARROW + ''' no-repeat right 12px center;
  padding-right: 36px;
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.admin-select:focus {
  outline: none;
  border-color: var(--clr-primary);
}'''
)

# 2. Remover bloco redundante user-form + select.admin-select (já coberto acima)
css = css.replace(
    '''/* ── DROPDOWN SELECT BONITO (formulário novo usuário) ─ */
.user-form .admin-input.admin-select,
select.admin-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") no-repeat right 12px center;
  padding-right: 36px;
  cursor: pointer;
}''',
    ''
)

# 3. Unificar .filter-select com mesmo estilo
old_filter = '''.filter-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") no-repeat right 10px center;
  padding: 9px 32px 9px 12px;
  border: 1.5px solid var(--clr-border);
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  font-family: inherit;
  color: var(--clr-text);
  cursor: pointer;
  transition: border-color 0.2s;
  white-space: nowrap;
}'''

new_filter = '''.filter-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) ''' + ARROW + ''' no-repeat right 10px center;
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
}'''

css = css.replace(old_filter, new_filter)

# 4. Unificar .role-select
old_role = '''.role-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") no-repeat right 8px center;
  border: 1.5px solid var(--clr-primary);
  border-radius: var(--radius-sm);
  padding: 4px 28px 4px 10px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--clr-text);
  cursor: pointer;
  outline: none;
}'''

new_role = '''.role-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) ''' + ARROW + ''' no-repeat right 8px center;
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

css = css.replace(old_role, new_role)

with open(path, 'w') as f:
    f.write(css)

print('Done')

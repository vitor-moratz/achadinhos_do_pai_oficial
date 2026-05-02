path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/pages/AdminPage.jsx'
with open(path, 'r') as f:
    content = f.read()

# Toolbar: remover condicional, sempre mostra o botão
content = content.replace(
    '''            {isAdmin
              ? <button className="admin-btn-primary" onClick={openAdd}>+ Novo Produto</button>
              : <span className="admin-readonly-badge">👁 Somente visualização</span>
            }''',
    '            <button className="admin-btn-primary" onClick={openAdd}>+ Novo Produto</button>'
)

# ProductCard: remover guard isAdmin dos botões editar/remover
content = content.replace(
    '''        {isAdmin && (
          <div className="ac-actions">
            <button className="al-btn al-edit" onClick={() => handleEdit(p)}>Editar</button>
            <button className="al-btn al-del" onClick={() => handleDelete(p.id)}>Remover</button>
          </div>
        )}''',
    '''        <div className="ac-actions">
            <button className="al-btn al-edit" onClick={() => handleEdit(p)}>Editar</button>
            <button className="al-btn al-del" onClick={() => handleDelete(p.id)}>Remover</button>
          </div>'''
)

# ProductRow: remover guard isAdmin dos ícones
content = content.replace(
    '''        {isAdmin && (
          <div className="al-actions">
            <button className="al-btn al-edit al-icon" onClick={() => handleEdit(p)} title="Editar">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button className="al-btn al-del al-icon" onClick={() => handleDelete(p.id)} title="Remover">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
            </button>
          </div>
        )}''',
    '''        <div className="al-actions">
            <button className="al-btn al-edit al-icon" onClick={() => handleEdit(p)} title="Editar">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button className="al-btn al-del al-icon" onClick={() => handleDelete(p.id)} title="Remover">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
            </button>
          </div>'''
)

# Empty state: sempre mostra botão adicionar
content = content.replace(
    '  : <><p>Nenhum produto ainda.</p>{isAdmin && <button className="admin-btn-primary" onClick={openAdd}>Adicionar primeiro produto</button>}</>',
    '  : <><p>Nenhum produto ainda.</p><button className="admin-btn-primary" onClick={openAdd}>Adicionar primeiro produto</button></>'
)

# Modal: remover guard isAdmin (qualquer autenticado pode abrir)
content = content.replace(
    '      {modalOpen && isAdmin && (',
    '      {modalOpen && ('
)

with open(path, 'w') as f:
    f.write(content)

print('Done')

import os

BASE_BACKEND = '/home/moratz/achadinhos_do_pai_oficial/backend'
BASE_FRONTEND = '/home/moratz/achadinhos_do_pai_oficial/frontend/src'

# ── 1. Adicionar rota PATCH /auth/users/<id> no auth.py ───────────────────
auth_path = f'{BASE_BACKEND}/routes/auth.py'
with open(auth_path, 'r') as f:
    auth = f.read()

patch_route = '''

@auth_bp.route("/users/<user_id>", methods=["PATCH"])
@jwt_required()
def update_user(user_id):
    uid, err = _require_admin()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    if role not in ("admin", "membro"):
        return jsonify({"error": "Role inválido"}), 400
    db = get_db()
    try:
        result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    except Exception:
        return jsonify({"error": "ID inválido"}), 400
    if result.matched_count == 0:
        return jsonify({"error": "Usuário não encontrado"}), 404
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return jsonify(_user_to_dict(user))
'''

# Inserir antes da rota DELETE
if 'methods=["PATCH"]' not in auth:
    auth = auth.replace(
        '@auth_bp.route("/users/<user_id>", methods=["DELETE"])',
        patch_route + '\n@auth_bp.route("/users/<user_id>", methods=["DELETE"])'
    )
    with open(auth_path, 'w') as f:
        f.write(auth)
    print('auth.py PATCH route OK')
else:
    print('auth.py PATCH already exists')

# ── 2. Adicionar updateUserRole na api.js ────────────────────────────────
api_path = f'{BASE_FRONTEND}/services/api.js'
with open(api_path, 'r') as f:
    api = f.read()

if 'updateUserRole' not in api:
    api = api.replace(
        "export const deleteUser = (id) => api.delete(`/auth/users/${id}`).then((r) => r.data)",
        "export const deleteUser = (id) => api.delete(`/auth/users/${id}`).then((r) => r.data)\nexport const updateUserRole = (id, role) => api.patch(`/auth/users/${id}`, { role }).then((r) => r.data)"
    )
    with open(api_path, 'w') as f:
        f.write(api)
    print('api.js updateUserRole OK')
else:
    print('api.js already has updateUserRole')

# ── 3. AdminPage.jsx — import updateUserRole + edit role inline ──────────
admin_path = f'{BASE_FRONTEND}/pages/AdminPage.jsx'
with open(admin_path, 'r') as f:
    jsx = f.read()

# Adicionar updateUserRole no import
jsx = jsx.replace(
    "  getUsers, createUser, deleteUser,",
    "  getUsers, createUser, deleteUser, updateUserRole,"
)

# Adicionar estado editingUserId após userStatus
jsx = jsx.replace(
    "  const [userStatus, setUserStatus] = useState({ type: '', msg: '' })",
    "  const [userStatus, setUserStatus] = useState({ type: '', msg: '' })\n  const [editingUserId, setEditingUserId] = useState(null)"
)

# Adicionar handler handleChangeRole após handleDeleteUser
old_handler_end = """  const filteredCategories = form.segment"""
new_handler_end = """  async function handleChangeRole(id, newRole) {
    try {
      const updated = await updateUserRole(id, newRole)
      setUsers((prev) => prev.map((u) => (u.id === id ? updated : u)))
      setEditingUserId(null)
    } catch (err) {
      alert(err.response?.data?.error || 'Erro ao alterar role.')
    }
  }

  const filteredCategories = form.segment"""

jsx = jsx.replace(old_handler_end, new_handler_end)

# Substituir a listagem de usuários para incluir edição inline de role
old_user_list = """          <div className="user-list">
            {users.map((u) => (
              <div key={u.id} className="user-row">
                <div className="user-info">
                  <span className="user-name">{u.username}</span>
                  <span className={`user-role ${u.role}`}>{roleLabel(u.role)}</span>
                </div>
                {u.id !== user?.id && (
                  <button className="al-btn al-del" onClick={() => handleDeleteUser(u.id)}>Remover</button>
                )}
              </div>
            ))}
          </div>"""

new_user_list = """          <div className="user-list">
            {users.map((u) => (
              <div key={u.id} className="user-row">
                <div className="user-info">
                  <span className="user-name">{u.username}</span>
                  {editingUserId === u.id ? (
                    <div className="role-edit-inline">
                      <select
                        className="role-select"
                        defaultValue={u.role}
                        onChange={(e) => handleChangeRole(u.id, e.target.value)}
                      >
                        <option value="admin">Admin</option>
                        <option value="membro">Membro</option>
                      </select>
                      <button className="role-cancel-btn" onClick={() => setEditingUserId(null)}>✕</button>
                    </div>
                  ) : (
                    <button
                      className={`user-role ${u.role}`}
                      onClick={() => u.id !== user?.id && setEditingUserId(u.id)}
                      title={u.id !== user?.id ? 'Clique para alterar' : ''}
                      style={{ cursor: u.id !== user?.id ? 'pointer' : 'default' }}
                    >
                      {roleLabel(u.role)}
                    </button>
                  )}
                </div>
                <div className="user-actions">
                  {u.id !== user?.id && (
                    <button className="al-btn al-del" onClick={() => handleDeleteUser(u.id)}>Remover</button>
                  )}
                </div>
              </div>
            ))}
          </div>"""

jsx = jsx.replace(old_user_list, new_user_list)

with open(admin_path, 'w') as f:
    f.write(jsx)
print('AdminPage.jsx OK')

# ── 4. AdminPage.css — dropdown bonito + user-row consertado ────────────
css_path = f'{BASE_FRONTEND}/pages/AdminPage.css'
with open(css_path, 'r') as f:
    css = f.read()

extra_css = """
/* ── USER ROW FIX ──────────────────────────────────── */
.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--clr-white);
  border: 1px solid var(--clr-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.user-actions {
  flex-shrink: 0;
}

/* ── USER ROLE BADGE (clicável) ────────────────────── */
.user-role {
  font-size: 0.72rem;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 600;
  border: none;
  cursor: default;
  transition: opacity 0.15s;
  white-space: nowrap;
}

.user-role:hover { opacity: 0.8; }

.user-role.admin  { background: #FFF7ED; color: var(--clr-primary-dark); }
.user-role.membro { background: var(--clr-bg); color: var(--clr-text-muted); border: 1px solid var(--clr-border); }

/* ── ROLE EDIT INLINE ──────────────────────────────── */
.role-edit-inline {
  display: flex;
  align-items: center;
  gap: 4px;
}

.role-select {
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
}

.role-cancel-btn {
  background: none;
  border: none;
  color: var(--clr-text-muted);
  cursor: pointer;
  font-size: 0.85rem;
  padding: 4px 6px;
  border-radius: var(--radius-sm);
  line-height: 1;
}

.role-cancel-btn:hover { background: var(--clr-bg); }

/* ── DROPDOWN SELECT BONITO (formulário novo usuário) ─ */
.user-form .admin-input.admin-select,
select.admin-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--clr-white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") no-repeat right 12px center;
  padding-right: 36px;
  cursor: pointer;
}
"""

if 'role-edit-inline' not in css:
    # Remove definições antigas de .user-row/.user-info/.user-role.admin/.user-role.membro
    # para não duplicar
    import re
    css = re.sub(r'/\* ── USUÁRIOS.*?\.user-role\.membro \{[^}]+\}', '', css, flags=re.DOTALL)
    css += extra_css
    with open(css_path, 'w') as f:
        f.write(css)
    print('AdminPage.css extras OK')
else:
    print('CSS extras already present')

print('\nAll done!')

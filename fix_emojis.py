path = '/home/moratz/achadinhos_do_pai_oficial/frontend/src/pages/AdminPage.jsx'
with open(path, 'r') as f:
    content = f.read()

# Substituir unicode escapes JS por emojis reais dentro do JSX
replacements = {
    r'\u{1F4E6}': '📦',
    r'\u{1F3D5}\ufe0f': '🏕️',
    r'\u{1F517}': '🔗',
    r'\u{1F50D}': '🔍',
}

for esc, emoji in replacements.items():
    content = content.replace(esc, emoji)

with open(path, 'w') as f:
    f.write(content)

print('Emojis corrigidos OK')

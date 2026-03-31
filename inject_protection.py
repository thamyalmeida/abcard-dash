#!/usr/bin/env python3
"""
inject_protection.py v3
Estratégia: cria uma página de login separada (index.html) que redireciona
para os arquivos reais após validar a senha. Os arquivos originais são renomeados
com um prefixo aleatório para dificultar acesso direto.
"""

import os
import shutil
import json
import secrets

PASSWORD = os.environ.get("PAGE_PASSWORD", "").strip()
if not PASSWORD:
    raise SystemExit("❌ GitHub Secret PAGE_PASSWORD não está definido.")

PASSWORD_JS = json.dumps(PASSWORD)

# Token aleatório gerado a cada deploy — dificulta adivinhar a URL dos arquivos reais
TOKEN = secrets.token_hex(12)

os.makedirs("protected", exist_ok=True)

# ── Página de login ────────────────────────────────────────────────────────────
LOGIN_HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ABCard Research · Acesso Restrito</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --purple: #820AD1;
      --bg: #0D0D0D;
      --surface: #161616;
      --border: rgba(130,10,209,0.3);
      --text: #F0E6FF;
      --muted: #9A8AAA;
      --error: #FF4D6D;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      background:
        radial-gradient(ellipse at 65% 35%, rgba(130,10,209,0.18) 0%, transparent 55%),
        radial-gradient(ellipse at 20% 75%, rgba(92,10,148,0.12) 0%, transparent 50%);
      pointer-events: none;
    }}
    .card {{
      position: relative;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 44px 40px;
      width: 100%;
      max-width: 380px;
      margin: 20px;
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 32px;
    }}
    .logo-icon {{
      width: 34px; height: 34px;
      background: var(--purple);
      border-radius: 9px;
      display: flex; align-items: center; justify-content: center;
      font-size: 14px; font-weight: 700; color: white; letter-spacing: -0.5px;
    }}
    .logo-text {{
      font-size: 12px; color: var(--muted);
      letter-spacing: 0.1em; text-transform: uppercase;
    }}
    h1 {{ font-size: 21px; font-weight: 600; margin-bottom: 6px; letter-spacing: -0.3px; }}
    .subtitle {{ font-size: 13px; color: var(--muted); margin-bottom: 28px; line-height: 1.55; }}
    label {{ display: block; font-size: 11px; font-weight: 600; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px; }}
    input[type="password"] {{
      width: 100%;
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 10px;
      padding: 13px 15px;
      font-family: inherit; font-size: 15px; color: var(--text);
      outline: none; margin-bottom: 14px;
      transition: border-color 0.2s;
    }}
    input[type="password"]:focus {{ border-color: var(--purple); }}
    .btn {{
      width: 100%; padding: 14px;
      background: var(--purple); border: none; border-radius: 10px;
      color: white; font-family: inherit; font-size: 15px; font-weight: 600;
      cursor: pointer; transition: background 0.15s;
    }}
    .btn:hover {{ background: #9B1AE8; }}
    .error-msg {{ display: none; color: var(--error); font-size: 12px; margin-top: 12px; text-align: center; }}
    .error-msg.visible {{ display: block; }}
    .footer {{ font-size: 11px; color: var(--muted); margin-top: 28px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); text-align: center; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">
      <div class="logo-icon">Nu</div>
      <span class="logo-text">Acesso Restrito</span>
    </div>
    <h1>Bem-vinda 👋</h1>
    <p class="subtitle">Este conteúdo é interno. Insira a senha para continuar.</p>
    <label for="pwd">Senha</label>
    <input type="password" id="pwd" placeholder="••••••••" autofocus />
    <button class="btn" onclick="checkPassword()">Entrar</button>
    <p class="error-msg" id="err">Senha incorreta. Tente novamente.</p>
    <p class="footer">Conteúdo interno Nubank · não compartilhe este link</p>
  </div>
  <script>
    const CORRECT = {PASSWORD_JS};
    const TOKEN = "{TOKEN}";

    // Se já autenticou nessa sessão, vai direto
    (function() {{
      if (sessionStorage.getItem("nu_auth") === TOKEN) {{
        window.location.href = "report_" + TOKEN + ".html";
      }}
    }})();

    function checkPassword() {{
      const val = document.getElementById("pwd").value;
      if (val === CORRECT) {{
        sessionStorage.setItem("nu_auth", TOKEN);
        window.location.href = "report_" + TOKEN + ".html";
      }} else {{
        const err = document.getElementById("err");
        err.classList.add("visible");
        setTimeout(() => err.classList.remove("visible"), 3000);
      }}
    }}

    document.getElementById("pwd").addEventListener("keydown", function(e) {{
      if (e.key === "Enter") checkPassword();
    }});
  </script>
</body>
</html>
"""

# ── Página de login PT-BR ──────────────────────────────────────────────────────
LOGIN_PTBR = LOGIN_HTML.replace(
    f'window.location.href = "report_" + TOKEN + ".html"',
    f'window.location.href = "ptbr_" + TOKEN + ".html"'
).replace(
    f'window.location.href = "report_" + TOKEN + ".html";',
    f'window.location.href = "ptbr_" + TOKEN + ".html";'
)

# ── Guarda de acesso direto (redireciona para login se acessar sem sessão) ─────
GUARD_SCRIPT = f"""
<script>
(function() {{
  if (sessionStorage.getItem("nu_auth") !== "{TOKEN}") {{
    window.location.replace("index.html");
  }}
}})();
</script>
"""

def add_guard(html_content):
    """Injeta o script de guarda logo após a tag <head> ou no início do arquivo."""
    if "<head>" in html_content:
        return html_content.replace("<head>", "<head>" + GUARD_SCRIPT, 1)
    elif "<HEAD>" in html_content:
        return html_content.replace("<HEAD>", "<HEAD>" + GUARD_SCRIPT, 1)
    else:
        return GUARD_SCRIPT + html_content

# ── Gera os arquivos ───────────────────────────────────────────────────────────

# 1. Página de login EN (vira o novo index.html)
with open("protected/index.html", "w", encoding="utf-8") as f:
    f.write(LOGIN_HTML)
print("✅ protected/index.html (login EN)")

# 2. Página de login PT-BR (vira o novo ptbr.html)
with open("protected/ptbr.html", "w", encoding="utf-8") as f:
    f.write(LOGIN_PTBR)
print("✅ protected/ptbr.html (login PT-BR)")

# 3. Arquivo real EN com guarda
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    guarded = add_guard(content)
    with open(f"protected/report_{TOKEN}.html", "w", encoding="utf-8") as f:
        f.write(guarded)
    print(f"✅ protected/report_{TOKEN}.html (conteúdo real EN)")
else:
    print("⚠️  index.html não encontrado")

# 4. Arquivo real PT-BR com guarda
if os.path.exists("ptbr.html"):
    with open("ptbr.html", "r", encoding="utf-8") as f:
        content = f.read()
    guarded = add_guard(content)
    with open(f"protected/ptbr_{TOKEN}.html", "w", encoding="utf-8") as f:
        f.write(guarded)
    print(f"✅ protected/ptbr_{TOKEN}.html (conteúdo real PT-BR)")
else:
    print("⚠️  ptbr.html não encontrado")

# 5. Copia outros assets (CSS, JS, imagens, fontes...)
for item in os.listdir("."):
    if item in ("index.html", "ptbr.html", "protected", "inject_protection.py", ".github"):
        continue
    if item.startswith("."):
        continue
    if os.path.isfile(item):
        shutil.copy2(item, os.path.join("protected", item))
        print(f"   📎 copiado: {item}")
    elif os.path.isdir(item):
        dest = os.path.join("protected", item)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(item, dest)
        print(f"   📁 copiado: {item}/")

print("\n🚀 Pronto! Pasta 'protected' gerada com sucesso.")
print(f"   Token desta build: {TOKEN}")

#!/usr/bin/env python3
"""
inject_protection.py
Wraps index.html and ptbr.html with a password-protected login screen.
The password is read from the PAGE_PASSWORD environment variable (GitHub Secret).
"""

import os
import shutil
import json

PASSWORD = os.environ.get("PAGE_PASSWORD", "").strip()
if not PASSWORD:
    raise SystemExit("❌ GitHub Secret PAGE_PASSWORD não está definido.")

# Escapa a senha para uso seguro dentro de JavaScript
PASSWORD_JS = json.dumps(PASSWORD)

FILES = ["index.html", "ptbr.html"]

os.makedirs("protected", exist_ok=True)

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Acesso Restrito</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --nu-purple: #820AD1;
      --bg: #0D0D0D;
      --surface: #161616;
      --border: rgba(130, 10, 209, 0.30);
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
      width: 34px;
      height: 34px;
      background: var(--nu-purple);
      border-radius: 9px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 700;
      color: white;
      letter-spacing: -0.5px;
    }}

    .logo-text {{
      font-size: 12px;
      font-weight: 400;
      color: var(--muted);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}

    h1 {{
      font-size: 21px;
      font-weight: 600;
      margin-bottom: 6px;
      letter-spacing: -0.3px;
    }}

    .subtitle {{
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 28px;
      line-height: 1.55;
    }}

    label {{
      display: block;
      font-size: 11px;
      font-weight: 600;
      color: var(--muted);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}

    input[type="password"] {{
      width: 100%;
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 10px;
      padding: 13px 15px;
      font-family: inherit;
      font-size: 15px;
      color: var(--text);
      outline: none;
      margin-bottom: 14px;
      transition: border-color 0.2s;
    }}

    input[type="password"]:focus {{
      border-color: var(--nu-purple);
    }}

    .btn {{
      width: 100%;
      padding: 14px;
      background: var(--nu-purple);
      border: none;
      border-radius: 10px;
      color: white;
      font-family: inherit;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s;
    }}

    .btn:hover {{ background: #9B1AE8; }}

    .error-msg {{
      display: none;
      color: var(--error);
      font-size: 12px;
      margin-top: 12px;
      text-align: center;
    }}

    .error-msg.visible {{ display: block; }}

    .footer {{
      font-size: 11px;
      color: var(--muted);
      margin-top: 28px;
      padding-top: 20px;
      border-top: 1px solid rgba(255,255,255,0.06);
      text-align: center;
    }}
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

  <div id="content" style="display:none;"></div>

  <script>
    const CORRECT = {PASSWORD_JS};
    const CONTENT = {CONTENT_PLACEHOLDER};

    (function () {{
      if (sessionStorage.getItem("nu_auth") === "ok") unlock();
    }})();

    function checkPassword() {{
      const val = document.getElementById("pwd").value;
      if (val === CORRECT) {{
        sessionStorage.setItem("nu_auth", "ok");
        unlock();
      }} else {{
        const err = document.getElementById("err");
        err.classList.add("visible");
        setTimeout(() => err.classList.remove("visible"), 3000);
      }}
    }}

    document.getElementById("pwd").addEventListener("keydown", function(e) {{
      if (e.key === "Enter") checkPassword();
    }});

    function unlock() {{
      document.querySelector(".card").style.display = "none";
      document.body.style.background = "transparent";
      const div = document.getElementById("content");
      div.style.display = "block";
      div.innerHTML = CONTENT;
      div.querySelectorAll("script").forEach(function(old) {{
        const s = document.createElement("script");
        if (old.src) {{ s.src = old.src; }}
        else {{ s.textContent = old.textContent; }}
        document.head.appendChild(s);
      }});
    }}
  </script>
</body>
</html>
"""

def inject(filename):
    if not os.path.exists(filename):
        print(f"⚠️  {filename} não encontrado, pulando.")
        return

    with open(filename, "r", encoding="utf-8") as f:
        original = f.read()

    content_json = json.dumps(original)

    protected = LOGIN_TEMPLATE.replace("{PASSWORD_JS}", PASSWORD_JS)
    protected = protected.replace("{CONTENT_PLACEHOLDER}", content_json)

    out_path = os.path.join("protected", filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(protected)

    print(f"✅ {filename} → protected/{filename}")

for fname in FILES:
    inject(fname)

# Copia outros assets (CSS, JS, imagens) que os HTMLs possam referenciar
for item in os.listdir("."):
    if item in FILES or item in ("protected", "inject_protection.py", ".github"):
        continue
    if os.path.isfile(item):
        shutil.copy2(item, os.path.join("protected", item))
    elif os.path.isdir(item) and not item.startswith("."):
        dest = os.path.join("protected", item)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(item, dest)

print("🚀 Pronto! Pasta 'protected' gerada com sucesso.")

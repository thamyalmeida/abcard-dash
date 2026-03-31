#!/usr/bin/env python3
"""
inject_protection.py
Wraps index.html and ptbr.html with a password-protected login screen.
The password is read from the PAGE_PASSWORD environment variable (GitHub Secret).
"""

import os
import shutil
import hashlib

PASSWORD = os.environ.get("PAGE_PASSWORD", "")
if not PASSWORD:
    raise SystemExit("❌ GitHub Secret PAGE_PASSWORD não está definido.")

# Hash SHA-256 da senha para não expor em plaintext no HTML
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode()).hexdigest()

FILES = ["index.html", "ptbr.html"]

os.makedirs("protected", exist_ok=True)

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Acesso Restrito</title>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --nu-purple: #820AD1;
      --nu-purple-dark: #5C0A94;
      --bg: #0D0D0D;
      --surface: #161616;
      --border: rgba(130, 10, 209, 0.25);
      --text: #F0E6FF;
      --muted: #7A6A8A;
      --error: #FF4D6D;
    }}

    body {{
      font-family: 'Sora', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}

    /* Fundo animado */
    body::before {{
      content: '';
      position: fixed;
      inset: -50%;
      background: radial-gradient(ellipse at 60% 40%, rgba(130,10,209,0.15) 0%, transparent 60%),
                  radial-gradient(ellipse at 20% 80%, rgba(92,10,148,0.1) 0%, transparent 50%);
      animation: drift 12s ease-in-out infinite alternate;
      pointer-events: none;
    }}

    @keyframes drift {{
      from {{ transform: translate(0, 0) rotate(0deg); }}
      to   {{ transform: translate(3%, 2%) rotate(1deg); }}
    }}

    .card {{
      position: relative;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 48px 44px;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 0 60px rgba(130,10,209,0.1), 0 24px 48px rgba(0,0,0,0.4);
      animation: fadeUp 0.5s ease both;
    }}

    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 36px;
    }}

    .logo-icon {{
      width: 36px;
      height: 36px;
      background: var(--nu-purple);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      font-weight: 600;
      color: white;
      letter-spacing: -1px;
    }}

    .logo-text {{
      font-size: 13px;
      font-weight: 300;
      color: var(--muted);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1 {{
      font-size: 22px;
      font-weight: 600;
      margin-bottom: 6px;
      letter-spacing: -0.3px;
    }}

    .subtitle {{
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 32px;
      line-height: 1.5;
    }}

    .field {{
      position: relative;
      margin-bottom: 20px;
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
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 10px;
      padding: 14px 16px;
      font-family: 'Sora', sans-serif;
      font-size: 15px;
      color: var(--text);
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}

    input[type="password"]:focus {{
      border-color: var(--nu-purple);
      box-shadow: 0 0 0 3px rgba(130,10,209,0.15);
    }}

    .btn {{
      width: 100%;
      padding: 15px;
      background: var(--nu-purple);
      border: none;
      border-radius: 10px;
      color: white;
      font-family: 'Sora', sans-serif;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
      margin-top: 8px;
    }}

    .btn:hover  {{ background: #9B1AE8; }}
    .btn:active {{ transform: scale(0.98); }}

    .error-msg {{
      display: none;
      color: var(--error);
      font-size: 12px;
      margin-top: 12px;
      text-align: center;
      animation: shake 0.3s ease;
    }}

    @keyframes shake {{
      0%,100% {{ transform: translateX(0); }}
      25%      {{ transform: translateX(-6px); }}
      75%      {{ transform: translateX(6px); }}
    }}

    .error-msg.visible {{ display: block; }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      color: var(--muted);
      margin-top: 28px;
      padding-top: 20px;
      border-top: 1px solid rgba(255,255,255,0.05);
      width: 100%;
    }}

    .badge::before {{
      content: '🔒';
      font-size: 12px;
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
    <p class="subtitle">Este conteúdo é interno. Por favor, insira a senha para continuar.</p>

    <div class="field">
      <label>Senha</label>
      <input type="password" id="pwd" placeholder="••••••••" autofocus />
    </div>

    <button class="btn" onclick="checkPassword()">Entrar</button>
    <p class="error-msg" id="err">Senha incorreta. Tente novamente.</p>

    <span class="badge">Conteúdo interno Nubank · não compartilhe este link</span>
  </div>

  <div id="content" style="display:none; width:100%; height:100vh;"></div>

  <script>
    const HASH = "{PASSWORD_HASH}";
    const CONTENT = {CONTENT_PLACEHOLDER};

    // Verifica sessão existente
    (function () {{
      const saved = sessionStorage.getItem("nu_auth");
      if (saved === HASH) unlock();
    }})();

    async function sha256(str) {{
      const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
      return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,"0")).join("");
    }}

    async function checkPassword() {{
      const val = document.getElementById("pwd").value;
      const h = await sha256(val);
      if (h === HASH) {{
        sessionStorage.setItem("nu_auth", HASH);
        unlock();
      }} else {{
        const err = document.getElementById("err");
        err.classList.add("visible");
        setTimeout(() => err.classList.remove("visible"), 3000);
      }}
    }}

    document.getElementById("pwd").addEventListener("keydown", e => {{
      if (e.key === "Enter") checkPassword();
    }});

    function unlock() {{
      document.querySelector(".card").style.display = "none";
      document.body.style.background = "white";
      const div = document.getElementById("content");
      div.style.display = "block";
      div.innerHTML = CONTENT;
      // Re-executa scripts do conteúdo original
      div.querySelectorAll("script").forEach(old => {{
        const s = document.createElement("script");
        if (old.src) s.src = old.src;
        else s.textContent = old.textContent;
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

    # Escapa o conteúdo original para JSON string segura
    import json
    content_json = json.dumps(original)

    protected = LOGIN_TEMPLATE.replace("{PASSWORD_HASH}", PASSWORD_HASH)
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

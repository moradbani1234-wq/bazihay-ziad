"""صفحات HTML به‌صورت رشته‌های پایتون؛ برای ساده نگه‌داشتن دیپلوی، بدون پوشه‌های جدا."""

import html

BASE_CSS = """
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');

:root {
    --bg: #101A30;
    --surface: #182A4A;
    --surface-raised: #1F3459;
    --border: #2D4670;
    --text: #EEEAE0;
    --text-muted: #93A2C4;
    --turquoise: #2FA9A0;
    --turquoise-dim: #23807A;
    --saffron: #E8A94A;
    --danger: #E2665E;
}

* { box-sizing: border-box; }

body {
    background: var(--bg); color: var(--text);
    font-family: 'Vazirmatn', Tahoma, sans-serif;
    margin: 0; padding: 0; direction: rtl;
    font-size: 15px; line-height: 1.8;
}

:focus-visible { outline: 2px solid var(--saffron); outline-offset: 2px; }

.nav {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 22px; background: var(--surface);
    border-bottom: 2px solid var(--border);
    position: relative;
}
.nav::after {
    content: ""; position: absolute; bottom: -2px; right: 0; left: 0; height: 2px;
    background: repeating-linear-gradient(-45deg, var(--turquoise) 0 6px, var(--saffron) 6px 12px);
    opacity: 0.5;
}
.nav-brand { font-weight: 700; font-size: 17px; display: flex; align-items: center; gap: 8px; }
.nav a { color: var(--turquoise); text-decoration: none; margin-inline-start: 16px; font-weight: 600; }
.nav a:hover { color: var(--saffron); }

.container { max-width: 620px; margin: 0 auto; padding: 24px 18px 60px; }

h1 { font-size: 25px; font-weight: 700; margin: 0 0 14px; line-height: 1.5; }
h2 { font-size: 18px; font-weight: 600; margin: 0 0 14px; color: var(--text); }
p { color: var(--text-muted); }

.card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
    padding: 24px; margin-bottom: 18px;
}

.hero {
    position: relative; overflow: hidden;
    background: linear-gradient(160deg, var(--surface-raised), var(--surface));
}
.hero::before {
    content: ""; position: absolute; inset: -30%;
    background-image: radial-gradient(circle, rgba(232,169,74,0.10) 0 2px, transparent 2.5px);
    background-size: 28px 28px;
    transform: rotate(12deg);
    pointer-events: none;
}
.hero > * { position: relative; }

input[type=text], input[type=password] {
    width: 100%; padding: 13px 14px; border-radius: 10px; border: 1px solid var(--border);
    background: var(--bg); color: var(--text); margin-bottom: 14px; font-size: 15px;
    font-family: inherit;
}
input:focus { border-color: var(--turquoise); }

button, .btn {
    background: var(--turquoise); color: #0B1626; border: none; padding: 13px 20px;
    border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer;
    text-decoration: none; display: inline-block; font-family: inherit;
    transition: background 0.15s ease;
}
button:hover, .btn:hover { background: var(--turquoise-dim); color: #fff; }

.error {
    color: var(--danger); background: rgba(226,102,94,0.1); border: 1px solid rgba(226,102,94,0.3);
    padding: 10px 14px; border-radius: 10px; margin-bottom: 14px; font-size: 14px;
}

.grid-links { display: grid; gap: 12px; margin-top: 6px; }
.grid-links a {
    background: var(--surface-raised); border: 1px solid var(--border); border-radius: 14px;
    padding: 20px; text-align: center; color: var(--text); text-decoration: none;
    font-size: 17px; font-weight: 600; transition: border-color 0.15s ease, transform 0.1s ease;
}
.grid-links a:hover { border-color: var(--saffron); transform: translateY(-1px); }

.chat-box {
    height: 380px; overflow-y: auto; background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px; margin-bottom: 14px; display: flex; flex-direction: column; gap: 8px;
}
.msg {
    padding: 9px 13px; border-radius: 12px 12px 12px 2px; background: var(--surface-raised);
    max-width: 78%; font-size: 14.5px; align-self: flex-start;
}
.msg.me {
    align-self: flex-end; background: var(--turquoise-dim); border-radius: 12px 12px 2px 12px;
}
.msg .sender { font-size: 12px; opacity: 0.65; display: block; margin-bottom: 2px; font-weight: 600; }
.chat-input-row { display: flex; gap: 8px; }
.chat-input-row input { flex: 1; margin-bottom: 0; }

.status-line {
    text-align: center; font-size: 15.5px; margin-bottom: 14px; color: var(--saffron); font-weight: 600;
}

.ttt-board {
    display: grid; grid-template-columns: repeat(3, 88px); grid-template-rows: repeat(3, 88px);
    gap: 8px; justify-content: center; margin: 20px 0;
}
.ttt-cell {
    background: var(--surface-raised); border: 1px solid var(--border); border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 34px; font-weight: 700; cursor: pointer; user-select: none;
    color: var(--turquoise); transition: background 0.15s ease;
}
.ttt-cell:hover { background: var(--border); }

.word-row { display: flex; gap: 6px; justify-content: center; margin-bottom: 6px; }
.letter-box {
    width: 46px; height: 46px; border: 2px solid var(--border); border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 21px; font-weight: 700;
    background: var(--surface-raised); color: var(--text);
}
.letter-box.correct { background: var(--turquoise-dim); border-color: var(--turquoise-dim); color: #fff; }
.letter-box.present { background: #8A6A25; border-color: #8A6A25; color: #fff; }
.letter-box.absent { background: var(--border); border-color: var(--border); color: var(--text-muted); }

.draw-round-info {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 10px; font-weight: 600; color: var(--text);
}
.draw-timer { color: var(--saffron); font-variant-numeric: tabular-nums; }

.draw-scorebar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.draw-score-chip {
    background: var(--surface-raised); border: 1px solid var(--border); border-radius: 20px;
    padding: 6px 14px; font-size: 13.5px; font-weight: 600; color: var(--text-muted);
}
.draw-score-chip.me { color: var(--turquoise); border-color: var(--turquoise-dim); }

.draw-canvas-wrap {
    background: #fff; border-radius: 14px; overflow: hidden; margin-bottom: 12px;
    border: 1px solid var(--border); line-height: 0;
}
.draw-canvas-wrap canvas {
    width: 100%; height: auto; display: block; touch-action: none; cursor: crosshair;
}

.draw-palette { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 12px; }
.draw-swatch {
    width: 32px; height: 32px; border-radius: 50%; cursor: pointer;
    border: 3px solid var(--surface); box-shadow: 0 0 0 1px var(--border);
}
.draw-swatch.active { box-shadow: 0 0 0 2px var(--saffron); }

.draw-word-box {
    text-align: center; background: var(--surface-raised); border: 1px dashed var(--saffron);
    border-radius: 10px; padding: 10px; margin-bottom: 12px; font-weight: 700; color: var(--saffron);
}

.draw-options {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 12px;
}
.draw-option-btn {
    background: var(--surface-raised); color: var(--text); border: 1px solid var(--border);
    padding: 12px 8px; font-size: 14px;
}
.draw-option-btn:hover:not(:disabled) { background: var(--turquoise-dim); color: #fff; }
.draw-option-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.draw-option-btn.wrong { border-color: var(--danger); text-decoration: line-through; }

.draw-result { text-align: center; background: var(--surface-raised); border-radius: 14px; padding: 18px; }
.draw-result-title { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
.draw-result-note { margin-top: 10px; color: var(--text-muted); font-size: 13.5px; }


.report-btn {
    margin-inline-start: 8px; padding: 3px 7px; border-radius: 7px;
    background: transparent; border: 1px solid var(--danger); color: var(--danger);
    font-size: 11px; cursor: pointer; opacity: .75;
}
.report-btn:hover { opacity: 1; background: rgba(226,102,94,.12); }
.draw-tools { display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-bottom:12px; }
.draw-tool, .draw-size {
    background:var(--surface-raised); color:var(--text); border:1px solid var(--border);
    padding:8px 12px; border-radius:10px; cursor:pointer;
}
.draw-tool.active, .draw-size.active { border-color:var(--saffron); box-shadow:0 0 0 2px rgba(232,169,74,.18); }
.page-enter { animation: pageIn .35s ease both; }
@keyframes pageIn { from {opacity:0; transform:translateY(8px) scale(.99)} to {opacity:1;transform:none} }
.glow-btn { box-shadow:0 0 0 rgba(47,169,160,0); transition:transform .2s, box-shadow .2s; }
.glow-btn:hover { transform:translateY(-2px); box-shadow:0 8px 28px rgba(47,169,160,.2); }
.leader-row { display:grid; grid-template-columns:42px 1fr 70px 70px; gap:8px; align-items:center; padding:12px; border-bottom:1px solid var(--border); }
.leader-row.me { background:rgba(47,169,160,.08); border-radius:10px; }
.rank-medal { font-size:20px; text-align:center; }
.admin-card { border-color:var(--saffron); }
.report-item { padding:14px; border:1px solid var(--border); border-radius:12px; margin-bottom:10px; background:var(--surface-raised); }
.report-meta { color:var(--text-muted); font-size:12px; }

@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; }
}
"""


def _nav(username: str | None) -> str:
    if username:
        u = html.escape(username)
        return f"""
        <div class="nav">
          <div class="nav-brand">🎲 بازی‌خونه — {u}</div>
          <div>
            <a href="/lobby">لابی</a>
            <a href="/logout">خروج</a>
          </div>
        </div>"""
    return """
    <div class="nav">
      <div class="nav-brand">🎲 بازی‌خونه</div>
      <div><a href="/login">ورود</a></div>
    </div>"""


def page_shell(title: str, body: str, username: str | None = None) -> str:
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{BASE_CSS}</style>
</head>
<body>
{_nav(username)}
<div class="container">
{body}
</div>
</body>
</html>"""


def login_page(error: str | None = None) -> str:
    err_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    body = f"""
    <div class="card">
      <h1>ورود به بازی‌خونه</h1>
      {err_html}
      <form method="post" action="/login">
        <input type="text" name="username" placeholder="نام کاربری" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button type="submit">ورود</button>
      </form>
      <p>حساب نداری؟ <a href="/signup" style="color:var(--turquoise)">ثبت‌نام کن</a></p>
    </div>"""
    return page_shell("ورود", body)


def signup_page(error: str | None = None) -> str:
    err_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    body = f"""
    <div class="card">
      <h1>ساخت حساب جدید</h1>
      {err_html}
      <form method="post" action="/signup">
        <input type="text" name="username" placeholder="نام کاربری (حداقل ۳ حرف)" required>
        <input type="password" name="password" placeholder="رمز عبور (حداقل ۴ حرف)" required>
        <button type="submit">ساخت حساب</button>
      </form>
      <p>حساب داری؟ <a href="/login" style="color:var(--turquoise)">وارد شو</a></p>
    </div>"""
    return page_shell("ثبت‌نام", body)


def lobby_page(username: str) -> str:
    body = f"""
    <div class="card hero">
      <h1>خوش اومدی، {html.escape(username)}!</h1>
      <p style="margin-bottom:18px">یه بازی رو انتخاب کن، یا برو تو چت با بقیه گپ بزن.</p>
      <div class="grid-links">
        <a href="/game/tictactoe">⭕ دوز دو نفره زنده</a>
        <a href="/game/drawing">🎨 نقاشی حدسی دو نفره</a>
        <a href="/chat/public">💬 چت عمومی</a>
      </div>
    </div>
    <div class="card">
      <h2>چت خصوصی</h2>
      <form method="post" action="/chat/private/start">
        <input type="text" name="other" placeholder="نام کاربری طرف مقابل" required>
        <button type="submit">شروع چت خصوصی</button>
      </form>
    </div>"""
    return page_shell("لابی", body, username)



def banned_page(username: str, scope: str, remaining: int, reason: str) -> str:
    mins = max(1, (remaining + 59) // 60)
    scope_text = {"games":"بازی‌ها", "chat":"چت‌ها", "drawing":"نقاشی", "tictactoe":"دوز", "all":"همه بخش‌ها"}.get(scope, scope)
    body=f"""
    <div class="card hero page-enter" style="text-align:center">
      <div style="font-size:52px">🚫</div>
      <h1>دسترسی موقتاً محدود شده</h1>
      <p>شما از <b>{html.escape(scope_text)}</b> محروم هستید.</p>
      <p>زمان باقی‌مانده: <b>{mins} دقیقه</b></p>
      <p>دلیل: {html.escape(reason or "نقض قوانین")}</p>
      <a class="btn glow-btn" href="/lobby">بازگشت به منو</a>
    </div>"""
    return page_shell("محرومیت موقت", body, username)

def leaderboard_page(username: str, rows: list[dict]) -> str:
    items=[]
    medals=["🥇","🥈","🥉"]
    for i,r in enumerate(rows,1):
        medal=medals[i-1] if i<=3 else str(i)
        cls=" me" if r["username"]==username else ""
        items.append(f"""<div class="leader-row{cls}">
          <div class="rank-medal">{medal}</div><div><b>{html.escape(r['username'])}</b></div>
          <div>{r['rating']} امتیاز</div><div>{r['wins']} برد</div>
        </div>""")
    body=f"""
    <div class="card hero page-enter"><h1>🏆 رتبه‌بندی</h1>
      <p>رتبه بر اساس برد و مساوی محاسبه می‌شود؛ امتیاز بازی هم به عنوان معیار دوم ثبت می‌شود.</p>
      <div>{''.join(items) or '<p>هنوز آماری ثبت نشده.</p>'}</div>
      <div style="text-align:center;margin-top:16px"><a class="btn" href="/lobby">لابی</a></div>
    </div>"""
    return page_shell("رتبه‌بندی",body,username)

def support_page(username: str, reports: list[dict]) -> str:
    items=[]
    for r in reports:
        status="حل‌شده" if r["status"]!="open" else "باز"
        items.append(f"""
        <div class="report-item" data-id="{r['id']}">
          <div><b>گزارش {r['id']}</b> — {html.escape(r['context'])} — <span>{status}</span></div>
          <div class="report-meta">گزارش‌دهنده: {html.escape(r['reporter'])} | کاربر گزارش‌شده: <b>{html.escape(r['target'])}</b></div>
          <p style="margin:8px 0"><b>محتوا:</b> {html.escape(r['content'])}</p>
          <div class="draw-tools">
            <select class="draw-size ban-scope"><option value="all">همه</option><option value="chat">چت</option><option value="games">بازی‌ها</option><option value="drawing">نقاشی</option><option value="tictactoe">دوز</option></select>
            <input class="ban-hours" type="number" min="1" max="168" value="3" style="width:80px;margin:0" title="ساعت">
            <button class="glow-btn" onclick="banUser({r['id']}, this)">محروم کن</button>
          </div>
        </div>""")
    body=f"""
    <div class="card admin-card page-enter">
      <h1>🛡️ پنل پشتیبانی</h1>
      <p>گزارش‌ها را بررسی کن و در صورت تخلف، محرومیت را فقط برای همان بخش یا برای همه بخش‌ها اعمال کن.</p>
      <div>{''.join(items) or '<p>گزارشی وجود ندارد.</p>'}</div>
      <a class="btn" href="/lobby">بازگشت</a>
    </div>
    <script>
    async function banUser(id, btn) {{
      const item=btn.closest('.report-item');
      const target=item.querySelector('.report-meta b').textContent.trim();
      const scope=item.querySelector('.ban-scope').value;
      const hours=Number(item.querySelector('.ban-hours').value);
      const reason=item.querySelector('p').textContent.replace(/^محتوا:\\s*/,'').slice(0,300);
      const r=await fetch('/support/ban',{{method:'POST',headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify({{report_id:id,target,scope,hours,reason}})}});
      const d=await r.json();
      if(d.ok) {{ btn.textContent='✅ محروم شد'; btn.disabled=true; }}
      else alert('خطا در اعمال محرومیت');
    }}
    </script>"""
    return page_shell("پنل پشتیبانی",body,username)

def _render_messages(messages: list[dict], username: str) -> str:
    if not messages:
        return '<div style="opacity:0.6;text-align:center;padding:20px 0">هنوز پیامی نیست...</div>'
    out = []
    for m in messages:
        cls = "msg me" if m["sender"] == username else "msg"
        sender=html.escape(m["sender"])
        content=html.escape(m["content"])
        report="" if m["sender"] == username else (
            f'<button class="report-btn" onclick="reportMsg({m["sender"]!r}, {m["content"]!r})">گزارش</button>')
        out.append(f'<div class="{cls}"><span class="sender">{sender}</span>{content}{report}</div>')
    return "".join(out)


def chat_public_page(username: str, messages: list[dict]) -> str:
    body = f"""
    <div class="card">
      <h1>💬 چت عمومی</h1>
      <div class="chat-box" id="chatBox">{_render_messages(messages, username)}</div>
      <div class="chat-input-row">
        <input type="text" id="msgInput" placeholder="پیامت رو بنویس..." autocomplete="off">
        <button onclick="sendMsg()">ارسال</button>
      </div>
    </div>
    <script>
    const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(wsProto + "//" + location.host + "/ws/chat/public");
    const box = document.getElementById("chatBox");
    const me = {username!r};
    function addMsg(sender, content) {{
        const div = document.createElement("div");
        div.className = sender === me ? "msg me" : "msg";
        div.innerHTML = "<span class='sender'></span>";
        div.querySelector(".sender").textContent = sender;
        div.appendChild(document.createTextNode(content));
        if (sender !== me) {{
            const rb=document.createElement("button"); rb.className="report-btn"; rb.textContent="گزارش";
            rb.onclick=()=>reportMsg(sender, content);
            div.appendChild(rb);
        }}
        box.appendChild(div);
        box.scrollTop = box.scrollHeight;
    }}
    ws.onmessage = (ev) => {{
        const data = JSON.parse(ev.data);
        addMsg(data.sender, data.content);
    }};
    async function reportMsg(target, content) {{
        if (!confirm("این پیام را گزارش می‌کنی؟")) return;
        const r = await fetch("/report", {{method:"POST", headers:{{"Content-Type":"application/json"}},
            body:JSON.stringify({{target, content, context:"chat_public"}})}});
        if ((await r.json()).ok) alert("گزارش ثبت شد.");
    }}
    function sendMsg() {{
        const input = document.getElementById("msgInput");
        const text = input.value.trim();
        if (!text) return;
        ws.send(JSON.stringify({{content: text}}));
        input.value = "";
    }}
    document.getElementById("msgInput").addEventListener("keydown", (e) => {{
        if (e.key === "Enter") sendMsg();
    }});
    box.scrollTop = box.scrollHeight;
    </script>"""
    return page_shell("چت عمومی", body, username)


def chat_private_page(username: str, other: str, messages: list[dict]) -> str:
    body = f"""
    <div class="card">
      <h1>💬 چت خصوصی با {html.escape(other)}</h1>
      <div class="chat-box" id="chatBox">{_render_messages(messages, username)}</div>
      <div class="chat-input-row">
        <input type="text" id="msgInput" placeholder="پیامت رو بنویس..." autocomplete="off">
        <button onclick="sendMsg()">ارسال</button>
      </div>
    </div>
    <script>
    const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(wsProto + "//" + location.host + "/ws/chat/private/{html.escape(other)}");
    const box = document.getElementById("chatBox");
    const me = {username!r};
    function addMsg(sender, content) {{
        const div = document.createElement("div");
        div.className = sender === me ? "msg me" : "msg";
        div.innerHTML = "<span class='sender'></span>";
        div.querySelector(".sender").textContent = sender;
        div.appendChild(document.createTextNode(content));
        if (sender !== me) {{
            const rb=document.createElement("button"); rb.className="report-btn"; rb.textContent="گزارش";
            rb.onclick=()=>reportMsg(sender, content);
            div.appendChild(rb);
        }}
        box.appendChild(div);
        box.scrollTop = box.scrollHeight;
    }}
    ws.onmessage = (ev) => {{
        const data = JSON.parse(ev.data);
        addMsg(data.sender, data.content);
    }};
    async function reportMsg(target, content) {{
        if (!confirm("این پیام را گزارش می‌کنی؟")) return;
        const r = await fetch("/report", {{method:"POST", headers:{{"Content-Type":"application/json"}},
            body:JSON.stringify({{target, content, context:"chat_private"}})}});
        if ((await r.json()).ok) alert("گزارش ثبت شد.");
    }}
    function sendMsg() {{
        const input = document.getElementById("msgInput");
        const text = input.value.trim();
        if (!text) return;
        ws.send(JSON.stringify({{content: text}}));
        input.value = "";
    }}
    document.getElementById("msgInput").addEventListener("keydown", (e) => {{
        if (e.key === "Enter") sendMsg();
    }});
    box.scrollTop = box.scrollHeight;
    </script>"""
    return page_shell(f"چت با {other}", body, username)


def tictactoe_page(username: str) -> str:
    body = f"""
    <div class="card">
      <h1>⭕ دوز دو نفره زنده</h1>
      <div class="status-line" id="status">در حال اتصال...</div>
      <div class="ttt-board" id="board"></div>
      <div style="text-align:center"><button onclick="location.reload()">بازی جدید / جستجوی دوباره</button></div>
    </div>
    <script>
    const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(wsProto + "//" + location.host + "/ws/tictactoe");
    const boardEl = document.getElementById("board");
    const statusEl = document.getElementById("status");
    let mySymbol = null;
    let currentBoard = Array(9).fill("");

    function render() {{
        boardEl.innerHTML = "";
        currentBoard.forEach((val, i) => {{
            const cell = document.createElement("div");
            cell.className = "ttt-cell";
            cell.textContent = val;
            cell.onclick = () => {{
                if (!val) ws.send(JSON.stringify({{type: "move", cell: i}}));
            }};
            boardEl.appendChild(cell);
        }});
    }}
    render();

    ws.onmessage = (ev) => {{
        const data = JSON.parse(ev.data);
        if (data.type === "waiting") {{
            statusEl.textContent = "⏳ در حال پیدا کردن حریف... (۳۰ ثانیه)";

        }} else if (data.type === "state") {{
            mySymbol = data.your_symbol;
            currentBoard = data.board;
            render();
            if (data.winner === "draw") {{
                statusEl.textContent = "🤝 مساوی شد!";
            }} else if (data.winner) {{
                statusEl.textContent = (data.winner === mySymbol) ? "🏆 بردی!" : "😢 باختی!";
            }} else {{
                statusEl.textContent = "شما: " + mySymbol + " | حریف: " + data.opponent +
                    " | نوبت: " + (data.turn === mySymbol ? "توئه!" : "حریف");
            }}
        }} else if (data.type === "opponent_left") {{
            statusEl.textContent = "❌ حریف بازی رو ترک کرد.";
        }}
    }};
    </script>"""
    return page_shell("دوز", body, username)


def drawing_page(username: str) -> str:
    body = """
    <div class="card">
      <h1>🎨 نقاشی حدسی دو نفره</h1>
      <div class="status-line" id="status">در حال اتصال...</div>

      <div id="roundInfo" class="draw-round-info" style="display:none">
        <span id="roundLabel"></span>
        <span id="timerLabel" class="draw-timer"></span>
      </div>

      <div id="scoreBar" class="draw-scorebar" style="display:none"></div>

      <div id="canvasWrap" class="draw-canvas-wrap" style="display:none">
        <canvas id="board" width="600" height="420"></canvas>
      </div>

      <div id="palette" class="draw-palette" style="display:none"></div>
      <div id="tools" class="draw-tools" style="display:none">
        <button class="draw-tool active" id="penTool">✏️ قلم</button>
        <button class="draw-tool" id="eraserTool">🧽 پاک‌کن</button>
        <button class="draw-size active" data-size="4">باریک</button>
        <button class="draw-size" data-size="8">متوسط</button>
        <button class="draw-size" data-size="14">ضخیم</button>
      </div>
      <div id="drawerWordBox" class="draw-word-box" style="display:none"></div>
      <div style="text-align:center;display:none" id="clearBtnWrap">
        <button id="clearBtn">🧹 پاک کردن بوم</button>
      </div>

      <div id="optionsGrid" class="draw-options" style="display:none"></div>

      <div id="resultPanel" class="draw-result" style="display:none"></div>

      <div style="text-align:center;margin-top:14px">
        <a class="btn glow-btn" href="/lobby" onclick="event.preventDefault(); fetch('/game/leave',{method:'POST'}).finally(()=>location.href='/lobby')">بازگشت به لابی</a>
      </div>
    </div>

    <script>
    const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(wsProto + "//" + location.host + "/ws/drawing");
    const me = """ + f"{username!r}" + """;

    const statusEl = document.getElementById("status");
    const roundInfo = document.getElementById("roundInfo");
    const roundLabel = document.getElementById("roundLabel");
    const timerLabel = document.getElementById("timerLabel");
    const scoreBar = document.getElementById("scoreBar");
    const canvasWrap = document.getElementById("canvasWrap");
    const canvas = document.getElementById("board");
    const ctx = canvas.getContext("2d");
    const palette = document.getElementById("palette");
    const tools = document.getElementById("tools");
    const penTool = document.getElementById("penTool");
    const eraserTool = document.getElementById("eraserTool");
    const drawerWordBox = document.getElementById("drawerWordBox");
    const clearBtnWrap = document.getElementById("clearBtnWrap");
    const clearBtn = document.getElementById("clearBtn");
    const optionsGrid = document.getElementById("optionsGrid");
    const resultPanel = document.getElementById("resultPanel");

    let role = null;
    let currentColor = "#111111";
    let currentSize = 4;
    let tool = "pen";
    let drawing = false;
    let lastX = null, lastY = null;
    let countdownTimer = null;

    function clearCanvas() {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    clearCanvas();

    function renderScoreBar(scores) {
        scoreBar.innerHTML = "";
        Object.entries(scores || {}).forEach(([name, score]) => {
            const chip = document.createElement("div");
            chip.className = "draw-score-chip" + (name === me ? " me" : "");
            chip.textContent = name + ": " + score;
            scoreBar.appendChild(chip);
        });
        scoreBar.style.display = "flex";
    }

    function startCountdown(seconds, onTick) {
        if (countdownTimer) clearInterval(countdownTimer);
        let remaining = seconds;
        onTick(remaining);
        countdownTimer = setInterval(() => {
            remaining -= 1;
            onTick(remaining);
            if (remaining <= 0) clearInterval(countdownTimer);
        }, 1000);
    }

    function normPoint(x, y) {
        return {x: x / canvas.width, y: y / canvas.height};
    }

    function canvasPos(ev) {
        const rect = canvas.getBoundingClientRect();
        const clientX = ev.touches ? ev.touches[0].clientX : ev.clientX;
        const clientY = ev.touches ? ev.touches[0].clientY : ev.clientY;
        return {
            x: (clientX - rect.left) * (canvas.width / rect.width),
            y: (clientY - rect.top) * (canvas.height / rect.height)
        };
    }

    function drawLine(x0, y0, x1, y1, color) {
        ctx.strokeStyle = color;
        ctx.lineWidth = currentSize;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
        ctx.stroke();
    }

    canvas.addEventListener("pointerdown", (ev) => {
        if (role !== "drawer") return;
        drawing = true;
        const p = canvasPos(ev);
        lastX = p.x; lastY = p.y;
    });
    canvas.addEventListener("pointermove", (ev) => {
        if (role !== "drawer" || !drawing) return;
        const p = canvasPos(ev);
        drawLine(lastX, lastY, p.x, p.y, currentColor);
        const n0 = normPoint(lastX, lastY);
        const n1 = normPoint(p.x, p.y);
        ws.send(JSON.stringify({type: "draw", x0: n0.x, y0: n0.y, x1: n1.x, y1: n1.y,
            color: tool === "eraser" ? "#ffffff" : currentColor, size: currentSize}));
        lastX = p.x; lastY = p.y;
    });
    ["pointerup", "pointerleave", "pointercancel"].forEach(evName => {
        canvas.addEventListener(evName, () => { drawing = false; });
    });

    clearBtn.addEventListener("click", () => {
        clearCanvas();
        ws.send(JSON.stringify({type: "clear"}));
    });
    penTool.onclick=()=>{tool="pen"; penTool.classList.add("active"); eraserTool.classList.remove("active");};
    eraserTool.onclick=()=>{tool="eraser"; eraserTool.classList.add("active"); penTool.classList.remove("active");};
    document.querySelectorAll(".draw-size").forEach(btn=>btn.onclick=()=>{
        currentSize=Number(btn.dataset.size)||4;
        document.querySelectorAll(".draw-size").forEach(x=>x.classList.remove("active"));
        btn.classList.add("active");
    });


    function buildPalette(colors) {
        palette.innerHTML = "";
        colors.forEach((c, i) => {
            const sw = document.createElement("div");
            sw.className = "draw-swatch" + (i === 0 ? " active" : "");
            sw.style.background = c;
            sw.onclick = () => {
                currentColor = c;
                [...palette.children].forEach(el => el.classList.remove("active"));
                sw.classList.add("active");
            };
            palette.appendChild(sw);
        });
        currentColor = colors[0];
    }

    function buildOptions(options) {
        optionsGrid.innerHTML = "";
        options.forEach((word) => {
            const btn = document.createElement("button");
            btn.className = "draw-option-btn";
            btn.textContent = word;
            btn.onclick = () => {
                if (btn.disabled) return;
                ws.send(JSON.stringify({type: "guess", word: word}));
            };
            btn.dataset.word = word;
            optionsGrid.appendChild(btn);
        });
    }

    function resetRoundUI() {
        resultPanel.style.display = "none";
        roundInfo.style.display = "flex";
        clearCanvas();
    }

    ws.onmessage = (ev) => {
        const data = JSON.parse(ev.data);

        if (data.type === "waiting") {
            statusEl.textContent = "⏳ در حال پیدا کردن حریف...";
            statusEl.style.display = "block";
            canvasWrap.style.display = "none";
            scoreBar.style.display = "none";
        }

        else if (data.type === "round_start") {
            statusEl.style.display = "none";
            resetRoundUI();
            role = data.role;
            renderScoreBar(data.scores);
            canvasWrap.style.display = "block";
            roundLabel.textContent = "دور " + data.round + " از " + data.total_rounds +
                (role === "drawer" ? " — نوبت نقاشی توئه" : " — حدس بزن " + data.opponent + " چی می‌کشه");

            if (role === "drawer") {
                drawerWordBox.style.display = "block";
                drawerWordBox.textContent = "کلمه‌ای که باید بکشی: " + data.word;
                palette.style.display = "flex";
                tools.style.display = "flex";
                clearBtnWrap.style.display = "block";
                optionsGrid.style.display = "none";
                buildPalette(data.colors);
            } else {
                drawerWordBox.style.display = "none";
                palette.style.display = "none";
                clearBtnWrap.style.display = "none";
                optionsGrid.style.display = "grid";
                buildOptions(data.options);
            }

            startCountdown(data.duration, (remaining) => {
                timerLabel.textContent = "⏱ " + Math.max(0, remaining) + " ثانیه";
            });
        }

        else if (data.type === "draw") {
            const x0 = data.x0 * canvas.width, y0 = data.y0 * canvas.height;
            const x1 = data.x1 * canvas.width, y1 = data.y1 * canvas.height;
            currentSize = Number(data.size) || 4;
            drawLine(x0, y0, x1, y1, data.color);
        }

        else if (data.type === "clear") {
            clearCanvas();
        }

        else if (data.type === "guess_wrong") {
            const btn = optionsGrid.querySelector('[data-word="' + CSS.escape(data.word) + '"]');
            if (btn) { btn.disabled = true; btn.classList.add("wrong"); }
        }

        else if (data.type === "round_result") {
            if (countdownTimer) clearInterval(countdownTimer);
            roundInfo.style.display = "none";
            palette.style.display = "none";
            clearBtnWrap.style.display = "none";
            drawerWordBox.style.display = "none";
            optionsGrid.style.display = "none";
            renderScoreBar(data.scores);

            resultPanel.style.display = "block";
            let html = "<div class='draw-result-title'>" +
                (data.correct ? "✅ حدس درست بود!" : "⌛ زمان تموم شد!") +
                "</div>";
            html += "<div>کلمه: <b>" + data.word + "</b></div>";
            if (data.correct) {
                html += "<div>" + data.guesser + " امتیاز " + data.points_guesser + " گرفت و " +
                    data.drawer + " امتیاز " + data.points_drawer + " گرفت.</div>";
            } else {
                html += "<div>این دور امتیازی داده نشد.</div>";
            }
            resultPanel.innerHTML = html;
            if (data.drawer !== me) {{
                const rb=document.createElement("button"); rb.className="report-btn"; rb.textContent="گزارش نقاشی";
                rb.onclick=async()=>{{
                    const r=await fetch("/report",{{method:"POST",headers:{{"Content-Type":"application/json"}},
                      body:JSON.stringify({{target:data.drawer,content:"نقاشی/محتوای دور گزارش شد",context:"drawing"}})}});
                    if((await r.json()).ok) alert("گزارش ثبت شد.");
                }};
                resultPanel.appendChild(rb);
            }}
            const noteEl = document.createElement("div");
            noteEl.className = "draw-result-note";
            resultPanel.appendChild(noteEl);
            startCountdown(data.break_seconds, (remaining) => {
                noteEl.textContent = data.is_last
                    ? "نمایش نتیجهٔ نهایی... " + Math.max(0, remaining)
                    : "دور بعدی تا " + Math.max(0, remaining) + " ثانیهٔ دیگر شروع می‌شود...";
            });
        }

        else if (data.type === "game_over") {
            if (countdownTimer) clearInterval(countdownTimer);
            statusEl.style.display = "none";
            roundInfo.style.display = "none";
            canvasWrap.style.display = "none";
            palette.style.display = "none";
            clearBtnWrap.style.display = "none";
            optionsGrid.style.display = "none";
            renderScoreBar(data.scores);

            resultPanel.style.display = "block";
            const entries = Object.entries(data.scores).sort((a, b) => b[1] - a[1]);
            let html = "<div class='draw-result-title'>🏁 نتیجهٔ نهایی</div>";
            entries.forEach(([name, score]) => {
                const tag = (data.winner === name) ? " 🏆" : "";
                html += "<div>" + name + ": " + score + tag + "</div>";
            });
            if (!data.winner) html += "<div>🤝 مساوی شدید!</div>";
            resultPanel.innerHTML = html;
        }

        else if (data.type === "opponent_left") {
            if (countdownTimer) clearInterval(countdownTimer);
            statusEl.style.display = "block";
            statusEl.textContent = "❌ حریف بازی رو ترک کرد.";
            roundInfo.style.display = "none";
            canvasWrap.style.display = "none";
            palette.style.display = "none";
            clearBtnWrap.style.display = "none";
            optionsGrid.style.display = "none";
        }
    };
    </script>"""
    return page_shell("نقاشی حدسی", body, username)

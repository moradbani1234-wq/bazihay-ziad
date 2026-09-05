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
        <a href="/game/wordgame">🔤 حدس کلمه</a>
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


def _render_messages(messages: list[dict], username: str) -> str:
    if not messages:
        return '<div style="opacity:0.6;text-align:center;padding:20px 0">هنوز پیامی نیست...</div>'
    out = []
    for m in messages:
        cls = "msg me" if m["sender"] == username else "msg"
        out.append(
            f'<div class="{cls}"><span class="sender">{html.escape(m["sender"])}</span>{html.escape(m["content"])}</div>'
        )
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
        box.appendChild(div);
        box.scrollTop = box.scrollHeight;
    }}
    ws.onmessage = (ev) => {{
        const data = JSON.parse(ev.data);
        addMsg(data.sender, data.content);
    }};
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
        box.appendChild(div);
        box.scrollTop = box.scrollHeight;
    }}
    ws.onmessage = (ev) => {{
        const data = JSON.parse(ev.data);
        addMsg(data.sender, data.content);
    }};
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
            statusEl.textContent = "⏳ در حال پیدا کردن حریف...";
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


def wordgame_page(username: str) -> str:
    body = """
    <div class="card">
      <h1>🔤 حدس کلمه (۵ حرفی فارسی)</h1>
      <div class="status-line" id="status">یه کلمهٔ ۵ حرفی حدس بزن! (۶ فرصت داری)</div>
      <div id="rows"></div>
      <div class="chat-input-row">
        <input type="text" id="guessInput" maxlength="5" placeholder="حدس تو..." autocomplete="off">
        <button onclick="submitGuess()">حدس</button>
      </div>
      <div style="text-align:center;margin-top:12px">
        <button onclick="startGame()">🔄 بازی جدید</button>
      </div>
    </div>
    <script>
    const rowsEl = document.getElementById("rows");
    const statusEl = document.getElementById("status");
    let wordLength = 5;
    let attempts = 0;
    let finished = false;

    async function startGame() {
        const res = await fetch("/api/wordgame/start", {method: "POST"});
        const data = await res.json();
        wordLength = data.length;
        attempts = 0;
        finished = false;
        rowsEl.innerHTML = "";
        statusEl.textContent = "یه کلمهٔ " + wordLength + " حرفی حدس بزن! (۶ فرصت داری)";
    }

    async function submitGuess() {
        if (finished) return;
        const input = document.getElementById("guessInput");
        const guess = input.value.trim();
        if (guess.length !== wordLength) {
            statusEl.textContent = "⚠️ کلمه باید " + wordLength + " حرف باشد.";
            return;
        }
        const res = await fetch("/api/wordgame/guess", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({guess: guess})
        });
        if (!res.ok) {
            const err = await res.json();
            statusEl.textContent = "⚠️ " + (err.detail || "خطا");
            return;
        }
        const data = await res.json();
        const row = document.createElement("div");
        row.className = "word-row";
        [...guess].forEach((ch, i) => {
            const box = document.createElement("div");
            box.className = "letter-box " + data.feedback[i];
            box.textContent = ch;
            row.appendChild(box);
        });
        rowsEl.appendChild(row);
        input.value = "";
        attempts = data.attempts;

        if (data.won) {
            statusEl.textContent = "🎉 بردی! کلمه همون بود که گفتی!";
            finished = true;
        } else if (data.lost) {
            statusEl.textContent = "😢 فرصت‌ها تموم شد. کلمه این بود: " + data.target;
            finished = true;
        } else {
            statusEl.textContent = "تلاش " + attempts + " از ۶";
        }
    }

    document.getElementById("guessInput").addEventListener("keydown", (e) => {
        if (e.key === "Enter") submitGuess();
    });

    startGame();
    </script>"""
    return page_shell("حدس کلمه", body, username)

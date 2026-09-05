"""صفحات HTML به‌صورت رشته‌های پایتون؛ برای ساده نگه‌داشتن دیپلوی، بدون پوشه‌های جدا."""

import html

BASE_CSS = """
* { box-sizing: border-box; }
body {
    background: #0f1117; color: #e8e8ec; font-family: Tahoma, sans-serif;
    margin: 0; padding: 0; direction: rtl;
}
.nav {
    display: flex; justify-content: space-between; align-items: center;
    padding: 14px 20px; background: #171a23; border-bottom: 1px solid #262a36;
}
.nav a { color: #8ab4ff; text-decoration: none; margin-inline-start: 14px; }
.container { max-width: 640px; margin: 0 auto; padding: 20px; }
.card {
    background: #171a23; border: 1px solid #262a36; border-radius: 14px;
    padding: 22px; margin-bottom: 16px;
}
h1, h2 { margin-top: 0; }
input[type=text], input[type=password] {
    width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #333747;
    background: #0f1117; color: #fff; margin-bottom: 12px; font-size: 15px;
}
button, .btn {
    background: #5865f2; color: #fff; border: none; padding: 12px 18px;
    border-radius: 8px; font-size: 15px; cursor: pointer; text-decoration: none;
    display: inline-block;
}
button:hover, .btn:hover { background: #4752c4; }
.error { color: #ff6b6b; margin-bottom: 10px; }
.grid-links { display: grid; gap: 12px; }
.grid-links a {
    background: #1f2330; border: 1px solid #2c3040; border-radius: 12px;
    padding: 18px; text-align: center; color: #fff; text-decoration: none; font-size: 17px;
}
.grid-links a:hover { background: #262b3b; }
.chat-box {
    height: 360px; overflow-y: auto; background: #0f1117; border: 1px solid #262a36;
    border-radius: 10px; padding: 10px; margin-bottom: 12px; display: flex; flex-direction: column; gap: 6px;
}
.msg { padding: 8px 12px; border-radius: 10px; background: #1f2330; max-width: 80%; }
.msg.me { align-self: flex-end; background: #5865f2; }
.msg .sender { font-size: 12px; opacity: 0.7; display: block; margin-bottom: 2px; }
.chat-input-row { display: flex; gap: 8px; }
.chat-input-row input { flex: 1; margin-bottom: 0; }
.ttt-board {
    display: grid; grid-template-columns: repeat(3, 90px); grid-template-rows: repeat(3, 90px);
    gap: 8px; justify-content: center; margin: 20px 0;
}
.ttt-cell {
    background: #1f2330; border: 1px solid #2c3040; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 36px; cursor: pointer; user-select: none;
}
.ttt-cell:hover { background: #262b3b; }
.status-line { text-align: center; font-size: 16px; margin-bottom: 8px; }
.word-row { display: flex; gap: 6px; justify-content: center; margin-bottom: 6px; }
.letter-box {
    width: 48px; height: 48px; border: 2px solid #333747; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 22px;
}
.letter-box.correct { background: #2e7d32; border-color: #2e7d32; }
.letter-box.present { background: #b8860b; border-color: #b8860b; }
.letter-box.absent { background: #333747; border-color: #333747; }
"""


def _nav(username: str | None) -> str:
    if username:
        u = html.escape(username)
        return f"""
        <div class="nav">
          <div>🎮 <b>{u}</b></div>
          <div>
            <a href="/lobby">لابی</a>
            <a href="/logout">خروج</a>
          </div>
        </div>"""
    return """
    <div class="nav">
      <div>🎮 بازی‌خونه</div>
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
      <h1>ورود</h1>
      {err_html}
      <form method="post" action="/login">
        <input type="text" name="username" placeholder="نام کاربری" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button type="submit">ورود</button>
      </form>
      <p>حساب نداری؟ <a href="/signup" style="color:#8ab4ff">ثبت‌نام کن</a></p>
    </div>"""
    return page_shell("ورود", body)


def signup_page(error: str | None = None) -> str:
    err_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    body = f"""
    <div class="card">
      <h1>ثبت‌نام</h1>
      {err_html}
      <form method="post" action="/signup">
        <input type="text" name="username" placeholder="نام کاربری (حداقل ۳ حرف)" required>
        <input type="password" name="password" placeholder="رمز عبور (حداقل ۴ حرف)" required>
        <button type="submit">ساخت حساب</button>
      </form>
      <p>حساب داری؟ <a href="/login" style="color:#8ab4ff">وارد شو</a></p>
    </div>"""
    return page_shell("ثبت‌نام", body)


def lobby_page(username: str) -> str:
    body = f"""
    <div class="card">
      <h1>خوش اومدی، {html.escape(username)}!</h1>
      <div class="grid-links">
        <a href="/game/tictactoe">⭕ دوز دو نفره زنده</a>
        <a href="/game/wordgame">🔤 حدس کلمه (فارسی)</a>
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
        return '<div style="opacity:0.6;text-align:center">هنوز پیامی نیست...</div>'
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

"""صفحات HTML به‌صورت رشته‌های پایتون؛ برای ساده نگه‌داشتن دیپلوی، بدون پوشه‌های جدا."""

import html
import time
from urllib.parse import quote

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
    box-shadow: 0 10px 30px -18px rgba(0,0,0,0.55);
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
    background: linear-gradient(160deg, var(--surface-raised), var(--surface));
    border: 1px solid var(--border); border-radius: 14px;
    padding: 20px; text-align: center; color: var(--text); text-decoration: none;
    font-size: 17px; font-weight: 600; transition: border-color 0.15s ease, transform 0.1s ease;
    position: relative; overflow: hidden;
}
.grid-links a::before {
    content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1px;
    background: linear-gradient(120deg, rgba(47,169,160,0), rgba(232,169,74,.35), rgba(47,169,160,0));
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude; opacity: 0; transition: opacity .2s ease;
}
.grid-links a:hover { border-color: var(--saffron); transform: translateY(-1px); }
.grid-links a:hover::before { opacity: 1; }

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

.draw-players-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
.draw-player-card {
    flex: 1 1 200px; display: flex; align-items: center; gap: 10px;
    background: var(--surface-raised); border: 2px solid var(--border); border-radius: 16px;
    padding: 9px 12px; min-width: 0; transition: border-color .2s ease, box-shadow .2s ease;
}
.draw-player-card.me { border-color: var(--turquoise-dim); }
.draw-player-card.turn { border-color: var(--saffron); box-shadow: 0 0 0 3px rgba(232,169,74,.16); }
.draw-player-avatar {
    width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
    background: var(--bg); border: 2px solid var(--turquoise-dim);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700; color: var(--turquoise); overflow: hidden;
}
.draw-player-card.turn .draw-player-avatar { border-color: var(--saffron); color: var(--saffron); }
.draw-player-info { min-width: 0; flex: 1; }
.draw-player-name-row { display: flex; align-items: center; gap: 6px; }
.draw-player-name { font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.draw-player-star {
    display: inline-flex; align-items: center; gap: 2px; font-size: 12px; font-weight: 700;
    color: var(--saffron); flex-shrink: 0;
}
.draw-player-role {
    font-size: 12px; color: var(--text-muted); margin-top: 2px;
    display: flex; align-items: center; gap: 4px;
}
.draw-player-card.turn .draw-player-role { color: var(--saffron); }

.draw-board-frame {
    background: linear-gradient(160deg, var(--surface-raised), var(--surface));
    border: 1px solid var(--border); border-radius: 20px; padding: 10px; margin-bottom: 12px;
    box-shadow: 0 12px 30px -18px rgba(0,0,0,.6), inset 0 0 0 1px rgba(255,255,255,.02);
}
.draw-canvas-wrap {
    background: #fff; border-radius: 13px; overflow: hidden;
    border: 1px solid var(--border); line-height: 0;
}
.draw-canvas-wrap canvas {
    width: 100%; height: auto; display: block; touch-action: none; cursor: crosshair;
}

.draw-palette { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 12px; }
.draw-swatch {
    width: 34px; height: 34px; border-radius: 50%; cursor: pointer;
    border: 3px solid var(--surface); box-shadow: 0 0 0 1px var(--border);
    transition: transform .12s ease;
}
.draw-swatch:hover { transform: scale(1.08); }
.draw-swatch.active { box-shadow: 0 0 0 2px var(--saffron); transform: scale(1.08); }

.draw-word-box {
    text-align: center; background: var(--surface-raised); border: 1px dashed var(--saffron);
    border-radius: 10px; padding: 10px; margin-bottom: 12px; font-weight: 700; color: var(--saffron);
}

.draw-options {
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 12px;
}
.draw-option-btn {
    background: var(--surface-raised); color: var(--text); border: 1px solid var(--border);
    padding: 10px 18px; font-size: 14px; font-weight: 600; flex: 0 1 auto; border-radius: 999px;
}
.draw-option-btn:hover:not(:disabled) { background: var(--turquoise-dim); color: #fff; border-color: var(--turquoise-dim); }
.draw-option-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.draw-option-btn.wrong { border-color: var(--danger); color: var(--danger); text-decoration: line-through; background: var(--surface-raised); }

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
.draw-size-slider-wrap { display:flex; align-items:center; gap:10px; background:var(--surface-raised); border:1px solid var(--border); border-radius:10px; padding:8px 14px; flex:1 1 200px; min-width:180px; }
.draw-size-label { color:var(--text-muted); font-size:13px; white-space:nowrap; }
.draw-size-value { color:var(--saffron); font-weight:700; font-size:14px; min-width:22px; text-align:center; }
.draw-size-slider-wrap input[type=range] { flex:1; accent-color: var(--saffron); cursor:pointer; }
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
.ban-controls { flex-wrap:wrap; align-items:center; }
.ban-unit { color:var(--text-muted); font-size:12.5px; margin-inline-end:6px; }
.ban-row {
    padding:14px; border:1px solid var(--border); border-radius:12px; margin-bottom:10px;
    background:var(--surface-raised); display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;
}
.ban-scope-tag {
    display:inline-block; margin-inline-start:8px; font-size:11.5px; font-weight:600; color:var(--saffron);
    background:rgba(232,169,74,.12); border:1px solid rgba(232,169,74,.3); border-radius:8px; padding:2px 8px;
}
.unban-btn { background:transparent; color:var(--turquoise); border:1px solid var(--turquoise-dim); padding:8px 16px; }
.unban-btn:hover { background:var(--turquoise-dim); color:#fff; }


.game-card, .grid-links a { transition: transform .22s ease, box-shadow .22s ease, filter .22s ease; }
.grid-links a:hover { transform: translateY(-4px) scale(1.015); filter: brightness(1.06); }
.grid-links a small { display:block; opacity:.7; font-size:11px; margin-top:4px; }
.status-line { min-height: 24px; transition: opacity .2s ease, transform .2s ease; }
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
            <a href="/leaderboard">🏆 رتبه‌بندی</a>
            {('<a href="/support">🛡️ پشتیبانی</a>' if username == 'morad' else '')}
            <a href="/logout">خروج</a>
          </div>
        </div>"""
    return """
    <div class="nav">
      <div class="nav-brand">🎲 بازی‌خونه</div>
      <div><a href="/login">ورود</a></div>
    </div>"""


def page_shell(title: str, body: str, username: str | None = None) -> str:
    active="home"
    if "رتبه" in title: active="leaderboard"
    elif "پیام" in title or "چت" in title or "گفتگو" in title: active="messages"
    elif "فروشگاه" in title: active="shop"
    elif "تنظیمات" in title: active="settings"
    nav=_neon_nav(username,active) if username else _nav(username)
    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><style>{BASE_CSS}</style></head><body>{nav}<div class="container">{body}</div></body></html>"""


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
        <a class="glow-btn" href="/game/tictactoe">⭕ دوز دو نفره زنده <small>رقابت سریع</small></a>
        <a class="glow-btn" href="/game/drawing">🎨 نقاشی حدسی دو نفره <small>همزمان و زنده</small></a>
        <a class="glow-btn" href="/chat/public">💬 چت عمومی <small>گفت‌وگو و گزارش</small></a>
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
    items=[]; medals=["🥇","🥈","🥉"]
    for i,r in enumerate(rows,1):
        medal=medals[i-1] if i<=3 else str(i)
        cls=" me" if r["username"]==username else ""
        items.append(f'''<div class="leader-row{cls}"><div class="rank-medal">{medal}</div><div><a class="profile-link" href="/profile?u={quote(r["username"],safe='')}"><b>{html.escape(r["username"])}</b></a><div class="report-meta">بازیکن Draw Battle</div></div><div><b>{r["rating"]}</b><small> امتیاز</small></div><div><b>{r["wins"]}</b><small> برد</small></div></div>''')
    body=f'''<div class="page-heading"><div><div class="sub">RANKING • TOP PLAYERS</div><h1>🏆 لیدر بورد</h1></div><a class="btn" href="/lobby">خانه</a></div><div class="card hero page-enter"><p>برترین بازیکن‌های بازی اینجا می‌درخشند. رتبه‌ها بر اساس عملکرد بازی محاسبه می‌شوند.</p><div>{"".join(items) or "<p>هنوز آماری ثبت نشده.</p>"}</div></div>'''
    return page_shell("رتبه‌بندی",body,username)

def support_page(username: str, reports: list[dict], active_bans: list[dict] | None = None, tickets: list[dict] | None = None) -> str:
    active_bans = active_bans or []
    tickets = tickets or []
    scope_label = {"all":"همه بخش‌ها","chat":"چت","games":"بازی‌ها","drawing":"نقاشی","tictactoe":"دوز"}

    items=[]
    for r in reports:
        status="حل‌شده" if r["status"]!="open" else "باز"
        items.append(f"""
        <div class="report-item" data-id="{r['id']}">
          <div><b>گزارش {r['id']}</b> — {html.escape(r['context'])} — <span>{status}</span></div>
          <div class="report-meta">گزارش‌دهنده: {html.escape(r['reporter'])} | کاربر گزارش‌شده: <b>{html.escape(r['target'])}</b></div>
          <p style="margin:8px 0"><b>محتوا:</b> {html.escape(r['content'])}</p>
          {('<img src="'+html.escape(r.get("attachment") or '')+'" style="max-width:100%;border-radius:12px;border:1px solid var(--border);margin:8px 0" alt="نقاشی گزارش‌شده">' if r.get("attachment") else '')}
          <div class="draw-tools ban-controls">
            <select class="draw-size ban-scope"><option value="all">همه</option><option value="chat">چت</option><option value="games">بازی‌ها</option><option value="drawing">نقاشی</option><option value="tictactoe">دوز</option></select>
            <input class="ban-hours" type="number" min="0" max="168" step="1" value="0" style="width:70px;margin:0" title="ساعت">
            <span class="ban-unit">ساعت</span>
            <input class="ban-minutes" type="number" min="0" max="59" step="1" value="3" style="width:70px;margin:0" title="دقیقه">
            <span class="ban-unit">دقیقه</span>
            <button class="glow-btn" onclick="banUser({r['id']}, this)">محروم کن</button>
            <button class="btn" onclick="banReporter({r['id']}, {r['reporter']!r})">🚫 محرومیت گزارش‌دهنده</button>
          </div>
        </div>""")

    ban_rows=[]
    for b in active_bans:
        remaining = max(0, b["until_ts"] - int(time.time()))
        h, rem = divmod(remaining, 3600)
        m = rem // 60
        left_txt = (f"{h} ساعت و " if h else "") + f"{m} دقیقه"
        ban_rows.append(f"""
        <div class="ban-row" data-target="{html.escape(b['username'])}" data-scope="{html.escape(b['scope'])}">
          <div><b>{html.escape(b['username'])}</b> <span class="ban-scope-tag">{scope_label.get(b['scope'], b['scope'])}</span></div>
          <div class="report-meta">دلیل: {html.escape(b.get('reason') or '—')} | باقی‌مانده: {left_txt}</div>
          <button class="btn unban-btn" onclick="unbanUser(this)">رفع محرومیت</button>
        </div>""")

    body=f"""
    <div class="card admin-card page-enter">
      <h1>🛡️ پنل پشتیبانی</h1>
      <p>گزارش‌ها را بررسی کن، محرومیت را برای مدت دلخواه (به ساعت و دقیقه) روی همان بخش یا همهٔ بخش‌ها اعمال کن، یا کاربری را مستقیماً محروم/رفعِ‌محرومیت کن.</p>
    </div>

    <div class="card">
      <h2>🔨 محروم کردن مستقیم یک کاربر</h2>
      <div class="draw-tools ban-controls" style="justify-content:flex-start">
        <input type="text" id="directTarget" placeholder="نام کاربری" style="width:140px;margin:0">
        <select class="draw-size" id="directScope"><option value="all">همه</option><option value="chat">چت</option><option value="games">بازی‌ها</option><option value="drawing">نقاشی</option><option value="tictactoe">دوز</option></select>
        <input type="number" id="directHours" min="0" max="168" step="1" value="0" style="width:70px;margin:0" title="ساعت">
        <span class="ban-unit">ساعت</span>
        <input type="number" id="directMinutes" min="0" max="59" step="1" value="10" style="width:70px;margin:0" title="دقیقه">
        <span class="ban-unit">دقیقه</span>
      </div>
      <div style="margin-top:10px">
        <input type="text" id="directReason" placeholder="دلیل محرومیت (اختیاری)" style="margin:0">
      </div>
      <button class="glow-btn" style="margin-top:12px" onclick="banDirect()">محروم کن</button>
    </div>

    <div class="card">
      <h2>⏳ محرومیت‌های فعال</h2>
      <div id="activeBans">{''.join(ban_rows) or '<p>در حال حاضر کسی محروم نیست.</p>'}</div>
    </div>

    <div class="card">
      <h2>🎵 مدیریت آهنگ چت عمومی</h2>
      <p>آهنگ روی سرور ذخیره می‌شود؛ برای جلوگیری از حالت رادیویی/جرجر، هیچ پخش خودکاری انجام نمی‌شود و هر کاربر خودش روی «پخش» می‌زند.</p>
      <input type="text" id="musicTitle" placeholder="نام آهنگ / عنوان (اختیاری)">
      <input type="text" id="musicTarget" placeholder="آیدی کاربر (اختیاری؛ فقط برای همان کاربر)">
      
      <input type="file" id="musicFile" accept="audio/*" style="width:100%;margin:8px 0 12px">
      <button class="glow-btn" onclick="setMusic()">🎵 انتخاب و فعال کردن آهنگ</button>
      <button class="btn" onclick="clearMusic()" style="margin-inline-start:6px">⏹ قطع برای همه</button>
      <div class="support-music-preview">ℹ️ حداکثر حجم فایل ۱۵ مگابایت. به‌خاطر محدودیت مرورگر، هر کاربر با دکمه «پخش» شروع می‌کند.</div>
    </div>

    <div class="card admin-card">
      <h2>🎫 تیکت‌های رسمی پشتیبانی</h2>
      <div>{''.join(f"<div class=\"report-item\"><b>#{t['id']} — {html.escape(t['subject'])}</b><div class=\"report-meta\">از {html.escape(t['user'])} | {html.escape(t['status'])}</div><p>{html.escape(t['content'])}</p></div>" for t in tickets) or '<p>تیکتی ثبت نشده.</p>'}</div>
    </div>

    <div class="card">
      <h2>📄 گزارش‌ها</h2>
      <div>{''.join(items) or '<p>گزارشی وجود ندارد.</p>'}</div>
    </div>
    <a class="btn" href="/lobby">بازگشت</a>

    <script>
    async function doBan(payload, btn, okText) {{
      const r=await fetch('/support/ban',{{method:'POST',headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify(payload)}});
      const d=await r.json();
      if(d.ok) {{ if(btn) {{ btn.textContent=okText; btn.disabled=true; }} location.reload(); }}
      else alert('خطا در اعمال محرومیت (مدت را بررسی کن؛ باید بیشتر از صفر باشد)');
    }}

    async function banUser(id, btn) {{
      const item=btn.closest('.report-item');
      const target=item.querySelector('.report-meta b').textContent.trim();
      const scope=item.querySelector('.ban-scope').value;
      const hours=Number(item.querySelector('.ban-hours').value);
      const minutes=Number(item.querySelector('.ban-minutes').value);
      const reason=item.querySelector('p').textContent.replace(/^محتوا:\\s*/,'').slice(0,300);
      await doBan({{report_id:id,target,scope,hours,minutes,reason}}, btn, '✅ محروم شد');
    }}

    async function banDirect() {{
      const target=document.getElementById('directTarget').value.trim();
      const scope=document.getElementById('directScope').value;
      const hours=Number(document.getElementById('directHours').value);
      const minutes=Number(document.getElementById('directMinutes').value);
      const reason=document.getElementById('directReason').value.trim() || 'نقض قوانین';
      if(!target) {{ alert('نام کاربری را وارد کن'); return; }}
      await doBan({{target,scope,hours,minutes,reason}}, null, '');
    }}

    async function banReporter(id, target) {{
      if(!confirm('اگر گزارش بی‌مورد بوده، گزارش‌دهنده را محروم کنیم؟')) return;
      await doBan({{report_id:id,target,scope:'chat',minutes:10,reason:'گزارش بی‌مورد'}}, null, '');
    }}

    async function setMusic() {{
      const file=document.getElementById('musicFile').files[0];
      const title=document.getElementById('musicTitle').value.trim();
      const target_user=document.getElementById('musicTarget').value.trim();
      if(!file){{alert('اول یک آهنگ از گوشی انتخاب کن.');return;}}
      if(file.size>15*1024*1024){{alert('حجم آهنگ نباید بیشتر از ۱۵ مگابایت باشد.');return;}}
      const fd=new FormData(); fd.append('music',file);
      const r=await fetch('/support/music?title='+encodeURIComponent(title)+'&target_user='+encodeURIComponent(target_user),{{method:'POST',body:fd}});
      const d=await r.json();
      if(d.ok){{alert(target_user?'🎵 آهنگ فقط برای همان کاربر فعال شد.':'🎵 آهنگ آماده شد؛ پخش خودکار ندارد و هر کاربر خودش پخش می‌کند.');}}else alert(d.error==='user_not_found'?'کاربر پیدا نشد.':d.error==='bad_audio'?'این فایل صوتی پشتیبانی نمی‌شود.':'خطا در فعال‌سازی آهنگ.');
    }}
    async function clearMusic() {{
      const r=await fetch('/support/music/clear',{{method:'POST'}}); const d=await r.json();
      if(d.ok) alert('آهنگ قطع شد.');
    }}

    async function unbanUser(btn) {{
      const row=btn.closest('.ban-row');
      const target=row.dataset.target, scope=row.dataset.scope;
      const r=await fetch('/support/unban',{{method:'POST',headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify({{target,scope}})}});
      const d=await r.json();
      if(d.ok) {{ row.remove(); }}
      else alert('خطا در رفع محرومیت');
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
    function onMessage(ev) {{
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
    <div class="card page-enter">
      <h1>⭕ دوز دو نفره زنده</h1>
      <div class="status-line" id="status">🔌 اتصال به سرور...</div>
      <div class="ttt-board" id="board"></div>
      <div style="text-align:center;display:flex;gap:8px;justify-content:center;flex-wrap:wrap"><button class="glow-btn" onclick="location.reload()">🔁 بازی جدید / جستجوی دوباره</button><a class="btn" href="/lobby" onclick="event.preventDefault(); intentionallyLeaving=true; fetch('/game/leave',{{method:'POST'}}).finally(()=>location.href='/lobby')">🏠 بازگشت به لابی</a></div>
    </div>
    <script>
    const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
    const boardEl = document.getElementById("board");
    const statusEl = document.getElementById("status");
    let ws = null, reconnectTimer = null, intentionallyLeaving = false;
    let mySymbol = null, currentBoard = Array(9).fill("");

    function connect() {{
      statusEl.textContent = "🔌 اتصال سریع به سرور بازی...";
      ws = new WebSocket(wsProto + "//" + location.host + "/ws/tictactoe");
      ws.onopen = () => statusEl.textContent = "⚡ وصل شد! در حال پیدا کردن حریف...";
      ws.onerror = () => statusEl.textContent = "⚠️ مشکل اتصال؛ دوباره تلاش می‌کنیم...";
      ws.onclose = () => {{
        if (!intentionallyLeaving && !reconnectTimer) {{
          statusEl.textContent = "🔄 اتصال قطع شد؛ تلاش مجدد...";
          reconnectTimer = setTimeout(() => {{ reconnectTimer = null; connect(); }}, 1200);
        }}
      }};
      ws.onmessage = onMessage;
    }}

    function render() {{
      boardEl.innerHTML = "";
      currentBoard.forEach((val, i) => {{
        const cell = document.createElement("div");
        cell.className = "ttt-cell" + (val ? " filled" : "");
        cell.textContent = val;
        cell.onclick = () => {{
          if (!val && ws && ws.readyState === WebSocket.OPEN)
            ws.send(JSON.stringify({{type:"move", cell:i}}));
        }};
        boardEl.appendChild(cell);
      }});
    }}

    function onMessage(ev) {{
      const data = JSON.parse(ev.data);
      if (data.type === "waiting") {{
        let left=30; statusEl.textContent = "⏳ در صف حریف — "+left+" ثانیه";
        clearInterval(window.queueTimer); window.queueTimer=setInterval(()=>{{left--; statusEl.textContent="⏳ در صف حریف — "+Math.max(0,left)+" ثانیه"; if(left<=0) clearInterval(window.queueTimer);}},1000);
      }} else if (data.type === "queue_timeout") {{
        statusEl.textContent = "⌛ حریفی پیدا نشد؛ برای جستجوی دوباره صفحه را تازه کن.";
      }} else if (data.type === "state") {{
        mySymbol = data.your_symbol; currentBoard = data.board; render();
        if (data.winner === "draw") statusEl.textContent = "🤝 مساوی شد!";
        else if (data.winner) statusEl.textContent = data.winner === mySymbol ? "🏆 بردی!" : "😢 باختی!";
        else statusEl.textContent = "شما: " + mySymbol + " | حریف: " + data.opponent + " | نوبت: " + (data.turn === mySymbol ? "توئه! 🔥" : "حریف");
      }} else if (data.type === "game_won") {{
        intentionallyLeaving = true;
        statusEl.textContent = "🏆 شما برنده شدید! حریف از بازی خارج شد.";
      }} else if (data.type === "opponent_left") {{
        statusEl.textContent = data.winner === me ? "🏆 شما برنده شدید! حریف از بازی خارج شد." : "❌ حریف بازی را ترک کرد.";
      }}
    }}

    render();
    connect();
    </script>"""
    return page_shell("دوز", body, username)


def drawing_page(username: str) -> str:
    body = """
    <div class="card">
      <h1>🎨 نقاشی حدسی دو نفره</h1>
      <div class="status-line" id="status">در حال اتصال...</div>
      <div id="queueBox" class="queue-widget" style="display:none"></div>

      <div id="playersRow" class="draw-players-row" style="display:none"></div>

      <div id="roundInfo" class="draw-round-info" style="display:none">
        <span id="roundLabel"></span>
        <span id="timerLabel" class="draw-timer"></span>
      </div>

      <div id="boardFrame" class="draw-board-frame" style="display:none">
        <div id="canvasWrap" class="draw-canvas-wrap">
          <canvas id="board" width="600" height="420"></canvas>
        </div>
      </div>

      <div id="palette" class="draw-palette" style="display:none"></div>
      <div id="tools" class="draw-tools" style="display:none">
        <button class="draw-tool active" id="penTool">✏️ قلم</button>
        <button class="draw-tool" id="eraserTool">🧽 پاک‌کن</button>
        <div class="draw-size-slider-wrap">
          <span class="draw-size-label">ضخامت</span>
          <input type="range" id="sizeSlider" min="1" max="30" value="4" step="1">
          <span id="sizeValue" class="draw-size-value">4</span>
        </div>
      </div>
      <div id="drawerWordBox" class="draw-word-box" style="display:none"></div>
      <div style="text-align:center;display:none" id="clearBtnWrap">
        <button id="clearBtn">🧹 پاک کردن بوم</button>
      </div>

      <div id="optionsGrid" class="draw-options" style="display:none"></div>

      <div id="resultPanel" class="draw-result" style="display:none"></div>

      <div style="text-align:center;margin-top:14px">
        <a class="btn glow-btn" href="/lobby" onclick="event.preventDefault(); intentionallyLeaving=true; fetch('/game/leave',{{method:'POST'}}).finally(()=>location.href='/lobby')">بازگشت به لابی</a>
      </div>
    </div>

    <script>
    const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
    let ws = null;
    let reconnectTimer = null;
    let intentionallyLeaving = false;
    const me = """ + f"{username!r}" + """;

    const statusEl = document.getElementById("status");
    const queueBox = document.getElementById("queueBox");
    const roundInfo = document.getElementById("roundInfo");
    const roundLabel = document.getElementById("roundLabel");
    const timerLabel = document.getElementById("timerLabel");
    const playersRow = document.getElementById("playersRow");
    const boardFrame = document.getElementById("boardFrame");
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

    function renderPlayers(scores, drawerName) {
        playersRow.innerHTML = "";
        Object.entries(scores || {}).forEach(([name, score]) => {
            const isMe = name === me;
            const isDrawer = drawerName != null && name === drawerName;
            const card = document.createElement("div");
            card.className = "draw-player-card" + (isMe ? " me" : "") + (isDrawer ? " turn" : "");

            const avatar = document.createElement("div");
            avatar.className = "draw-player-avatar";
            avatar.textContent = name.slice(0, 1).toUpperCase();
            card.appendChild(avatar);

            const info = document.createElement("div");
            info.className = "draw-player-info";

            const nameRow = document.createElement("div");
            nameRow.className = "draw-player-name-row";
            const link = document.createElement("a");
            link.className = "profile-link draw-player-name";
            link.href = "/profile?u=" + encodeURIComponent(name);
            link.target = "_blank";
            link.rel = "noopener";
            link.textContent = name;
            const star = document.createElement("span");
            star.className = "draw-player-star";
            star.textContent = "⭐ " + score;
            nameRow.appendChild(link);
            nameRow.appendChild(star);
            info.appendChild(nameRow);

            if (drawerName != null) {
                const roleEl = document.createElement("div");
                roleEl.className = "draw-player-role";
                roleEl.textContent = isDrawer ? "✏️ نقاش" : "👁 حدس‌زن";
                info.appendChild(roleEl);
            }

            card.appendChild(info);
            playersRow.appendChild(card);
        });
        playersRow.style.display = "flex";
    }

    function renderQueue(count, needed) {
        queueBox.style.display = "flex";
        let dots = "";
        for (let i = 0; i < needed; i++) dots += '<div class="queue-dot' + (i < count ? ' filled' : '') + '"></div>';
        queueBox.innerHTML = '<div class="queue-spinner"></div><div class="queue-dots">' + dots +
            '</div><div class="queue-text">' + count + ' از ' + needed + ' نفر در صف هستند</div>' +
            '<div class="queue-sub">صبور باش؛ به‌محض تکمیل ظرفیت، بازی شروع می‌شود ✨</div>';
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

    function drawLine(x0, y0, x1, y1, color, size = currentSize) {
        ctx.strokeStyle = color;
        ctx.lineWidth = size;
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
        const paintColor = tool === "eraser" ? "#ffffff" : currentColor;
        drawLine(lastX, lastY, p.x, p.y, paintColor, currentSize);
        const n0 = normPoint(lastX, lastY);
        const n1 = normPoint(p.x, p.y);
        if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({type: "draw", x0: n0.x, y0: n0.y, x1: n1.x, y1: n1.y,
            color: tool === "eraser" ? "#ffffff" : currentColor, size: currentSize}));
        lastX = p.x; lastY = p.y;
    });
    ["pointerup", "pointerleave", "pointercancel"].forEach(evName => {
        canvas.addEventListener(evName, () => { drawing = false; });
    });

    clearBtn.addEventListener("click", () => {
        clearCanvas();
        if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({type: "clear"}));
    });
    penTool.onclick=()=>{tool="pen"; penTool.classList.add("active"); eraserTool.classList.remove("active");};
    eraserTool.onclick=()=>{tool="eraser"; eraserTool.classList.add("active"); penTool.classList.remove("active");};
    const sizeSlider = document.getElementById("sizeSlider");
    const sizeValue = document.getElementById("sizeValue");
    sizeSlider.addEventListener("input", () => {
        currentSize = Number(sizeSlider.value) || 4;
        sizeValue.textContent = currentSize;
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
                if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({type: "guess", word: word}));
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

    function connectDrawing() {
        statusEl.style.display = "block";
        statusEl.textContent = "🔌 اتصال سریع به سرور بازی...";
        ws = new WebSocket(wsProto + "//" + location.host + "/ws/drawing");
        ws.onopen = () => { statusEl.textContent = "⚡ وصل شد! حریف در حال پیدا شدن..."; };
        ws.onerror = () => { statusEl.textContent = "⚠️ اتصال ناپایدار؛ دوباره تلاش می‌کنیم..."; };
        ws.onclose = () => {
            if (!intentionallyLeaving && !reconnectTimer) {
                statusEl.textContent = "🔄 اتصال قطع شد؛ اتصال مجدد...";
                reconnectTimer = setTimeout(() => { reconnectTimer=null; connectDrawing(); }, 1200);
            }
        };
        ws.onmessage = onDrawingMessage;
    }

    function onDrawingMessage(ev) {
        const data = JSON.parse(ev.data);

        if (data.type === "waiting") {
            statusEl.style.display = "none";
            renderQueue(data.count || 1, data.needed || 2);
            boardFrame.style.display = "none";
            playersRow.style.display = "none";
        }

        else if (data.type === "queue_timeout") {
            queueBox.style.display = "none";
            statusEl.style.display = "block";
            statusEl.textContent = "⌛ حریفی پیدا نشد؛ برای جستجوی دوباره وارد شو.";
            boardFrame.style.display = "none";
        }

        else if (data.type === "round_start") {
            statusEl.style.display = "none";
            queueBox.style.display = "none";
            resetRoundUI();
            role = data.role;
            const drawerName = role === "drawer" ? me : data.opponent;
            renderPlayers(data.scores, drawerName);
            boardFrame.style.display = "block";
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
                optionsGrid.style.display = "flex";
                buildOptions(data.options);
            }

            startCountdown(data.duration, (remaining) => {
                timerLabel.textContent = "⏱ " + Math.max(0, remaining) + " ثانیه";
            });
        }

        else if (data.type === "draw") {
            const x0 = data.x0 * canvas.width, y0 = data.y0 * canvas.height;
            const x1 = data.x1 * canvas.width, y1 = data.y1 * canvas.height;
            const remoteSize = Math.max(1, Math.min(30, Number(data.size) || 4));
            drawLine(x0, y0, x1, y1, data.color || "#111111", remoteSize);
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
            renderPlayers(data.scores, data.drawer);

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
            if (data.drawer !== me) {
                const rb=document.createElement("button"); rb.className="report-btn"; rb.textContent="گزارش نقاشی";
                rb.onclick=async()=>{
                    const r=await fetch("/report",{method:"POST",headers:{"Content-Type":"application/json"},
                      body:JSON.stringify({target:data.drawer,content:"نقاشی/محتوای دور گزارش شد",context:"drawing",attachment:(canvas.toDataURL("image/jpeg",0.65)||"")})});
                    if((await r.json()).ok) alert("گزارش ثبت شد.");
                };
                resultPanel.appendChild(rb);
            }
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
            boardFrame.style.display = "none";
            palette.style.display = "none";
            clearBtnWrap.style.display = "none";
            optionsGrid.style.display = "none";
            renderPlayers(data.scores, null);

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

        else if (data.type === "game_won") {
            if (countdownTimer) clearInterval(countdownTimer);
            statusEl.style.display = "block";
            statusEl.textContent = "🏆 شما برنده شدید! حریف از بازی خارج شد.";
            roundInfo.style.display = "none";
            boardFrame.style.display = "none";
            palette.style.display = "none";
            clearBtnWrap.style.display = "none";
            optionsGrid.style.display = "none";
            resultPanel.style.display = "block";
            resultPanel.innerHTML = "<div class='draw-result-title'>🏆 شما برنده شدید!</div><div>حریف از بازی خارج شد و برد به شما رسید.</div>";
        }

        else if (data.type === "opponent_left") {
            if (countdownTimer) clearInterval(countdownTimer);
            statusEl.style.display = "block";
            statusEl.textContent = "❌ حریف بازی رو ترک کرد.";
        }
    }
    connectDrawing();
    </script>"""
    return page_shell("نقاشی حدسی", body, username)


BASE_CSS += """
.chat-screen{max-width:720px;margin:-8px auto 0;background:linear-gradient(180deg,#0c0e20,#080914);border:1px solid #25284a;border-radius:26px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.35)}
.chat-top{position:sticky;top:0;z-index:10;background:rgba(15,16,35,.96);backdrop-filter:blur(12px);border-bottom:1px solid #292c4c;padding:10px 12px}.chat-toolbar{display:flex;align-items:center;justify-content:space-between;gap:8px}.chat-title{font-weight:800;font-size:17px}.chat-top-actions{display:flex;gap:7px}.icon-btn{width:42px;height:42px;padding:0!important;border-radius:13px!important;background:#171a35!important;color:#ddd!important;border:1px solid #2a2e51!important;display:flex!important;align-items:center;justify-content:center}.icon-btn.active{box-shadow:0 0 0 2px rgba(123,92,255,.28) inset;color:#b7a8ff!important}
.music-bar{display:flex;align-items:center;gap:9px;margin-top:9px;padding:8px 10px;border:1px solid #292d52;border-radius:15px;background:#13152d}.music-meta{min-width:0;flex:1}.music-name{font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.music-sub{font-size:11px;color:#8388aa}.music-controls{display:flex;gap:6px}.music-controls button{padding:7px 10px;font-size:12px;background:#20244a;color:#d8d3ff;border:1px solid #363b6d}.chat-box{height:calc(100vh - 310px);min-height:430px;max-height:650px;overflow-y:auto;background:radial-gradient(circle at 50% 0,#151832 0,#090a15 65%);border:0;border-radius:0;padding:16px 13px 24px;display:flex;flex-direction:column;gap:9px;scroll-behavior:smooth}
.msg{position:relative;padding:10px 13px 8px;border-radius:18px 18px 4px 18px;background:#191b31;border:1px solid #292d4a;max-width:82%;align-self:flex-start;box-shadow:0 6px 18px rgba(0,0,0,.14);cursor:pointer;user-select:none;-webkit-user-select:none}.msg.me{align-self:flex-end;background:#171934;border-color:#393b72;border-radius:18px 18px 18px 4px}.msg .sender{display:block;color:#a996ff;font-weight:800;font-size:13px;margin-bottom:2px}.msg .content{display:block;white-space:pre-wrap;word-break:break-word;font-size:14px}.msg-time{display:block;text-align:left;color:#626681;font-size:10px;margin-top:3px}.msg-reply{border-right:3px solid #7965ff;background:#202341;color:#9da2c1;padding:4px 7px;border-radius:7px;margin-bottom:6px;font-size:11px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}.msg-hint{font-size:9px;color:#646985;text-align:center;margin-top:2px}.reply-bar{display:flex;gap:8px;align-items:center;background:#171a34;border-top:1px solid #2c3052;padding:9px 12px}.reply-preview{flex:1;color:#a7abca;font-size:12px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}.chat-input-wrap{padding:10px 12px 12px;background:#0d0f20;border-top:1px solid #242743}.chat-input-row{display:flex;gap:8px;align-items:center}.chat-input-row input{margin:0!important;border-radius:17px!important;background:#171a30!important;border-color:#2b2f50!important}.send-btn{min-width:54px;height:50px;padding:0!important;border-radius:16px!important;background:#7865f7!important;color:#fff!important;font-size:21px!important}.profile-link{color:inherit;text-decoration:none}.chat-empty{opacity:.55;text-align:center;padding:55px 20px;font-size:13px}.support-music-preview{padding:9px 11px;border:1px solid var(--border);border-radius:12px;margin-top:10px;color:var(--text-muted);font-size:12px}.profile-avatar-img{width:92px;height:92px;border-radius:50%;object-fit:cover;border:2px solid #7965ff;display:block}.avatar-picker{display:flex;flex-direction:column;align-items:center;gap:12px;padding:14px;border:1px dashed #3a3f68;border-radius:16px;background:#11142a}.avatar-crop-wrap{width:190px;height:190px;border-radius:50%;overflow:hidden;background:#0a0d1b;border:2px solid #7965ff;position:relative}.avatar-crop-wrap img{position:absolute;max-width:none;transform-origin:center center;user-select:none;-webkit-user-drag:none}.zoom-row{width:100%;display:flex;align-items:center;gap:10px}.zoom-row input{flex:1;margin:0!important}.avatar-preview-hint{font-size:11px;color:var(--text-muted);text-align:center}.chat-avatar{width:28px;height:28px;border-radius:50%;object-fit:cover;vertical-align:middle;margin-left:5px;border:1px solid #454b78}.chat-avatar-fallback{display:inline-flex;width:28px;height:28px;border-radius:50%;align-items:center;justify-content:center;background:#252a4a;margin-left:5px;vertical-align:middle;font-size:15px}
@media(max-width:600px){.container{padding:8px 5px 25px}.chat-screen{border-radius:22px 22px 0 0;margin:0 -5px}.chat-box{height:calc(100vh - 290px);min-height:430px;padding:12px 9px}.msg{max-width:86%}.chat-title{font-size:15px}.icon-btn{width:38px;height:38px}}
"""


BASE_CSS += """
html{background:#09051d}body{background:radial-gradient(circle at 50% -10%,rgba(150,50,255,.22),transparent 34%),linear-gradient(180deg,#0b0620,#09051b 55%,#070414);min-height:100vh}.container{max-width:920px;padding:22px 16px 80px}.nav{display:none}.neon-nav-wrap{padding:10px 0 22px;position:relative}.neon-nav{position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:5px;min-height:142px;padding:16px 10px 10px;border:2px solid #9c2cff;border-radius:32px;background:linear-gradient(180deg,#220c4b,#0c0725);box-shadow:0 0 0 1px rgba(255,91,246,.35) inset,0 0 18px rgba(153,39,255,.7),0 0 55px rgba(99,29,218,.25);overflow:visible}.neon-nav:before{content:"";position:absolute;left:3%;right:3%;top:-7px;height:12px;border-radius:50%;border-top:3px solid #ff4edb;box-shadow:0 -1px 12px #ff4edb,0 0 15px #762cff}.neon-nav:after{content:"◆";position:absolute;top:-30px;left:50%;transform:translateX(-50%);width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:23px;background:radial-gradient(circle,#ff55ea 0 24%,#7a2dff 25% 55%,#18063c 56%);border:2px solid #ff9aee;box-shadow:0 0 12px #ff4ddc,0 0 34px rgba(136,40,255,.8)}.neon-item{min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#fff;text-decoration:none;border-radius:22px;padding:9px 4px 4px;transition:.25s;position:relative}.neon-item .ni-icon{font-size:48px;line-height:1;filter:drop-shadow(0 0 8px rgba(255,78,221,.45));transition:.25s;animation:neonFloat 3s ease-in-out infinite}.neon-item .ni-title{font-size:19px;font-weight:950;text-shadow:0 0 9px rgba(255,255,255,.25)}.neon-item .ni-line{width:82px;max-width:80%;height:4px;border-radius:999px;background:linear-gradient(90deg,transparent,#ff5fe3,transparent);box-shadow:0 0 9px #ff5fe3}.neon-item:hover,.neon-item.active{background:radial-gradient(circle at 50% 70%,rgba(214,50,255,.2),transparent 62%);transform:translateY(-4px)}.neon-item:hover .ni-icon,.neon-item.active .ni-icon{transform:scale(1.08);filter:drop-shadow(0 0 12px #ff54dc)}.neon-item.active .ni-title{text-shadow:0 0 11px #ff5ce0}.neon-item.active .ni-line{box-shadow:0 0 14px #ff5ce0}.page-heading{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:4px 0 18px}.page-heading h1{margin:0;font-size:28px;color:#fff;text-shadow:0 0 14px rgba(238,88,226,.35)}.page-heading .sub{color:#9a91bd;font-size:12px}.card,.hero{background:linear-gradient(145deg,rgba(30,17,67,.97),rgba(13,10,36,.97));border-color:#3a2269;box-shadow:0 14px 45px rgba(0,0,0,.3),0 0 25px rgba(113,31,214,.08)}.card{border-radius:24px}.leader-row{border-color:#32205a;background:linear-gradient(90deg,rgba(65,29,112,.12),transparent);border-radius:16px;margin:6px 0}.leader-row.me{background:linear-gradient(90deg,rgba(212,48,228,.18),rgba(91,42,197,.12))}.friend-row{border-color:#382261;background:linear-gradient(145deg,#191032,#100b25);transition:.22s}.friend-row:hover{transform:translateY(-2px);border-color:#9143df;box-shadow:0 8px 24px rgba(126,35,224,.18)}.profile-card{background:linear-gradient(145deg,#21134d,#0f0a2a);border:2px solid #7626c8;box-shadow:0 0 30px rgba(154,45,255,.2)}.chat-screen{border-color:#5c2ca1;box-shadow:0 0 34px rgba(128,36,235,.2),0 20px 60px rgba(0,0,0,.45)}.music-bar{border-color:#4b267a;background:linear-gradient(90deg,#1b0d38,#100a26)}@keyframes neonFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}@media(max-width:650px){.container{padding:12px 8px 55px}.neon-nav{min-height:112px;border-radius:23px;padding:10px 4px 7px}.neon-nav:after{width:44px;height:44px;top:-24px;font-size:17px}.neon-item{border-radius:16px;padding:6px 2px 3px}.neon-item .ni-icon{font-size:34px}.neon-item .ni-title{font-size:14px}.neon-item .ni-line{width:54px;height:3px}.page-heading h1{font-size:23px}}@media(max-width:420px){.neon-item .ni-icon{font-size:29px}.neon-item .ni-title{font-size:12px}.neon-nav{gap:1px}}
"""

def _neon_nav(username, active="home"):
    if not username:return ""
    items=[("leaderboard","🏆","لیدر بورد","/leaderboard"),("messages","💬","گفتگوها","/messages"),("shop","🛍️","فروشگاه","/shop"),("settings","⚙️","تنظیمات","/settings")]
    cells=[]
    for key,icon,title,url in items:
        cls=" active" if active==key else ""
        cells.append(f'<a class="neon-item{cls}" href="{url}"><span class="ni-icon">{icon}</span><span class="ni-title">{title}</span><span class="ni-line"></span></a>')
    return '<div class="neon-nav-wrap"><div class="neon-nav">'+''.join(cells)+'</div></div>'

def _nav(username):
    if username:
        u=html.escape(username)
        return f'<div class="nav"><div class="nav-brand">🎲 بازی‌خونه — {u}</div></div>'
    return '<div class="nav"><div class="nav-brand">🎲 بازی‌خونه</div></div>'


def lobby_page(username):
    body=f"""<div class="lobby-shell page-enter"><div class="page-heading"><div><div class="sub">DRAW BATTLE • ARCADE</div><h1>خوش اومدی، {html.escape(username)} ✨</h1></div><a class="btn" href="/profile?u={quote(username,safe='')}">👤 پروفایل</a></div><div class="lobby-profile hero"><div class="lobby-profile-main"><a href="/profile?u={quote(username,safe='')}" class="lobby-avatar">🎮</a><div><div class="lobby-name">{html.escape(username)}</div><div class="lobby-sub">برای پروفایل کلیک کن 👆</div></div></div><div class="lobby-stats"><span>🏆 جدول امتیازات</span><span>💎 امتیاز و دستاوردها</span></div></div><div class="lobby-promo-grid"><a class="promo-card orange" href="/leaderboard"><span>🏆</span><b>لیدر بورد</b><small>برترین بازیکنان</small></a><a class="promo-card purple" href="/shop"><span>🛍️</span><b>فروشگاه</b><small>آیتم و سکه</small><em>🎁 ۲ روز</em></a></div><div class="lobby-sep">یا</div><div class="lobby-duo"><a href="/messages">💬<b>گفتگوها</b></a><a href="/chat/public">🌐<b>چت عمومی</b></a></div><div class="lobby-sep">یا</div><a class="lobby-play" href="/games">🎮 ورود به بازی</a><div class="lobby-mini-actions"><a href="/messages">💌 پیام‌ها</a><a href="/support/ticket">🛡️ تیکت پشتیبانی</a><a href="/settings">⚙️ تنظیمات</a></div></div>"""
    return page_shell('لابی',body,username)

def games_page(username):
    body=f'''<div class="card hero page-enter game-choice"><div class="game-choice-icon">🎮</div><h1>انتخاب حالت بازی</h1><p>یکی را انتخاب کن و وارد مسابقه زنده شو. اگر وسط بازی به لابی برگردی، محروم نمی‌شی؛ حریفت برنده اعلام می‌شه.</p><div class="game-choice-grid"><a class="game-choice-card" href="/game/tictactoe"><span>⭕</span><b>دوز</b><small>دو نفره، سریع و زنده</small></a><a class="game-choice-card" href="/game/drawing"><span>🎨</span><b>نقاشی</b><small>۴ دور نقاشی و حدس</small></a></div><a class="btn" href="/lobby">← بازگشت به لابی</a></div>'''
    return page_shell('انتخاب بازی',body,username)

def _avatar_html(avatar, cls="profile-avatar-img", alt="تصویر کاربر"):
    avatar = avatar or "🎮"
    if str(avatar).startswith("data:image/"):
        return f'<img class="{cls}" src="{html.escape(str(avatar), quote=True)}" alt="{html.escape(alt)}">'
    return f'<div class="avatar-big">{html.escape(str(avatar))}</div>' if cls == "profile-avatar-img" else f'<span class="chat-avatar-fallback">{html.escape(str(avatar)[:2])}</span>'

def profile_page(username, prof):
    prof = prof or {'username': username, 'display_name': username, 'bio': '', 'avatar': '🎮', 'wins':0, 'losses':0, 'draws':0, 'points':0, 'correct_guesses':0, 'wrong_guesses':0}
    total=prof.get('correct_guesses',0)+prof.get('wrong_guesses',0)
    correct=round(prof.get('correct_guesses',0)*100/total,1) if total else 0; wrong=round(prof.get('wrong_guesses',0)*100/total,1) if total else 0
    avatar_html=_avatar_html(prof.get('avatar') or '🎮'); is_support=prof['username']=='morad'
    badge='<div class="verified-support">✓ پشتیبانی رسمی</div>' if is_support else ''
    if prof['username']!=username:
        actions='<div class="profile-actions"><form method="post" action="/friends/request/form"><input type="hidden" name="target" value="'+html.escape(prof['username'],quote=True)+'"><button class="glow-btn" type="submit">🤝 افزودن به دوستان</button></form><a class="btn" href="/chat/private/'+quote(prof['username'],safe='')+'">💬 پیام خصوصی</a><button class="btn" onclick="inviteGame()">🎮 دعوت به بازی</button></div><script>async function inviteGame(){const choice=prompt("حالت بازی: 4 یا 6","4");const mode=choice==="6"?"drawing6":"drawing4";const r=await fetch("/game/invite",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({receiver:"'+html.escape(prof['username'],quote=True)+'",mode})});const d=await r.json();alert(d.ok?"🎮 دعوت ارسال شد!":"❌ ارسال دعوت ناموفق بود.")}</script>'
    else: actions='<div class="profile-actions"><a class="btn" href="/settings">⚙️ ویرایش پروفایل</a></div>'
    support_box='<a class="support-mini-card" href="/support/ticket">🛡️ <b>پشتیبانی رسمی</b><span>برای ارتباط مستقیم، تیکت ثبت کن</span></a>' if is_support else ''
    body=f'<div class="profile-card hero page-enter"><div class="profile-head"><div>{avatar_html}</div><div><h1>{html.escape(prof.get('display_name') or prof['username'])}</h1><p style="margin:0">@{html.escape(prof['username'])}</p>{badge}</div></div><p>{html.escape(prof.get('bio') or 'این کاربر هنوز بیوگرافی ننوشته.')}</p><div class="stat-grid"><div class="stat-box"><b>{correct}%</b><br>حدس درست</div><div class="stat-box"><b>{wrong}%</b><br>حدس غلط</div><div class="stat-box"><b>{prof.get('wins',0)}</b><br>برد</div><div class="stat-box"><b>{prof.get('points',0)}</b><br>امتیاز</div></div>{actions}</div>{support_box}<div style="text-align:center"><a class="btn" href="/lobby">🏠 لابی</a></div>'
    return page_shell('پروفایل',body,username)

def settings_page(username, prof):
    prof = prof or {"username": username, "display_name": username, "bio": "", "avatar": "🎮"}
    avatar=prof.get('avatar') or '🎮'
    if str(avatar).startswith('data:image/'):
        preview=f'<img id="avatarPreview" class="profile-avatar-img" src="{html.escape(str(avatar),quote=True)}" alt="پیش‌نمایش">'
    else:
        preview=f'<div id="avatarFallback" class="avatar-big">{html.escape(str(avatar))}</div>'
    body=f'''<div class="card hero page-enter"><h1>⚙️ تنظیمات پروفایل</h1><p>اطلاعاتت را ویرایش کن. عکس پروفایل روی خود دستگاه برش می‌خورد و با نوار زوم می‌توانی کادر را تنظیم کنی.</p><label>آیدی حساب</label><input type="text" value="{html.escape(username)}" disabled><label>نام نمایشی</label><input type="text" id="displayNameInput" value="{html.escape(prof.get('display_name') or username)}" maxlength="40"><label>عکس پروفایل</label><div class="avatar-picker"><div class="avatar-crop-wrap" id="cropWrap">{preview}</div><div class="zoom-row"><span>−</span><input type="range" id="zoom" min="1" max="3" step="0.01" value="1"><span>＋</span></div><input type="file" id="avatarFile" accept="image/*" style="width:100%;margin:0"><div class="avatar-preview-hint">عکس را انتخاب کن و با نوار زوم کادر را تنظیم کن؛ بعد ذخیره کن تا بقیه هم آن را ببینند.</div></div><label style="display:block;margin-top:14px">بیوگرافی</label><textarea id="bioInput" maxlength="300" style="width:100%;min-height:110px;padding:12px;border-radius:10px;background:var(--bg);color:var(--text);border:1px solid var(--border);font-family:inherit">{html.escape(prof.get('bio') or '')}</textarea><button class="glow-btn" style="margin-top:12px" onclick="saveProfile()">💾 ذخیره پروفایل</button><div id="saveStatus" class="status-line" style="display:none;margin-top:10px"></div></div><div class="card page-enter"><h2>🔐 تغییر رمز عبور</h2><input type="password" id="oldPasswordInput" placeholder="رمز فعلی"><input type="password" id="newPasswordInput" placeholder="رمز جدید"><button class="glow-btn" onclick="changePass()">تغییر رمز</button></div><div style="text-align:center"><a class="btn" href="/profile?u={quote(username,safe='')}">پروفایل</a> <a class="btn" href="/lobby">لابی</a></div><script>
let avatarData={str(avatar)!r};let img=null;let zoom=1;
const wrap=document.getElementById('cropWrap'), z=document.getElementById('zoom'), file=document.getElementById('avatarFile');
function applyCrop(){{if(!img)return;const sw=img.naturalWidth,sh=img.naturalHeight;const scale=Math.max(190/sw,190/sh)*zoom;img.style.width=(sw*scale)+'px';img.style.height=(sh*scale)+'px';img.style.left=((190-sw*scale)/2)+'px';img.style.top=((190-sh*scale)/2)+'px'}}
function makeCrop(){{if(!img)return;const c=document.createElement('canvas');c.width=512;c.height=512;const ctx=c.getContext('2d');const sw=img.naturalWidth,sh=img.naturalHeight;const scale=Math.max(512/sw,512/sh)*zoom;const dw=sw*scale,dh=sh*scale;ctx.drawImage(img,(512-dw)/2,(512-dh)/2,dw,dh);avatarData=c.toDataURL('image/jpeg',0.78)}}
z.oninput=()=>{{zoom=Number(z.value);applyCrop();makeCrop()}};
file.onchange=()=>{{const f=file.files&&file.files[0];if(!f)return;if(!f.type.startsWith('image/')){{alert('لطفاً یک عکس انتخاب کن.');file.value='';return}}if(f.size>8*1024*1024){{alert('حجم عکس باید کمتر از ۸ مگابایت باشد.');file.value='';return}}const u=URL.createObjectURL(f);const next=new Image();next.onload=()=>{{img=next;zoom=1;z.value='1';wrap.innerHTML='';wrap.appendChild(img);applyCrop();makeCrop();URL.revokeObjectURL(u)}};next.onerror=()=>{{URL.revokeObjectURL(u);alert('خواندن عکس ناموفق بود.')}};next.src=u}};
async function saveProfile(){{const status=document.getElementById('saveStatus');try{{if(img)makeCrop();const payload={{display_name:document.getElementById('displayNameInput').value.trim(),bio:document.getElementById('bioInput').value.trim(),avatar:avatarData}};const r=await fetch('/settings/profile',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});const d=await r.json();status.style.display='block';status.textContent=d.ok?'✅ پروفایل با موفقیت ذخیره شد.':(d.error==='image_too_large'?'❌ عکس خیلی بزرگ است.':'❌ ذخیره پروفایل ناموفق بود.');status.style.color=d.ok?'var(--turquoise)':'var(--danger)'}}catch(e){{status.style.display='block';status.textContent='❌ خطا در ارتباط با سرور.';status.style.color='var(--danger)'}}}}
async function changePass(){{try{{const r=await fetch('/settings/password',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{old_password:document.getElementById('oldPasswordInput').value,new_password:document.getElementById('newPasswordInput').value}})}});const d=await r.json();alert(d.ok?'رمز تغییر کرد.':d.error==='old_password'?'رمز فعلی اشتباه است.':'رمز جدید کوتاه است.')}}catch(e){{alert('خطا در ارتباط با سرور.')}}}}
</script>'''
    return page_shell('تنظیمات',body,username)

def _fmt_time(ts):
    try:return time.strftime('%H:%M', time.localtime(int(ts)))
    except Exception:return '--:--'

def _render_messages(messages, username):
    if not messages:return '<div class="chat-empty">✨ هنوز پیامی نیست... اولین پیام رو بفرست!</div>'
    by_id={int(m.get('id') or 0):m for m in messages}; out=[]
    for m in messages:
        mid=int(m.get('id') or 0); sender=m['sender']; content=m['content']; cls='msg me' if sender==username else 'msg'; ref=by_id.get(int(m.get('reply_to_id') or 0)); reply=f'<div class="msg-reply">↩️ {html.escape(ref["sender"])}: {html.escape(ref["content"])}</div>' if ref else ''
        safe_sender=quote(sender, safe='')
        av=m.get('avatar') or '🎮'
        if str(av).startswith('data:image/'):
            avatar_html=f'<img class="chat-avatar" src="{html.escape(str(av),quote=True)}" alt="">'
        else:
            avatar_html=f'<span class="chat-avatar-fallback">{html.escape(str(av)[:2])}</span>'
        sender_link=f'<a class="profile-link" href="/profile?u={safe_sender}">{avatar_html}{html.escape(sender)}</a>'
        out.append(f'<div class="{cls}" data-id="{mid}" data-sender="{html.escape(sender)}" data-content="{html.escape(content)}"><span class="sender">{sender_link}</span>{reply}<span class="content">{html.escape(content)}</span><span class="msg-time">{_fmt_time(m.get("created_at"))}</span></div>')
    return ''.join(out)

def chat_public_page(username,messages):
    body=f'''<div class="chat-screen"><div class="chat-top"><div class="chat-toolbar"><div class="chat-top-actions"><a class="icon-btn" href="/lobby">‹</a><button class="icon-btn active" id="soundBtn">🔊</button><button class="icon-btn" id="musicBtn">🎵</button></div><div class="chat-title">💬 چت عمومی</div><button class="icon-btn" id="shareBtn">↗</button></div><div class="music-bar" id="musicBar" style="display:none"><div style="font-size:22px">🎵</div><div class="music-meta"><div class="music-name" id="musicName">—</div><div class="music-sub" id="musicSub">آهنگ فعال چت روم</div></div><div class="music-controls"><button id="playMusic">▶ پخش</button><button id="stopMusic">⏹ قطع</button></div><audio id="roomAudio" preload="none"></audio></div></div><div class="chat-box" id="chatBox">{_render_messages(messages,username)}</div><div class="reply-bar" id="replyBar" style="display:none"><span class="reply-preview" id="replyPreview"></span><button class="icon-btn" id="cancelReply">✕</button></div><div class="chat-input-wrap"><div class="chat-input-row"><button class="send-btn" onclick="sendMsg()">➤</button><input type="text" id="msgInput" placeholder="پیامت رو بنویس..." autocomplete="off" maxlength="500"></div><div class="msg-hint">برای ریپلای، روی پیام موردنظر دوبار لمس/کلیک کن • برای پروفایل، روی نام کاربر بزن</div></div></div><script>
    const wsProto=location.protocol==='https:'?'wss:':'ws:';const me={username!r},box=document.getElementById('chatBox'),input=document.getElementById('msgInput'),replyBar=document.getElementById('replyBar'),replyPreview=document.getElementById('replyPreview');let replyId=null,lastId=0,ws=null,reconnect=null,soundOn=true;const audio=document.getElementById('roomAudio');document.querySelectorAll('.msg[data-id]').forEach(e=>lastId=Math.max(lastId,Number(e.dataset.id)||0));
    function esc(v){{const d=document.createElement('div');d.textContent=v;return d.innerHTML}}function fmt(ts){{const d=new Date(Number(ts)*1000);return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0')}}function replyTo(el){{replyId=Number(el.dataset.id);replyBar.style.display='flex';replyPreview.textContent='↩️ پاسخ به '+el.dataset.sender+': '+el.dataset.content;input.focus()}}function bindMsg(el){{let lastTap=0;el.addEventListener('dblclick',()=>replyTo(el));el.addEventListener('touchend',e=>{{const now=Date.now();if(now-lastTap<330){{e.preventDefault();replyTo(el)}}lastTap=now}})}}document.querySelectorAll('.msg[data-id]').forEach(bindMsg);document.getElementById('cancelReply').onclick=()=>{{replyId=null;replyBar.style.display='none'}};
    function addMsg(m){{if(!m||!m.id||Number(m.id)<=lastId)return;lastId=Number(m.id);const d=document.createElement('div');d.className=m.sender===me?'msg me':'msg';d.dataset.id=m.id;d.dataset.sender=m.sender;d.dataset.content=m.content;d.innerHTML='<span class="sender"><a class="profile-link" href="/profile?u='+encodeURIComponent(m.sender)+'">'+(m.avatar&&String(m.avatar).startsWith('data:image/')?'<img class="chat-avatar" src="'+esc(m.avatar)+'" alt="">':'<span class="chat-avatar-fallback">🎮</span>')+esc(m.sender)+'</a></span>'+(m.reply_to_id?'<div class="msg-reply">↩️ پاسخ به پیام قبلی</div>':'')+'<span class="content"></span><span class="msg-time">'+fmt(m.created_at)+'</span>';d.querySelector('.content').textContent=m.content;box.appendChild(d);bindMsg(d);box.scrollTop=box.scrollHeight}}
    function handleMusic(m){{if(!m)return;document.getElementById('musicBar').style.display='flex';document.getElementById('musicName').textContent=m.title||'آهنگ چت روم';document.getElementById('musicSub').textContent=m.target_user?'🎧 اختصاص داده‌شده برای '+m.target_user+' • قابل پخش برای همه':'🎧 آهنگ آمادهٔ پخش • با دکمه پخش شروع کن';audio.src=m.url}}
    async function loadMusic(){{try{{const r=await fetch('/chat/public/music',{{cache:'no-store'}});const d=await r.json();if(d.music)handleMusic(d.music)}}catch(e){{}}}}
    function connect(){{ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/public');ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.type==='music')handleMusic(d.music);else if(d.type==='music_clear'){{audio.pause();audio.removeAttribute('src');document.getElementById('musicBar').style.display='none'}}else if(d.sender)addMsg(d)}};ws.onclose=()=>{{if(!reconnect)reconnect=setTimeout(()=>{{reconnect=null;connect()}},1200)}}}}
    async function poll(){{try{{const r=await fetch('/chat/public/messages?after='+lastId,{{cache:'no-store'}});const d=await r.json();if(d.ok)d.messages.forEach(addMsg)}}catch(e){{}}}}
    function sendMsg(){{const t=input.value.trim();if(!t)return;const payload={{content:t,reply_to_id:replyId}};if(ws&&ws.readyState===1)ws.send(JSON.stringify(payload));else{{poll();return}}input.value='';replyId=null;replyBar.style.display='none'}}input.addEventListener('keydown',e=>{{if(e.key==='Enter'){{e.preventDefault();sendMsg()}}}});
    document.getElementById('playMusic').onclick=async()=>{{try{{audio.volume=soundOn?1:0;await audio.play()}}catch(e){{alert('برای پخش، یک بار روی دکمه پخش بزن')}}}};document.getElementById('stopMusic').onclick=()=>{{audio.pause();audio.currentTime=0}};document.getElementById('soundBtn').onclick=()=>{{soundOn=!soundOn;audio.muted=!soundOn;document.getElementById('soundBtn').textContent=soundOn?'🔊':'🔇'}};document.getElementById('musicBtn').onclick=()=>{{const b=document.getElementById('musicBar');b.style.display=b.style.display==='none'?'flex':'none'}};document.getElementById('shareBtn').onclick=async()=>{{try{{await navigator.share({{title:'چت عمومی',url:location.href}})}}catch(e){{try{{await navigator.clipboard.writeText(location.href);alert('لینک چت کپی شد')}}catch(_){{}}}}}};loadMusic();connect();setInterval(poll,1400);setInterval(loadMusic,3000);box.scrollTop=box.scrollHeight;
    </script>'''
    return page_shell('چت عمومی',body,username)

def chat_private_page(username,other,messages):
    body=f'''<div class="chat-screen"><div class="chat-top"><div class="chat-toolbar"><a class="icon-btn" href="/lobby">‹</a><div class="chat-title">💌 {html.escape(other)}</div><a class="icon-btn" href="/profile?u={quote(other,safe='')}">👤</a></div></div><div class="chat-box" id="chatBox">{_render_messages(messages,username)}</div><div class="reply-bar" id="replyBar" style="display:none"><span class="reply-preview" id="replyPreview"></span><button class="icon-btn" id="cancelReply">✕</button></div><div class="chat-input-wrap"><div class="chat-input-row"><button class="send-btn" onclick="sendMsg()">➤</button><input type="text" id="msgInput" placeholder="پیام خصوصی..." autocomplete="off" maxlength="500"></div><div class="msg-hint">برای ریپلای، روی پیام دوبار لمس/کلیک کن</div></div></div><script>const wsProto=location.protocol==='https:'?'wss:':'ws:',me={username!r},box=document.getElementById('chatBox'),input=document.getElementById('msgInput'),replyBar=document.getElementById('replyBar'),replyPreview=document.getElementById('replyPreview');let replyId=null,lastId=0,ws=null,reconnect=null;document.querySelectorAll('.msg[data-id]').forEach(e=>lastId=Math.max(lastId,Number(e.dataset.id)||0));function esc(v){{const d=document.createElement('div');d.textContent=v;return d.innerHTML}}function fmt(ts){{const d=new Date(Number(ts)*1000);return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0')}}function replyTo(el){{replyId=Number(el.dataset.id);replyBar.style.display='flex';replyPreview.textContent='↩️ پاسخ به '+el.dataset.sender+': '+el.dataset.content;input.focus()}}function bind(el){{let t=0;el.addEventListener('dblclick',()=>replyTo(el));el.addEventListener('touchend',e=>{{let n=Date.now();if(n-t<330){{e.preventDefault();replyTo(el)}}t=n}})}}document.querySelectorAll('.msg[data-id]').forEach(bind);document.getElementById('cancelReply').onclick=()=>{{replyId=null;replyBar.style.display='none'}};function addMsg(m){{if(!m.id||Number(m.id)<=lastId)return;lastId=Number(m.id);const d=document.createElement('div');d.className=m.sender===me?'msg me':'msg';d.dataset.id=m.id;d.dataset.sender=m.sender;d.dataset.content=m.content;d.innerHTML='<span class="sender">'+esc(m.sender)+'</span>'+(m.reply_to_id?'<div class="msg-reply">↩️ پاسخ به پیام قبلی</div>':'')+'<span class="content"></span><span class="msg-time">'+fmt(m.created_at)+'</span>';d.querySelector('.content').textContent=m.content;box.appendChild(d);bind(d);box.scrollTop=box.scrollHeight}}function connect(){{ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/private/{html.escape(other)}');ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.sender)addMsg(d)}};ws.onclose=()=>{{if(!reconnect)reconnect=setTimeout(()=>{{reconnect=null;connect()}},1200)}}}}function sendMsg(){{const t=input.value.trim();if(!t||!ws||ws.readyState!==1)return;ws.send(JSON.stringify({{content:t,reply_to_id:replyId}}));input.value='';replyId=null;replyBar.style.display='none'}}input.addEventListener('keydown',e=>{{if(e.key==='Enter'){{e.preventDefault();sendMsg()}}}});connect();box.scrollTop=box.scrollHeight;</script>'''
    return page_shell('چت خصوصی',body,username)


BASE_CSS += """
.game-choice{text-align:center;overflow:hidden}.game-choice-icon{font-size:58px;filter:drop-shadow(0 8px 18px rgba(47,169,160,.22));animation:floatGame 2.8s ease-in-out infinite}.game-choice-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:22px 0}.game-choice-card{display:flex;flex-direction:column;align-items:center;gap:4px;padding:24px 12px;border:1px solid var(--border);border-radius:20px;background:linear-gradient(145deg,var(--surface-raised),var(--surface));color:var(--text);text-decoration:none;transform:translateZ(0);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}.game-choice-card span{font-size:46px}.game-choice-card b{font-size:19px}.game-choice-card small{color:var(--text-muted)}.game-choice-card:hover{transform:translateY(-5px);border-color:var(--turquoise);box-shadow:0 12px 30px rgba(47,169,160,.16)}.ttt-cell{transform:translateZ(0);transition:transform .16s ease,background .16s ease,box-shadow .16s ease}.ttt-cell:hover{transform:translateY(-2px);box-shadow:0 8px 18px rgba(47,169,160,.12)}.draw-result{animation:pageIn .25s ease both}.card{transform:translateZ(0)}@keyframes floatGame{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}@media(max-width:520px){.game-choice-grid{grid-template-columns:1fr}.ttt-board{grid-template-columns:repeat(3,minmax(70px,88px));grid-template-rows:repeat(3,minmax(70px,88px))}}@media(prefers-reduced-motion:reduce){.game-choice-icon{animation:none}}
"""


BASE_CSS += """
.lobby-shell{max-width:560px;margin:0 auto;padding:10px 0 35px}.lobby-profile{border:2px solid #633f8f;border-radius:24px;padding:22px;box-shadow:0 0 35px rgba(123,71,202,.2);animation:cardPop .45s ease both}.lobby-profile-main{display:flex;align-items:center;gap:14px}.lobby-avatar{width:92px;height:92px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:44px;text-decoration:none;background:linear-gradient(145deg,#f25bbd,#8554f5);border:5px solid #e889df;box-shadow:0 0 28px rgba(230,85,215,.3)}.lobby-name{font-size:25px;font-weight:900;color:#ef70ca}.lobby-sub{color:#8886a7;font-size:13px}.lobby-stats{display:flex;flex-direction:column;gap:7px;margin-top:14px;color:#8f8aa9}.lobby-promo-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:28px}.promo-card{position:relative;min-height:170px;border-radius:22px;padding:20px 14px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none;color:#fff;box-shadow:0 12px 30px rgba(0,0,0,.22);transition:transform .25s,filter .25s}.promo-card:hover{transform:translateY(-6px) scale(1.02);filter:brightness(1.08)}.promo-card span{font-size:46px}.promo-card b{font-size:23px}.promo-card small{font-size:14px;opacity:.9}.promo-card.orange{background:linear-gradient(145deg,#ffad0a,#f24d40)}.promo-card.purple{background:linear-gradient(145deg,#9b5cff,#7353ee)}.promo-card em{position:absolute;right:-8px;top:70px;background:#ffb71b;border:3px solid #ffd65d;color:#402700;border-radius:18px;padding:7px 10px;font-style:normal;font-weight:900;box-shadow:0 0 18px rgba(255,183,27,.45);animation:giftFloat 2s ease-in-out infinite}.lobby-sep{text-align:center;color:#777696;font-size:16px;margin:18px 0}.lobby-duo{display:grid;grid-template-columns:1fr 1fr;background:linear-gradient(145deg,#ffc400,#ffab00);border-radius:22px;overflow:hidden;box-shadow:0 12px 30px rgba(255,177,0,.2)}.lobby-duo a{min-height:120px;display:flex;align-items:center;justify-content:center;gap:8px;flex-direction:column;color:#151515;text-decoration:none;font-size:22px;transition:transform .2s}.lobby-duo a:first-child{border-left:3px solid rgba(80,50,0,.25)}.lobby-duo a:hover{transform:scale(1.03)}.lobby-play{display:flex;align-items:center;justify-content:center;min-height:92px;border-radius:20px;background:linear-gradient(145deg,#39db7a,#16ad61);color:#fff;text-decoration:none;font-size:24px;font-weight:900;box-shadow:0 12px 30px rgba(35,203,112,.25);transition:transform .2s,filter .2s}.lobby-play:hover{transform:translateY(-4px);filter:brightness(1.08)}.lobby-mini-actions{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:18px}.lobby-mini-actions a{padding:8px 12px;border:1px solid #303257;border-radius:12px;color:#a9add0;text-decoration:none;background:#15182e}.profile-actions{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:18px}.verified-support{display:inline-block;margin-top:7px;padding:4px 10px;border-radius:999px;background:linear-gradient(90deg,#7a5cff,#d65ee5);color:white;font-size:11px;font-weight:900;box-shadow:0 0 18px rgba(128,92,255,.35)}.support-mini-card{display:flex;flex-direction:column;gap:2px;margin:14px 0;padding:15px 17px;border:1px solid #7d61ff;border-radius:18px;background:linear-gradient(145deg,#1e1b45,#17162e);color:#fff;text-decoration:none;box-shadow:0 8px 25px rgba(113,82,255,.16)}.support-mini-card span{font-size:11px;color:#9fa4c8}.friend-row{display:flex;align-items:center;gap:10px;padding:11px;border:1px solid #2b3054;border-radius:15px;background:#15182e;margin-bottom:8px}.friend-row .avatar{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#282d52}.friend-row .grow{flex:1}.request-actions{display:flex;gap:6px}.ticket-card textarea{width:100%;min-height:160px;padding:12px;border-radius:13px;background:var(--bg);color:var(--text);border:1px solid var(--border);font-family:inherit}.ticket-card input{margin-bottom:10px}@keyframes cardPop{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:none}}@keyframes giftFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}@media(max-width:520px){.lobby-promo-grid{gap:10px}.promo-card{min-height:150px}.lobby-duo a{min-height:105px;font-size:18px}}
"""

def messages_page(username, friends, requests):
    req_html=''.join(f"""<div class="friend-row page-enter"><div class="avatar">{html.escape(str(r.get('avatar') or '🎮')[:2])}</div><div class="grow"><a class="profile-link" href="/profile?u={quote(r['sender'],safe='')}"><b>{html.escape(r.get('display_name') or r['sender'])}</b></a><div class="report-meta">@{html.escape(r['sender'])} برای دوستی درخواست داده</div></div><div class="request-actions"><button onclick="respond({r['sender']!r},true)">✓</button><button class="btn" onclick="respond({r['sender']!r},false)">✕</button></div></div>""" for r in requests) or '<p style="opacity:.55;text-align:center;padding:25px">درخواست دوستی جدیدی نداری.</p>'
    fr_html=''.join(f"""<div class="friend-row"><div class="avatar">{html.escape(str(f.get('avatar') or '🎮')[:2])}</div><div class="grow"><a class="profile-link" href="/profile?u={quote(f['username'],safe='')}"><b>{html.escape(f.get('display_name') or f['username'])}</b></a><div class="report-meta">@{html.escape(f['username'])}</div></div><a class="btn" href="/chat/private/{quote(f['username'],safe='')}">💬</a></div>""" for f in friends) or '<p style="opacity:.55;text-align:center;padding:25px">هنوز دوستی نداری.</p>'
    body=f"""<div class="card hero page-enter"><div style="display:flex;justify-content:space-between;align-items:center"><h1>💬 پیام‌ها</h1><a class="btn" href="/lobby">خانه ←</a></div><div class="tabs"><a class="active" href="/messages">💬 مکالمات</a><span>👥 دوستان</span><span>📨 درخواست‌ها <b>{len(requests)}</b></span></div><input id="userSearch" type="text" placeholder="🔎 جستجوی کاربر..." oninput="searchUser()"><div id="searchResult"></div></div><div class="card"><h2>📨 درخواست‌های دوستی</h2>{req_html}</div><div class="card"><h2>👥 دوستان من</h2>{fr_html}</div><script>async function respond(sender,accept){{const r=await fetch('/friends/respond',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{sender,accept}})}});if((await r.json()).ok)location.reload()}}let timer;async function searchUser(){{clearTimeout(timer);const q=document.getElementById('userSearch').value.trim(),box=document.getElementById('searchResult');if(!q){{box.innerHTML='';return}};timer=setTimeout(async()=>{{const r=await fetch('/profile?u='+encodeURIComponent(q));box.innerHTML=r.ok?'<a class="friend-row" href="/profile?u='+encodeURIComponent(q)+'"><div class="grow">👤 باز کردن پروفایل <b>@'+q.replace(/[<>&]/g,'')+'</b></div><span>→</span></a>':'<p class="report-meta">کاربر پیدا نشد.</p>'}},250)}}</script>"""
    return page_shell('پیام‌ها',body,username)

def support_ticket_page(username):
    body=f"""<div class="card hero page-enter ticket-card"><h1>🛡️ تیکت پشتیبانی رسمی</h1><p>پیامت مستقیم در صف پشتیبانی ثبت می‌شود.</p><input id="subject" placeholder="موضوع تیکت" maxlength="120"><textarea id="content" maxlength="3000" placeholder="توضیحت را بنویس..."></textarea><button class="glow-btn" onclick="sendTicket()">🎫 ثبت تیکت</button><div id="status" class="status-line" style="display:none"></div></div><div style="text-align:center"><a class="btn" href="/lobby">بازگشت به منو</a></div><script>async function sendTicket(){{const subject=document.getElementById('subject').value.trim(),content=document.getElementById('content').value.trim(),s=document.getElementById('status');if(!subject||!content){{s.style.display='block';s.textContent='موضوع و توضیح را کامل کن.';return}}const r=await fetch('/support/ticket',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{subject,content}})}}),d=await r.json();s.style.display='block';s.textContent=d.ok?'✅ تیکت #'+d.ticket_id+' ثبت شد.':'❌ ثبت تیکت ناموفق بود.'}}</script>"""
    return page_shell('تیکت پشتیبانی',body,username)


def shop_page(username):
    body=f'''<div class="page-heading"><div><div class="sub">ARCADE STORE • ITEMS</div><h1>🛍️ فروشگاه</h1></div><a class="btn" href="/lobby">خانه</a></div><div class="card hero page-enter"><p>سکه‌ها و آیتم‌های تزئینی بازی را از اینجا مدیریت کن.</p><div class="lobby-promo-grid"><div class="promo-card purple"><span>💎</span><b>بسته سکه</b><small>به‌زودی</small></div><div class="promo-card orange"><span>🎁</span><b>آیتم ویژه</b><small>به‌زودی</small></div></div></div><div class="card page-enter"><h2>✨ ویترین ویژه</h2><p>آیتم‌های بعدی با همین استایل نئونی اضافه می‌شوند.</p></div>'''
    return page_shell("فروشگاه",body,username)

BASE_CSS += """
.lobby-bg{background:repeating-linear-gradient(45deg,rgba(255,255,255,.035) 0 5px,transparent 5px 14px),radial-gradient(circle at 20% 10%,rgba(255,160,0,.22),transparent 24%),radial-gradient(circle at 80% 5%,rgba(255,0,100,.2),transparent 26%),linear-gradient(135deg,#24100c,#641a18 30%,#4d0d38 52%,#152b58 76%,#1c611e);border-radius:28px;padding:14px 8px 110px;box-shadow:inset 0 0 80px rgba(0,0,0,.35)}
.lobby-top-title{text-align:center;color:#fff;font-size:30px;font-weight:1000;text-shadow:0 3px 0 rgba(0,0,0,.25),0 0 16px rgba(255,255,255,.2);margin:3px 0 14px}.lobby-user-card{background:linear-gradient(180deg,#fff,#f1f1f1);color:#2d3042;border:3px solid #ddd;border-radius:30px;padding:16px 13px 14px;box-shadow:0 12px 30px rgba(0,0,0,.35);position:relative;margin:48px 0 18px}.lobby-user-avatar{position:absolute;top:-76px;left:50%;transform:translateX(-50%);width:112px;height:112px;border-radius:50%;background:linear-gradient(145deg,#d4d4d4,#fff);border:4px solid #11c65b;box-shadow:0 0 0 4px rgba(255,255,255,.7),0 8px 25px rgba(0,0,0,.2);display:flex;align-items:center;justify-content:center;font-size:55px;text-decoration:none}.lobby-user-name{margin:70px auto 12px;max-width:340px;text-align:center;background:linear-gradient(180deg,#00d92f,#00a922);color:#fff;border-radius:999px;padding:5px 12px;font-size:23px;font-weight:1000;box-shadow:inset 0 2px 4px rgba(255,255,255,.4),0 4px 10px rgba(0,0,0,.2)}.lobby-stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.lobby-stat{background:#fff;border:3px solid #27c86a;border-radius:22px;padding:10px 4px;text-align:center;min-height:112px;display:flex;flex-direction:column;align-items:center;justify-content:center}.lobby-stat:nth-child(2){border-color:#b567ed}.lobby-stat:nth-child(3){border-color:#3d85e8}.lobby-stat .ico{font-size:38px;line-height:1}.lobby-stat b{font-size:26px;color:#303547}.lobby-stat span{color:#8b8e9b;font-size:13px}.lobby-bottom-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:12px}.lobby-bottom-actions a{border-radius:19px;padding:9px 5px;text-align:center;color:#fff;text-decoration:none;font-size:16px;font-weight:900;box-shadow:0 7px 0 rgba(0,0,0,.12),0 8px 18px rgba(0,0,0,.16);transition:.2s}.lobby-bottom-actions a:hover{transform:translateY(-3px)}.lobby-bottom-actions .green{background:linear-gradient(180deg,#77d52b,#43b91c)}.lobby-bottom-actions .purple{background:linear-gradient(180deg,#bd61ff,#9445df)}.lobby-bottom-actions .gold{background:linear-gradient(180deg,#ffd43b,#efaa00)}.mode-pill{display:block;width:max-content;max-width:90%;margin:18px auto -1px;padding:7px 22px;border-radius:999px;background:#16aee8;color:#fff;border:5px solid #fff;box-shadow:0 5px 18px rgba(0,0,0,.25);font-size:20px;font-weight:1000;position:relative;z-index:2}.mode-card{background:#fff;border:3px solid #ddd;border-radius:30px;padding:22px 15px 18px;color:#2d3042;box-shadow:0 12px 30px rgba(0,0,0,.3);margin-bottom:16px}.mode-card h2{color:#2e3142;font-size:25px;text-align:center;margin:0 0 8px}.mode-card p{color:#666b7b;text-align:center;margin:0 0 15px}.mode-actions{display:grid;grid-template-columns:1fr 1.7fr;gap:10px}.mode-actions a{display:flex;align-items:center;justify-content:center;border-radius:22px;padding:15px 8px;text-decoration:none;color:#fff;font-size:19px;font-weight:1000;box-shadow:0 6px 0 rgba(0,0,0,.12);transition:.2s}.mode-actions a:hover{transform:translateY(-3px)}.mode-actions .friends{background:linear-gradient(180deg,#88aef7,#5f8fe9)}.mode-actions .start4{background:linear-gradient(180deg,#8bd735,#4fbd1d)}.mode-actions .start6{background:linear-gradient(180deg,#ff75bf,#db3d8e)}.neon-bottom-nav{position:fixed;z-index:50;bottom:10px;left:50%;transform:translateX(-50%);width:min(94vw,760px);display:grid;grid-template-columns:repeat(4,1fr);gap:5px;background:rgba(18,10,43,.94);border:2px solid #a044ff;border-radius:24px;padding:7px;box-shadow:0 0 25px rgba(155,51,255,.55),0 12px 35px rgba(0,0,0,.45);backdrop-filter:blur(12px)}.neon-bottom-nav a{color:#fff;text-decoration:none;text-align:center;padding:6px 3px;border-radius:17px;font-size:12px;font-weight:900;transition:.2s}.neon-bottom-nav a span{display:block;font-size:25px;line-height:1.1}.neon-bottom-nav a:hover,.neon-bottom-nav a.active{background:linear-gradient(180deg,rgba(226,71,255,.28),rgba(103,54,255,.18));box-shadow:0 0 13px rgba(228,71,255,.25)}.mp-game{background:linear-gradient(145deg,#171033,#09071b);border:2px solid #7f35df;border-radius:28px;box-shadow:0 0 35px rgba(138,54,255,.18);overflow:hidden}.mp-head{padding:15px;text-align:center;background:linear-gradient(90deg,#38126e,#171039);border-bottom:1px solid #5d2aa1}.mp-head h1{margin:0;color:#fff}.mp-meta{display:flex;justify-content:space-between;gap:7px;flex-wrap:wrap;color:#b7afd2;font-size:12px}.mp-canvas{display:block;width:100%;height:auto;aspect-ratio:600/420;background:#fff;touch-action:none}.mp-options{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;padding:10px}.mp-options button{background:#27204a;color:#fff;border:1px solid #6045a1;border-radius:15px;padding:10px 14px;flex:0 1 auto}.mp-guess{display:flex;gap:8px;padding:10px}.mp-guess input{margin:0;flex:1}.mp-score{display:flex;gap:6px;overflow:auto;padding:8px}.mp-player{min-width:105px;background:#17132d;border:1px solid #3d3265;border-radius:13px;padding:6px;text-align:center;color:#d7d1ee}.mp-player.out{opacity:.35;text-decoration:line-through}.mp-result{padding:24px;text-align:center;animation:cardPop .3s ease}.coin-bar{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:10px 0}.coin-pill{padding:7px 12px;border-radius:999px;background:#18132f;border:1px solid #5733a2;color:#fff;font-weight:900}.store-item{padding:15px;border:1px solid #3e2a6f;border-radius:18px;background:linear-gradient(145deg,#211345,#100b27);margin-bottom:10px;display:flex;align-items:center;gap:10px}.store-item .grow{flex:1}.store-item .price{color:#ffd75b;font-weight:900}.invite-box{position:fixed;z-index:70;top:16px;right:16px;max-width:340px;background:#16102d;border:2px solid #d553ff;border-radius:20px;padding:14px;color:#fff;box-shadow:0 0 28px rgba(213,83,255,.45);display:none}
.mode-actions .start2{background:linear-gradient(180deg,#5ec8ff,#1f8fe0)}
.queue-widget{display:flex;flex-direction:column;align-items:center;gap:14px;padding:30px 16px 10px;text-align:center;animation:pageIn .3s ease both}
.queue-spinner{width:60px;height:60px;border-radius:50%;border:5px solid rgba(255,255,255,.12);border-top-color:#ff5ce0;border-right-color:#9c2cff;animation:queueSpin .9s linear infinite}
.queue-dots{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;max-width:320px}
.queue-dot{width:16px;height:16px;border-radius:50%;background:rgba(255,255,255,.12);border:2px solid rgba(255,255,255,.28);transition:.3s}
.queue-dot.filled{background:linear-gradient(145deg,#ff5ce0,#9c2cff);border-color:#ff9aee;box-shadow:0 0 12px rgba(255,92,224,.65);animation:queuePop .35s ease}
.queue-text{font-size:19px;font-weight:900;color:#fff;text-shadow:0 0 10px rgba(255,92,224,.35)}
.queue-sub{font-size:13px;color:#a79fc9}
@keyframes queueSpin{to{transform:rotate(360deg)}}
@keyframes queuePop{0%{transform:scale(.4)}70%{transform:scale(1.15)}100%{transform:scale(1)}}
@media(prefers-reduced-motion:reduce){.queue-spinner{animation:none}.queue-dot.filled{animation:none}}@media(max-width:600px){.lobby-top-title{font-size:26px}.lobby-stat{min-height:100px}.lobby-stat .ico{font-size:31px}.lobby-stat b{font-size:22px}.lobby-bottom-actions a{font-size:14px}.mode-actions{grid-template-columns:1fr 1.5fr}.mode-actions a{font-size:16px}.neon-bottom-nav{bottom:5px}}
"""

def _bottom_nav(active="home"):
    items=[("leaderboard","🏆","لیدر بورد"),("messages","💬","گفتگوها"),("shop","🛍️","فروشگاه"),("settings","⚙️","تنظیمات")]
    return '<div class="neon-bottom-nav">'+''.join(f'<a class="{("active" if active==k else "")}" href="/{k}"><span>{ic}</span>{title}</a>' for k,ic,title in items)+'</div>'

def lobby_page(username, prof=None, wallet=None):
    body=f"""<div class="lobby-bg page-enter"><div class="lobby-top-title">🎨 تخته گچی</div><div class="lobby-user-card"><a class="lobby-user-avatar" href="/profile?u={quote(username,safe='')}">🎮</a><div class="lobby-user-name">{html.escape(username)}</div><div class="lobby-stat-grid"><div class="lobby-stat"><div class="ico">🎮</div><b>{(prof or {}).get("wins",0)+(prof or {}).get("losses",0)+(prof or {}).get("draws",0)}</b><span>بازی ها</span></div><div class="lobby-stat"><div class="ico">🏆</div><b>{(prof or {}).get("wins",0)}</b><span>جام ها</span></div><div class="lobby-stat"><div class="ico">💎</div><b>{(wallet or {}).get("diamonds",5)}</b><span>الماس</span></div></div></div><span class="mode-pill" style="background:#1f8fe0">⚡ دو نفره سریع</span><div class="mode-card"><h2>🎨 حدس نقاشی دو نفره</h2><p>۲ بازیکن • ۶ دور • به نوبت یک نفر نقاشی می‌کشد و دیگری حدس می‌زند.</p><div class="mode-actions"><a class="friends" href="/messages">👥 دوستان</a><a class="start2" href="/game/drawing">▶ شروع بازی</a></div></div><span class="mode-pill">🎨 بازی حدس نقاشی</span><div class="mode-card"><h2>🎨 حدس نقاشی ۴ نفره</h2><p>۴ بازیکن • ۴ دور • هر دور یک نفر نقاش است و بقیه حدس می‌زنند.</p><div class="mode-actions"><a class="friends" href="/messages">👥 دوستان</a><a class="start4" href="/game/drawing4">▶ شروع بازی</a></div></div><span class="mode-pill" style="background:#d83f96">🔥 حالت حذفی ۶ نفره</span><div class="mode-card"><h2>🎯 حدس نقاشی ۶ نفره</h2><p>۶ بازیکن • ۶ دور • در هر دور کندترین بازیکنِ درست‌حدس‌زن حذف می‌شود.</p><div class="mode-actions"><a class="friends" href="/messages">👥 دوستان</a><a class="start6" href="/game/drawing6">▶ شروع بازی</a></div></div><div class="card" style="margin-top:12px;text-align:center;background:rgba(12,8,29,.75)"><a class="btn" href="/chat/public">🌐 چت عمومی</a> <a class="btn" href="/support/ticket">🛡️ پشتیبانی</a></div></div>{_bottom_nav("home")}<div id="inviteBox" class="invite-box"></div><script>async function pollNotify(){{try{{const d=await (await fetch('/notifications')).json();const inv=d.invites?.[0];if(inv){{const box=document.getElementById('inviteBox');box.innerHTML='🎮 <b>'+inv.sender+'</b> تو را به بازی '+(inv.mode==='drawing6'?'۶ نفره':'۴ نفره')+' دعوت کرده!<div style="display:flex;gap:6px;margin-top:9px"><button onclick="answerInvite('+inv.id+',true)">قبول</button><button onclick="answerInvite('+inv.id+',false)">رد</button></div>';box.style.display='block';}}}}catch(e){{}}}}async function answerInvite(id,accept){{const d=await (await fetch('/game/invite/respond',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{id,accept}})}})).json();if(d.ok&&accept)location.href='/game/'+d.mode;else document.getElementById('inviteBox').style.display='none'}}pollNotify();setInterval(pollNotify,5000);</script>"""
    return page_shell('منوی اصلی',body,username)

def games_page(username):
    body=f"""<div class="card hero page-enter"><h1>🎨 انتخاب حالت بازی</h1><div class="game-choice-grid"><a class="game-choice-card" href="/game/tictactoe"><span>⭕</span><b>دوز</b><small>دو نفره، سریع و زنده</small></a><a class="game-choice-card" href="/game/drawing"><span>🎨</span><b>حدس نقاشی دو نفره</b><small>۶ دور، به نوبت</small></a><a class="game-choice-card" href="/game/drawing4"><span>👥</span><b>حدس نقاشی ۴ نفره</b><small>۴ دور، بدون حذف</small></a><a class="game-choice-card" href="/game/drawing6"><span>🔥</span><b>حدس نقاشی ۶ نفره</b><small>۶ دور، حذف کندترین حدس‌زن</small></a></div><a class="btn" href="/lobby">← بازگشت</a></div>"""
    return page_shell('انتخاب بازی',body,username)

def multiplayer_drawing_page(username, mode):
    title='حدس نقاشی ۴ نفره' if mode==4 else 'حدس نقاشی ۶ نفره حذفی'
    body=f"""<div class="mp-game page-enter"><div class="mp-head"><h1>🎨 {title}</h1><div class="mp-meta"><span id="round">در انتظار بازیکن‌ها...</span><span id="timer">⏱️ --</span></div></div><div id="queueBox" class="queue-widget"><div class="queue-spinner"></div><div class="queue-text">🔌 در حال اتصال...</div></div><div id="gameArea" style="display:none"><div id="score" class="mp-score"></div><canvas id="canvas" class="mp-canvas" width="600" height="420"></canvas><div id="options" class="mp-options"></div><div class="mp-guess"><input id="guess" placeholder="حدست رو بنویس..." autocomplete="off"><button onclick="sendGuess()">حدس</button></div></div><div id="status" class="status-line" style="display:none"></div><div id="result" class="mp-result"></div></div><div style="text-align:center;margin-top:12px"><a class="btn" href="/lobby" onclick="event.preventDefault();fetch('/game/leave',{{method:'POST'}}).finally(()=>location.href='/lobby')">🏠 خروج</a></div><script>
const mode={mode}, me={username!r}, wsProto=location.protocol==='https:'?'wss:':'ws:';let ws,recon,timerInt;const c=document.getElementById('canvas'),ctx=c.getContext('2d'),status=document.getElementById('status'),round=document.getElementById('round'),timer=document.getElementById('timer'),opts=document.getElementById('options'),score=document.getElementById('score'),result=document.getElementById('result'),queueBox=document.getElementById('queueBox'),gameArea=document.getElementById('gameArea');let drawer=false,drawing=false,last=null;
function renderQueue(n,needed){{queueBox.style.display='flex';gameArea.style.display='none';status.style.display='none';let dots='';for(let i=0;i<needed;i++)dots+='<div class="queue-dot'+(i<n?' filled':'')+'"></div>';queueBox.innerHTML='<div class="queue-spinner"></div><div class="queue-dots">'+dots+'</div><div class="queue-text">'+n+' از '+needed+' نفر در صف هستند</div><div class="queue-sub">صبور باش؛ به‌محض تکمیل ظرفیت، بازی شروع می‌شود ✨</div>'}}
function enterGame(){{queueBox.style.display='none';gameArea.style.display='block';status.style.display='block'}}
function paint(x0,y0,x1,y1,color,size){{ctx.strokeStyle=color;ctx.lineWidth=size;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(x0,y0);ctx.lineTo(x1,y1);ctx.stroke()}}function clearBoard(){{ctx.clearRect(0,0,c.width,c.height);ctx.fillStyle='#fff';ctx.fillRect(0,0,c.width,c.height)}}clearBoard();function pos(e){{const r=c.getBoundingClientRect();return {{x:(e.clientX-r.left)*c.width/r.width,y:(e.clientY-r.top)*c.height/r.height}}}}c.addEventListener('pointerdown',e=>{{if(!drawer)return;drawing=true;last=pos(e)}});c.addEventListener('pointermove',e=>{{if(!drawer||!drawing)return;const p=pos(e),st={{type:'draw',x0:last.x,y0:last.y,x1:p.x,y1:p.y,color:'#20163a',size:5}};paint(st.x0,st.y0,st.x1,st.y1,st.color,st.size);ws?.send(JSON.stringify(st));last=p}});window.addEventListener('pointerup',()=>drawing=false);
function renderScores(scores,active){{score.innerHTML='';Object.entries(scores||{{}}).sort((a,b)=>b[1]-a[1]).forEach(([u,s])=>{{const d=document.createElement('div');d.className='mp-player'+((active||[]).includes(u)?'':' out');const a2=document.createElement('a');a2.className='profile-link';a2.target='_blank';a2.rel='noopener';a2.href='/profile?u='+encodeURIComponent(u);a2.textContent=u+' • '+s+' ⭐';d.appendChild(a2);score.appendChild(d)}})}}function connect(){{ws=new WebSocket(wsProto+'//'+location.host+'/ws/drawing-multi/'+mode);ws.onopen=()=>status.textContent='🟢 وصل شد؛ در حال پیدا کردن بازیکن‌ها...';ws.onclose=()=>{{if(!recon)recon=setTimeout(()=>{{recon=null;connect()}},1200)}};ws.onmessage=e=>onMsg(JSON.parse(e.data))}}function onMsg(d){{if(d.type==='rejoin'){{enterGame();drawer=d.role==='drawer';round.textContent='دور '+d.round+' / '+d.total_rounds+(drawer?' • تو نقاشی 🎨':' • حدس بزن 🔎');opts.innerHTML='';clearBoard();renderScores(d.scores,d.active);(d.strokes||[]).forEach(st=>paint(st.x0,st.y0,st.x1,st.y1,st.color,st.size));status.textContent=drawer?'کلمه: '+d.word:'نقاش: '+d.drawer;return}}if(d.type==='waiting'){{renderQueue(d.count,d.needed);return}}if(d.type==='round_start'){{enterGame();drawer=d.role==='drawer';round.textContent='دور '+d.round+' / '+d.total_rounds+(drawer?' • تو نقاشی 🎨':' • حدس بزن 🔎');result.textContent='';opts.innerHTML='';clearBoard();renderScores(d.scores,d.active);status.textContent=drawer?'کلمه: '+d.word:'نقاش: '+d.drawer;(d.options||[]).forEach(w=>{{const b=document.createElement('button');b.textContent=w;b.onclick=()=>{{document.getElementById('guess').value=w;sendGuess()}};opts.appendChild(b)}});let left=d.duration;clearInterval(timerInt);timer.textContent='⏱️ '+left;timerInt=setInterval(()=>{{left--;timer.textContent='⏱️ '+Math.max(0,left);if(left<=0)clearInterval(timerInt)}},1000);return}}if(d.type==='draw'){{paint(d.x0,d.y0,d.x1,d.y1,d.color,d.size);return}}if(d.type==='clear'){{clearBoard();return}}if(d.type==='guess_wrong'){{status.textContent='❌ '+d.word+' درست نبود';return}}if(d.type==='correct'){{status.textContent='✅ درست! +'+d.points+' امتیاز';return}}if(d.type==='round_result'){{result.innerHTML='🎯 <b>کلمه: '+d.word+'</b>'+(d.eliminated?' <br>💥 حذف شد: <b>'+d.eliminated+'</b>':'')+'<br>دور بعدی تا ۵ ثانیه دیگر...';renderScores(d.scores,d.active);return}}if(d.type==='game_over'){{round.textContent='🏆 بازی تمام شد';result.innerHTML='🏆 برنده: <b>'+((d.winner)||'مساوی')+'</b>';renderScores(d.scores,d.active);clearInterval(timerInt)}}if(d.type==='player_left')status.textContent='⚠️ '+d.username+' خارج شد'}}connect();</script>"""
    return page_shell(title,body,username)

def shop_page(username, wallet=None):
    w=wallet or {'coins':500,'diamonds':5,'streak':0}
    items=[('neon_pen','✏️','قلم نئونی','رنگ و افکت ویژه قلم',250),('profile_frame','🖼️','قاب پروفایل','قاب درخشان برای پروفایل',400),('victory_fx','✨','افکت پیروزی','انیمیشن ویژه پایان بازی',650),('crown_badge','👑','نشان تاج','نشان ویژه کنار نام',900)]
    cards=''.join(f'''<div class="store-item"><div style="font-size:38px">{ic}</div><div class="grow"><b>{name}</b><div style="color:#9b96b8;font-size:12px">{desc}</div></div><span class="price">{cost} 🪙</span><button onclick="buy('{key}',{cost})">خرید</button></div>''' for key,ic,name,desc,cost in items)
    body=f'''<div class="page-heading"><div><div class="sub">ARCADE STORE • ITEMS</div><h1>🛍️ فروشگاه</h1></div><a class="btn" href="/lobby">خانه</a></div><div class="card hero page-enter"><div class="coin-bar"><span class="coin-pill">🪙 {w.get('coins',500)} سکه</span><span class="coin-pill">💎 {w.get('diamonds',5)} الماس</span><span class="coin-pill">🔥 روزهای متوالی {w.get('streak',0)}</span></div><button class="glow-btn" onclick="claimDaily()">🎁 جایزه روزانه</button><div id="dailyStatus" class="status-line"></div></div><div class="card">{cards}</div><div style="text-align:center"><a class="btn" href="/lobby">← بازگشت</a></div><script>async function claimDaily(){{const d=await(await fetch('/daily/claim',{{method:'POST'}})).json();document.getElementById('dailyStatus').textContent=d.message; if(d.ok)setTimeout(()=>location.reload(),700)}}async function buy(key,cost){{const d=await(await fetch('/shop/buy',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{item_key:key,cost}})}})).json();alert(d.ok?'✨ خرید موفق بود!':d.status==='owned'?'این آیتم را داری.': 'سکه کافی نیست.');if(d.ok)location.reload()}}</script>'''
    return page_shell('فروشگاه',body,username)

def chat_private_page(username, other, messages):
    body=f'''<div class="chat-screen page-enter"><div class="chat-top"><div class="chat-toolbar"><a class="icon-btn" href="/messages">←</a><div class="chat-title">💬 {html.escape(other)} <span id="online" style="color:#35df7a;font-size:10px">● آنلاین</span></div><a class="icon-btn" href="/profile?u={quote(other,safe='')}">👤</a></div></div><div class="chat-box" id="chatBox">{_render_messages(messages, username)}</div><div id="typing" style="padding:5px 12px;color:#9a8ed1;font-size:11px;height:25px"></div><div class="chat-input-wrap"><div class="chat-input-row"><input type="text" id="msgInput" placeholder="پیامت رو بنویس..." autocomplete="off"><button class="send-btn" onclick="sendMsg()">➤</button></div></div></div><script>const wsProto=location.protocol==='https:'?'wss:':'ws:',me={username!r},other={other!r},box=document.getElementById('chatBox'),inp=document.getElementById('msgInput'),typing=document.getElementById('typing');let ws,recon,typingTimer;function addMsg(d){{if(d.sender===me&&[...box.querySelectorAll('.msg')].some(x=>x.dataset.id==d.id))return;const el=document.createElement('div');el.className='msg '+(d.sender===me?'me':'');el.dataset.id=d.id;const s=document.createElement('span');s.className='sender';s.textContent=d.display_name||d.sender;const c=document.createElement('span');c.className='content';c.textContent=d.content;el.append(s,c);box.appendChild(el);box.scrollTop=box.scrollHeight}}function connect(){{ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/private/'+encodeURIComponent(other));ws.onopen=()=>document.getElementById('online').textContent='● آنلاین';ws.onclose=()=>{{document.getElementById('online').textContent='● تلاش برای اتصال...';if(!recon)recon=setTimeout(()=>{{recon=null;connect()}},1200)}};ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.type==='typing'&&d.sender!==me){{typing.textContent=d.typing?'در حال نوشتن...':'';return}}if(d.content!==undefined)addMsg(d)}}}}function sendMsg(){{const v=inp.value.trim();if(!v||!ws||ws.readyState!==1)return;ws.send(JSON.stringify({{content:v}}));inp.value='';ws.send(JSON.stringify({{type:'typing',typing:false}}))}}inp.addEventListener('input',()=>{{if(ws?.readyState===1)ws.send(JSON.stringify({{type:'typing',typing:true}}));clearTimeout(typingTimer);typingTimer=setTimeout(()=>ws?.send(JSON.stringify({{type:'typing',typing:false}})),900)}});inp.addEventListener('keydown',e=>{{if(e.key==='Enter')sendMsg()}});box.scrollTop=box.scrollHeight;connect();</script>'''
    return page_shell(f'چت با {other}',body,username)

"""صفحات HTML به‌صورت رشته‌های پایتون؛ برای ساده نگه‌داشتن دیپلوی، بدون پوشه‌های جدا."""

import html
import time
from urllib.parse import quote
from frame_assets import GOLD_FRAME_OVERLAY_B64, ICE_FRAME_OVERLAY_B64, GOLD_FRAME_ICON_B64, ICE_FRAME_ICON_B64

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
    report_modal = """<div id="reportModal" class="report-modal" aria-hidden="true"><div class="report-modal-card"><button class="report-modal-close" onclick="closeReportModal()">×</button><div class="report-modal-title">🚩 گزارش کاربر</div><div class="report-modal-sub">دلیل گزارش را انتخاب کن:</div><div id="reportReasons" class="report-reasons"><button data-cat="collusion">🤝 تبانی/تقلب</button><button data-cat="profile">🖼️ پروفایل نامناسب</button><button data-cat="username">🆔 آیدی نامناسب</button><button data-cat="spam">📢 اسپم</button><button data-cat="chat">💬 پیام چت نامناسب</button><button data-cat="bio">📝 بیوگرافی نامناسب</button></div><textarea id="reportExtra" maxlength="300" placeholder="توضیح کوتاه (اختیاری)"></textarea><div class="report-modal-hint">با انتخاب یکی از گزینه‌ها گزارش ارسال می‌شود.</div></div></div>
<script>
let __reportPayload=null;
function openReportModal(target,content,context,attachment){__reportPayload={target,content,context,attachment:attachment||""};const m=document.getElementById("reportModal");if(m){m.classList.add("show");m.setAttribute("aria-hidden","false");}}
function closeReportModal(){const m=document.getElementById("reportModal");if(m){m.classList.remove("show");m.setAttribute("aria-hidden","true");}}
document.querySelectorAll("#reportReasons button").forEach(b=>b.addEventListener("click",async()=>{if(!__reportPayload)return;const category=b.dataset.cat,extra=document.getElementById("reportExtra").value.trim();b.disabled=true;try{const payload={...__reportPayload,category,content:(__reportPayload.content||"")+(extra?"\\nتوضیح: "+extra:"")};const r=await fetch("/report",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});const d=await r.json();if(d.ok){closeReportModal();alert("✅ گزارش ثبت شد.");}else alert("❌ ثبت گزارش ناموفق بود.");}finally{b.disabled=false;}}));
</script>"""
    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><style>{BASE_CSS}</style></head><body><div class="container">{body}</div>{report_modal}</body></html>"""


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
    <div class="auth-screen page-enter">
      <div class="auth-orb">🎨</div>
      <div class="auth-card">
        <div class="auth-kicker">DRAW BATTLE • NEW PLAYER</div>
        <h1>حساب جدید بساز 🚀</h1>
        <p>اول یک آیدی مخصوص خودت انتخاب کن.</p>
        {err_html}
        <form method="post" action="/signup" autocomplete="off">
          <label for="signupUsername">آیدی بازی</label>
          <input id="signupUsername" class="auth-input" type="text" name="username" placeholder="مثلاً gamer123"
                 minlength="3" maxlength="32" pattern="[a-z0-9]+" inputmode="latin" autocomplete="username"
                 autocapitalize="none" spellcheck="false" required>
          <div class="field-hint">فقط حروف کوچک انگلیسی <b>a-z</b> و عدد <b>0-9</b>؛ بدون فاصله و علامت.</div>
          <label for="signupPassword">رمز عبور</label>
          <input id="signupPassword" class="auth-input" type="password" name="password"
                 placeholder="حداقل ۴ کاراکتر" minlength="4" maxlength="128" autocomplete="new-password" required>
          <button class="auth-submit" type="submit">ساخت حساب ✨</button>
        </form>
        <p class="auth-bottom">حساب داری؟ <a href="/login">وارد شو</a></p>
      </div>
    </div>"""
    return page_shell("ثبت‌نام", body)

def lobby_page(username: str, prof=None, wallet=None) -> str:
    prof = prof or {"username": username, "bio": "", "avatar": "", "age": 18, "wins": 0, "points": 0}
    avatar_html = _avatar_html(prof.get("avatar") or "")
    age = int(prof.get("age") or 18)
    wins = int(prof.get("wins") or 0)
    points = int(prof.get("points") or 0)
    coins = int((wallet or {}).get("coins", 0) or 0)
    owned=set(prof.get("owned_items") or [])
    frame_class = 'frame-davinci' if 'davinci_frame' in owned else ('frame-picasso' if 'picasso_frame' in owned else ('frame-bronze' if 'bronze_frame' in owned else ('frame-premium' if 'profile_frame' in owned else '')))
    effect_class = 'effect-davinci' if 'davinci_effect' in owned else ('effect-picasso' if 'picasso_effect' in owned else '')
    name_class = 'name-glow' if 'name_effect' in owned else ''
    crown = '👑 ' if 'crown_badge' in owned else ''
    body=f"""<div class="lobby-bg page-enter">
      <div class="lobby-topbar">
        <div><div class="lobby-kicker">DRAW BATTLE</div><div class="lobby-title">تخته گچی ⚡</div></div>
        <div style="display:flex;gap:7px;align-items:center"><a class="lobby-settings" href="/settings" aria-label="تنظیمات">⚙️</a>{("<a class=\"lobby-settings\" href=\"/support\" aria-label=\"پنل پشتیبانی\">🛡️</a>" if username == "morad" else "")}</div>
      </div>
      <a class="lobby-profile hero {frame_class} {effect_class}" href="/profile?u={quote(username,safe='')}">
        <div class="lobby-profile-avatar">{avatar_html}</div>
        <div class="lobby-profile-info">
          <div class="lobby-profile-name {name_class}">{crown}@{html.escape(username)}</div>
          <div class="lobby-profile-meta">🎂 {age} سال <span>•</span> 🏆 {wins} جام <span>•</span> 💎 {points} امتیاز</div>
        </div>
        <div class="lobby-profile-arrow">‹</div>
      </a>
      <div class="lobby-wallet">💰 <b>{coins:,}</b> سکه <span>•</span> آماده‌ای؟</div>
      <div class="section-heading"><span>حالت‌های بازی</span><small>یکی رو انتخاب کن و شروع کن</small></div>
      <div class="game-mode-card mode-speed">
        <div class="mode-badge">⚡ دو نفره سرعتی</div>
        <div class="mode-icon">🎨</div>
        <div class="mode-copy"><h2>حدس نقاشی</h2><p>۲ بازیکن • نقاشی و حدس سریع</p></div>
        <a class="mode-start" href="/game/drawing">شروع <span>←</span></a>
      </div>
      <div class="game-mode-card mode-draw">
        <div class="mode-badge">🎨 رقابت نقاشان</div>
        <div class="mode-icon">🖌️</div>
        <div class="mode-copy"><h2>نقاشی ۴ نفره</h2><p>۴ بازیکن • نقاشی و حدس</p></div>
        <a class="mode-start" href="/game/drawing4">شروع <span>←</span></a>
      </div>
      <div class="lobby-quick-grid">
        <a href="/chat/public">💬 <b>چت عمومی</b><small>گپ با همه</small></a>
        <a href="/leaderboard">🏆 <b>رتبه‌بندی</b><small>بهترین‌ها</small></a>
        <a href="/shop">🛍️ <b>فروشگاه</b><small>آیتم‌ها</small></a>
        <a href="/profile?u={quote(username,safe='')}">👤 <b>پروفایل من</b><small>مشاهده پروفایل</small></a>
        {('<a href="/support">🛡️ <b>پنل پشتیبانی</b><small>مدیریت گزارش‌ها</small></a>' if username == 'morad' else '')}
      </div>
    </div>{_bottom_nav("home")}"""
    return page_shell("لابی", body, username)

def banned_page(username: str, scope: str, remaining: int, reason: str) -> str:
    mins = max(1, (remaining + 59) // 60)
    scope_text = {"games":"بازی‌ها", "chat":"چت‌ها", "drawing":"نقاشی", "profile":"پروفایل", "bio":"بیوگرافی", "username":"آیدی", "all":"همه بخش‌ها"}.get(scope, scope)
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

def support_page(username: str, reports: list[dict], active_bans: list[dict] | None = None, tickets: list[dict] | None = None, receipts: list[dict] | None = None) -> str:
    active_bans=active_bans or []; tickets=tickets or []; receipts=receipts or []
    labels={'all':'همه امکانات','games':'بازی‌ها','chat':'چت','drawing':'نقاشی','profile':'پروفایل','bio':'بیوگرافی','username':'آیدی'}
    cat_labels={'collusion':'تبانی/تقلب','profile':'پروفایل نامناسب','username':'آیدی نامناسب','spam':'اسپم','chat':'پیام چت نامناسب','drawing':'نقاشی نامناسب','bio':'بیوگرافی نامناسب','other':'سایر'}
    items=[]
    for r in reports:
        cat=r.get('category') or 'other'; status='حل‌شده' if r['status']!='open' else 'باز'; attachment=(' <img src="'+html.escape(r.get('attachment') or '')+'" class="report-image">') if r.get('attachment') else ''
        items.append(f'''<div class="report-item"><div><b>گزارش #{r['id']}</b> <span class="report-category">{cat_labels.get(cat,cat)}</span> — {status}</div><div class="report-meta">گزارش‌دهنده: {html.escape(r['reporter'])} | کاربر: <b>{html.escape(r['target'])}</b></div><p>{html.escape(r['content'])}</p>{attachment}<div class="support-action-grid"><select class="ban-scope"><option value="all">همه امکانات</option><option value="chat">چت</option><option value="games">بازی‌ها</option><option value="drawing">نقاشی</option><option value="profile">پروفایل</option><option value="bio">بیوگرافی</option><option value="username">آیدی</option></select><input class="ban-hours" type="number" min="0" max="168" value="0"><input class="ban-minutes" type="number" min="1" max="59" value="10"><button class="glow-btn" onclick="banUser({r['id']},this)">🚫 محروم کن</button></div></div>''')
    bans=[]
    for b in active_bans:
        remaining=max(0,b['until_ts']-int(time.time())); h,rem=divmod(remaining,3600); m=rem//60; left=(f'{h} ساعت و ' if h else '')+f'{m} دقیقه'
        bans.append(f'''<div class="ban-row" data-target="{html.escape(b['username'])}" data-scope="{html.escape(b['scope'])}"><b>@{html.escape(b['username'])}</b> <span class="ban-scope-tag">{labels.get(b['scope'],b['scope'])}</span><div class="report-meta">{html.escape(b.get('reason') or '—')} • {left}</div><button class="btn" onclick="unbanUser(this)">رفع محرومیت</button></div>''')
    ticket_items=''.join(f'<div class="report-item"><b>#{t["id"]} — {html.escape(t["subject"])}</b><div class="report-meta">از {html.escape(t["user"])}</div><p>{html.escape(t["content"])}</p></div>' for t in tickets)
    receipt_items=''
    receipt_labels={'new':'جدید','reviewed':'در حال بررسی','accepted':'تأیید شده','rejected':'رد شده'}
    for r in receipts:
        rid=int(r['id']); status=r.get('status') or 'new'; label=receipt_labels.get(status,status)
        actions=f'<a class="btn" target="_blank" href="/support/receipt/{rid}">👁️ مشاهده رسید</a>'
        if status not in ('accepted','rejected'):
            actions += f'<button class="btn" onclick="receiptStatus({rid},\'accepted\')">تأیید</button><button class="btn" onclick="receiptStatus({rid},\'rejected\')">رد</button>'
        receipt_items += f'<div class="receipt-row"><div><b>🧾 @{html.escape(r["username"])}</b><div class="report-meta">۱۰۰۰ سکه • {html.escape(r["filename"])} • وضعیت: {label}</div></div><div class="receipt-actions">{actions}</div></div>'

    body=f'''<div class="card admin-card page-enter"><h1>🛡️ مرکز فرماندهی پشتیبانی</h1><p>گزارش‌ها، محرومیت‌ها، موجودی کاربران و رسیدهای پرداخت از یکجا.</p></div>
    <div class="card support-admin-card"><h2>💰 مدیریت سکه و جام</h2><div class="support-direct-grid"><input id="walletTarget" placeholder="آیدی کاربر"><input id="coinDelta" type="number" placeholder="تغییر سکه، مثلاً +1000 یا -500"><input id="trophyDelta" type="number" placeholder="تغییر جام، مثلاً +5 یا -2"><button class="glow-btn" onclick="adjustWallet()">اعمال تغییر</button></div><div id="walletStatus" class="status-line"></div></div>
    <div class="card support-admin-card"><h2>🧾 صندوق رسیدهای پرداخت</h2><div class="payment-note">هر بسته: <b>۱۰۰۰ سکه = ۱۰۰٬۰۰۰ تومان</b> • کارت: <b>۶۲۱۹۸۶۱۸۵۱۱۶۰۰۶۸</b></div>{receipt_items or '<p>هنوز رسیدی ارسال نشده.</p>'}</div>
    <div class="card"><h2>📣 پیام رسمی به کاربر</h2><div class="support-direct-grid"><input id="officialTarget" placeholder="آیدی کاربر"><input id="officialText" placeholder="متن پیام رسمی"><button class="glow-btn" onclick="sendOfficial()">ارسال پیام</button></div></div>
    <div class="card"><h2>🏷️ تگ پشتیبانی</h2><div class="support-direct-grid"><input id="tagTarget" placeholder="آیدی کاربر"><input id="tagText" maxlength="40" placeholder="مثلاً بازیکن برتر"><button class="glow-btn" onclick="addTag()">ثبت تگ</button><button class="btn" onclick="removeTags()">حذف تگ‌ها</button></div></div>
    <div class="card"><h2>🔨 محرومیت مستقیم</h2><div class="support-direct-grid"><input id="directTarget" placeholder="آیدی کاربر"><select id="directScope"><option value="all">همه امکانات</option><option value="chat">چت</option><option value="games">بازی‌ها</option><option value="drawing">نقاشی</option><option value="profile">پروفایل</option><option value="bio">بیوگرافی</option><option value="username">آیدی</option></select><input id="directHours" type="number" min="0" max="168" value="0"><input id="directMinutes" type="number" min="1" max="59" value="10"></div><input id="directReason" placeholder="دلیل محرومیت"><button class="glow-btn" onclick="banDirect()">🚫 محروم کن</button></div>
    <div class="card"><h2>⏳ محرومیت‌های فعال</h2><div id="activeBans">{''.join(bans) or '<p>محرومیت فعالی وجود ندارد.</p>'}</div></div>
    <div class="card"><h2>🎫 تیکت‌ها</h2>{ticket_items or '<p>تیکتی ثبت نشده.</p>'}</div>
    <div class="card"><h2>🚩 گزارش‌ها</h2>{''.join(items) or '<p>گزارشی وجود ندارد.</p>'}</div>
    <div style="text-align:center"><a class="btn" href="/chat/private/morad">💬 پیوی پشتیبانی</a> <a class="btn" href="/chat/public">چت عمومی</a> <a class="btn" href="/lobby">لابی</a></div>
    <script>
    async function post(url,payload){{const r=await fetch(url,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});return r.json()}}
    async function doBan(p){{const d=await post('/support/ban',p);if(d.ok)location.reload();else alert('❌ اطلاعات را بررسی کن.')}}
    async function banUser(id,btn){{const item=btn.closest('.report-item');const target=item.querySelector('.report-meta b').textContent.trim();document.getElementById('directTarget').value=target;document.getElementById('directScope').value=item.querySelector('.ban-scope').value;await doBan({{report_id:id,target,scope:item.querySelector('.ban-scope').value,hours:Number(item.querySelector('.ban-hours').value)||0,minutes:Number(item.querySelector('.ban-minutes').value)||0,reason:'بر اساس گزارش #'+id}})}}
    async function banDirect(){{const target=directTarget.value.trim();if(!target)return;await doBan({{target,scope:directScope.value,hours:Number(directHours.value)||0,minutes:Number(directMinutes.value)||0,reason:directReason.value.trim()||'نقض قوانین'}})}}
    async function unbanUser(btn){{const row=btn.closest('.ban-row');const d=await post('/support/unban',{{target:row.dataset.target,scope:row.dataset.scope}});if(d.ok)row.remove()}}
    async function adjustWallet(){{const target=walletTarget.value.trim();if(!target)return;const d=await post('/support/adjust',{{target,coins:Number(coinDelta.value)||0,trophies:Number(trophyDelta.value)||0}});walletStatus.textContent=d.ok?'✅ تغییر با موفقیت اعمال شد. موجودی جدید: '+(d.wallet?.coins??0)+' سکه':'❌ انجام نشد';}}
    async function receiptStatus(id,status){{const d=await post('/support/receipt/status',{{id,status}});if(d.ok)location.reload();else alert(d.message||'این رسید قابل تغییر نیست.')}}
    async function sendOfficial(){{const target=officialTarget.value.trim(),content=officialText.value.trim();if(!target||!content)return alert('آیدی و پیام را کامل کن.');const d=await post('/support/message',{{target,content}});alert(d.ok?'✅ پیام رسمی ارسال شد.':'❌ ارسال ناموفق بود.');if(d.ok)officialText.value=''}}
    async function addTag(){{const target=tagTarget.value.trim(),tag=tagText.value.trim();if(!target||!tag)return;const d=await post('/support/tag',{{target,tag}});alert(d.ok?'🏷️ تگ ثبت شد.':'❌ ثبت نشد.')}}
    async function removeTags(){{const target=tagTarget.value.trim();if(!target)return;const d=await post('/support/tag/remove',{{target}});if(d.ok)alert('تگ‌ها حذف شدند.')}}
    </script>'''
    return page_shell('پنل پشتیبانی',body,username)

def _render_messages(messages: list[dict], username: str, support=False) -> str:
    if not messages: return '<div class="chat-empty">هنوز پیامی نیست...</div>'
    out=[]
    for m in messages:
        owned = set(str(m.get("owned_items") or "").split(",")) if m.get("owned_items") else set()
        bubble = " chat-bubble-owned" if "chat_bubble" in owned else ""
        namefx = " name-effect-owned" if "name_effect" in owned else ""
        cls=("msg me" if m["sender"]==username else "msg")+bubble
        sender=html.escape(str(m.get("public_username") or m["sender"])); content=html.escape(m["content"])
        actions=''
        if m['sender']!=username: actions+=f'<button class="report-btn" onclick="openReportModal({m["sender"]!r},{m["content"]!r},\'chat\',\'\')">🚩 گزارش</button>'
        if support: actions+=f'<button class="pin-btn" onclick="pinMessage({int(m["id"])})">📌 پین</button>'
        out.append(f'<div class="{cls}" data-id="{int(m["id"])}"><span class="sender{namefx}">{sender}</span><span class="content">{content}</span>{actions}</div>')
    return ''.join(out)

def chat_public_page(username: str, messages: list[dict], pinned: list[dict] | None = None) -> str:
    pinned=pinned or []; support=username=='morad'
    pinned_html=''.join(f'<div class="pinned-item" data-id="{p["message_id"]}">📌 <b>@{html.escape(p["sender"])}</b> — {html.escape(p["content"])}</div>' for p in pinned) or '<div class="pinned-empty">پیام سنجاق‌شده‌ای نیست.</div>'
    pin_js="const pb=document.createElement('button');pb.className='pin-btn';pb.textContent='📌 پین';pb.onclick=()=>pinMessage(d.id);div.append(pb);" if support else ''
    body=f'''<div class="chat-screen page-enter"><div class="chat-top"><div class="chat-toolbar"><div class="chat-title">💬 چت عمومی</div><a class="btn" href="/lobby">خانه</a></div><div id="pinnedBox" class="pinned-box">{pinned_html}</div></div><div class="chat-box" id="chatBox">{_render_messages(messages,username,support)}</div><div class="chat-input-wrap"><div class="chat-input-row"><input type="text" id="msgInput" placeholder="پیامت رو بنویس..." autocomplete="off"><button class="send-btn" onclick="sendMsg()">➤</button></div></div></div><script>const wsProto=location.protocol==='https:'?'wss:':'ws:',ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/public'),box=document.getElementById('chatBox'),me={username!r};function addMsg(d){{const div=document.createElement('div');div.className='msg '+(d.sender===me?'me':'')+((d.owned_items||[]).includes('chat_bubble')?' chat-bubble-owned':'');div.dataset.id=d.id;const s=document.createElement('span');s.className='sender';s.textContent=d.sender;const c=document.createElement('span');c.className='content';c.textContent=d.content;div.append(s,c);if(d.sender!==me){{const b=document.createElement('button');b.className='report-btn';b.textContent='🚩 گزارش';b.onclick=()=>openReportModal(d.sender,d.content,'chat','');div.append(b)}}{pin_js}box.appendChild(div);box.scrollTop=box.scrollHeight}}function renderPinned(arr){{document.getElementById('pinnedBox').innerHTML=(arr||[]).map(p=>`<div class="pinned-item">📌 <b>@${{p.sender}}</b> — ${{p.content}}</div>`).join('')||'<div class="pinned-empty">پیام سنجاق‌شده‌ای نیست.</div>'}}ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.type==='pinned_messages'){{renderPinned(d.messages);return}}if(d.content!==undefined)addMsg(d)}};async function pinMessage(id){{const r=await fetch('/support/pin',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message_id:id,room:'public'}})}});const d=await r.json();if(d.ok)renderPinned(d.messages)}}function sendMsg(){{const i=document.getElementById('msgInput'),v=i.value.trim();if(!v||ws.readyState!==1)return;ws.send(JSON.stringify({{content:v}}));i.value=''}}document.getElementById('msgInput').addEventListener('keydown',e=>{{if(e.key==='Enter')sendMsg()}});box.scrollTop=box.scrollHeight;</script>'''
    return page_shell('چت عمومی',body,username)

def chat_private_page(username: str, other: str, messages: list[dict]) -> str:
    body=f'''<div class="chat-screen page-enter"><div class="chat-top"><div class="chat-toolbar"><div class="chat-title">💬 @{html.escape(other)}</div><a class="btn" href="/messages">پیام‌ها</a></div></div><div class="chat-box" id="chatBox">{_render_messages(messages,username,False)}</div><div class="chat-input-wrap"><div class="chat-input-row"><input type="text" id="msgInput" placeholder="پیامت رو بنوی..." autocomplete="off"><button class="send-btn" onclick="sendMsg()">➤</button></div></div></div><script>const wsProto=location.protocol==='https:'?'wss:':'ws:',ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/private/{html.escape(other)}'),box=document.getElementById('chatBox'),me={username!r};function addMsg(d){{const div=document.createElement('div');div.className='msg '+(d.sender===me?'me':'');const s=document.createElement('span');s.className='sender';s.textContent=d.sender;const c=document.createElement('span');c.className='content';c.textContent=d.content;div.append(s,c);if(d.sender!==me){{const b=document.createElement('button');b.className='report-btn';b.textContent='🚩 گزارش';b.onclick=()=>openReportModal(d.sender,d.content,'chat','');div.append(b)}}box.appendChild(div);box.scrollTop=box.scrollHeight}}ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.content!==undefined)addMsg(d)}};function sendMsg(){{const i=document.getElementById('msgInput'),v=i.value.trim();if(!v||ws.readyState!==1)return;ws.send(JSON.stringify({{content:v}}));i.value=''}}document.getElementById('msgInput').addEventListener('keydown',e=>{{if(e.key==='Enter')sendMsg()}});box.scrollTop=box.scrollHeight;</script>'''
    return page_shell(f'چت با {other}',body,username)

def _drawing_battle_page(username: str, mode: int) -> str:
    title = "🎨 حدس نقاشی دو نفره" if mode == 2 else "🎨 نقاشی ۴ نفره"
    path = "/ws/drawing" if mode == 2 else "/ws/drawing-multi/4"
    total_rounds = 6 if mode == 2 else 4
    duration = 45 if mode == 2 else 35
    body = f"""<div class="draw-battle page-enter">
      <div class="draw-hero"><div><div class="draw-kicker">DRAW BATTLE • LIVE</div><h1>{title}</h1><div id="status" class="draw-status">🔌 در حال اتصال...</div></div><div class="draw-mode-badge">{mode} بازیکن</div></div>
      <div id="queueBox" class="queue-widget"><div class="queue-spinner"></div><div class="queue-text">🔌 در حال پیدا کردن بازیکن‌ها...</div></div>
      <div id="playersRow" class="draw-players-grid"></div>
      <div id="roundInfo" class="draw-round-info"><span id="roundLabel">دور ۱ از {total_rounds}</span><span id="timerLabel" class="draw-timer">⏱ --</span></div>
      <div id="previewPanel" class="draw-preview" style="display:none"><div class="preview-orb">🎨</div><div class="preview-title">آماده شو!</div><div id="previewText">موضوع برای نقاش آماده می‌شود...</div><div id="previewTimer" class="preview-count">5</div></div>
      <div id="boardFrame" class="draw-board-frame" style="display:none"><div class="draw-board-top"><span id="turnBadge">LIVE</span><span id="drawerLabel"></span></div><div class="draw-canvas-wrap"><canvas id="board" width="700" height="360"></canvas></div></div>
      <div id="palette" class="draw-palette" style="display:none"></div>
      <div id="tools" class="draw-tools" style="display:none"><button class="draw-tool active" id="penTool">✏️ قلم</button><button class="draw-tool" id="eraserTool">🧽 پاک‌کن</button><div class="draw-size-slider-wrap"><span class="draw-size-label">ضخامت</span><input type="range" id="sizeSlider" min="1" max="30" value="5"><span id="sizeValue" class="draw-size-value">5</span></div><button class="draw-tool" id="clearBtn">🧹 پاک‌کردن</button></div>
      <div id="drawerWordBox" class="draw-word-box" style="display:none"></div>
      <div id="optionsGrid" class="draw-options" style="display:none"></div>
      <div id="resultPanel" class="draw-result" style="display:none"></div>
    </div>
    <script>
    const me={username!r}, MODE={mode}, TOTAL_ROUNDS={total_rounds}, DURATION={duration}, WS_PATH={path!r};
    const proto=location.protocol==='https:'?'wss:':'ws:'; let ws=null,recon=null,intentionallyLeaving=false,timerInt=null,previewInt=null,role=null,currentColor='#20163a',currentSize=5,tool='pen',drawing=false,last=null,pending=[];
    const $=id=>document.getElementById(id), status=$('status'),queue=$('queueBox'),players=$('playersRow'),roundInfo=$('roundInfo'),roundLabel=$('roundLabel'),timer=$('timerLabel'),preview=$('previewPanel'),previewText=$('previewText'),previewTimer=$('previewTimer'),boardFrame=$('boardFrame'),drawerLabel=$('drawerLabel'),canvas=$('board'),ctx=canvas.getContext('2d'),palette=$('palette'),tools=$('tools'),wordBox=$('drawerWordBox'),opts=$('optionsGrid'),result=$('resultPanel');
    function clearBoard(){{ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height)}} clearBoard();
    function avatarNode(profile){{const wrap=document.createElement('div');wrap.className='draw-avatar';const a=profile?.avatar||'●';if(typeof a==='string'&&a.startsWith('data:image/')){{const img=document.createElement('img');img.src=a;img.alt='';wrap.appendChild(img)}}else wrap.textContent=a||'●';return wrap}}
    function renderPlayers(scores,active,drawerName,profiles){{players.innerHTML='';Object.entries(scores||{{}}).sort((a,b)=>b[1]-a[1]).forEach(([u,sc],i)=>{{const p=(profiles||{{}})[u]||{{username:u,display_name:u,avatar:'●'}};const card=document.createElement('div');card.className='draw-player-card'+(u===me?' me':'')+(u===drawerName?' turn':'')+((active||[]).includes(u)?'':' out');const info=document.createElement('div');info.className='draw-player-info';const name=document.createElement('b');name.textContent=p.display_name||u;const handle=document.createElement('span');handle.textContent='@'+u;const score=document.createElement('strong');score.textContent='⭐ '+sc;info.append(name,handle);const main=document.createElement('div');main.className='draw-player-main';main.appendChild(avatarNode(p));main.append(info,score);if(!p.profile_banned){{const link=document.createElement('a');link.href='/profile?u='+encodeURIComponent(u);link.target='_blank';link.rel='noopener';link.className='draw-player-main draw-profile-link';link.appendChild(avatarNode(p));link.append(info,score);card.append(link)}}else{{card.append(main)}}const role=document.createElement('div');role.className='draw-role';role.textContent=u===drawerName?'✏️ نقاش':'🔎 حدس‌زن';card.append(role);players.appendChild(card)}})}}
    function queueUI(n,needed){{queue.style.display='flex';let dots='';for(let i=0;i<needed;i++)dots+='<i class="queue-dot'+(i<n?' filled':'')+'"></i>';queue.innerHTML='<div class="queue-spinner"></div><div class="queue-dots">'+dots+'</div><div class="queue-text">'+n+' از '+needed+' نفر آماده‌اند</div><div class="queue-sub">به‌محض تکمیل ظرفیت، رقابت شروع می‌شود ✨</div>'}}
    function countdown(sec,fn,clearOld=true){{if(clearOld&&timerInt)clearInterval(timerInt);let left=Math.max(0,Math.ceil(sec));fn(left);timerInt=setInterval(()=>{{left--;fn(Math.max(0,left));if(left<=0)clearInterval(timerInt)}},1000)}}
    function previewCountdown(sec){{if(previewInt)clearInterval(previewInt);let left=Math.max(0,Math.ceil(sec));previewTimer.textContent=left;previewInt=setInterval(()=>{{left--;previewTimer.textContent=Math.max(0,left);if(left<=0)clearInterval(previewInt)}},1000)}}
    function paint(x0,y0,x1,y1,color,size){{const neon=((window.__profiles?.[me]?.owned_items||[]).includes('neon_pen'));ctx.save();ctx.strokeStyle=color||'#20163a';ctx.lineWidth=Math.max(1,Math.min(30,Number(size)||5));ctx.lineCap='round';ctx.shadowBlur=neon?12:0;ctx.shadowColor=neon?(color||'#00e5ff'):'transparent';ctx.beginPath();ctx.moveTo(x0*canvas.width,y0*canvas.height);ctx.lineTo(x1*canvas.width,y1*canvas.height);ctx.stroke();ctx.restore()}}
    function pos(e){{const r=canvas.getBoundingClientRect();return {{x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height}}}}
    function sendPending(){{if(pending.length&&ws?.readyState===1){{ws.send(JSON.stringify({{type:'draw_batch',segments:pending}}));pending=[]}}}}
    canvas.addEventListener('pointerdown',e=>{{if(role!=='drawer')return;drawing=true;canvas.setPointerCapture(e.pointerId);last=pos(e)}});canvas.addEventListener('pointermove',e=>{{if(role!=='drawer'||!drawing)return;const evs=e.getCoalescedEvents?e.getCoalescedEvents():[e];for(const ce of evs){{const p=pos(ce);const color=tool==='eraser'?'#fff':currentColor;paint(last.x,last.y,p.x,p.y,color,currentSize);pending.push({{x0:last.x,y0:last.y,x1:p.x,y1:p.y,color,size:currentSize}});last=p}}if(pending.length>=8)sendPending()}});window.addEventListener('pointerup',()=>{{drawing=false;sendPending()}});
    $('penTool').onclick=()=>{{tool='pen';$('penTool').classList.add('active');$('eraserTool').classList.remove('active')}};$('eraserTool').onclick=()=>{{tool='eraser';$('eraserTool').classList.add('active');$('penTool').classList.remove('active')}};$('clearBtn').onclick=()=>{{clearBoard();ws?.send(JSON.stringify({{type:'clear'}}))}};$('sizeSlider').oninput=e=>{{currentSize=Number(e.target.value)||5;$('sizeValue').textContent=currentSize}};
    function buildPalette(colors){{palette.innerHTML='';(colors||[]).forEach((c,i)=>{{const b=document.createElement('button');b.className='draw-swatch'+(i===0?' active':'');b.style.background=c;b.onclick=()=>{{currentColor=c;[...palette.children].forEach(x=>x.classList.remove('active'));b.classList.add('active')}};palette.appendChild(b)}});if(colors?.length)currentColor=colors[0]}}
    function buildOptions(arr){{opts.innerHTML='';(arr||[]).forEach(w=>{{const b=document.createElement('button');b.className='draw-option-btn';b.textContent=w;b.onclick=()=>sendGuess(w);b.dataset.word=w;opts.appendChild(b)}})}}
    function sendGuess(word){{const v=(word||'').trim();if(!v||ws?.readyState!==1)return;ws.send(JSON.stringify({{type:'guess',word:v}}));}}
    function showRoundUI(){{queue.style.display='none';preview.style.display='none';roundInfo.style.display='flex';boardFrame.style.display='block';result.style.display='none'}}
    function renderResult(d){{if(timerInt)clearInterval(timerInt);roundInfo.style.display='none';boardFrame.style.display='none';palette.style.display='none';tools.style.display='none';wordBox.style.display='none';opts.style.display='none';result.style.display='block';renderPlayers(d.scores,d.active,d.drawer,d.profiles);const rows=Object.entries(d.scores||{{}}).sort((a,b)=>b[1]-a[1]).map(([u,s],i)=>'<div class="result-row"><span>#'+(i+1)+'</span><b>'+((d.profiles||{{}})[u]?.display_name||u)+'</b><strong>⭐ '+s+' کل</strong></div>').join('');const roundRows=Object.entries(d.points_map||{{}}).map(([u,s])=>'<div class="result-row round-points"><span>+</span><b>'+((d.profiles||{{}})[u]?.display_name||u)+'</b><strong>+'+s+' امتیاز این دور</strong></div>').join('');result.innerHTML='<div class="result-glow">'+(d.correct?'🎯':'⌛')+'</div><div class="draw-result-title">'+(d.correct?'حدس درست بود!':'زمان این دور تمام شد')+'</div><div class="result-word">موضوع: <b>'+String(d.word||'—')+'</b></div><div class="result-subtitle">امتیاز این دور</div><div class="result-table">'+(roundRows||'<div class="report-meta">این دور امتیازی ثبت نشد.</div>')+'</div><div class="result-subtitle">امتیاز کل بازی</div><div class="result-table">'+rows+'</div><div id="breakText" class="draw-result-note"></div><div class="draw-result-exit"><a class="btn glow-btn" href="/lobby">🏠 بازگشت به لابی</a></div>';const bt=$('breakText');countdown(d.break_seconds||10,x=>bt.textContent=d.is_last?'🏁 نتیجه نهایی در حال آماده‌سازی… '+x+' ثانیه':'⚡ دور بعدی تا '+x+' ثانیه دیگر');}}
    function connect(){{ws=new WebSocket(proto+'//'+location.host+WS_PATH);ws.onopen=()=>status.textContent='🟢 وصل شد؛ در حال پیدا کردن بازیکن…';ws.onclose=()=>{{if(!intentionallyLeaving&&!recon)recon=setTimeout(()=>{{recon=null;connect()}},1200)}};ws.onerror=()=>status.textContent='⚠️ اتصال ناپایدار؛ دوباره تلاش می‌کنیم';ws.onmessage=e=>onMsg(JSON.parse(e.data))}}
    function onMsg(d){{if(d.type==='waiting'){{queueUI(d.count,d.needed);return}}if(d.type==='queue_timeout'){{queue.innerHTML='<div class="queue-text">⌛ بازیکنی پیدا نشد. دوباره وارد شو.</div>';return}}if(d.type==='round_preview'){{role=d.role;queue.style.display='none';preview.style.display='block';boardFrame.style.display='none';roundInfo.style.display='flex';roundLabel.textContent='دور '+d.round+' از '+d.total_rounds;renderPlayers(d.scores,d.active,d.drawer,d.profiles);previewText.textContent=role==='drawer'?'موضوع نقاشی: '+(d.word||'—'):'موضوع مخفی است؛ آماده حدس‌زدن شو!';preview.classList.toggle('drawer-preview',role==='drawer');previewCountdown(d.remaining||5);status.textContent=role==='drawer'?'✏️ موضوع را ببین و آماده شو!':'🔎 آماده باش؛ نقاش به‌زودی شروع می‌کند';return}}if(d.type==='round_start'){{showRoundUI();role=d.role;roundLabel.textContent='دور '+d.round+' از '+d.total_rounds;drawerLabel.textContent=role==='drawer'?'✏️ تو نقاشی':'🎯 نقاش: '+(d.drawer||'—');renderPlayers(d.scores,d.active,d.drawer,d.profiles);clearBoard();(d.strokes||[]).forEach(s=>paint(s.x0,s.y0,s.x1,s.y1,s.color,s.size));if(role==='drawer'){{wordBox.style.display='block';wordBox.textContent='🎯 موضوع: '+d.word;palette.style.display='flex';tools.style.display='flex';opts.style.display='none';buildPalette(d.colors)}}else{{wordBox.style.display='none';palette.style.display='none';tools.style.display='none';opts.style.display='flex';buildOptions(d.options)}}countdown(d.remaining||d.duration,x=>timer.textContent='⏱ '+x+' ثانیه');status.textContent=role==='drawer'?'✏️ بکش!':'🔎 حدس بزن!';return}}if(d.type==='draw'){{paint(d.x0,d.y0,d.x1,d.y1,d.color,d.size);return}}if(d.type==='draw_batch'){{(d.segments||[]).forEach(s=>paint(s.x0,s.y0,s.x1,s.y1,s.color,s.size));return}}if(d.type==='clear'){{clearBoard();return}}if(d.type==='guess_wrong'){{opts.querySelectorAll('button').forEach(b=>{{b.disabled=true}});const b=opts.querySelector('[data-word="'+CSS.escape(d.word)+'"]');if(b)b.classList.add('wrong');status.textContent='❌ حدست اشتباه بود؛ این دور دیگر امکان حدس نداری.';return}}if(d.type==='correct'){{status.textContent='✅ درست! +'+d.points+' امتیاز';return}}if(d.type==='round_result'){{renderResult(d);return}}if(d.type==='game_over'){{if(timerInt)clearInterval(timerInt);preview.style.display='none';boardFrame.style.display='none';roundInfo.style.display='none';palette.style.display='none';tools.style.display='none';wordBox.style.display='none';opts.style.display='none';result.style.display='block';renderPlayers(d.scores,d.active,null,d.profiles);const entries=Object.entries(d.scores||{{}}).sort((a,b)=>b[1]-a[1]);result.classList.toggle('victory-owned',(d.winner===me)&&((d.profiles?.[me]?.owned_items||[]).includes('victory_fx')));result.innerHTML='<div class="result-glow">🏆</div><div class="draw-result-title">نتیجه نهایی</div>'+entries.map(([u,s],i)=>'<div class="result-row '+(u===d.winner?'winner':'')+'"><span>#'+(i+1)+'</span><b>'+((d.profiles||{{}})[u]?.display_name||u)+'</b><strong>⭐ '+s+(u===d.winner?' 🏆':'')+'</strong></div>').join('')+'<div class="draw-result-exit"><a class="btn glow-btn" href="/lobby">🏠 بازگشت به لابی</a></div>';status.textContent=d.winner===me?'🏆 قهرمان شدی!':'بازی تمام شد';return}}if(d.type==='player_left')status.textContent='⚠️ '+d.username+' از بازی خارج شد'}}
    connect();
    </script>"""
    return page_shell(title, body, username)

def drawing_page(username: str) -> str:
    return _drawing_battle_page(username, 2)


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
    if username == "morad": items.append(("support","🛡️","پنل پشتیبانی","/support"))
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
    body=f"""<div class="lobby-bg page-enter">
      <div class="section-heading"><span>🎮 حالت‌های بازی</span><small>دو حالت، یک رقابت</small></div>
      <div class="game-mode-card mode-speed">
        <div class="mode-badge">⚡ دو نفره سرعتی</div><div class="mode-icon">⭕</div>
        <div class="mode-copy"><h2>حدس نقاشی</h2><p>۲ بازیکن • نقاشی و حدس سریع</p></div>
        <a class="mode-start" href="/game/drawing">شروع <span>←</span></a>
      </div>
      <div class="game-mode-card mode-draw">
        <div class="mode-badge">🎨 رقابت نقاشان</div><div class="mode-icon">🖌️</div>
        <div class="mode-copy"><h2>نقاشی ۴ نفره</h2><p>۴ بازیکن • نقاشی و حدس</p></div>
        <a class="mode-start" href="/game/drawing4">شروع <span>←</span></a>
      </div>
      <a class="btn" href="/lobby">← بازگشت به لابی</a>
    </div>{_bottom_nav("home")}"""
    return page_shell('انتخاب بازی',body,username)

def _avatar_html(avatar, cls="profile-avatar-img", alt="تصویر کاربر"):
    avatar = str(avatar or "").strip()
    if avatar.startswith("data:image/"):
        return f'<img class="{cls}" src="{html.escape(avatar, quote=True)}" alt="{html.escape(alt)}">'
    return f'<div class="avatar-big avatar-placeholder" aria-label="{html.escape(alt)}">●</div>'

def restricted_profile_page(username, target):
    body=f'''<div class="profile-card hero page-enter" style="text-align:center;padding:36px 20px"><div style="font-size:54px">🔒</div><h1>پروفایل در دسترس نیست</h1><p>پروفایل @{html.escape(target)} به‌طور موقت توسط پشتیبانی محدود شده و در هیچ بخش عمومی نمایش داده نمی‌شود.</p><a class="btn" href="/lobby">🏠 بازگشت به لابی</a></div>'''
    return page_shell('پروفایل محدود شده',body,username)

def profile_page(username, prof):
    prof = prof or {'username': username, 'bio': '', 'avatar': '', 'age':18, 'wins':0, 'losses':0, 'draws':0, 'points':0, 'correct_guesses':0, 'wrong_guesses':0, 'support_tags':[]}
    total=int(prof.get('correct_guesses',0) or 0)+int(prof.get('wrong_guesses',0) or 0)
    correct=round(int(prof.get('correct_guesses',0) or 0)*100/total,1) if total else 0
    wrong=round(int(prof.get('wrong_guesses',0) or 0)*100/total,1) if total else 0
    avatar_banned=bool(prof.get('profile_banned')); bio_banned=bool(prof.get('bio_banned'))
    avatar_html='<div class="avatar-hidden">●</div>' if avatar_banned else _avatar_html(prof.get('avatar') or '')
    is_support=prof['username']=='morad'
    badge='<div class="verified-support">✓ پشتیبانی رسمی</div>' if is_support else ''
    tags=''.join(f'<span class="support-tag">🏷️ {html.escape(str(t.get("tag") or ""))}</span>' for t in (prof.get('support_tags') or []))
    tag_box=f'<div class="support-tags">{tags}</div>' if tags else ''
    friend_status=prof.get('friend_status','none')
    blocked_by_me=bool(prof.get('blocked_by_me'))
    if prof['username']!=username:
        target_js=html.escape(prof['username'],quote=True)
        if friend_status=="friends":
            friend_btn='<button class="circle-action friend-ok" disabled>✓</button>'
            chat_btn=f'<a class="btn" href="/chat/private/{quote(prof["username"],safe="")}">💬 چت خصوصی</a>'
        elif friend_status=="outgoing":
            friend_btn='<button class="circle-action" disabled>✓</button>'
            chat_btn='<button class="btn" onclick="needFriend()">💬 چت خصوصی</button>'
        elif friend_status=="incoming":
            friend_btn='<button class="circle-action" disabled>📨</button>'
            chat_btn='<button class="btn" onclick="needFriend()">💬 چت خصوصی</button>'
        else:
            friend_btn='<button class="circle-action" title="درخواست دوستی" onclick="askFriend()">+</button>'
            chat_btn='<button class="btn" onclick="needFriend()">💬 چت خصوصی</button>'
        report_btn='' if prof['username'].lower()=='morad' else f'<button class="circle-action report-circle" title="گزارش" onclick="openReportModal(\'{target_js}\',\'پروفایل کاربر\',\'profile\',\'\')">🚩</button>'
        block_btn='' if prof['username'].lower()=='morad' else f'<button id="blockBtn" class="circle-action block-circle" title="{"آنبلاک" if blocked_by_me else "بلاک"}" onclick="toggleBlock()">{"✓" if blocked_by_me else "×"}</button>'
        support_tools=''
        if username=='morad':
            support_tools=f'''<div class="support-profile-tools"><b>🛡️ مدیریت پروفایل</b><div class="support-profile-row"><input id="profileBanTarget" value="{target_js}" readonly><select id="profileBanHours"><option value="1">۱ ساعت</option><option value="6">۶ ساعت</option><option value="24">۲۴ ساعت</option><option value="72">۳ روز</option><option value="168">۷ روز</option></select><button class="btn" onclick="banProfile()">🚫 محرومیت پروفایل</button></div></div>'''
        actions=f'''<div class="profile-actions"><div class="profile-action-row">{friend_btn}{report_btn}{block_btn}</div>{chat_btn}</div>{support_tools}'''
        scripts=f'''<script>
        function askFriend(){{
          if(document.getElementById('friendConfirm'))return;
          const m=document.createElement('div');m.id='friendConfirm';m.className='confirm-overlay';
          m.innerHTML='<div class="confirm-card"><b>👥 درخواست دوستی</b><p>آیا از ارسال درخواست دوستی به @{target_js} مطمئن هستید؟</p><div><button onclick="confirmFriend(true)">بله</button><button class="btn" onclick="confirmFriend(false)">خیر</button></div></div>';
          document.body.appendChild(m);
        }}
        async function confirmFriend(ok){{
          const m=document.getElementById('friendConfirm');if(m)m.remove();if(!ok)return;
          const r=await fetch('/friends/request',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target:'{target_js}'}})}});
          const d=await r.json();alert(d.ok?'✅ درخواست دوستی ارسال شد.':d.status==='already_sent'?'این درخواست قبلاً ارسال شده است.':'❌ درخواست ارسال نشد.');if(d.ok)location.reload();
        }}
        function needFriend(){{alert('💬 اول باید درخواست دوستی ارسال کنید و طرف مقابل آن را قبول کند.');}}
        async function toggleBlock(){{
          const blocked={str(blocked_by_me).lower()};
          if(!confirm(blocked?'آیا می‌خواهید این کاربر را آنبلاک کنید؟':'آیا از بلاک کردن این کاربر مطمئن هستید؟'))return;
          const r=await fetch('/users/block',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target:'{target_js}'}})}});
          const d=await r.json();if(d.ok)location.reload();
        }}
        async function banProfile(){{
          const target=document.getElementById('profileBanTarget').value;
          const hours=Number(document.getElementById('profileBanHours').value)||1;
          const r=await fetch('/support/ban',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target,scope:'profile',hours,minutes:0,reason:'محرومیت پروفایل توسط پشتیبانی'}})}});
          const d=await r.json();alert(d.ok?'✅ پروفایل کاربر برای '+hours+' ساعت محدود شد.':'❌ انجام نشد.');if(d.ok)location.reload();
        }}
        </script>'''
    else:
        actions='<div class="profile-actions"><a class="btn" href="/settings">⚙️ تنظیمات پروفایل</a></div>'
        scripts=''
    support_box='<a class="support-mini-card" href="/support/ticket">🛡️ <b>پشتیبانی رسمی</b><span>برای ارتباط مستقیم، تیکت ثبت کن</span></a>' if is_support else ''
    bio='<div class="moderation-hidden">این بخش به‌طور موقت محدود شده است.</div>' if bio_banned else html.escape(prof.get('bio') or 'این کاربر هنوز بیوگرافی ننوشته.')
    notice=f'<div class="error" style="margin-bottom:12px;text-align:center">💬 {html.escape(str(prof.get("chat_notice") or ""))}</div>' if prof.get("chat_notice") else ''
    body=f'''<div class="profile-card hero page-enter">{notice}<div class="profile-head"><div>{avatar_html}</div><div><div class="profile-kicker">PLAYER PROFILE</div><h1>@{html.escape(prof['username'])}</h1><div class="profile-age">🎂 {int(prof.get('age') or 18)} سال</div>{badge}</div></div>{tag_box}<div class="profile-bio">{bio}</div><div class="stat-grid"><div class="stat-box"><b>{correct}%</b><br>حدس درست</div><div class="stat-box"><b>{wrong}%</b><br>حدس غلط</div><div class="stat-box"><b>{prof.get('wins',0)}</b><br>جام</div><div class="stat-box"><b>{prof.get('points',0)}</b><br>امتیاز</div></div>{actions}{support_box}</div>{scripts}<div style="text-align:center;margin-top:14px"><a class="btn" href="/lobby">← بازگشت به لابی</a></div>'''
    return page_shell('پروفایل',body,username)

def settings_page(username, prof):
    prof = prof or {'username': username, 'bio': '', 'avatar': '', 'age': 18}
    raw_avatar = prof.get('avatar') or ''
    avatar_html = _avatar_html(raw_avatar, cls="profile-avatar-img")
    bio = html.escape(prof.get('bio') or '')
    age = int(prof.get('age') or 18)
    body = f'''<div class="settings-screen page-enter">
      <div class="settings-header"><div class="settings-gear">⚙️</div><h1>تنظیمات</h1><a class="settings-close" href="/lobby">×</a></div>
      <div class="settings-card">
        <div class="settings-kicker">پروفایل</div>
        <div class="settings-avatar-row">
          <div class="settings-avatar" id="avatarPreview">{avatar_html}</div>
          <div><p>آواتار فقط با <b>تصویر</b> قابل تنظیم است؛ گزینه آواتار ایموجی حذف شده.</p></div>
        </div>
        <input type="file" id="avatarFile" class="file-input" accept="image/*">
        <label for="bioInput">بیوگرافی</label>
        <textarea id="bioInput" maxlength="70" placeholder="چیزی درباره‌ی خودت بنویس...">{bio}</textarea>
        <div class="char-counter"><span id="bioCount">0</span>/70</div>
        <div class="age-row"><span>سن:</span><input type="number" id="ageInput" min="1" max="90" value="{age}"></div>
        <button class="settings-save" id="saveProfileBtn" onclick="saveProfile()">💾 ذخیره تغییرات</button>
        <div id="profileStatus" class="status-line" style="display:none"></div>
      </div>
      <div class="settings-card">
        <div class="settings-kicker">امنیت حساب</div>
        <label for="oldPassword">رمز عبور فعلی</label>
        <input type="password" id="oldPassword" placeholder="رمز فعلی">
        <label for="newPassword">رمز عبور جدید</label>
        <input type="password" id="newPassword" placeholder="حداقل ۴ کاراکتر">
        <button class="settings-save" id="savePasswordBtn" onclick="savePassword()">🔑 تغییر رمز عبور</button>
        <div id="passwordStatus" class="status-line" style="display:none"></div>
      </div>
      <div class="settings-card logout-card"><button class="logout-btn" onclick="logoutAccount()">🚪 خروج از حساب</button></div>
      <div class="settings-note">تغییرات بلافاصله روی پروفایل عمومی اعمال می‌شود.</div>
      <div class="settings-links"><a href="/lobby">🏠 لابی</a><a href="/profile?u={quote(username,safe='')}">👤 پروفایل من</a></div>
    </div>
    <script>
    let pendingAvatar=null;
    const bioEl=document.getElementById('bioInput'),bioCount=document.getElementById('bioCount');
    function refreshCount(){{bioCount.textContent=bioEl.value.length}}
    refreshCount(); bioEl.addEventListener('input',refreshCount);
    document.getElementById('avatarFile').addEventListener('change',function(e){{
      const file=e.target.files[0]; if(!file)return;
      if(!file.type.startsWith('image/')){{alert('فقط تصویر مجاز است.');return}}
      const reader=new FileReader();
      reader.onload=function(ev){{
        const img=new Image();
        img.onload=function(){{
          const size=Math.min(img.width,img.height);
          const canvas=document.createElement('canvas'); canvas.width=320; canvas.height=320;
          const ctx=canvas.getContext('2d');
          ctx.drawImage(img,(img.width-size)/2,(img.height-size)/2,size,size,0,0,320,320);
          pendingAvatar=canvas.toDataURL('image/jpeg',0.85);
          document.getElementById('avatarPreview').innerHTML='<img src="'+pendingAvatar+'" class="profile-avatar-img">';
        }};
        img.src=ev.target.result;
      }};
      reader.readAsDataURL(file);
    }});
    async function saveProfile(){{
      const btn=document.getElementById('saveProfileBtn'); btn.disabled=true;
      const bio=bioEl.value.trim(); const age=Number(document.getElementById('ageInput').value)||18;
      const payload={{bio,age}}; if(pendingAvatar)payload.avatar=pendingAvatar;
      const s=document.getElementById('profileStatus'); s.style.display='block';
      try{{
        const r=await fetch('/settings/profile',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});
        const d=await r.json(); s.textContent=d.ok?'✅ تغییرات ذخیره شد.':'❌ ذخیره نشد؛ شاید پروفایل یا بیو موقتاً محدود شده باشد.';
        if(d.ok){{pendingAvatar=null;setTimeout(()=>location.reload(),700)}}
      }}catch(e){{s.textContent='❌ خطا در ارتباط با سرور.'}}
      btn.disabled=false;
    }}
    async function savePassword(){{
      const old_password=document.getElementById('oldPassword').value,new_password=document.getElementById('newPassword').value;
      const s=document.getElementById('passwordStatus'); s.style.display='block';
      if(new_password.length<4){{s.textContent='رمز جدید باید حداقل ۴ کاراکتر باشد.';return}}
      const btn=document.getElementById('savePasswordBtn'); btn.disabled=true;
      try{{
        const r=await fetch('/settings/password',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{old_password,new_password}})}});
        const d=await r.json(); s.textContent=d.ok?'✅ رمز عبور تغییر کرد.':'❌ رمز فعلی اشتباه است یا رمز جدید کوتاه است.';
        if(d.ok){{document.getElementById('oldPassword').value='';document.getElementById('newPassword').value=''}}
      }}catch(e){{s.textContent='❌ خطا در ارتباط با سرور.'}}
      btn.disabled=false;
    }}
    function logoutAccount(){{location.href='/logout'}}
    </script>'''
    return page_shell('تنظیمات', body, username)


BASE_CSS += """
.game-choice{text-align:center;overflow:hidden}.game-choice-icon{font-size:58px;filter:drop-shadow(0 8px 18px rgba(47,169,160,.22));animation:floatGame 2.8s ease-in-out infinite}.game-choice-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:22px 0}.game-choice-card{display:flex;flex-direction:column;align-items:center;gap:4px;padding:24px 12px;border:1px solid var(--border);border-radius:20px;background:linear-gradient(145deg,var(--surface-raised),var(--surface));color:var(--text);text-decoration:none;transform:translateZ(0);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}.game-choice-card span{font-size:46px}.game-choice-card b{font-size:19px}.game-choice-card small{color:var(--text-muted)}.game-choice-card:hover{transform:translateY(-5px);border-color:var(--turquoise);box-shadow:0 12px 30px rgba(47,169,160,.16)}.draw-result{animation:pageIn .25s ease both}.card{transform:translateZ(0)}@keyframes floatGame{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}@media(max-width:520px){.game-choice-grid{grid-template-columns:1fr}}@media(prefers-reduced-motion:reduce){.game-choice-icon{animation:none}}
"""


BASE_CSS += """
.lobby-shell{max-width:560px;margin:0 auto;padding:10px 0 35px}.lobby-profile{border:2px solid #633f8f;border-radius:24px;padding:22px;box-shadow:0 0 35px rgba(123,71,202,.2);animation:cardPop .45s ease both}.lobby-profile-main{display:flex;align-items:center;gap:14px}.lobby-avatar{width:92px;height:92px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:44px;text-decoration:none;background:linear-gradient(145deg,#f25bbd,#8554f5);border:5px solid #e889df;box-shadow:0 0 28px rgba(230,85,215,.3)}.lobby-name{font-size:25px;font-weight:900;color:#ef70ca}.lobby-sub{color:#8886a7;font-size:13px}.lobby-stats{display:flex;flex-direction:column;gap:7px;margin-top:14px;color:#8f8aa9}.lobby-promo-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:28px}.promo-card{position:relative;min-height:170px;border-radius:22px;padding:20px 14px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none;color:#fff;box-shadow:0 12px 30px rgba(0,0,0,.22);transition:transform .25s,filter .25s}.promo-card:hover{transform:translateY(-6px) scale(1.02);filter:brightness(1.08)}.promo-card span{font-size:46px}.promo-card b{font-size:23px}.promo-card small{font-size:14px;opacity:.9}.promo-card.orange{background:linear-gradient(145deg,#ffad0a,#f24d40)}.promo-card.purple{background:linear-gradient(145deg,#9b5cff,#7353ee)}.promo-card em{position:absolute;right:-8px;top:70px;background:#ffb71b;border:3px solid #ffd65d;color:#402700;border-radius:18px;padding:7px 10px;font-style:normal;font-weight:900;box-shadow:0 0 18px rgba(255,183,27,.45);animation:giftFloat 2s ease-in-out infinite}.lobby-sep{text-align:center;color:#777696;font-size:16px;margin:18px 0}.lobby-duo{display:grid;grid-template-columns:1fr 1fr;background:linear-gradient(145deg,#ffc400,#ffab00);border-radius:22px;overflow:hidden;box-shadow:0 12px 30px rgba(255,177,0,.2)}.lobby-duo a{min-height:120px;display:flex;align-items:center;justify-content:center;gap:8px;flex-direction:column;color:#151515;text-decoration:none;font-size:22px;transition:transform .2s}.lobby-duo a:first-child{border-left:3px solid rgba(80,50,0,.25)}.lobby-duo a:hover{transform:scale(1.03)}.lobby-play{display:flex;align-items:center;justify-content:center;min-height:92px;border-radius:20px;background:linear-gradient(145deg,#39db7a,#16ad61);color:#fff;text-decoration:none;font-size:24px;font-weight:900;box-shadow:0 12px 30px rgba(35,203,112,.25);transition:transform .2s,filter .2s}.lobby-play:hover{transform:translateY(-4px);filter:brightness(1.08)}.lobby-mini-actions{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:18px}.lobby-mini-actions a{padding:8px 12px;border:1px solid #303257;border-radius:12px;color:#a9add0;text-decoration:none;background:#15182e}.profile-actions{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:18px}.verified-support{display:inline-block;margin-top:7px;padding:4px 10px;border-radius:999px;background:linear-gradient(90deg,#7a5cff,#d65ee5);color:white;font-size:11px;font-weight:900;box-shadow:0 0 18px rgba(128,92,255,.35)}.support-mini-card{display:flex;flex-direction:column;gap:2px;margin:14px 0;padding:15px 17px;border:1px solid #7d61ff;border-radius:18px;background:linear-gradient(145deg,#1e1b45,#17162e);color:#fff;text-decoration:none;box-shadow:0 8px 25px rgba(113,82,255,.16)}.support-mini-card span{font-size:11px;color:#9fa4c8}.friend-row{display:flex;align-items:center;gap:10px;padding:11px;border:1px solid #2b3054;border-radius:15px;background:#15182e;margin-bottom:8px}.friend-row .avatar{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#282d52}.friend-row .grow{flex:1}.request-actions{display:flex;gap:6px}.ticket-card textarea{width:100%;min-height:160px;padding:12px;border-radius:13px;background:var(--bg);color:var(--text);border:1px solid var(--border);font-family:inherit}.ticket-card input{margin-bottom:10px}@keyframes cardPop{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:none}}@keyframes giftFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}@media(max-width:520px){.lobby-promo-grid{gap:10px}.promo-card{min-height:150px}.lobby-duo a{min-height:105px;font-size:18px}}
"""

def messages_page(username, friends, requests):
    req_cards=[]
    for r in requests:
        rname=html.escape(r.get('display_name') or r['sender'])
        rlink='' if r.get('profile_banned') else f'<a class="profile-link" href="/profile?u={quote(r["sender"],safe="")}"><b>{rname}</b></a>'
        if not rlink: rlink=f'<b>{rname}</b>'
        req_cards.append(f'<div class="friend-row page-enter"><div class="avatar">●</div><div class="grow">{rlink}<div class="report-meta">@{html.escape(r["sender"])} برای دوستی درخواست داده</div></div><div class="request-actions"><button onclick="respond({r["sender"]!r},true)">✓</button><button class="btn" onclick="respond({r["sender"]!r},false)">✕</button></div></div>')
    req_html=''.join(req_cards) or '<p style="opacity:.55;text-align:center;padding:25px">درخواست دوستی جدیدی نداری.</p>'
    friend_cards=[]
    now=int(time.time())
    for f in friends:
        age_sec=now-int(f.get('created_at') or now)
        can_remove=age_sec>=5*3600
        remove_btn=f'<button class="circle-action block-circle" title="حذف دوست" onclick="removeFriend(\'{html.escape(f["username"],quote=True)}\')">×</button>' if can_remove else f'<span class="report-meta" title="حذف دوست بعد از ۵ ساعت فعال می‌شود">⏳</span>'
        fname=html.escape(f.get('display_name') or f['username'])
        flink='' if f.get('profile_banned') else f'<a class="profile-link" href="/profile?u={quote(f["username"],safe="")}"><b>{fname}</b></a>'
        if not flink: flink=f'<b>{fname}</b>'
        friend_cards.append(f'<div class="friend-row"><div class="avatar">●</div><div class="grow">{flink}<div class="report-meta">@{html.escape(f["username"])}</div></div><a class="btn" href="/chat/private/{quote(f["username"],safe="")}">💬</a>{remove_btn}</div>')
    fr_html=''.join(friend_cards) or '<p style="opacity:.55;text-align:center;padding:25px">هنوز دوستی نداری.</p>'
    body=f"""<div class="card hero page-enter"><div style="display:flex;justify-content:space-between;align-items:center"><h1>💬 پیام‌ها</h1><a class="btn" href="/lobby">خانه ←</a></div><div class="tabs"><a class="active" href="/messages">💬 مکالمات</a><span>👥 دوستان</span><span>📨 درخواست‌ها <b>{len(requests)}</b></span></div><input id="userSearch" type="text" placeholder="🔎 جستجوی کاربر..." oninput="searchUser()"><div id="searchResult"></div></div><div class="card"><h2>📨 درخواست‌های دوستی</h2>{req_html}</div><div class="card"><h2>👥 دوستان من</h2>{fr_html}</div><script>async function respond(sender,accept){{const r=await fetch('/friends/respond',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{sender,accept}})}});if((await r.json()).ok)location.reload()}}async function removeFriend(target){{const r=await fetch('/friends/remove',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target}})}});const d=await r.json();if(d.ok)location.reload();else if(d.status==='too_soon')alert('⏳ حذف دوست بعد از ۵ ساعت دوستی امکان‌پذیر است.')}}let timer;async function searchUser(){{clearTimeout(timer);const q=document.getElementById('userSearch').value.trim(),box=document.getElementById('searchResult');if(!q){{box.innerHTML='';return}};timer=setTimeout(async()=>{{const r=await fetch('/profile?u='+encodeURIComponent(q));box.innerHTML=r.ok?'<a class="friend-row" href="/profile?u='+encodeURIComponent(q)+'"><div class="grow">👤 باز کردن پروفایل <b>@'+q.replace(/[<>&]/g,'')+'</b></div><span>→</span></a>':'<p class="report-meta">کاربر پیدا نشد.</p>'}},250)}}</script>"""
    return page_shell('پیام‌ها',body,username)

def support_ticket_page(username):
    body=f"""<div class="card hero page-enter ticket-card"><h1>🛡️ تیکت پشتیبانی رسمی</h1><p>پیامت مستقیم در صف پشتیبانی ثبت می‌شود.</p><input id="subject" placeholder="موضوع تیکت" maxlength="120"><textarea id="content" maxlength="3000" placeholder="توضیحت را بنویس..."></textarea><button class="glow-btn" onclick="sendTicket()">🎫 ثبت تیکت</button><div id="status" class="status-line" style="display:none"></div></div><div style="text-align:center"><a class="btn" href="/lobby">بازگشت به منو</a></div><script>async function sendTicket(){{const subject=document.getElementById('subject').value.trim(),content=document.getElementById('content').value.trim(),s=document.getElementById('status');if(!subject||!content){{s.style.display='block';s.textContent='موضوع و توضیح را کامل کن.';return}}const r=await fetch('/support/ticket',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{subject,content}})}}),d=await r.json();s.style.display='block';s.textContent=d.ok?'✅ تیکت #'+d.ticket_id+' ثبت شد.':'❌ ثبت تیکت ناموفق بود.'}}</script>"""
    return page_shell('تیکت پشتیبانی',body,username)


def shop_page(username):
    body=f'''<div class="page-heading"><div><div class="sub">ARCADE STORE • ITEMS</div><h1>🛍️ فروشگاه</h1></div><a class="btn" href="/lobby">خانه</a></div><div class="card hero page-enter"><p>سکه‌ها و آیتم‌های تزئینی بازی را از اینجا مدیریت کن.</p><div class="lobby-promo-grid"><div class="promo-card purple"><span>💎</span><b>بسته سکه</b><small>به‌زودی</small></div><div class="promo-card orange"><span>🎁</span><b>آیتم ویژه</b><small>به‌زودی</small></div></div></div><div class="card page-enter"><h2>✨ ویترین ویژه</h2><p>آیتم‌های بعدی با همین استایل نئونی اضافه می‌شوند.</p></div>'''
    return page_shell("فروشگاه",body,username)

BASE_CSS += """
.lobby-bg{background:repeating-linear-gradient(45deg,rgba(255,255,255,.035) 0 5px,transparent 5px 14px),radial-gradient(circle at 20% 10%,rgba(255,160,0,.22),transparent 24%),radial-gradient(circle at 80% 5%,rgba(255,0,100,.2),transparent 26%),linear-gradient(135deg,#24100c,#641a18 30%,#4d0d38 52%,#152b58 76%,#1c611e);border-radius:28px;padding:14px 8px 110px;box-shadow:inset 0 0 80px rgba(0,0,0,.35)}
.lobby-top-title{text-align:center;color:#fff;font-size:30px;font-weight:1000;text-shadow:0 3px 0 rgba(0,0,0,.25),0 0 16px rgba(255,255,255,.2);margin:3px 0 14px}.lobby-user-card{background:linear-gradient(180deg,#fff,#f1f1f1);color:#2d3042;border:3px solid #ddd;border-radius:30px;padding:16px 13px 14px;box-shadow:0 12px 30px rgba(0,0,0,.35);position:relative;margin:48px 0 18px}.lobby-user-avatar{position:absolute;top:-76px;left:50%;transform:translateX(-50%);width:112px;height:112px;border-radius:50%;background:linear-gradient(145deg,#d4d4d4,#fff);border:4px solid #11c65b;box-shadow:0 0 0 4px rgba(255,255,255,.7),0 8px 25px rgba(0,0,0,.2);display:flex;align-items:center;justify-content:center;font-size:55px;text-decoration:none}.lobby-user-name{margin:70px auto 12px;max-width:340px;text-align:center;background:linear-gradient(180deg,#00d92f,#00a922);color:#fff;border-radius:999px;padding:5px 12px;font-size:23px;font-weight:1000;box-shadow:inset 0 2px 4px rgba(255,255,255,.4),0 4px 10px rgba(0,0,0,.2)}.lobby-stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.lobby-stat{background:#fff;border:3px solid #27c86a;border-radius:22px;padding:10px 4px;text-align:center;min-height:112px;display:flex;flex-direction:column;align-items:center;justify-content:center}.lobby-stat:nth-child(2){border-color:#b567ed}.lobby-stat:nth-child(3){border-color:#3d85e8}.lobby-stat .ico{font-size:38px;line-height:1}.lobby-stat b{font-size:26px;color:#303547}.lobby-stat span{color:#8b8e9b;font-size:13px}.lobby-bottom-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:12px}.lobby-bottom-actions a{border-radius:19px;padding:9px 5px;text-align:center;color:#fff;text-decoration:none;font-size:16px;font-weight:900;box-shadow:0 7px 0 rgba(0,0,0,.12),0 8px 18px rgba(0,0,0,.16);transition:.2s}.lobby-bottom-actions a:hover{transform:translateY(-3px)}.lobby-bottom-actions .green{background:linear-gradient(180deg,#77d52b,#43b91c)}.lobby-bottom-actions .purple{background:linear-gradient(180deg,#bd61ff,#9445df)}.lobby-bottom-actions .gold{background:linear-gradient(180deg,#ffd43b,#efaa00)}.mode-pill{display:block;width:max-content;max-width:90%;margin:18px auto -1px;padding:7px 22px;border-radius:999px;background:#16aee8;color:#fff;border:5px solid #fff;box-shadow:0 5px 18px rgba(0,0,0,.25);font-size:20px;font-weight:1000;position:relative;z-index:2}.mode-card{background:#fff;border:3px solid #ddd;border-radius:30px;padding:22px 15px 18px;color:#2d3042;box-shadow:0 12px 30px rgba(0,0,0,.3);margin-bottom:16px}.mode-card h2{color:#2e3142;font-size:25px;text-align:center;margin:0 0 8px}.mode-card p{color:#666b7b;text-align:center;margin:0 0 15px}.mode-actions{display:grid;grid-template-columns:1fr 1.7fr;gap:10px}.mode-actions a{display:flex;align-items:center;justify-content:center;border-radius:22px;padding:15px 8px;text-decoration:none;color:#fff;font-size:19px;font-weight:1000;box-shadow:0 6px 0 rgba(0,0,0,.12);transition:.2s}.mode-actions a:hover{transform:translateY(-3px)}.mode-actions .friends{background:linear-gradient(180deg,#88aef7,#5f8fe9)}.mode-actions .start4{background:linear-gradient(180deg,#8bd735,#4fbd1d)}.neon-bottom-nav{position:fixed;z-index:50;bottom:10px;left:50%;transform:translateX(-50%);width:min(94vw,760px);display:grid;grid-template-columns:repeat(4,1fr);gap:5px;background:rgba(18,10,43,.94);border:2px solid #a044ff;border-radius:24px;padding:7px;box-shadow:0 0 25px rgba(155,51,255,.55),0 12px 35px rgba(0,0,0,.45);backdrop-filter:blur(12px)}.neon-bottom-nav a{color:#fff;text-decoration:none;text-align:center;padding:6px 3px;border-radius:17px;font-size:12px;font-weight:900;transition:.2s}.neon-bottom-nav a span{display:block;font-size:25px;line-height:1.1}.neon-bottom-nav a:hover,.neon-bottom-nav a.active{background:linear-gradient(180deg,rgba(226,71,255,.28),rgba(103,54,255,.18));box-shadow:0 0 13px rgba(228,71,255,.25)}.mp-game{background:linear-gradient(145deg,#171033,#09071b);border:2px solid #7f35df;border-radius:28px;box-shadow:0 0 35px rgba(138,54,255,.18);overflow:hidden}.mp-head{padding:15px;text-align:center;background:linear-gradient(90deg,#38126e,#171039);border-bottom:1px solid #5d2aa1}.mp-head h1{margin:0;color:#fff}.mp-meta{display:flex;justify-content:space-between;gap:7px;flex-wrap:wrap;color:#b7afd2;font-size:12px}.mp-canvas{display:block;width:100%;height:auto;aspect-ratio:600/420;background:#fff;touch-action:none}.mp-options{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;padding:10px}.mp-options button{background:#27204a;color:#fff;border:1px solid #6045a1;border-radius:15px;padding:10px 14px;flex:0 1 auto}.mp-guess{display:flex;gap:8px;padding:10px}.mp-guess input{margin:0;flex:1}.mp-score{display:flex;gap:6px;overflow:auto;padding:8px}.mp-player{min-width:105px;background:#17132d;border:1px solid #3d3265;border-radius:13px;padding:6px;text-align:center;color:#d7d1ee}.mp-player.out{opacity:.35;text-decoration:line-through}.mp-result{padding:24px;text-align:center;animation:cardPop .3s ease}.coin-bar{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:10px 0}.coin-pill{padding:7px 12px;border-radius:999px;background:#18132f;border:1px solid #5733a2;color:#fff;font-weight:900}.store-item{padding:15px;border:1px solid #3e2a6f;border-radius:18px;background:linear-gradient(145deg,#211345,#100b27);margin-bottom:10px;display:flex;align-items:center;gap:10px}.store-item .grow{flex:1}.store-item .price{color:#ffd75b;font-weight:900}.invite-box{display:none!important}
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
/* === Neon redesign: lightweight, bright and mobile-first === */
body{background:#080b18;color:#f7f8ff}
.container{max-width:760px;padding:14px 12px 90px}
.auth-screen{min-height:calc(100vh - 28px);display:flex;align-items:center;justify-content:center;position:relative;padding:18px}
.auth-card{width:min(100%,440px);background:linear-gradient(155deg,#171b3c,#0e1026);border:1px solid rgba(255,255,255,.12);border-radius:28px;padding:28px 22px;box-shadow:0 18px 55px rgba(0,0,0,.45),0 0 35px rgba(89,63,255,.14);position:relative;z-index:2}
.auth-orb{position:absolute;width:150px;height:150px;border-radius:50%;display:grid;place-items:center;font-size:58px;background:linear-gradient(145deg,#ff4fc8,#704bff);box-shadow:0 0 55px rgba(255,79,200,.4);top:6%;right:8%;opacity:.9}
.auth-kicker,.settings-kicker,.profile-kicker,.lobby-kicker{font-size:11px;letter-spacing:2px;color:#9d91ff;font-weight:900}
.auth-card h1{font-size:28px;margin:6px 0}.auth-card p{margin:4px 0 18px}
.auth-card label,.settings-card label{display:block;margin:13px 0 7px;font-weight:800;color:#fff}
.auth-input{background:#090c1c!important;border-color:#30375f!important;border-radius:14px!important;padding:14px!important;margin-bottom:5px!important}
.field-hint{font-size:11px;color:#8f96b7;margin:5px 0 8px}.field-hint b{color:#d8d3ff}
.auth-submit{width:100%;margin-top:14px;border-radius:14px;background:linear-gradient(135deg,#ff4fca,#754cff);color:#fff;box-shadow:0 8px 24px rgba(117,76,255,.3)}
.auth-bottom{text-align:center!important;margin-top:18px!important}.auth-bottom a{color:#ff74d5;font-weight:900;text-decoration:none}

.lobby-bg{border-radius:30px;padding:14px 10px 105px;background:
radial-gradient(circle at 12% 3%,rgba(0,210,255,.24),transparent 25%),
radial-gradient(circle at 88% 8%,rgba(255,49,188,.25),transparent 27%),
radial-gradient(circle at 55% 70%,rgba(92,65,255,.18),transparent 35%),
linear-gradient(150deg,#101a3c 0%,#0d0a24 52%,#170d31 100%);
box-shadow:inset 0 0 70px rgba(0,0,0,.3),0 15px 45px rgba(0,0,0,.3)}
.lobby-topbar{display:flex;align-items:center;justify-content:space-between;padding:5px 7px 15px}
.lobby-title{font-size:27px;font-weight:1000;color:#fff;text-shadow:0 0 18px rgba(255,255,255,.22)}
.lobby-settings{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;text-decoration:none;color:#fff;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.13)}
.lobby-profile{display:flex;align-items:center;gap:12px;padding:13px;border-radius:22px;text-decoration:none;color:#fff;background:linear-gradient(135deg,rgba(35,40,86,.92),rgba(19,20,49,.92));border:1px solid rgba(139,116,255,.42);box-shadow:0 12px 30px rgba(0,0,0,.24),0 0 20px rgba(100,74,255,.1)}
.lobby-profile-avatar{width:62px;height:62px;border-radius:18px;overflow:hidden;display:grid;place-items:center;background:#11152d;border:2px solid #ff5ecb;box-shadow:0 0 18px rgba(255,94,203,.25);flex:none}
.lobby-profile-avatar>*{max-width:100%;max-height:100%}.lobby-profile-info{min-width:0;flex:1}.lobby-profile-name{font-size:20px;font-weight:1000;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lobby-profile-meta{font-size:11px;color:#aeb4d3;margin-top:4px}.lobby-profile-meta span{opacity:.5;margin:0 3px}.lobby-profile-arrow{font-size:30px;color:#bcaeff}
.lobby-wallet{margin:10px auto 18px;width:max-content;max-width:100%;padding:7px 15px;border-radius:999px;background:rgba(255,205,71,.1);border:1px solid rgba(255,205,71,.35);color:#ffe08a;font-size:13px}.lobby-wallet span{opacity:.4;margin:0 5px}
.section-heading{display:flex;align-items:end;justify-content:space-between;margin:0 4px 9px;color:#fff;font-weight:1000}.section-heading small{font-size:10px;color:#8f96b7;font-weight:600}
.game-mode-card{position:relative;min-height:108px;margin:9px 2px;padding:14px 12px 13px 76px;border-radius:19px;display:flex;align-items:center;gap:10px;border:1px solid rgba(255,255,255,.14);overflow:hidden;box-shadow:0 10px 24px rgba(0,0,0,.22)}
.game-mode-card::after{content:"";position:absolute;width:150px;height:150px;border-radius:50%;right:-90px;top:-80px;background:rgba(255,255,255,.1);pointer-events:none}
.mode-speed{background:linear-gradient(135deg,#132c55,#14204c)}.mode-draw{background:linear-gradient(135deg,#3a154f,#241947)}
.mode-badge{position:absolute;top:8px;right:10px;font-size:10px;font-weight:1000;padding:4px 8px;border-radius:999px;background:rgba(255,255,255,.1);color:#fff}.mode-icon{font-size:37px;flex:none}.mode-copy{min-width:0;flex:1}.mode-copy h2{font-size:18px;margin:15px 0 1px;color:#fff}.mode-copy p{font-size:10px;margin:0;color:#adb3d0}.mode-start{display:flex;align-items:center;gap:5px;text-decoration:none;color:#fff;background:linear-gradient(135deg,#6b5cff,#a348ff);border-radius:12px;padding:9px 10px;font-size:11px;font-weight:1000;box-shadow:0 5px 15px rgba(110,77,255,.24);z-index:1}.mode-speed .mode-start{background:linear-gradient(135deg,#12bfff,#476dff)}.mode-draw .mode-start{background:linear-gradient(135deg,#ff4fca,#a04bff)}
.lobby-quick-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:12px}.lobby-quick-grid a{min-width:0;text-decoration:none;color:#fff;background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.09);border-radius:15px;padding:10px 4px;text-align:center;font-size:19px}.lobby-quick-grid b,.lobby-quick-grid small{display:block}.lobby-quick-grid b{font-size:10px}.lobby-quick-grid small{font-size:8px;color:#8f96b7;margin-top:2px}

.profile-card{background:linear-gradient(150deg,#171b3c,#0c1024);border:1px solid #413a79;border-radius:25px;padding:20px;box-shadow:0 15px 45px rgba(0,0,0,.35),0 0 25px rgba(91,69,255,.12)}
.profile-head{display:flex;align-items:center;gap:14px}.profile-head>div:first-child{width:92px;height:92px;border-radius:50%;overflow:hidden;display:grid;place-items:center;background:#11152d;border:2px solid #ff5ccf}.profile-head>div:first-child img{max-width:100%;max-height:100%}.profile-head h1{font-size:24px;margin:3px 0}.profile-age{font-size:12px;color:#b8bdd5;margin-top:3px}.profile-bio{margin:18px 0;padding:13px;border-radius:15px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.08);color:#d9dcef;word-break:break-word}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}.stat-box{background:#11162e;border:1px solid #2d3561;border-radius:13px;padding:9px 3px;text-align:center;font-size:10px;color:#929ab9}.stat-box b{font-size:15px;color:#fff}.profile-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:15px}.profile-actions form{margin:0}.verified-support{display:inline-block;margin-top:5px;padding:3px 7px;border-radius:999px;background:rgba(0,216,255,.1);color:#63e6ff;font-size:10px}.support-mini-card{display:flex;flex-direction:column;margin-top:10px;padding:13px;border-radius:15px;text-decoration:none;color:#fff;background:#151a35;border:1px solid #343d72}.support-mini-card span{font-size:11px;color:#9ba3c2;margin-top:2px}

.settings-screen{min-height:calc(100vh - 28px);padding-bottom:25px}.settings-header{display:flex;align-items:center;gap:12px;padding:6px 3px 16px}.settings-header h1{margin:0;font-size:27px}.settings-gear{margin-right:auto;width:45px;height:45px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(135deg,#ff43c8,#704bff);box-shadow:0 0 20px rgba(255,67,200,.25)}.settings-close{width:45px;height:45px;border-radius:50%;display:grid;place-items:center;text-decoration:none;background:#e9ebf2;color:#252a3d;font-size:30px}
.settings-card{background:linear-gradient(150deg,#171b3c,#0d1025);border:1px solid #343b67;border-radius:23px;padding:18px;margin-bottom:12px;box-shadow:0 12px 30px rgba(0,0,0,.25)}
.settings-avatar-row{display:flex;align-items:center;gap:13px}.settings-avatar{width:86px;height:86px;border-radius:21px;overflow:hidden;display:grid;place-items:center;background:#0a0d1d;border:2px solid #10d6ff;flex:none}.settings-avatar p,.settings-avatar-row p{font-size:10px;color:#9299b8;margin:3px 0 0}.avatar-crop-wrap{position:relative;width:86px;height:86px;overflow:hidden;border-radius:19px}.avatar-crop-wrap img{position:absolute;max-width:none}.file-input{width:100%;margin:12px 0 6px;padding:10px;border-radius:12px;background:#0a0d1d;color:#b8bed7;border:1px solid #2c345a}
.zoom-row{display:flex;align-items:center;gap:9px;color:#9fa7c5}.zoom-row input{flex:1;accent-color:#ff55cc}.age-row{display:flex;align-items:center;gap:8px}.age-row input{width:100%;margin:0!important;background:#090c1c!important;border-color:#30375f!important}.age-row span{color:#aab1cb;white-space:nowrap}
.settings-card textarea{width:100%;min-height:92px;resize:none;padding:12px;border-radius:13px;background:#090c1c;color:#fff;border:1px solid #30375f;font-family:inherit}.char-counter{text-align:left;direction:ltr;color:#777f9f;font-size:10px;margin-top:3px}.settings-save{width:100%;margin-top:10px;background:linear-gradient(135deg,#00c8ff,#5b5cff);color:#fff}.settings-note{text-align:center;color:#7f88a8;font-size:11px;margin:14px 0}.settings-links{display:flex;justify-content:center;gap:8px}.settings-links a{color:#fff;text-decoration:none;background:#171b37;border:1px solid #343d6c;border-radius:12px;padding:8px 15px;font-size:12px}

.neon-bottom-nav{background:rgba(10,10,28,.97);border-color:#704cff;box-shadow:0 0 22px rgba(112,76,255,.32),0 12px 35px rgba(0,0,0,.45)}
button,.btn{transition:transform .12s ease,filter .12s ease}.btn:hover,button:hover{transform:translateY(-1px);filter:brightness(1.08)}
@media(max-width:600px){.container{padding:8px 8px 86px}.auth-orb{width:110px;height:110px;font-size:42px;top:3%;right:2%}.auth-card{padding:23px 17px}.lobby-title{font-size:24px}.game-mode-card{min-height:102px;padding-left:67px}.mode-icon{font-size:31px}.mode-copy h2{font-size:16px}.mode-start{padding:8px 9px}.lobby-quick-grid{grid-template-columns:repeat(2,1fr)}.stat-grid{grid-template-columns:repeat(2,1fr)}}
@media(prefers-reduced-motion:reduce){.page-enter,.glow-btn,.btn,button{animation:none!important;transition:none!important}}

"""

def _bottom_nav(active="home", username=None):
    items=[("leaderboard","🏆","لیدر بورد"),("messages","💬","گفتگوها"),("shop","🛍️","فروشگاه"),("settings","⚙️","تنظیمات")]
    if username == "morad": items.append(("support","🛡️","پشتیبانی"))
    return '<div class="neon-bottom-nav">'+''.join(f'<a class="{("active" if active==k else "")}" href="/{k}"><span>{ic}</span>{title}</a>' for k,ic,title in items)+'</div>'

def lobby_page(username, prof=None, wallet=None):
    prof = prof or {"username": username, "bio": "", "avatar": "", "age": 18, "wins": 0, "points": 0}
    wallet = wallet or {"coins": 0}
    banned=bool(prof.get("profile_banned")); avatar_html = '<div class="avatar-hidden">●</div>' if banned else _avatar_html(prof.get("avatar") or "")
    age=int(prof.get("age") or 18); wins=int(prof.get("wins") or 0); points=int(prof.get("points") or 0); coins=int(wallet.get("coins") or 0)
    profile_open = f'<a class="lobby-profile hero" href="/profile?u={quote(username,safe="")}">' if not banned else '<div class="lobby-profile hero">'
    profile_close = '</a>' if not banned else '</div>'
    profile_hint = 'مشاهده پروفایل' if not banned else 'پروفایل موقتاً محدود شده'
    quick_profile = f'<a href="/profile?u={quote(username,safe="")}">👤 <b>پروفایل من</b><small>مشاهده پروفایل</small></a>' if not banned else '<div class="lobby-quick-grid-placeholder">🔒 <b>پروفایل محدود</b><small>موقتاً غیرفعال</small></div>'
    support_link = '<a href="/support">🛡️ <b>پنل پشتیبانی</b><small>مدیریت گزارش‌ها</small></a>' if username=='morad' else ''
    body=f'''<div class="lobby-bg page-enter">
      <div class="lobby-topbar"><div><div class="lobby-kicker">DRAW BATTLE • ONLINE</div><div class="lobby-title">تخته گچی ⚡</div></div><div style="display:flex;gap:7px;align-items:center"><a class="lobby-settings" href="/settings">⚙️</a>{('<a class=\"lobby-settings\" href=\"/support\">🛡️</a>' if username=='morad' else '')}</div></div>
      {profile_open}<div class="lobby-profile-avatar">{avatar_html}</div><div class="lobby-profile-info"><div class="lobby-profile-name">@{html.escape(username)}</div><div class="lobby-profile-meta">🎂 {age} سال <span>•</span> 🏆 {wins} جام <span>•</span> 💎 {points} امتیاز</div><div class="lobby-profile-meta">{profile_hint}</div></div><div class="lobby-profile-arrow">‹</div>{profile_close}
      <div class="lobby-wallet">💰 <b>{coins:,}</b> سکه <span>•</span> آماده‌ی رقابتی؟</div>
      <button class="notification-bell" onclick="toggleNotifications()">🔔 <span id="notifCount">0</span></button><div id="notificationPanel" class="notification-panel"><div class="notification-head"><b>🔔 اعلان‌ها</b><button onclick="markNotifsRead()">خوانده شد</button></div><div id="notificationList"><div class="pinned-empty">در حال دریافت اعلان‌ها...</div></div></div>
      <div class="section-heading"><span>🎮 حالت‌های بازی</span><small>یک حالت را انتخاب کن</small></div>
      <div class="game-mode-card mode-speed"><div class="mode-badge">⚡ دو نفره سرعتی</div><div class="mode-icon">🎨</div><div class="mode-copy"><h2>حدس نقاشی</h2><p>۲ بازیکن • نقاشی و حدس سریع</p></div><a class="mode-start" href="/game/drawing">شروع <span>←</span></a></div>
      <div class="game-mode-card mode-draw"><div class="mode-badge">🎨 رقابت نقاشان</div><div class="mode-icon">🖌️</div><div class="mode-copy"><h2>نقاشی ۴ نفره</h2><p>۴ بازیکن • نقاشی و حدس</p></div><a class="mode-start" href="/game/drawing4">شروع <span>←</span></a></div>
      <div class="lobby-quick-grid"><a href="/chat/public">💬 <b>چت عمومی</b><small>گپ با همه</small></a><a href="/leaderboard">🏆 <b>رتبه‌بندی</b><small>بهترین‌ها</small></a><a href="/shop">🛍️ <b>فروشگاه</b><small>آیتم‌ها</small></a>{quick_profile}{support_link}</div>
    </div><script>async function loadNotifications(){{try{{const r=await fetch('/notifications');const d=await r.json();const all=[...(d.notifications||[])];(d.friend_requests||[]).forEach(x=>all.unshift({{title:'درخواست دوستی جدید',content:'@'+x.sender+' برای شما درخواست دوستی فرستاد.',read:0}}));document.getElementById('notificationList').innerHTML=all.length?all.slice(0,30).map(n=>`<div class="notification-item ${{n.read?'':'unread'}}"><b>${{n.title||'اعلان'}}</b><span>${{n.content||''}}</span></div>`).join(''):'<div class="pinned-empty">اعلان جدیدی نداری.</div>';document.getElementById('notifCount').textContent=d.count||0}}catch(e){{}}}}function toggleNotifications(){{document.getElementById('notificationPanel').classList.toggle('show');loadNotifications()}}async function markNotifsRead(){{await fetch('/notifications/read',{{method:'POST'}});loadNotifications()}}loadNotifications();setInterval(loadNotifications,5000);</script>{{_bottom_nav("home", username)}}'''
    return page_shell('منوی اصلی',body,username)

def games_page(username):
    body=f"""<div class=\"lobby-bg page-enter\"><div class=\"section-heading\"><span>🎮 حالت‌های بازی</span><small>دو حالت، یک رقابت</small></div><div class=\"game-mode-card mode-speed\"><div class=\"mode-badge\">⚡ دو نفره سرعتی</div><div class=\"mode-icon\">🎨</div><div class=\"mode-copy\"><h2>حدس نقاشی</h2><p>۲ بازیکن • نقاشی و حدس سریع</p></div><a class=\"mode-start\" href=\"/game/drawing\">شروع <span>←</span></a></div><div class=\"game-mode-card mode-draw\"><div class=\"mode-badge\">🎨 رقابت نقاشان</div><div class=\"mode-icon\">🖌️</div><div class=\"mode-copy\"><h2>نقاشی ۴ نفره</h2><p>۴ بازیکن • نقاشی و حدس</p></div><a class=\"mode-start\" href=\"/game/drawing4\">شروع <span>←</span></a></div><a class=\"btn\" href=\"/lobby\">← بازگشت به لابی</a></div>{_bottom_nav("home")}"""
    return page_shell('انتخاب بازی',body,username)

def multiplayer_drawing_page(username, mode):
    return _drawing_battle_page(username, 4)


def shop_page(username, wallet=None):
    w=wallet or {'coins':500,'diamonds':5,'streak':0};
    items=[
      ('neon_pen','✏️','قلم نئونی','خط درخشان برای نقاشی','250','custom'),('profile_frame','🖼️','قاب درخشان','قاب متحرک و جذاب پروفایل','400','custom'),('victory_fx','✨','افکت پیروزی','افکت ویژه پایان دور','650','custom'),('crown_badge','👑','نشان تاج','نشان ویژه کنار نام','900','custom'),('chat_bubble','💬','حباب چت','استایل ویژه پیام‌های تو','300','custom'),('name_effect','🌟','افکت نام','درخشش نام کاربری','500','custom'),('draw_glow','🖌️','قلم نورانی','افکت ویژه قلم نقاش','450','custom'),
      ('bronze_frame','🥉','قاب برنزی','ویژه لیگ برنزی • ۲۵۰ جام','550','league'),('bronze_badge','🏅','نشان برنزی','نشان اختصاصی لیگ برنزی','350','league'),('davinci_frame','🔷','قاب داوینچی','ویژه لیگ داوینچی • ۷۵۰ جام','1100','league'),('davinci_effect','💠','افکت داوینچی','افکت اختصاصی لیگ داوینچی','900','league'),('picasso_frame','🔴','قاب پیکاسو','ویژه لیگ پیکاسو • ۱۵۰۰ جام','1800','league'),('picasso_effect','🎨','افکت پیکاسو','افکت اختصاصی لیگ پیکاسو','1500','league')]
    cards=''.join(f'''<div class="store-item store-custom"><div class="store-item-icon">{ic}</div><div class="grow"><b>{name}</b><div class="store-desc">{desc}</div></div><span class="price">{cost} 🪙</span><button onclick="buy('{key}',{cost})">خرید</button></div>''' for key,ic,name,desc,cost,_ in items[:7])
    league_cards=''.join(f'''<div class="store-item store-league"><div class="store-item-icon">{ic}</div><div class="grow"><b>{name}</b><div class="store-desc">{desc}</div></div><span class="price">{cost} 🪙</span><button onclick="buy('{key}',{cost})">خرید</button></div>''' for key,ic,name,desc,cost,_ in items[7:])
    body=f'''<div class="page-heading"><div><div class="sub">ARCADE STORE • CUSTOMIZE</div><h1>🛍️ فروشگاه</h1></div><a class="btn" href="/lobby">خانه</a></div><div class="card hero page-enter"><div class="coin-bar"><span class="coin-pill">🪙 {w.get('coins',500)} سکه</span><span class="coin-pill">💎 {w.get('diamonds',5)} الماس</span><span class="coin-pill">🔥 روزهای متوالی {w.get('streak',0)}</span></div><button class="glow-btn" onclick="claimDaily()">🎁 جایزه روزانه</button><div id="dailyStatus" class="status-line"></div></div><div class="card coin-pack-card"><div class="coin-pack-icon">🪙</div><div><div class="sub">COIN PACK</div><h2>۱۰۰۰ سکه</h2><p>قیمت: <b>۱۰۰٬۰۰۰ تومان</b></p></div><div class="coin-pack-cardnum">💳 ۶۲۱۹۸۶۱۸۵۱۱۶۰۰۶۸</div><div class="coin-pack-steps">۱ مبلغ را واریز کن • ۲ رسید را در پیوی پشتیبانی ارسال کن</div><a class="glow-btn receipt-shop-btn" href="/chat/private/morad">🧾 ارسال رسید به پشتیبانی</a></div><div class="card"><h2>🎨 شخصی‌سازی</h2><p class="store-section-note">همه آیتم‌ها با 🪙 سکه خریداری می‌شوند و بعد از خرید روی حساب تو باقی می‌مانند.</p>{cards}</div><div class="card"><h2>🏆 آیتم‌های مخصوص لیگ</h2><p class="store-section-note">این آیتم‌ها فقط با رسیدن به لیگ مربوطه قابل خرید هستند؛ خرید به‌تنهایی لیگ را باز نمی‌کند.</p>{league_cards}</div><div style="text-align:center"><a class="btn" href="/lobby">← بازگشت</a></div><script>async function claimDaily(){{const d=await(await fetch('/daily/claim',{{method:'POST'}})).json();document.getElementById('dailyStatus').textContent=d.message;if(d.ok)setTimeout(()=>location.reload(),700)}}async function buy(key,cost){{const d=await(await fetch('/shop/buy',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{item_key:key,cost}})}})).json();if(d.ok){{alert('✨ خرید موفق بود!');location.reload()}}else if(d.status==='owned')alert('این آیتم را قبلاً داری.');else if(d.status==='league_locked')alert('🏆 این آیتم مخصوص لیگ بالاتر است.');else if(d.status==='not_enough')alert('🪙 سکه کافی نیست.');else alert('❌ خرید انجام نشد.')}} </script>'''
    return page_shell('فروشگاه',body,username)


def chat_private_page(username, other, messages):
    body=f'''<div class="chat-screen page-enter"><div class="chat-top"><div class="chat-toolbar"><div class="chat-title">💬 @{html.escape(other)} <span id="presenceDot" style="font-size:10px;color:#888">● بررسی...</span></div><a class="btn" href="/messages">پیام‌ها</a></div></div><div class="chat-box" id="chatBox">{_render_messages(messages,username,False)}</div><div class="chat-input-wrap"><div class="chat-input-row"><input type="text" id="msgInput" placeholder="پیامت رو بنوی..." autocomplete="off"><button class="send-btn" onclick="sendMsg()">➤</button></div></div></div><script>const wsProto=location.protocol==='https:'?'wss:':'ws:',ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/private/{quote(other,safe="")}'),box=document.getElementById('chatBox'),me={username!r},dot=document.getElementById('presenceDot');async function presence(){{try{{const d=await (await fetch('/presence/'+encodeURIComponent({other!r}))).json();dot.textContent=d.online?'● آنلاین':'● آفلاین';dot.style.color=d.online?'#35df7a':'#888'}}catch(e){{dot.textContent='● نامشخص'}}}}function addMsg(d){{if(d.content===undefined)return;const div=document.createElement('div');div.className='msg '+(d.sender===me?'me':'');const ss=document.createElement('span');ss.className='sender';ss.textContent=d.sender;const c=document.createElement('span');c.className='content';c.textContent=d.content;div.append(ss,c);if(d.sender!==me){{const b=document.createElement('button');b.className='report-btn';b.textContent='🚩 گزارش';b.onclick=()=>openReportModal(d.sender,d.content,'chat','');div.append(b)}}box.appendChild(div);box.scrollTop=box.scrollHeight}}ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.content!==undefined)addMsg(d)}};function sendMsg(){{const i=document.getElementById('msgInput'),v=i.value.trim();if(!v||ws.readyState!==1)return;ws.send(JSON.stringify({{content:v}}));i.value=''}}document.getElementById('msgInput').addEventListener('keydown',e=>{{if(e.key==='Enter')sendMsg()}});presence();setInterval(presence,4000);box.scrollTop=box.scrollHeight;</script>'''
    return page_shell(f'چت با {other}',body,username)


BASE_CSS += """
/* FINAL UI PATCH */
body{background:radial-gradient(circle at 10% 0%,rgba(0,229,255,.20),transparent 26%),radial-gradient(circle at 90% 0%,rgba(255,45,190,.20),transparent 28%),linear-gradient(180deg,#070b1d,#0b0820 55%,#090615);}
.lobby-bg{position:relative;overflow:hidden;background:radial-gradient(circle at 8% 0%,rgba(0,229,255,.32),transparent 24%),radial-gradient(circle at 92% 3%,rgba(255,55,198,.32),transparent 25%),radial-gradient(circle at 50% 52%,rgba(108,76,255,.23),transparent 38%),linear-gradient(145deg,#071b38 0%,#10072b 48%,#22072f 100%);box-shadow:inset 0 0 55px rgba(0,0,0,.35),0 18px 50px rgba(0,0,0,.28)}
.game-mode-card{min-height:88px;margin:10px 2px;padding:12px 12px 11px 66px;border-radius:14px;border:1px solid rgba(255,255,255,.20);box-shadow:0 8px 18px rgba(0,0,0,.20),0 0 18px rgba(74,108,255,.10);backdrop-filter:none}
.game-mode-card::after{width:110px;height:110px;right:-68px;top:-60px;background:rgba(255,255,255,.08)}
.mode-speed{background:linear-gradient(135deg,#0c4b73,#182b62)}.mode-draw{background:linear-gradient(135deg,#65205d,#30215f)}
.mode-badge{top:7px;right:8px;font-size:9px;padding:3px 7px;background:rgba(255,255,255,.13)}.mode-icon{font-size:30px}.mode-copy h2{font-size:16px;margin:13px 0 1px}.mode-copy p{font-size:9px}.mode-start{border-radius:10px;padding:8px 10px;font-size:10px;box-shadow:0 4px 12px rgba(0,0,0,.18)}
.mode-speed .mode-start{background:linear-gradient(135deg,#00d9ff,#386bff);box-shadow:0 0 14px rgba(0,217,255,.22)}.mode-draw .mode-start{background:linear-gradient(135deg,#ff43c8,#8b50ff);box-shadow:0 0 14px rgba(255,67,200,.20)}
.lobby-profile{background:linear-gradient(135deg,rgba(17,54,94,.94),rgba(38,14,66,.94));border-color:rgba(71,220,255,.35);box-shadow:0 10px 24px rgba(0,0,0,.20),0 0 20px rgba(0,220,255,.08)}.lobby-profile-avatar{border-color:#00dcff;box-shadow:0 0 16px rgba(0,220,255,.22)}
.avatar-editor{display:flex;gap:18px;align-items:center;flex-wrap:wrap}.avatar-crop-wrap{position:relative;width:190px;height:190px;flex:0 0 190px;overflow:hidden;border-radius:50%;background:#080b18;border:3px solid #19ddff;box-shadow:0 0 0 4px rgba(25,221,255,.08),0 0 28px rgba(25,221,255,.18);touch-action:none;cursor:grab}.avatar-crop-wrap:active{cursor:grabbing}.avatar-crop-wrap img{position:absolute;max-width:none;user-select:none;-webkit-user-drag:none;pointer-events:none}.avatar-crop-wrap .avatar-big{width:100%;height:100%;display:grid;place-items:center;font-size:72px}.avatar-controls{min-width:180px;flex:1}.upload-btn{display:block!important;text-align:center;padding:11px 14px;border-radius:12px;background:linear-gradient(135deg,#00c8ff,#7251ff);cursor:pointer;box-shadow:0 0 18px rgba(0,200,255,.16)}.file-input-hidden{display:none!important}.crop-label{font-size:10px;color:#929ab9;margin:9px 0}.crop-reset{width:100%;margin-top:8px!important;background:#161d3a!important;border:1px solid #36416d!important;color:#fff!important}.settings-select{width:100%;margin:0!important;background:#090c1c!important;color:#fff!important;border:1px solid #30375f!important;border-radius:13px!important;padding:13px!important;font-family:inherit}.profile-editor-card{border-color:rgba(0,214,255,.28);box-shadow:0 12px 34px rgba(0,0,0,.28),0 0 25px rgba(0,214,255,.06)}.profile-editor-title p{font-size:10px;color:#9299b8;margin:4px 0 12px}.settings-save:disabled{opacity:.65;transform:none!important}
@media(max-width:600px){.game-mode-card{min-height:84px;padding-left:60px;border-radius:13px}.mode-icon{font-size:27px}.mode-copy h2{font-size:15px}.mode-start{padding:7px 8px}.mode-badge{font-size:8px}.avatar-editor{justify-content:center}.avatar-controls{width:100%}.avatar-crop-wrap{width:180px;height:180px;flex-basis:180px}.lobby-quick-grid{gap:6px}}
"""

BASE_CSS += """
/* V3 */
body *{backdrop-filter:none!important}
.profile-head>div:first-child{width:92px;height:92px;border-radius:50%!important;overflow:hidden;display:grid;place-items:center;background:#080b18;border:3px solid #ff5ccf;box-shadow:0 0 0 3px rgba(255,92,207,.10),0 0 24px rgba(0,214,255,.18)}
.profile-head>div:first-child img,.profile-avatar-img{width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;object-fit:cover;border-radius:50%!important;display:block}.profile-head>div:first-child .avatar-big{width:100%;height:100%;border-radius:50%;display:grid;place-items:center;font-size:48px}.avatar-hidden{width:100%;height:100%;border-radius:50%;display:grid;place-items:center;background:#17132d;color:#ff74c8;font-size:34px}.moderation-hidden{padding:10px 12px;border-radius:12px;background:rgba(255,70,160,.07);border:1px solid rgba(255,70,160,.18);color:#b8b0d0}
.report-modal{position:fixed;inset:0;z-index:9999;background:rgba(3,4,14,.78);display:none;align-items:center;justify-content:center;padding:16px}.report-modal.show{display:flex}.report-modal-card{width:min(100%,430px);background:linear-gradient(145deg,#1c1041,#0d0a24);border:2px solid #ff4fd8;border-radius:24px;padding:18px;box-shadow:0 0 40px rgba(255,60,205,.28),0 18px 60px rgba(0,0,0,.45);position:relative}.report-modal-close{position:absolute;left:12px;top:12px;width:38px;height:38px;padding:0;border-radius:50%;background:#252043;color:#fff}.report-modal-title{font-size:21px;font-weight:950;color:#fff}.report-modal-sub{font-size:12px;color:#aaa4c2;margin:5px 0 12px}.report-reasons{display:grid;grid-template-columns:1fr 1fr;gap:8px}.report-reasons button{padding:11px 8px;border-radius:13px;background:#17112f;border:1px solid #463273;color:#fff;font-size:12px}.report-reasons button:hover{border-color:#ff4fd8;box-shadow:0 0 12px rgba(255,79,216,.18)}#reportExtra{width:100%;min-height:72px;margin:10px 0;padding:10px;border-radius:12px;background:#0a0a1a;color:#fff;border:1px solid #38305a;font-family:inherit}.report-modal-hint{font-size:10px;color:#8883a5;text-align:center}.report-category{display:inline-block;padding:2px 7px;border-radius:999px;background:rgba(255,79,216,.12);color:#ff8de5;font-size:10px}.report-image{max-width:100%;border-radius:14px;display:block;margin:8px 0;border:1px solid #403368}.support-action-grid,.support-direct-grid{display:grid;grid-template-columns:1.3fr .7fr .7fr 1fr;gap:7px;align-items:center}.support-direct-grid{grid-template-columns:1.5fr 1.2fr .7fr .7fr;margin-bottom:9px}.support-action-grid input,.support-action-grid select,.support-direct-grid input,.support-direct-grid select{margin:0!important;width:100%;background:#0d0b22;color:#fff;border:1px solid #3b315b;border-radius:11px;padding:10px;font-family:inherit}.leader-podium{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;align-items:end;margin:14px 0 20px}.leader-podium-card{position:relative;text-decoration:none;color:#fff;text-align:center;border-radius:26px;padding:18px 8px 14px;background:linear-gradient(145deg,#21104c,#0d0a23);border:2px solid #6c36cf;box-shadow:0 0 22px rgba(130,50,255,.22);transition:.2s}.leader-podium-card.rank-1{transform:scale(1.08);border-color:#ff4fd8;box-shadow:0 0 32px rgba(255,79,216,.42),0 0 60px rgba(100,55,255,.22);z-index:2}.leader-podium-card.rank-2{transform:scale(1.02);border-color:#65d9ff;box-shadow:0 0 26px rgba(101,217,255,.30)}.leader-podium-card.rank-3{border-color:#a986ff}.leader-rank{font-size:25px;margin-bottom:6px}.leader-podium-card .leader-avatar{width:82px;height:82px;margin:auto;border-radius:50%;object-fit:cover;border:3px solid #fff;box-shadow:0 0 18px rgba(255,255,255,.22);display:block}.leader-podium-card.rank-1 .leader-avatar{width:104px;height:104px;border-color:#ff8be5;box-shadow:0 0 25px rgba(255,79,216,.55)}.leader-name{font-weight:950;font-size:14px;margin-top:7px;overflow:hidden;text-overflow:ellipsis}.leader-age{font-size:10px;color:#aaa5c4}.leader-score{font-size:11px;color:#67e8ff;margin-top:4px}.leader-list{display:grid;gap:6px}.leader-row{display:grid!important;grid-template-columns:38px 34px 1fr auto;align-items:center;gap:7px;padding:9px!important;text-decoration:none;color:#fff}.leader-list-avatar .leader-avatar{width:34px;height:34px;border-radius:50%;object-fit:cover;border:1px solid #6c55b0}.ban-row{padding:11px;border:1px solid #3a2d60;border-radius:14px;margin:7px 0;background:#100c25}.ban-scope-tag{font-size:10px;padding:3px 7px;border-radius:999px;background:#241640;color:#ff8de5}.lobby-profile-avatar,.lobby-avatar{border-radius:50%!important;overflow:hidden}.lobby-profile-avatar .profile-avatar-img,.lobby-profile-avatar img{width:100%;height:100%;object-fit:cover;border-radius:50%}.game-mode-card{width:min(100%,650px);margin:9px auto;min-height:76px;padding:10px 12px 10px 62px;border-radius:18px!important}.mode-copy h2{font-size:15px}.mode-copy p{font-size:9px}.mode-start{font-size:10px;padding:7px 10px}.lobby-bg{box-shadow:inset 0 0 80px rgba(0,220,255,.10),inset 0 0 120px rgba(255,50,210,.08)}
@media(max-width:600px){.leader-podium{gap:6px}.leader-podium-card{padding:13px 5px}.leader-podium-card.rank-1 .leader-avatar{width:82px;height:82px}.leader-podium-card .leader-avatar{width:64px;height:64px}.support-action-grid,.support-direct-grid{grid-template-columns:1fr 1fr}.support-action-grid button{grid-column:1/-1}.report-reasons{grid-template-columns:1fr}.profile-head>div:first-child{width:84px;height:84px}}
"""

BASE_CSS += """
.notification-bell{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;margin:10px 0;padding:10px 14px;border-radius:16px;background:linear-gradient(135deg,#271052,#112d59);color:#fff;border:1px solid #6d48d8;box-shadow:0 0 18px rgba(114,70,255,.18)}.notification-bell span{min-width:22px;height:22px;border-radius:50%;display:inline-grid;place-items:center;background:#ff3fb9;font-size:11px}.notification-panel{display:none;margin:0 0 12px;border:1px solid #51358e;border-radius:18px;background:#0e0b21;box-shadow:0 0 28px rgba(125,60,255,.18);overflow:hidden}.notification-panel.show{display:block}.notification-head{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-bottom:1px solid #29234a}.notification-head button{padding:6px 9px;font-size:10px;background:#25204a;color:#fff}.notification-item{padding:10px 12px;border-bottom:1px solid #201c39;display:flex;flex-direction:column;gap:2px}.notification-item b{color:#fff;font-size:12px}.notification-item span{color:#aaa7c4;font-size:11px}.notification-item.unread{background:rgba(255,65,190,.06);border-right:3px solid #ff4fbf}.support-tag{display:inline-block;margin:4px 3px 0 0;padding:4px 9px;border-radius:999px;background:linear-gradient(90deg,#ff43c8,#7658ff);color:#fff;font-size:10px;font-weight:900;box-shadow:0 0 12px rgba(255,67,200,.25)}.support-tags{margin-top:5px}.report-user-main{background:linear-gradient(135deg,#ff416c,#b721ff)!important;color:#fff!important}.pin-btn{margin-inline-start:6px;padding:3px 7px;border-radius:7px;background:rgba(100,82,255,.12);border:1px solid #5b4bb1;color:#aaa1ff;font-size:10px}.pinned-box{display:flex;gap:6px;overflow:auto;padding-top:8px}.pinned-item{white-space:nowrap;padding:6px 9px;border-radius:10px;background:#1b1434;border:1px solid #45317b;color:#d7d0ff;font-size:11px}.pinned-empty{opacity:.55;text-align:center;padding:10px;font-size:11px}
.leader-tabs{display:flex;gap:8px;margin-bottom:14px}.leader-tab{flex:1;text-align:center;padding:10px 8px;border-radius:14px;text-decoration:none;font-size:13px;font-weight:900;color:#c9c4e6;background:#171339;border:1px solid #372c66}.leader-tab.active{color:#fff;background:linear-gradient(135deg,#ff43c8,#7658ff);border-color:transparent;box-shadow:0 0 16px rgba(255,67,200,.3)}
"""

BASE_CSS += """
/* DRAW BATTLE + PAYMENT + SUPPORT V4 */
.draw-battle{max-width:900px;margin:0 auto;background:linear-gradient(145deg,#11092a,#070615);border:1px solid #6b2bd6;border-radius:30px;padding:12px;box-shadow:0 0 45px rgba(133,48,255,.18),0 22px 70px rgba(0,0,0,.45);overflow:hidden}.draw-hero{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:17px;border-radius:23px;background:radial-gradient(circle at 15% 0,rgba(0,218,255,.24),transparent 35%),linear-gradient(135deg,#25105d,#100822);border:1px solid #7043d6}.draw-kicker{font-size:10px;letter-spacing:2px;color:#67eaff}.draw-hero h1{margin:3px 0;color:#fff;font-size:25px}.draw-status{font-size:11px;color:#aaa6c4}.draw-mode-badge{padding:8px 12px;border-radius:999px;background:linear-gradient(135deg,#ff42c8,#6b4cff);color:#fff;font-weight:900;box-shadow:0 0 18px rgba(255,66,200,.25)}.draw-players-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:8px;margin:10px 0}.draw-player-card{position:relative;display:flex;align-items:center;gap:8px;padding:9px;border-radius:17px;background:linear-gradient(145deg,#1a1238,#0e0a22);border:1px solid #38266c;transition:.2s}.draw-player-card.me{border-color:#16d9ff;box-shadow:0 0 16px rgba(22,217,255,.12)}.draw-player-card.turn{border-color:#ff48cb;box-shadow:0 0 20px rgba(255,72,203,.18)}.draw-player-card.out{opacity:.4}.draw-player-main{display:flex;align-items:center;gap:8px;min-width:0;flex:1;color:#fff;text-decoration:none}.draw-avatar{width:43px;height:43px;flex:0 0 43px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#26305e,#11142a);border:2px solid #7650ff;overflow:hidden;font-size:23px}.draw-avatar img{width:100%;height:100%;object-fit:cover}.draw-player-info{min-width:0;display:flex;flex-direction:column}.draw-player-info b{font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.draw-player-info span{font-size:9px;color:#8783a7}.draw-player-main strong{margin-right:auto;color:#ffd95c;font-size:11px;white-space:nowrap}.draw-role{position:absolute;left:7px;top:5px;font-size:8px;color:#9f96ca}.draw-round-info{display:flex;justify-content:space-between;align-items:center;padding:9px 12px;margin-bottom:8px;border-radius:14px;background:#0e0b22;border:1px solid #33215e;color:#fff;font-weight:900}.draw-timer{color:#6de9ff;font-variant-numeric:tabular-nums}.draw-preview{min-height:250px;margin:10px 0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border-radius:25px;background:radial-gradient(circle at 50% 35%,rgba(255,75,207,.22),transparent 30%),linear-gradient(145deg,#211047,#0c0820);border:2px solid #8d37e8;box-shadow:inset 0 0 40px rgba(118,35,255,.18),0 0 30px rgba(255,57,210,.13)}.preview-orb{width:65px;height:65px;border-radius:50%;display:grid;place-items:center;font-size:31px;background:radial-gradient(circle,#ff6bdd,#7139ff);box-shadow:0 0 28px rgba(255,82,221,.45);animation:previewPulse 1s infinite}.preview-title{font-size:25px;font-weight:1000;color:#fff;margin-top:10px}.draw-preview #previewText{font-size:15px;color:#b9b1d8;margin:5px 0}.preview-count{font-size:40px;font-weight:1000;color:#67eaff;text-shadow:0 0 18px rgba(103,234,255,.5)}.draw-preview.drawer-preview #previewText{color:#ff86dc;font-weight:900}.draw-board-frame{padding:8px;border-radius:22px;background:linear-gradient(145deg,#291057,#0b0820);border:1px solid #6f35c8;box-shadow:0 0 30px rgba(105,42,232,.15)}.draw-board-top{display:flex;justify-content:space-between;padding:7px 9px;color:#fff;font-size:11px}.draw-canvas-wrap{border-radius:16px;overflow:hidden}.draw-canvas-wrap canvas{display:block;width:100%;height:auto;background:#fff;touch-action:none}.draw-palette{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;padding:10px}.draw-swatch{width:28px;height:28px;border-radius:50%;border:2px solid #fff3;cursor:pointer;box-shadow:0 0 0 0 transparent;transition:.15s}.draw-swatch.active{box-shadow:0 0 0 3px #ff53d3,0 0 12px #ff53d3;transform:scale(1.12)}.draw-tools{display:flex;align-items:center;gap:7px;flex-wrap:wrap;padding:8px;background:#0d0920;border:1px solid #2e2054;border-radius:15px;margin-bottom:8px}.draw-tool{padding:8px 10px;border-radius:10px;background:#18112e;color:#fff;border:1px solid #3c2a6b}.draw-tool.active{border-color:#ff50d0;box-shadow:0 0 12px rgba(255,80,208,.2)}.draw-size-slider-wrap{display:flex;align-items:center;gap:8px;flex:1;min-width:170px}.draw-size-slider-wrap input{flex:1}.draw-size-label,.draw-size-value{font-size:10px;color:#aaa3c4}.draw-word-box{margin:8px 0;padding:12px;border-radius:15px;text-align:center;background:linear-gradient(135deg,#ff3dbb,#6b49ff);color:#fff;font-weight:1000;box-shadow:0 0 18px rgba(255,61,187,.2)}.draw-options{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;padding:8px}.draw-option-btn{padding:10px 14px;border-radius:14px;background:#17112f;color:#fff;border:1px solid #4a3181;font-weight:800}.draw-option-btn.wrong{opacity:.45;text-decoration:line-through}.draw-guess-box{display:flex;gap:7px;padding:8px}.draw-guess-box input{margin:0!important;flex:1}.draw-guess-box button{border-radius:13px;background:linear-gradient(135deg,#00d9ff,#7b4dff);color:#fff;border:0;font-weight:900;padding:0 15px}.draw-result{margin-top:10px;padding:20px;border-radius:23px;text-align:center;background:radial-gradient(circle at 50% 0,rgba(255,73,202,.18),transparent 35%),linear-gradient(145deg,#1a0e3c,#0c081e);border:2px solid #7433d2;box-shadow:0 0 32px rgba(131,46,240,.2);animation:resultPop .35s ease both}.result-glow{font-size:45px;filter:drop-shadow(0 0 12px rgba(255,90,210,.5))}.draw-result-title{font-size:23px;font-weight:1000;color:#fff}.result-word{margin:5px 0 12px;color:#bdb5d9}.result-table{display:grid;gap:6px;text-align:right}.result-row{display:grid;grid-template-columns:35px 1fr auto;align-items:center;gap:7px;padding:9px 11px;border-radius:12px;background:#12102a;border:1px solid #33255c;color:#fff}.result-row.winner{border-color:#ff53d1;box-shadow:0 0 14px rgba(255,83,209,.14)}.result-row strong{color:#ffd75c}.draw-result-note{margin-top:12px;color:#67eaff;font-weight:900}.draw-exit{text-align:center;margin:12px 0 4px}.receipt-shop-btn{display:inline-block;text-decoration:none;text-align:center}.coin-pack-card{position:relative;overflow:hidden;background:radial-gradient(circle at 10% 20%,rgba(255,215,71,.17),transparent 28%),linear-gradient(145deg,#261043,#100a27)!important;border:2px solid #9c4dff!important}.coin-pack-icon{font-size:55px;filter:drop-shadow(0 0 15px rgba(255,215,71,.35))}.coin-pack-card h2{margin:0;color:#fff}.coin-pack-card p{color:#aaa2c2}.coin-pack-cardnum{margin:12px 0;padding:12px;border-radius:14px;text-align:center;background:#0b091a;border:1px solid #584087;color:#ffd75b;font-size:18px;font-weight:1000;letter-spacing:1px}.coin-pack-steps{color:#bcb5d1;font-size:12px;line-height:1.9}.coin-pack-steps span{display:inline-grid;place-items:center;width:23px;height:23px;border-radius:50%;background:#7548ff;color:#fff;font-weight:900;margin:0 4px}.coin-pack-steps a{color:#6eeaff;font-weight:900}.receipt-row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px;margin-top:8px;border-radius:15px;background:#120d28;border:1px solid #3b2867}.receipt-actions{display:flex;gap:5px;flex-wrap:wrap}.receipt-actions .btn{padding:7px 9px}.payment-note{padding:10px;border-radius:13px;background:#0d0a1e;border:1px solid #4d357c;color:#d7d0e8}.support-receipt-upload{display:flex;align-items:center;gap:8px;margin-top:8px;padding:8px;border-radius:13px;background:#120d29;border:1px dashed #7041ce}.receipt-btn{padding:9px 12px;border-radius:11px;background:linear-gradient(135deg,#00cfff,#7850ff);color:#fff;border:0;font-weight:900}.support-receipt-upload small{color:#9992b6}.support-admin-card{border-color:#6531b5}.support-admin-card h2{color:#fff}.receipt-actions a{text-decoration:none}@keyframes previewPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}@keyframes resultPop{from{opacity:0;transform:translateY(8px) scale(.98)}to{opacity:1;transform:none}}@media(max-width:600px){.draw-hero{padding:13px}.draw-hero h1{font-size:20px}.draw-players-grid{grid-template-columns:1fr 1fr}.draw-player-card{padding:7px}.draw-avatar{width:37px;height:37px;flex-basis:37px}.draw-role{font-size:7px}.draw-guess-box{flex-direction:column}.draw-guess-box button{padding:11px}.coin-pack-cardnum{font-size:13px}.receipt-row{align-items:flex-start;flex-direction:column}.receipt-actions{width:100%}}
"""


BASE_CSS += """
/* REQUESTED SOCIAL + MODERATION UI */
.avatar-placeholder{display:flex!important;align-items:center;justify-content:center;background:linear-gradient(145deg,#2b2052,#14102d);color:#7d70b8;font-size:34px!important}
.profile-action-row{display:flex;align-items:center;gap:8px;justify-content:center;margin-bottom:10px}
.circle-action{width:42px;height:42px;padding:0!important;border-radius:50%!important;display:inline-flex!important;align-items:center;justify-content:center;font-size:22px;font-weight:1000;background:#17102f!important;color:#fff!important;border:1px solid #7040b8!important;box-shadow:0 0 12px rgba(130,54,235,.18)}
.circle-action:hover{transform:translateY(-2px);filter:brightness(1.12)}
.circle-action:disabled{opacity:.7;cursor:default}
.friend-ok{border-color:#2bd9a1!important;color:#55efc4!important}.report-circle{border-color:#d95d87!important;font-size:17px!important}.block-circle{border-color:#a34d6f!important}
.confirm-overlay{position:fixed;inset:0;z-index:9999;background:rgba(3,2,12,.78);display:flex;align-items:center;justify-content:center;padding:18px;backdrop-filter:blur(8px)}
.confirm-card{width:min(420px,100%);background:linear-gradient(145deg,#241047,#0e0924);border:2px solid #8a42dd;border-radius:22px;padding:24px;text-align:center;box-shadow:0 0 40px rgba(126,42,229,.3)}
.confirm-card b{font-size:19px}.confirm-card p{color:#bcb5d2}.confirm-card button{margin:5px;min-width:90px}
.support-profile-tools{margin-top:14px;padding:13px;border:1px solid #5e328e;border-radius:15px;background:#100a26}
.support-profile-row{display:flex;gap:7px;align-items:center;margin-top:9px}.support-profile-row input{flex:1;margin:0!important}.support-profile-row select{padding:10px;border-radius:10px;background:#0a0718;color:#fff;border:1px solid #3d2865}
.logout-card{text-align:center}.logout-btn{background:linear-gradient(135deg,#d64f83,#7f3bd2)!important;color:#fff!important;min-width:180px}
.draw-options{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px!important}
.draw-option-btn{min-width:0!important;padding:8px 5px!important;font-size:12px!important;line-height:1.25!important;border-radius:11px!important;white-space:normal}
.draw-palette{gap:5px!important;padding:7px!important}.draw-swatch{width:22px!important;height:22px!important}
.draw-canvas-wrap canvas{aspect-ratio:700/360}
.draw-result-exit{margin-top:14px}
@media(max-width:600px){.draw-options{grid-template-columns:repeat(4,minmax(0,1fr))!important}.draw-option-btn{font-size:10px!important;padding:7px 3px!important}.draw-swatch{width:21px!important;height:21px!important}.support-profile-row{flex-wrap:wrap}.support-profile-row input,.support-profile-row select,.support-profile-row button{width:100%}}
"""

BASE_CSS += """
/* Final polish */
.draw-swatch{width:27px;height:27px;border-width:2px}.draw-palette{gap:6px}.draw-options{gap:6px}.draw-option-btn{padding:7px 10px;font-size:12px;min-width:78px}.draw-canvas-wrap canvas{aspect-ratio:700/360}.profile-actions{align-items:center}.circle-action{width:38px;height:38px;padding:0!important;border-radius:50%!important;display:inline-grid!important;place-items:center!important}
"""

BASE_CSS += """.result-subtitle{margin:10px 0 5px;text-align:right;color:#ff82d9;font-size:12px;font-weight:900}.round-points{border-color:#5b3b91}.lobby-quick-grid-placeholder{min-width:0;text-align:center;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:15px;padding:10px 4px;font-size:19px}.lobby-quick-grid-placeholder b,.lobby-quick-grid-placeholder small{display:block}.lobby-quick-grid-placeholder b{font-size:10px}.lobby-quick-grid-placeholder small{font-size:8px;color:#8f96b7}"""

# ===== FINAL OVERRIDES =====
BASE_CSS += """
/* Final requested leagues / drawing / moderation polish */
.league-starter{--league-accent:#8b93a7}.league-bronze{--league-accent:#cd7f32}.league-davinci{--league-accent:#32d9d0}.league-picasso{--league-accent:#ff4a4a}
.league-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:999px;border:1px solid var(--league-accent);color:#fff;background:color-mix(in srgb,var(--league-accent) 16%,#0c0920);box-shadow:0 0 16px color-mix(in srgb,var(--league-accent) 25%,transparent);font-size:11px;font-weight:950}
.league-bronze .league-badge{color:#ffd6a1}.league-davinci .league-badge{color:#bafff8}.league-picasso .league-badge{color:#ffb0b0}
.profile-card.league-bronze{border-color:#cd7f32}.profile-card.league-davinci{border-color:#32d9d0}.profile-card.league-picasso{border-color:#ff4a4a}
.lobby-profile.league-bronze{border-color:#cd7f32}.lobby-profile.league-davinci{border-color:#32d9d0}.lobby-profile.league-picasso{border-color:#ff4a4a}
.draw-battle .draw-board-frame{width:100%;padding:9px;border-width:2px}.draw-battle .draw-canvas-wrap canvas{width:100%;height:auto;aspect-ratio:900/400;min-height:280px;max-height:58vh}
.draw-battle .draw-swatch{width:24px!important;height:24px!important;box-shadow:0 0 0 1px rgba(255,255,255,.3)}
.draw-battle .draw-options{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:6px!important}.draw-battle .draw-option-btn{min-height:40px!important;font-size:11px!important;font-weight:950!important;background:#21183f!important;border:2px solid #6e43b7!important;color:#fff!important;box-shadow:0 3px 10px rgba(0,0,0,.2)}.draw-battle .draw-option-btn:hover{filter:brightness(1.25)}
.draw-notice{margin:8px 0;padding:9px 11px;border-radius:13px;background:#17112f;border:1px solid #5d3e96;color:#fff;font-size:12px;font-weight:850;text-align:center;min-height:18px}.draw-notice.ok{border-color:#28d5aa;color:#9bffe8}.draw-notice.bad{border-color:#ef587e;color:#ffb1c6}
.drawing-report-btn{display:none;margin:9px auto 0!important;background:#24142f!important;border:1px solid #df5a9b!important;color:#ffb7d8!important;font-size:12px!important}
.result-report-btn{display:inline-block!important}.report-media-link{display:inline-block;margin-top:8px;color:#7cefff;text-decoration:none;font-weight:900}.report-media-video{width:100%;max-height:480px;border-radius:14px;background:#05050d;margin-top:8px}.report-media-fallback{padding:10px;border-radius:12px;background:#11102a;border:1px solid #40346b;color:#bdb6d8;margin-top:8px}
.username-ban-note{margin-top:7px;padding:8px;border-radius:11px;background:rgba(255,78,140,.08);border:1px solid rgba(255,78,140,.2);color:#ffb2cb;font-size:11px}
@media(max-width:600px){.draw-battle .draw-options{grid-template-columns:repeat(5,minmax(0,1fr))!important}.draw-battle .draw-option-btn{font-size:9px!important;padding:6px 2px!important;min-height:38px!important}.draw-battle .draw-canvas-wrap canvas{min-height:245px}.league-badge{font-size:10px}}
"""


def _league_data(prof):
    return prof.get('league') or {'key':'starter','name':'مبتدی','theme':'league-starter','min':0}


def _public_id(prof):
    return str(prof.get('public_username') or prof.get('username') or '')


def _frame_overlay_html(owned):
    # قاب تصویری فروشگاه: عکس مستقیم به‌صورت base64 داخل صفحه embed می‌شود (نه فایل جدا)
    # تا روی هر هاستی بدون درخواست شبکه‌ی اضافه و بدون شکستن تصویر نمایش داده شود.
    # استایل به‌صورت inline نوشته شده تا وابسته به بارگذاری شیت CSS جداگانه نباشد.
    # هیچ متنی (طلایی/یخی) نوشته نمی‌شود؛ فقط جلوه‌ی بصری (ذرات ریز CSS، بدون تصویر اضافه => بدون لگ).
    _st = ("position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);"
           "pointer-events:none;z-index:5;object-fit:contain;border-radius:0;"
           "max-width:none;max-height:none;display:block;")
    if 'gold_frame' in owned:
        img = f'<img class="avatar-frame-img frame-img-gold" alt="" style="{_st}width:172%;height:172%" src="data:image/webp;base64,{GOLD_FRAME_OVERLAY_B64}">'
        sparks = ''.join(f'<span class="gold-spark gold-spark-{i}"></span>' for i in (1,2,3,4))
        return img + sparks
    if 'ice_frame' in owned:
        img = f'<img class="avatar-frame-img frame-img-ice" alt="" style="{_st}width:163%;height:163%" src="data:image/webp;base64,{ICE_FRAME_OVERLAY_B64}">'
        shards = ''.join(f'<span class="ice-shard ice-shard-{i}"></span>' for i in (1,2,3,4))
        return img + shards
    return ''


def profile_page(username, prof):
    prof=prof or {'username':username,'public_username':username,'bio':'','avatar':'','age':18,'wins':0,'losses':0,'draws':0,'points':0,'correct_guesses':0,'wrong_guesses':0,'support_tags':[]}
    league=_league_data(prof); theme=league['theme']; public_id=_public_id(prof); owned=set(prof.get('owned_items') or [])
    frame_class = 'frame-picasso' if 'picasso_frame' in owned else ('frame-gold' if 'gold_frame' in owned else ('frame-ice' if 'ice_frame' in owned else ('frame-davinci' if 'davinci_frame' in owned else ('frame-bronze' if 'bronze_frame' in owned else ('frame-premium' if 'profile_frame' in owned else '')))))
    effect_class = 'effect-davinci' if 'davinci_effect' in owned else ('effect-picasso' if 'picasso_effect' in owned else '')
    total=int(prof.get('correct_guesses',0) or 0)+int(prof.get('wrong_guesses',0) or 0)
    correct=round(int(prof.get('correct_guesses',0) or 0)*100/total,1) if total else 0
    wrong=round(int(prof.get('wrong_guesses',0) or 0)*100/total,1) if total else 0
    avatar_banned=bool(prof.get('profile_banned')); bio_banned=bool(prof.get('bio_banned'))
    avatar_html='<div class="avatar-hidden">●</div>' if avatar_banned else _avatar_html(prof.get('avatar') or '')
    img_frame='' if avatar_banned else _frame_overlay_html(owned)
    avatar_wrap_cls=' has-img-frame' if img_frame else ''
    avatar_wrap_style=' style="position:relative;overflow:visible"' if img_frame else ''
    is_support=prof['username'].lower()=='morad'; badge='<div class="verified-support">✓ پشتیبانی رسمی</div>' if is_support else '';
    if 'crown_badge' in owned and not is_support: badge += '<div class="shop-badge crown-owned">👑 ویژه</div>'
    if 'bronze_badge' in owned: badge += '<div class="shop-badge bronze-owned">🥉 برنزی</div>'
    if 'davinci_frame' in owned or 'davinci_effect' in owned: badge += '<div class="shop-badge davinci-owned">🔷 داوینچی</div>'
    if 'picasso_frame' in owned or 'picasso_effect' in owned: badge += '<div class="shop-badge picasso-owned">🎨 پیکاسو</div>'
    tags=''.join(f'<span class="support-tag">🏷️ {html.escape(str(t.get("tag") or ""))}</span>' for t in (prof.get('support_tags') or []))
    tag_box=f'<div class="support-tags">{tags}</div>' if tags else ''
    league_html=f'<div class="league-badge">🏆 لیگ {html.escape(league["name"])} • {int(league.get("min",0))} جام+</div>'
    if prof['username']!=username:
        target_js=html.escape(prof['username'],quote=True)
        fs=prof.get('friend_status','none'); blocked=bool(prof.get('blocked_by_me'))
        if fs=='friends': friend_btn='<button class="circle-action friend-ok" disabled title="دوست هستید">✓</button>'; chat_btn=f'<a class="btn" href="/chat/private/{quote(prof["username"],safe="")}">💬 چت خصوصی</a>'
        elif fs=='outgoing': friend_btn='<button class="circle-action" disabled title="درخواست ارسال شده">✓</button>'; chat_btn='<button class="btn" onclick="needFriend()">💬 چت خصوصی</button>'
        elif fs=='incoming': friend_btn='<button class="circle-action" disabled title="درخواست دریافتی">📨</button>'; chat_btn='<button class="btn" onclick="needFriend()">💬 چت خصوصی</button>'
        else: friend_btn='<button class="circle-action" title="درخواست دوستی" onclick="askFriend()">+</button>'; chat_btn='<button class="btn" onclick="needFriend()">💬 چت خصوصی</button>'
        report_btn='' if is_support else f'<button class="circle-action report-circle" title="گزارش" onclick="openReportModal(\'{target_js}\',\'پروفایل کاربر\',\'profile\',\'\')">🚩</button>'
        block_btn='' if is_support else f'<button id="blockBtn" class="circle-action block-circle" title="{"آنبلاک" if blocked else "بلاک"}" onclick="toggleBlock()">{"✓" if blocked else "×"}</button>'
        support_tools=''
        if username=='morad':
            support_tools=f'''<div class="support-profile-tools"><b>🛡️ مدیریت محدودیت</b><div class="support-profile-row"><input value="{target_js}" readonly><select id="profileBanHours"><option value="1">۱ ساعت</option><option value="6">۶ ساعت</option><option value="24">۲۴ ساعت</option><option value="72">۳ روز</option><option value="168">۷ روز</option></select><button class="btn" onclick="banProfile()">🚫 محدودیت پروفایل</button></div><div class="support-profile-row"><select id="bioBanHours"><option value="1">۱ ساعت</option><option value="6">۶ ساعت</option><option value="24">۲۴ ساعت</option><option value="72">۳ روز</option><option value="168">۷ روز</option></select><button class="btn" onclick="banBio()">📝 محدودیت بیو</button></div></div>'''
        actions=f'<div class="profile-actions"><div class="profile-action-row">{friend_btn}{report_btn}{block_btn}</div>{chat_btn}</div>{support_tools}'
        scripts=f'''<script>
        function askFriend(){{if(document.getElementById('friendConfirm'))return;const m=document.createElement('div');m.id='friendConfirm';m.className='confirm-overlay';m.innerHTML='<div class="confirm-card"><b>👥 درخواست دوستی</b><p>آیا از ارسال درخواست دوستی به @{html.escape(public_id)} مطمئن هستید؟</p><div><button onclick="confirmFriend(true)">بله</button><button class="btn" onclick="confirmFriend(false)">خیر</button></div></div>';document.body.appendChild(m)}}
        async function confirmFriend(ok){{const m=document.getElementById('friendConfirm');if(m)m.remove();if(!ok)return;const r=await fetch('/friends/request',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target:'{target_js}'}})}});const d=await r.json();if(d.ok)location.reload();else alert(d.status==='already_sent'?'این درخواست قبلاً ارسال شده است.':'❌ درخواست ارسال نشد.')}}
        function needFriend(){{alert('💬 اول باید درخواست دوستی ارسال کنید و طرف مقابل آن را قبول کند.')}}
        async function toggleBlock(){{const blocked={str(blocked).lower()};if(!confirm(blocked?'آیا می‌خواهید این کاربر را آنبلاک کنید؟':'آیا از بلاک کردن این کاربر مطمئن هستید؟'))return;const r=await fetch('/users/block',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target:'{target_js}'}})}});const d=await r.json();if(d.ok)location.reload();else alert(d.message||'❌ عملیات انجام نشد.')}}
        async function banProfile(){{const r=await fetch('/support/ban',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target:'{target_js}',scope:'profile',hours:Number(document.getElementById('profileBanHours').value)||1,reason:'محرومیت تصویر پروفایل توسط پشتیبانی'}})}});const d=await r.json();alert(d.ok?'✅ تصویر پروفایل محدود شد.':'❌ انجام نشد.');if(d.ok)location.reload()}}
        async function banBio(){{const r=await fetch('/support/ban',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target:'{target_js}',scope:'bio',hours:Number(document.getElementById('bioBanHours').value)||1,reason:'محرومیت بیوگرافی توسط پشتیبانی'}})}});const d=await r.json();alert(d.ok?'✅ بیو محدود شد.':'❌ انجام نشد.');if(d.ok)location.reload()}}
        </script>'''
    else:
        actions='<div class="profile-actions"><a class="btn" href="/settings">⚙️ تنظیمات پروفایل</a></div>';scripts=''
    support_box='<a class="support-mini-card" href="/support/ticket">🛡️ <b>پشتیبانی رسمی</b><span>برای ارتباط مستقیم، تیکت ثبت کن</span></a>' if is_support else ''
    bio='<div class="moderation-hidden">این بخش موقتاً محدود شده است.</div>' if bio_banned else html.escape(prof.get('bio') or 'این کاربر هنوز بیوگرافی ننوشته.')
    notice=f'<div class="error" style="margin-bottom:12px;text-align:center">💬 {html.escape(str(prof.get("chat_notice") or ""))}</div>' if prof.get('chat_notice') else ''
    body=f'''<div class="profile-card hero page-enter {theme} {frame_class} {effect_class} {"has-frame" if (owned & {"profile_frame","bronze_frame","davinci_frame","picasso_frame","gold_frame","ice_frame"}) else ""} {"name-glow" if "name_effect" in owned else ""}">{notice}<div class="profile-head"><div class="{avatar_wrap_cls}"{avatar_wrap_style}>{avatar_html}{img_frame}</div><div><div class="profile-kicker">PLAYER PROFILE</div><h1>@{html.escape(public_id)}</h1><div class="profile-age">🎂 {int(prof.get('age') or 18)} سال</div>{league_html}{badge}</div></div>{tag_box}<div class="profile-bio">{bio}</div><div class="stat-grid"><div class="stat-box"><b>{correct}%</b><br>حدس درست</div><div class="stat-box"><b>{wrong}%</b><br>حدس غلط</div><div class="stat-box"><b>{int(prof.get('wins',0) or 0)}</b><br>جام</div><div class="stat-box"><b>{int(prof.get('points',0) or 0)}</b><br>امتیاز</div></div>{actions}{support_box}</div>{scripts}<div style="text-align:center;margin-top:14px"><a class="btn" href="/lobby">← بازگشت به لابی</a></div>'''
    return page_shell('پروفایل',body,username)


def lobby_page(username, prof=None, wallet=None):
    prof=prof or {'username':username,'public_username':username,'bio':'','avatar':'','age':18,'wins':0,'points':0,'league':{'name':'مبتدی','theme':'league-starter'}}
    league=_league_data(prof); theme=league['theme']; owned=set(prof.get('owned_items') or []); avatar='<div class="avatar-hidden">●</div>' if prof.get('profile_banned') else _avatar_html(prof.get('avatar') or '')
    frame_class = 'frame-picasso' if 'picasso_frame' in owned else ('frame-gold' if 'gold_frame' in owned else ('frame-ice' if 'ice_frame' in owned else ('frame-davinci' if 'davinci_frame' in owned else ('frame-bronze' if 'bronze_frame' in owned else ('frame-premium' if 'profile_frame' in owned else '')))))
    effect_class = 'effect-davinci' if 'davinci_effect' in owned else ('effect-picasso' if 'picasso_effect' in owned else '')
    name_class = 'name-glow' if 'name_effect' in owned else ''
    crown = '👑 ' if 'crown_badge' in owned else ''
    img_frame = '' if prof.get('profile_banned') else _frame_overlay_html(owned)
    avatar_wrap_cls = ' has-img-frame' if img_frame else ''
    avatar_wrap_style = ' style="position:relative;overflow:visible"' if img_frame else ''
    public_id=_public_id(prof); wins=int(prof.get('wins') or 0); points=int(prof.get('points') or 0); coins=int((wallet or {}).get('coins') or 0); age=int(prof.get('age') or 18)
    support_link='<a href="/support">🛡️ <b>پنل پشتیبانی</b><small>مدیریت گزارش‌ها</small></a>' if username=='morad' else ''
    body=f'''<div class="lobby-bg page-enter"><div class="lobby-topbar"><div><div class="lobby-kicker">DRAW BATTLE • ONLINE</div><div class="lobby-title">تخته گچی ⚡</div></div><div style="display:flex;gap:7px"><a class="lobby-settings" href="/settings">⚙️</a>{('<a class="lobby-settings" href="/support">🛡️</a>' if username=='morad' else '')}</div></div><a class="lobby-profile hero {theme} {frame_class} {effect_class} {"has-frame" if (owned & {"profile_frame","bronze_frame","davinci_frame","picasso_frame","gold_frame","ice_frame"}) else ""} {"name-glow" if "name_effect" in owned else ""}" href="/profile?u={quote(username,safe='')}"><div class="lobby-profile-avatar{avatar_wrap_cls}"{avatar_wrap_style}>{avatar}{img_frame}</div><div class="lobby-profile-info"><div class="lobby-profile-name {name_class}">{crown}@{html.escape(public_id)}</div><div class="lobby-profile-meta">🎂 {age} سال <span>•</span> 🏆 {wins} جام <span>•</span> 💎 {points} امتیاز</div><div class="lobby-profile-meta"><span class="league-badge">🏆 لیگ {html.escape(league['name'])}</span></div></div><div class="lobby-profile-arrow">‹</div></a><div class="lobby-wallet">💰 <b>{coins:,}</b> سکه</div><button class="notification-bell" onclick="toggleNotifications()">🔔 <span id="notifCount">0</span></button><div id="notificationPanel" class="notification-panel"><div class="notification-head"><b>🔔 اعلان‌ها</b><button onclick="markNotifsRead()">خوانده شد</button></div><div id="notificationList"></div></div><div class="section-heading"><span>🎮 حالت‌های بازی</span><small>یک حالت را انتخاب کن</small></div><div class="game-mode-card mode-speed"><div class="mode-badge">⚡ دو نفره سرعتی</div><div class="mode-icon">🎨</div><div class="mode-copy"><h2>حدس نقاشی</h2><p>۲ بازیکن • ۴۵ ثانیه برای هر دور</p></div><a class="mode-start" href="/game/drawing">شروع <span>←</span></a></div><div class="game-mode-card mode-draw"><div class="mode-badge">🎨 رقابت نقاشان</div><div class="mode-icon">🖌️</div><div class="mode-copy"><h2>نقاشی ۴ نفره</h2><p>۴ بازیکن • ۳۵ ثانیه برای هر دور</p></div><a class="mode-start" href="/game/drawing4">شروع <span>←</span></a></div><div class="lobby-quick-grid"><a href="/chat/public">💬 <b>چت عمومی</b><small>گپ با همه</small></a><a href="/messages">💌 <b>چت خصوصی</b><small>دوستان و درخواست‌ها</small></a><a href="/leaderboard">🏆 <b>رتبه‌بندی</b><small>جام و لیگ</small></a><a href="/shop">🛍️ <b>فروشگاه</b><small>آیتم‌ها</small></a>{support_link}</div></div><script>async function loadNotifications(){{try{{const r=await fetch('/notifications');const d=await r.json();let all=[...(d.notifications||[])];(d.friend_requests||[]).forEach(x=>all.unshift({{title:'درخواست دوستی جدید',content:'@'+x.sender+' برای شما درخواست دوستی فرستاد.',read:0}}));document.getElementById('notificationList').innerHTML=all.length?all.slice(0,30).map(n=>`<div class="notification-item ${{n.read?'':'unread'}}"><b>${{n.title||'اعلان'}}</b><span>${{n.content||''}}</span></div>`).join(''):'<div class="pinned-empty">اعلان جدیدی نداری.</div>';document.getElementById('notifCount').textContent=d.count||0}}catch(e){{}}}}function toggleNotifications(){{document.getElementById('notificationPanel').classList.toggle('show');loadNotifications()}}async function markNotifsRead(){{await fetch('/notifications/read',{{method:'POST'}});loadNotifications()}}loadNotifications();setInterval(loadNotifications,5000);</script>{_bottom_nav('home',username)}'''
    return page_shell('منوی اصلی',body,username)


def _leader_avatar(r, cls="leader-avatar"):
    if r.get('profile_banned'):
        return f'<div class="{cls} leader-avatar-fallback">●</div>'
    raw = r.get('avatar') or ''
    return _avatar_html(raw, cls=cls) if raw else f'<div class="{cls} leader-avatar-fallback">●</div>'

def leaderboard_page(username, rows, by='wins'):
    value_key='points' if by=='points' else 'wins'; value_label='امتیاز' if by=='points' else 'جام'; value_icon='💎' if by=='points' else '🏆'
    podium=[]; rest=[]
    for i,r in enumerate(rows,1):
        league=_league_data(r)
        public_id=str(r.get('public_username') or r.get('username'))
        value=int(r.get(value_key) or 0)
        href=f'/profile?u={quote(str(r.get("username")),safe="")}'
        if i<=3:
            av=_leader_avatar(r)
            medal=['🥇','🥈','🥉'][i-1]
            podium.append(f'<a class="leader-podium-card rank-{i} {league["theme"]}" href="{href}"><div class="leader-rank">{medal}</div>{av}<div class="leader-name">@{html.escape(public_id)}</div><div class="leader-score">{value_icon} {value} {value_label}</div><div class="report-meta">🏆 {html.escape(league["name"])}</div></a>')
        else:
            av=_leader_avatar(r)
            cls=' me' if r.get('username')==username else ''
            rest.append(f'<a class="leader-row{cls} {league["theme"]}" href="{href}"><div class="rank-medal">{i}</div><div class="leader-list-avatar">{av}</div><div><b>@{html.escape(public_id)}</b><div class="report-meta">🏆 لیگ {html.escape(league["name"])}</div></div><div><b>{value}</b><small> {value_label}</small></div></a>')
    tabs=f'<div class="leader-tabs"><a class="leader-tab{" active" if by=="wins" else ""}" href="/leaderboard?by=wins">🏆 بیشترین جام</a><a class="leader-tab{" active" if by=="points" else ""}" href="/leaderboard?by=points">💎 بیشترین امتیاز</a></div>'
    podium_html=f'<div class="leader-podium">{"".join(podium)}</div>' if podium else ''
    rest_html=f'<div class="leader-list">{"".join(rest)}</div>' if rest else ('' if podium else '<p>هنوز آماری ثبت نشده.</p>')
    body=f'<div class="page-heading"><div><div class="sub">RANKING • LEAGUES</div><h1>🏆 رتبه‌بندی و لیگ‌ها</h1></div><a class="btn" href="/lobby">خانه</a></div><div class="card hero page-enter">{tabs}<p>سه نفر اول با قاب دایره‌ای ویژه نمایش داده می‌شوند؛ لیگ بر اساس جام‌ها: برنزی از ۲۵۰، داوینچی از ۷۵۰ و پیکاسو از ۱۵۰۰ جام.</p>{podium_html}{rest_html}</div>'
    return page_shell('رتبه‌بندی',body,username)

def settings_page(username, prof):
    prof=prof or {'username':username,'public_username':username,'bio':'','avatar':'','age':18}
    public_id=html.escape(str(prof.get('public_username') or username)); bio=html.escape(prof.get('bio') or ''); age=int(prof.get('age') or 18)
    body=f'''<div class="settings-screen page-enter"><div class="settings-header"><div class="settings-gear">⚙️</div><h1>تنظیمات</h1><a class="settings-close" href="/lobby">×</a></div><div class="settings-card profile-editor-card"><div class="settings-kicker">پروفایل</div><div class="settings-avatar-row"><div class="settings-avatar" id="avatarPreview">{_avatar_html(prof.get('avatar') or '')}</div><div><p>آواتار فقط تصویر است؛ ایموجی به‌عنوان آواتار قابل انتخاب نیست.</p></div></div><input type="file" id="avatarFile" class="file-input" accept="image/*"><label for="publicUsername">آیدی نمایشی</label><input id="publicUsername" type="text" value="{public_id}" minlength="3" maxlength="32" pattern="[a-z0-9]+" inputmode="latin" autocapitalize="none" spellcheck="false"><div class="field-hint">۳ تا ۳۲ کاراکتر؛ فقط a-z و عدد. هنگام محرومیت آیدی امکان تغییر ندارد.</div><label for="bioInput">بیوگرافی</label><textarea id="bioInput" maxlength="70" placeholder="چیزی درباره‌ی خودت بنویس...">{bio}</textarea><div class="char-counter"><span id="bioCount">0</span>/70</div><div class="age-row"><span>سن:</span><input type="number" id="ageInput" min="1" max="90" value="{age}"></div><button class="settings-save" id="saveProfileBtn" onclick="saveProfile()">💾 ذخیره تغییرات</button><div id="profileStatus" class="status-line" style="display:none"></div></div><div class="settings-card"><div class="settings-kicker">امنیت حساب</div><label for="oldPassword">رمز عبور فعلی</label><input type="password" id="oldPassword" placeholder="رمز فعلی"><label for="newPassword">رمز عبور جدید</label><input type="password" id="newPassword" placeholder="حداقل ۴ کاراکتر"><button class="settings-save" id="savePasswordBtn" onclick="savePassword()">🔑 تغییر رمز عبور</button><div id="passwordStatus" class="status-line" style="display:none"></div></div><div class="settings-card logout-card"><button class="logout-btn" onclick="logoutAccount()">🚪 خروج از حساب</button></div><div class="settings-links"><a href="/lobby">🏠 لابی</a><a href="/profile?u={quote(username,safe='')}">👤 پروفایل من</a></div></div><script>
    let pendingAvatar=null;const bioEl=document.getElementById('bioInput'),bioCount=document.getElementById('bioCount');function refreshCount(){{bioCount.textContent=bioEl.value.length}}refreshCount();bioEl.addEventListener('input',refreshCount);
    document.getElementById('avatarFile').addEventListener('change',function(e){{const file=e.target.files[0];if(!file)return;if(!file.type.startsWith('image/'))return alert('فقط تصویر مجاز است.');const reader=new FileReader();reader.onload=ev=>{{const img=new Image();img.onload=()=>{{const size=Math.min(img.width,img.height),c=document.createElement('canvas');c.width=320;c.height=320;c.getContext('2d').drawImage(img,(img.width-size)/2,(img.height-size)/2,size,size,0,0,320,320);pendingAvatar=c.toDataURL('image/jpeg',0.85);document.getElementById('avatarPreview').innerHTML='<img src="'+pendingAvatar+'" class="profile-avatar-img">'}};img.src=ev.target.result}};reader.readAsDataURL(file)}});
    async function saveProfile(){{const btn=document.getElementById('saveProfileBtn');btn.disabled=true;const s=document.getElementById('profileStatus');s.style.display='block';try{{const payload={{public_username:document.getElementById('publicUsername').value.trim().toLowerCase(),bio:bioEl.value.trim(),age:Number(document.getElementById('ageInput').value)||18}};if(pendingAvatar)payload.avatar=pendingAvatar;const r=await fetch('/settings/profile',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});const d=await r.json();s.textContent=d.ok?'✅ ذخیره شد.':d.message||'❌ ذخیره نشد.';if(d.ok){{pendingAvatar=null;setTimeout(()=>location.reload(),500)}}}}catch(e){{s.textContent='❌ خطا در ارتباط با سرور.'}}btn.disabled=false}}
    async function savePassword(){{const old_password=document.getElementById('oldPassword').value,new_password=document.getElementById('newPassword').value,s=document.getElementById('passwordStatus');s.style.display='block';if(new_password.length<4)return s.textContent='رمز جدید باید حداقل ۴ کاراکتر باشد.';const r=await fetch('/settings/password',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{old_password,new_password}})}}),d=await r.json();s.textContent=d.ok?'✅ رمز عبور تغییر کرد.':'❌ رمز فعلی اشتباه است.';if(d.ok){{document.getElementById('oldPassword').value='';document.getElementById('newPassword').value=''}}}}
    function logoutAccount(){{location.href='/logout'}}
    </script>'''
    return page_shell('تنظیمات',body,username)


def messages_page(username, friends, requests):
    req=[]
    for r in requests:
        rid=str(r.get('sender')); public=str(r.get('public_username') or rid); req.append(f'<div class="friend-row"><div class="avatar">●</div><div class="grow"><b>@{html.escape(public)}</b><div class="report-meta">درخواست دوستی</div></div><div class="request-actions"><button onclick="respond({rid!r},true)">✓</button><button class="btn" onclick="respond({rid!r},false)">✕</button></div></div>')
    fr=[]; now=int(time.time())
    for f in friends:
        internal=str(f['username']); public=str(f.get('public_username') or internal); can=now-int(f.get('created_at') or now)>=5*3600
        rm=f'<button class="circle-action block-circle" title="حذف دوست" onclick="removeFriend(\'{html.escape(internal,quote=True)}\')">×</button>' if can else '<span class="report-meta">⏳ ۵ ساعت</span>'
        fr.append(f'<div class="friend-row"><div class="avatar">●</div><div class="grow"><a class="profile-link" href="/profile?u={quote(internal,safe="")}"><b>@{html.escape(public)}</b></a><div class="report-meta">لیگ و پروفایل</div></div><a class="btn" href="/chat/private/{quote(internal,safe="")}">💬</a>{rm}</div>')
    body=f'''<div class="card hero page-enter"><div style="display:flex;justify-content:space-between;align-items:center"><h1>💬 پیام‌ها و دوستان</h1><a class="btn" href="/lobby">خانه ←</a></div><input id="userSearch" type="text" placeholder="🔎 جستجوی کاربر..." oninput="searchUser()"><div id="searchResult"></div></div><div class="card"><h2>📨 درخواست‌های دوستی</h2>{''.join(req) or '<p>درخواستی نداری.</p>'}</div><div class="card"><h2>👥 دوستان من</h2>{''.join(fr) or '<p>هنوز دوستی نداری.</p>'}</div><script>async function respond(sender,accept){{const r=await fetch('/friends/respond',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{sender,accept}})}});const d=await r.json();if(d.ok)location.reload()}}async function removeFriend(target){{const r=await fetch('/friends/remove',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{target}})}});const d=await r.json();if(d.ok)location.reload();else alert(d.status==='too_soon'?'⏳ حذف دوست بعد از ۵ ساعت ممکن است.':'❌ حذف نشد.')}}let st;async function searchUser(){{clearTimeout(st);const q=document.getElementById('userSearch').value.trim(),box=document.getElementById('searchResult');if(!q)return box.innerHTML='';st=setTimeout(async()=>{{const r=await fetch('/profile?u='+encodeURIComponent(q));box.innerHTML=r.ok?'<a class="friend-row" href="/profile?u='+encodeURIComponent(q)+'">👤 باز کردن پروفایل @'+q.replace(/[<>&]/g,'')+' →</a>':'<p class="report-meta">کاربر پیدا نشد.</p>'}},250)}}</script>'''
    return page_shell('پیام‌ها',body,username)


def support_page(username, reports, active_bans=None, tickets=None, receipts=None):
    active_bans=active_bans or []; tickets=tickets or []; receipts=receipts or []
    labels={'all':'همه امکانات','games':'بازی‌ها','chat':'چت','drawing':'نقاشی','profile':'تصویر پروفایل','bio':'بیوگرافی','username':'آیدی'}
    cats={'collusion':'تبانی/تقلب','profile':'پروفایل','username':'آیدی نامناسب','spam':'اسپم','chat':'چت','drawing':'نقاشی','bio':'بیوگرافی','other':'سایر'}
    drawing_items=[]; other_items=[]
    for r in reports:
        cat=r.get('category') or 'other'; target=str(r.get('target') or ''); status='حل‌شده' if r.get('status')!='open' else 'باز'
        media=''
        if r.get('media_mime'):
            href=f'/support/report/{int(r["id"])}/media'; mime=str(r['media_mime'])
            if mime.startswith('video/'):
                media=f'<video class="report-media-video" controls playsinline preload="metadata" src="{href}"></video>'
            else:
                media=f'<a class="report-media-link" target="_blank" href="{href}">👁️ مشاهده فایل گزارش</a>'
        elif r.get('replay_mime'):
            media=f'<button class="btn" onclick="replayReport({int(r["id"])} )">▶️ پخش بازپخش نقاشی</button><div id="replay-{int(r["id"])}" class="report-media-fallback" style="display:none"></div>'
        selected=''.join(f'<option value="{v}">{labels[k]}</option>' for k,v in [("all","all"),("chat","chat"),("games","games"),("drawing","drawing"),("profile","profile"),("bio","bio"),("username","username")])
        review=''
        if cat=='drawing' or r.get('context')=='drawing':
            review=f'<div class="support-review-row"><button onclick="reviewReport({int(r["id"])},\'valid\')">✅ نقاشی تخلف بود</button><button onclick="reviewReport({int(r["id"])},\'invalid\')">⚠️ گزارش بی‌اساس</button></div>'
        card=f'''<div class="report-item" data-report-id="{int(r['id'])}"><div><b>گزارش #{int(r['id'])}</b> <span class="report-category">{html.escape(cats.get(cat,cat))}</span> — {status}</div><div class="report-meta">گزارش‌دهنده: @{html.escape(str(r.get('reporter') or ''))} | کاربر: <b>@{html.escape(target)}</b></div><p>{html.escape(str(r.get('content') or ''))}</p>{media}<div class="support-action-grid"><select class="ban-scope">{selected}</select><input class="ban-hours" type="number" min="0" max="168" value="0"><input class="ban-minutes" type="number" min="1" max="59" value="10"><button class="glow-btn" onclick="banUser({int(r['id'])},this)">🚫 تأیید و محروم کن</button><button class="btn danger-btn" onclick="deleteReport({int(r['id'])})">🗑️ حذف گزارش</button></div>{review}</div>'''
        (drawing_items if (cat=='drawing' or r.get('context')=='drawing') else other_items).append(card)
    bans=[]
    for b in active_bans:
        remaining=max(0,int(b['until_ts'])-int(time.time())); h,rem=divmod(remaining,3600); m=rem//60; left=(f'{h} ساعت و ' if h else '')+f'{m} دقیقه'
        bans.append(f'<div class="ban-row" data-target="{html.escape(b["username"])}" data-scope="{html.escape(b["scope"])}"><b>@{html.escape(b["username"])}</b> <span class="ban-scope-tag">{labels.get(b["scope"],b["scope"])}</span><div class="report-meta">{html.escape(b.get("reason") or "—")} • {left}</div><button class="btn" onclick="unbanUser(this)">رفع محرومیت</button></div>')
    receipt_labels={'new':'جدید','reviewed':'در حال بررسی','accepted':'تأیید شده','rejected':'رد شده'}; receipt_items=[]
    for r in receipts:
        status=r.get('status') or 'new'; actions=f'<a class="btn" target="_blank" href="/support/receipt/{int(r["id"])}">👁️ مشاهده رسید</a>'
        if status not in ('accepted','rejected'): actions+=f'<button class="btn" onclick="receiptStatus({int(r["id"])},\'accepted\')">تأیید</button><button class="btn" onclick="receiptStatus({int(r["id"])},\'rejected\')">رد</button>'
        receipt_items.append(f'<div class="receipt-row"><div><b>🧾 @{html.escape(str(r["username"]))}</b><div class="report-meta">۱۰۰۰ سکه • {html.escape(str(r["filename"]))} • وضعیت: {receipt_labels.get(status,status)}</div></div><div class="receipt-actions">{actions}</div></div>')
    body=f'''<div class="card admin-card page-enter"><h1>🛡️ مرکز فرماندهی پشتیبانی</h1><p>مدیریت رسیدها، گزارش‌ها، محرومیت‌ها و داوری نقاشی.</p></div><div class="card support-admin-card"><h2>💰 مدیریت سکه و جام</h2><div class="support-direct-grid"><input id="walletTarget" placeholder="آیدی کاربر"><input id="coinDelta" type="number" placeholder="تغییر سکه"><input id="trophyDelta" type="number" placeholder="تغییر جام"><button onclick="adjustWallet()">اعمال</button></div><div id="walletStatus" class="status-line"></div></div><div class="card"><h2>🧾 صندوق رسیدها</h2>{''.join(receipt_items) or '<p>رسیدی وجود ندارد.</p>'}</div><div class="card"><h2>🎨 داوری نقاشی</h2><p class="report-meta">فقط گزارش‌های نقاشی در این بخش هستند؛ ویدئو یا بازپخش را بررسی کن.</p>{''.join(drawing_items) or '<p>گزارش نقاشی‌ای برای داوری وجود ندارد.</p>'}</div><div class="card"><h2>🚩 سایر گزارش‌ها</h2>{''.join(other_items) or '<p>گزارش دیگری وجود ندارد.</p>'}</div><div class="card"><h2>🔨 محرومیت مستقیم</h2><div class="support-direct-grid"><input id="directTarget" placeholder="آیدی کاربر"><select id="directScope"><option value="all">همه امکانات</option><option value="chat">چت</option><option value="games">بازی‌ها</option><option value="drawing">نقاشی</option><option value="profile">تصویر پروفایل</option><option value="bio">بیوگرافی</option><option value="username">آیدی</option></select><input id="directHours" type="number" min="0" max="168" value="0"><input id="directMinutes" type="number" min="1" max="59" value="10"></div><input id="directReason" placeholder="دلیل محرومیت"><button onclick="banDirect()">🚫 محروم کن</button></div><div class="card"><h2>⏳ محرومیت‌های فعال</h2>{''.join(bans) or '<p>محرومیت فعالی نیست.</p>'}</div><div class="card"><h2>🎫 تیکت‌ها</h2>{''.join(f'<div class="report-item"><b>#{int(t["id"])} — {html.escape(str(t["subject"]))}</b><p>{html.escape(str(t["content"]))}</p></div>' for t in tickets) or '<p>تیکتی نیست.</p>'}</div><div style="text-align:center"><a class="btn" href="/chat/private/morad">💬 پیوی پشتیبانی</a> <a class="btn" href="/chat/public">🏠 چت عمومی</a> <a class="btn" href="/lobby">لابی</a></div><script>
    async function post(url,payload){{const r=await fetch(url,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(payload)}});return r.json()}}
    async function doBan(p){{const d=await post('/support/ban',p);if(d.ok)location.reload();else alert(d.message||'❌ انجام نشد.')}}
    async function banUser(id,btn){{const item=btn.closest('.report-item'),target=item.querySelector('.report-meta b').textContent.trim().replace(/^@/,''),scope=item.querySelector('.ban-scope').value;await doBan({{report_id:id,target,scope,hours:Number(item.querySelector('.ban-hours').value)||0,minutes:Number(item.querySelector('.ban-minutes').value)||0,reason:'بر اساس گزارش #'+id}})}}
    async function banDirect(){{const target=directTarget.value.trim();if(!target)return;await doBan({{target,scope:directScope.value,hours:Number(directHours.value)||0,minutes:Number(directMinutes.value)||0,reason:directReason.value.trim()||'نقض قوانین'}})}}
    async function unbanUser(btn){{const row=btn.closest('.ban-row');const d=await post('/support/unban',{{target:row.dataset.target,scope:row.dataset.scope}});if(d.ok)row.remove()}}
    async function adjustWallet(){{const d=await post('/support/adjust',{{target:walletTarget.value.trim(),coins:Number(coinDelta.value)||0,trophies:Number(trophyDelta.value)||0}});walletStatus.textContent=d.ok?'✅ اعمال شد.':'❌ انجام نشد.'}}
    async function receiptStatus(id,status){{const d=await post('/support/receipt/status',{{id,status}});if(d.ok)location.reload();else alert(d.message||'این رسید نهایی شده است.')}}
    async function reviewReport(id,decision){{const d=await post('/support/report/review',{{report_id:id,decision}});if(d.ok)location.reload();else alert(d.message||'❌ بررسی انجام نشد.')}}
    async function deleteReport(id){{if(!confirm('این گزارش برای همیشه حذف شود؟'))return;const d=await post('/support/report/delete',{{report_id:id}});if(d.ok){{const x=document.querySelector('[data-report-id=\"'+id+'\"]');if(x)x.remove();}}else alert('❌ حذف نشد.')}}
    async function replayReport(id){{const box=document.getElementById('replay-'+id);box.style.display='block';box.textContent='در حال دریافت بازپخش...';const r=await fetch('/support/report/'+id+'/replay');const arr=await r.json();if(!Array.isArray(arr)){{box.textContent='بازپخش در دسترس نیست.';return}}const c=document.createElement('canvas');c.width=900;c.height=400;c.style.width='100%';c.style.background='#fff';box.innerHTML='';box.appendChild(c);const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,c.width,c.height);let i=0;function step(){{if(i>=arr.length)return;const z=arr[i++];x.strokeStyle=z.color||'#111';x.lineWidth=z.size||4;x.lineCap='round';x.beginPath();x.moveTo(z.x0*c.width,z.y0*c.height);x.lineTo(z.x1*c.width,z.y1*c.height);x.stroke();setTimeout(step,10)}}step()}}
    </script>'''
    return page_shell('پنل پشتیبانی',body,username)


def _drawing_battle_page(username: str, mode: int) -> str:
    title='🎨 حدس نقاشی دو نفره' if mode==2 else '🎨 نقاشی ۴ نفره'; path='/ws/drawing' if mode==2 else '/ws/drawing-multi/4'; total_rounds=6 if mode==2 else 4; duration=45 if mode==2 else 35
    body=f'''<div class="draw-battle page-enter"><div class="draw-hero"><div><div class="draw-kicker">DRAW BATTLE • LIVE</div><h1>{title}</h1><div id="status" class="draw-status">🔌 در حال اتصال...</div></div><div class="draw-mode-badge">{mode} بازیکن</div></div><div id="queueBox" class="queue-widget"><div class="queue-spinner"></div><div class="queue-text">🔌 در حال پیدا کردن بازیکن‌ها...</div></div><div id="playersRow" class="draw-players-grid"></div><div id="roundInfo" class="draw-round-info"><span id="roundLabel">دور ۱ از {total_rounds}</span><span id="timerLabel" class="draw-timer">⏱ --</span></div><div id="previewPanel" class="draw-preview" style="display:none"><div class="preview-orb">🎨</div><div class="preview-title">آماده شو!</div><div id="previewText">موضوع برای نقاش آماده می‌شود...</div><div id="previewTimer" class="preview-count">5</div></div><div id="boardFrame" class="draw-board-frame" style="display:none"><div class="draw-board-top"><span>LIVE</span><span id="drawerLabel"></span></div><div class="draw-canvas-wrap"><canvas id="board" width="900" height="400"></canvas></div></div><div id="palette" class="draw-palette" style="display:none"></div><div id="tools" class="draw-tools" style="display:none"><button class="draw-tool active" id="penTool">✏️ قلم</button><button class="draw-tool" id="eraserTool">🧽 پاک‌کن</button><div class="draw-size-slider-wrap"><span class="draw-size-label">ضخامت</span><input type="range" id="sizeSlider" min="1" max="30" value="5"><span id="sizeValue" class="draw-size-value">5</span></div><button class="draw-tool" id="clearBtn">🧹 پاک‌کردن</button></div><div id="drawerWordBox" class="draw-word-box" style="display:none"></div><div id="drawerNotice" class="draw-notice" style="display:none"></div><button id="drawingReportBtn" class="drawing-report-btn" onclick="openDrawingReport()">🚩 گزارش نقاشی</button><div id="optionsGrid" class="draw-options" style="display:none"></div><div id="resultPanel" class="draw-result" style="display:none"></div></div><script>
    const me={username!r},MODE={mode},TOTAL_ROUNDS={total_rounds},DURATION={duration},WS_PATH={path!r},proto=location.protocol==='https:'?'wss:':'ws:';let ws=null,recon=null,intentionallyLeaving=false,timerInt=null,previewInt=null,role=null,currentColor='#111111',currentSize=5,tool='pen',drawing=false,last=null,pending=[],mediaRecorder=null,mediaChunks=[],drawingBlob=null,lastRoundVideoBlob=null,currentStrokes=[];
    const $=id=>document.getElementById(id),status=$('status'),queue=$('queueBox'),players=$('playersRow'),roundInfo=$('roundInfo'),roundLabel=$('roundLabel'),timer=$('timerLabel'),preview=$('previewPanel'),previewText=$('previewText'),previewTimer=$('previewTimer'),boardFrame=$('boardFrame'),drawerLabel=$('drawerLabel'),canvas=$('board'),ctx=canvas.getContext('2d'),palette=$('palette'),tools=$('tools'),wordBox=$('drawerWordBox'),opts=$('optionsGrid'),result=$('resultPanel'),reportBtn=$('drawingReportBtn'),drawerNotice=$('drawerNotice');
    function clearBoard(){{ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);currentStrokes=[]}}clearBoard();
    function avatarNode(p){{const w=document.createElement('div');w.className='draw-avatar';const a=p?.avatar||'';if(a.startsWith('data:image/')){{const i=document.createElement('img');i.src=a;w.appendChild(i)}}else w.textContent='●';return w}}
    function renderPlayers(scores,active,drawerName,profiles){{players.innerHTML='';Object.entries(scores||{{}}).sort((a,b)=>b[1]-a[1]).forEach(([u,sc])=>{{const p=(profiles||{{}})[u]||{{username:u,display_name:u,avatar:''}};const card=document.createElement('div');card.className='draw-player-card'+(u===me?' me':'')+(u===drawerName?' turn':'')+((active||[]).includes(u)?'':' out');const info=document.createElement('div');info.className='draw-player-info';const n=document.createElement('b');n.textContent=(p.owned_items||[]).includes('crown_badge')?'👑 '+(p.display_name||u):(p.display_name||u);if((p.owned_items||[]).includes('name_effect'))n.classList.add('name-effect-owned');const h=document.createElement('span');h.textContent='@'+(p.public_username||u);const score=document.createElement('strong');score.textContent='⭐ '+sc;info.append(n,h,score);card.append(avatarNode(p),info);if(p.league){{const lg=document.createElement('small');lg.className='league-mini '+p.league.theme;lg.textContent='🏆 '+p.league.name;card.append(lg)}}const rr=document.createElement('div');rr.className='draw-role';rr.textContent=u===drawerName?'✏️ نقاش':'🔎 حدس‌زن';card.append(rr);players.appendChild(card)}})}}
    function queueUI(n,needed){{queue.style.display='flex';queue.innerHTML='<div class="queue-spinner"></div><div class="queue-text">'+n+' از '+needed+' نفر آماده‌اند</div><div class="queue-sub">به‌محض تکمیل ظرفیت، رقابت شروع می‌شود ✨</div>'}}
    function countdown(sec,fn){{if(timerInt)clearInterval(timerInt);let left=Math.max(0,Math.ceil(sec));fn(left);timerInt=setInterval(()=>{{left--;fn(Math.max(0,left));if(left<=0)clearInterval(timerInt)}},1000)}}
    function previewCountdown(sec){{if(previewInt)clearInterval(previewInt);let left=Math.max(0,Math.ceil(sec));previewTimer.textContent=left;previewInt=setInterval(()=>{{left--;previewTimer.textContent=Math.max(0,left);if(left<=0)clearInterval(previewInt)}},1000)}}
    function paint(x0,y0,x1,y1,color,size){{ctx.strokeStyle=color||'#111';ctx.lineWidth=Math.max(1,Math.min(30,Number(size)||5));ctx.lineCap='round';ctx.beginPath();ctx.moveTo(x0*canvas.width,y0*canvas.height);ctx.lineTo(x1*canvas.width,y1*canvas.height);ctx.stroke()}}
    function pos(e){{const r=canvas.getBoundingClientRect();return{{x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height}}}}
    function sendPending(){{if(pending.length&&ws?.readyState===1){{ws.send(JSON.stringify({{type:'draw_batch',segments:pending}}));pending=[]}}}}
    canvas.addEventListener('pointerdown',e=>{{if(role!=='drawer')return;drawing=true;canvas.setPointerCapture(e.pointerId);last=pos(e)}});canvas.addEventListener('pointermove',e=>{{if(role!=='drawer'||!drawing)return;const evs=e.getCoalescedEvents?e.getCoalescedEvents():[e];for(const ce of evs){{const p=pos(ce),color=tool==='eraser'?'#fff':currentColor;paint(last.x,last.y,p.x,p.y,color,currentSize);const seg={{x0:last.x,y0:last.y,x1:p.x,y1:p.y,color,size:currentSize}};currentStrokes.push(seg);pending.push(seg);last=p}}if(pending.length>=8)sendPending()}});window.addEventListener('pointerup',()=>{{drawing=false;sendPending()}});
    $('penTool').onclick=()=>{{tool='pen';$('penTool').classList.add('active');$('eraserTool').classList.remove('active')}};$('eraserTool').onclick=()=>{{tool='eraser';$('eraserTool').classList.add('active');$('penTool').classList.remove('active')}};$('clearBtn').onclick=()=>{{clearBoard();ws?.send(JSON.stringify({{type:'clear'}}))}};$('sizeSlider').oninput=e=>{{currentSize=Number(e.target.value)||5;$('sizeValue').textContent=currentSize}};
    function buildPalette(colors){{palette.innerHTML='';(colors||[]).forEach((c,i)=>{{const b=document.createElement('button');b.className='draw-swatch'+(i===0?' active':'');b.style.background=c;b.onclick=()=>{{currentColor=c;[...palette.children].forEach(x=>x.classList.remove('active'));b.classList.add('active')}};palette.appendChild(b)}});if(colors?.length)currentColor=colors[0]}}
    function buildOptions(arr){{opts.innerHTML='';(arr||[]).forEach(w=>{{const b=document.createElement('button');b.className='draw-option-btn';b.textContent=w;b.onclick=()=>sendGuess(w);b.dataset.word=w;opts.appendChild(b)}})}}
    function sendGuess(word){{const v=(word||'').trim();if(!v||ws?.readyState!==1)return;opts.querySelectorAll('button').forEach(b=>b.disabled=true);ws.send(JSON.stringify({{type:'guess',word:v}}))}}
    function startRecording(){{try{{if(role!=='drawer'||!window.MediaRecorder||!canvas.captureStream)return;const stream=canvas.captureStream(12);const mime=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'].find(x=>MediaRecorder.isTypeSupported(x))||'';mediaRecorder=new MediaRecorder(stream,mime?{{mimeType:mime}}:undefined);mediaChunks=[];drawingBlob=null;mediaRecorder.ondataavailable=e=>{{if(e.data?.size)mediaChunks.push(e.data)}};mediaRecorder.onstop=()=>{{if(mediaChunks.length){{drawingBlob=new Blob(mediaChunks,{{type:mediaChunks[0].type||'video/webm'}});lastRoundVideoBlob=drawingBlob}}}};mediaRecorder.start(1000)}}catch(e){{mediaRecorder=null}}}}
    function stopRecording(){{try{{if(mediaRecorder&&mediaRecorder.state!=='inactive')mediaRecorder.stop()}}catch(e){{}}}}
    function stopRecordingAndWait(){{return new Promise(resolve=>{{if(!mediaRecorder||mediaRecorder.state==='inactive')return resolve();const r=mediaRecorder;r.addEventListener('stop',()=>setTimeout(resolve,80),{{once:true}});try{{r.stop()}}catch(e){{resolve()}}}})}}
    function openDrawingReport(){{const old=document.getElementById('drawingConfirm');if(old)old.remove();const m=document.createElement('div');m.id='drawingConfirm';m.className='confirm-overlay';m.innerHTML='<div class="confirm-card"><b>🚩 گزارش نقاشی</b><p>گزارش به تیم پشتیبانی ارسال می‌شود و آنان گزارش را بررسی می‌کنند. اگر گزارش الکی ارسال شود شما محروم می‌شوید.<br><br>آیا از گزارش مطمئن هستید؟</p><button onclick="confirmDrawingReport(true)">بله</button><button class="btn" onclick="confirmDrawingReport(false)">خیر</button></div>';document.body.appendChild(m)}}
    async function confirmDrawingReport(ok){{const m=document.getElementById('drawingConfirm');if(m)m.remove();if(!ok)return;const drawer=(window.__lastDrawer||'');if(!drawer)return alert('نقاش پیدا نشد.');await stopRecordingAndWait();const fd=new FormData();fd.append('target',drawer);fd.append('content','گزارش نقاشی دور جاری');fd.append('drawing_data',JSON.stringify(currentStrokes.slice(0,6000)));const reportVideo=lastRoundVideoBlob||drawingBlob;if(reportVideo)fd.append('video',reportVideo,'drawing.webm');const r=await fetch('/report/drawing',{{method:'POST',body:fd}});const d=await r.json();alert(d.ok?'✅ گزارش برای پشتیبانی ارسال شد.':'❌ ارسال گزارش ناموفق بود.')}}
    function showRoundUI(){{queue.style.display='none';preview.style.display='none';roundInfo.style.display='flex';boardFrame.style.display='block';result.style.display='none';opts.style.display='none';reportBtn.style.display='inline-block';drawerNotice.style.display='none'}}
    function renderResult(d){{if(timerInt)clearInterval(timerInt);stopRecording();roundInfo.style.display='none';boardFrame.style.display='none';palette.style.display='none';tools.style.display='none';wordBox.style.display='none';opts.style.display='none';reportBtn.style.display='inline-block';result.style.display='block';renderPlayers(d.scores,d.active,d.drawer,d.profiles);window.__lastDrawer=d.drawer;const rows=Object.entries(d.scores||{{}}).sort((a,b)=>b[1]-a[1]).map(([u,s],i)=>'<div class="result-row"><span>#'+(i+1)+'</span><b>'+((d.profiles||{{}})[u]?.public_username||u)+'</b><strong>⭐ '+s+' کل</strong></div>').join('');const roundRows=Object.entries(d.points_map||{{}}).map(([u,s])=>'<div class="result-row round-points"><span>+</span><b>'+((d.profiles||{{}})[u]?.public_username||u)+'</b><strong>+'+s+' امتیاز این دور</strong></div>').join('');result.innerHTML='<div class="result-glow">'+(d.correct?'🎯':'⌛')+'</div><div class="draw-result-title">'+(d.correct?'حدس درست بود!':'زمان این دور تمام شد')+'</div><div class="result-word">موضوع: <b>'+String(d.word||'—')+'</b></div><div class="result-subtitle">امتیاز این دور</div><div class="result-table">'+(roundRows||'<div class="report-meta">این دور امتیازی ثبت نشد.</div>')+'</div><div class="result-subtitle">امتیاز کل بازی</div><div class="result-table">'+rows+'</div><div id="breakText" class="draw-result-note"></div><div class="draw-result-exit"><a class="btn glow-btn" href="/lobby">🏠 بازگشت به لابی</a></div>';const bt=$('breakText');countdown(d.break_seconds||10,x=>bt.textContent=d.is_last?'🏁 نتیجه نهایی در حال آماده‌سازی… '+x+' ثانیه':'⚡ دور بعدی تا '+x+' ثانیه دیگر')}}
    function connect(){{ws=new WebSocket(proto+'//'+location.host+WS_PATH);ws.onopen=()=>status.textContent='🟢 وصل شد؛ در حال پیدا کردن بازیکن…';ws.onclose=()=>{{if(!intentionallyLeaving&&!recon)recon=setTimeout(()=>{{recon=null;connect()}},1200)}};ws.onerror=()=>status.textContent='⚠️ اتصال ناپایدار';ws.onmessage=e=>onMsg(JSON.parse(e.data))}}
    function onMsg(d){{if(d.type==='waiting'){{queueUI(d.count,d.needed);return}}if(d.type==='queue_timeout'){{queue.innerHTML='<div class="queue-text">⌛ بازیکنی پیدا نشد. دوباره تلاش کن.</div>';return}}if(d.type==='round_preview'){{role=d.role;window.__lastDrawer=d.drawer;reportBtn.style.display='none';queue.style.display='none';preview.style.display='block';boardFrame.style.display='none';roundInfo.style.display='flex';roundLabel.textContent='دور '+d.round+' از '+d.total_rounds;renderPlayers(d.scores,d.active,d.drawer,d.profiles);previewText.textContent=role==='drawer'?'موضوع نقاشی: '+(d.word||'—'):'موضوع مخفی است؛ آماده حدس‌زدن شو!';preview.classList.toggle('drawer-preview',role==='drawer');previewCountdown(d.remaining||5);status.textContent=role==='drawer'?'✏️ موضوع را ببین و آماده شو!':'🔎 آماده باش';return}}if(d.type==='round_start'){{showRoundUI();role=d.role;window.__lastDrawer=d.drawer;roundLabel.textContent='دور '+d.round+' از '+d.total_rounds;drawerLabel.textContent=role==='drawer'?'✏️ تو نقاشی':'🎯 نقاش: '+(d.profiles?.[d.drawer]?.public_username||d.drawer||'—');window.__profiles=d.profiles||{{}};renderPlayers(d.scores,d.active,d.drawer,d.profiles);boardFrame.classList.toggle('shop-board-glow',(d.profiles?.[me]?.owned_items||[]).includes('draw_glow')||(d.profiles?.[me]?.owned_items||[]).includes('neon_pen'));clearBoard();(d.strokes||[]).forEach(s=>{{paint(s.x0,s.y0,s.x1,s.y1,s.color,s.size);currentStrokes.push(s)}});if(role==='drawer'){{wordBox.style.display='block';wordBox.textContent='🎯 موضوع: '+d.word;palette.style.display='flex';tools.style.display='flex';opts.style.display='none'}}else{{wordBox.style.display='none';palette.style.display='none';tools.style.display='none';opts.style.display='grid';buildOptions(d.options)}}buildPalette(d.colors||[]);startRecording();countdown(d.remaining||d.duration,x=>timer.textContent='⏱ '+x+' ثانیه');status.textContent=role==='drawer'?'✏️ بکش!':'🔎 حدس بزن!';return}}if(d.type==='guess_notice'){{if(role==='drawer'){{drawerNotice.style.display='block';drawerNotice.className='draw-notice '+(d.correct?'ok':'bad');drawerNotice.textContent=d.message}}return}}if(d.type==='draw'){{paint(d.x0,d.y0,d.x1,d.y1,d.color,d.size);currentStrokes.push(d);return}}if(d.type==='draw_batch'){{(d.segments||[]).forEach(s=>{{paint(s.x0,s.y0,s.x1,s.y1,s.color,s.size);currentStrokes.push(s)}});return}}if(d.type==='clear'){{clearBoard();return}}if(d.type==='guess_wrong'){{opts.querySelectorAll('button').forEach(b=>{{b.disabled=true}});const b=opts.querySelector('[data-word="'+CSS.escape(d.word)+'"]');if(b)b.classList.add('wrong');status.textContent='❌ حدست اشتباه بود؛ این دور دیگر امکان حدس نداری.';return}}if(d.type==='correct'){{status.textContent='✅ درست! +'+d.points+' امتیاز';return}}if(d.type==='round_result'){{renderResult(d);return}}if(d.type==='game_over'){{if(timerInt)clearInterval(timerInt);stopRecording();preview.style.display='none';boardFrame.style.display='none';roundInfo.style.display='none';palette.style.display='none';tools.style.display='none';wordBox.style.display='none';opts.style.display='none';reportBtn.style.display='none';result.style.display='block';renderPlayers(d.scores,d.active,null,d.profiles);result.innerHTML='<div class="result-glow">🏆</div><div class="draw-result-title">نتیجه نهایی</div>'+Object.entries(d.scores||{{}}).sort((a,b)=>b[1]-a[1]).map(([u,s],i)=>'<div class="result-row"><span>#'+(i+1)+'</span><b>'+((d.profiles||{{}})[u]?.public_username||u)+'</b><strong>⭐ '+s+'</strong></div>').join('')+'<div class="draw-result-exit"><a class="btn glow-btn" href="/lobby">🏠 بازگشت به لابی</a></div>';return}}if(d.type==='player_left')status.textContent='⚠️ بازیکن خارج شد'}}connect();
    </script>'''
    return page_shell(title,body,username)
BASE_CSS += ".support-review-row{display:flex;gap:7px;justify-content:flex-start;margin-top:8px;flex-wrap:wrap}.support-review-row button{padding:8px 11px;font-size:11px}.league-mini{display:inline-block;margin-top:3px;padding:2px 6px;border-radius:999px;font-size:9px;border:1px solid currentColor}.league-mini.league-bronze{color:#cd7f32}.league-mini.league-davinci{color:#32d9d0}.league-mini.league-picasso{color:#ff5a5a}"

def chat_private_page(username, other, messages, other_display=None):
    title_id=str(other_display or other); initial=_render_messages(messages,username,False)
    receipt_ui=''
    if str(other).lower()=='morad' and username.lower()!='morad':
        receipt_ui='''<div class="receipt-chat-upload"><label class="receipt-btn" for="receiptFile">🧾 ارسال رسید پرداخت</label><input id="receiptFile" type="file" accept="image/jpeg,image/png,image/webp,application/pdf" hidden><span id="receiptStatus" class="report-meta">حداکثر ۸ مگابایت</span></div>'''
    body=f'''<div class="chat-screen page-enter"><div class="chat-top"><div class="chat-toolbar"><div class="chat-title">💬 @{html.escape(title_id)}</div><a class="btn" href="/messages">پیام‌ها</a></div></div><div class="chat-box" id="chatBox">{initial}</div>{receipt_ui}<div class="chat-input-wrap"><div class="chat-input-row"><input type="text" id="msgInput" placeholder="پیامت رو بنویس..." autocomplete="off"><button class="send-btn" onclick="sendMsg()">➤</button></div></div></div><script>const wsProto=location.protocol==='https:'?'wss:':'ws:',ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/private/{html.escape(other)}'),box=document.getElementById('chatBox'),me={username!r};function addMsg(d){{if(d.content===undefined)return;const div=document.createElement('div');div.className='msg '+(d.sender===me?'me':'');const s=document.createElement('span');s.className='sender';s.textContent=d.public_username||d.sender;const c=document.createElement('span');c.className='content';c.textContent=d.content;div.append(s,c);if(d.sender!==me){{const b=document.createElement('button');b.className='report-btn';b.textContent='🚩 گزارش';b.onclick=()=>openReportModal(d.sender,d.content,'chat','');div.append(b)}}box.appendChild(div);box.scrollTop=box.scrollHeight}}ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.type==='friend_required'){{alert('💬 اول باید درخواست دوستی ارسال و پذیرفته شود.');location.href='/profile?u='+encodeURIComponent('{html.escape(other)}');return}}if(d.type==='blocked'){{alert(d.message||'این گفت‌وگو مسدود است.');return}}if(d.content!==undefined)addMsg(d)}};function sendMsg(){{const i=document.getElementById('msgInput'),v=i.value.trim();if(!v||ws.readyState!==1)return;ws.send(JSON.stringify({{content:v}}));i.value=''}}document.getElementById('msgInput').addEventListener('keydown',e=>{{if(e.key==='Enter')sendMsg()}});const rf=document.getElementById('receiptFile');if(rf)rf.addEventListener('change',async()=>{{const f=rf.files[0];if(!f)return;const st=document.getElementById('receiptStatus');if(f.size>8*1024*1024){{st.textContent='❌ فایل بیشتر از ۸ مگابایت است.';rf.value='';return}}st.textContent='⏳ در حال ارسال رسید...';const fd=new FormData();fd.append('receipt',f);try{{const r=await fetch('/support/receipt',{{method:'POST',body:fd}}),d=await r.json();st.textContent=d.ok?'✅ رسید برای پشتیبانی ارسال شد.':('❌ '+(d.message||'ارسال نشد.'));if(d.ok)rf.value=''}}catch(e){{st.textContent='❌ خطا در ارسال رسید.'}}}});box.scrollTop=box.scrollHeight;</script>'''
    return page_shell(f'چت با {title_id}',body,username)

BASE_CSS += """
.receipt-chat-upload{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 12px;margin:8px 0;border:1px dashed #5d43a4;border-radius:14px;background:#100c25}.receipt-chat-upload .receipt-btn{cursor:pointer;display:inline-block}.report-media-video{width:min(100%,720px);max-height:430px;background:#000;border-radius:16px;margin:10px 0;display:block}.danger-btn{border-color:#a33a62!important;color:#ff91b4!important}.support-review-row{display:flex;gap:7px;justify-content:flex-start;margin-top:8px;flex-wrap:wrap}.support-review-row button{padding:8px 11px;font-size:11px}
"""

BASE_CSS += """
.store-item{display:flex;align-items:center;gap:10px;padding:12px;margin-top:9px;border-radius:17px;background:linear-gradient(145deg,#17112f,#0f0a24);border:1px solid #3d2b70;box-shadow:0 8px 20px rgba(0,0,0,.18);transition:transform .18s,box-shadow .18s}.store-item:hover{transform:translateY(-2px);box-shadow:0 12px 25px rgba(0,0,0,.24)}.store-item-icon{width:45px;height:45px;display:grid;place-items:center;border-radius:14px;background:linear-gradient(145deg,#29205a,#171332);font-size:27px;flex:0 0 45px}.store-desc{font-size:11px;color:#9d97b8;margin-top:3px}.store-item .price{font-weight:950;color:#ffd75b;white-space:nowrap}.store-item button{border:0;border-radius:11px;padding:8px 12px;background:linear-gradient(135deg,#00d9ff,#7451ff);color:#fff;font-weight:900;cursor:pointer}.store-league{border-color:#6b4bd0}.store-section-note{font-size:11px;color:#9d97b8}.league-davinci{color:#32d9d0}.league-picasso{color:#ff5a5a}
"""

# ===== V4.2 FINAL OVERRIDES =====
def shop_page(username, wallet=None, owned=None):
    w = wallet or {'coins': 500, 'diamonds': 5, 'streak': 0}
    owned = set(owned or [])
    items = [
        ('neon_pen','✏️','قلم نئونی','هاله درخشان قلم در بازی','250','custom'),
        ('profile_frame','🖼️','قاب درخشان','قاب ویژه آواتار','400','custom'),
        ('victory_fx','✨','افکت پیروزی','افکت ویژه نتیجه برد','650','custom'),
        ('crown_badge','👑','نشان تاج','تاج کنار نام کاربری','900','custom'),
        ('chat_bubble','💬','حباب چت','حباب ویژه پیام‌ها','300','custom'),
        ('name_effect','🌟','افکت نام','درخشش متحرک نام','500','custom'),
        ('draw_glow','🖌️','قلم نورانی','هاله ویژه تخته','450','custom'),
        ('bronze_frame','🥉','قاب برنزی','ویژه لیگ برنزی • ۲۵۰ جام','550','league'),
        ('bronze_badge','🏅','نشان برنزی','ویژه لیگ برنزی','350','league'),
        ('davinci_frame','🔷','قاب داوینچی','ویژه لیگ داوینچی • ۷۵۰ جام','1100','league'),
        ('davinci_effect','💠','افکت داوینچی','ویژه لیگ داوینچی','900','league'),
        ('picasso_frame','🔴','قاب پیکاسو','ویژه لیگ پیکاسو • ۱۵۰۰ جام','1800','league'),
        ('picasso_effect','🎨','افکت پیکاسو','ویژه لیگ پیکاسو','1500','league'),
        ('gold_frame',f'<img alt="" style="width:100%;height:100%;object-fit:contain;display:block" src="data:image/webp;base64,{GOLD_FRAME_ICON_B64}">','قاب طلایی افسانه‌ای','قاب اختصاصی دور آواتار با تاج و ستاره طلایی','1300','custom'),
        ('ice_frame',f'<img alt="" style="width:100%;height:100%;object-fit:contain;display:block" src="data:image/webp;base64,{ICE_FRAME_ICON_B64}">','قاب یخی الماسی','قاب اختصاصی دور آواتار با کریستال‌های یخی درخشان','1300','custom')]
    def cards(kind):
        out=[]
        for key,ic,name,desc,cost,k in items:
            if k != kind: continue
            css='store-league' if k=='league' else 'store-custom'
            is_owned = key in owned
            purchased_cls = ' purchased' if is_owned else ''
            btn_html = '<button class="store-buy" disabled>✓ فعال</button>' if is_owned else f'<button class="store-buy" onclick="buyItem(\'{key}\')">خرید</button>'
            badge_html = '<span class="shop-active-badge">✨ فعال</span>' if is_owned else ''
            out.append(f'<div class="store-item {css}{purchased_cls}" data-item="{key}"><div class="store-item-icon">{ic}</div><div class="grow"><b>{name}</b><div class="store-desc">{desc}</div>{badge_html}</div><span class="price">{cost} 🪙</span>{btn_html}</div>')
        return ''.join(out)
    body=f'''<div class="page-heading"><div><div class="sub">ARCADE STORE • CUSTOMIZE</div><h1>🛍️ فروشگاه</h1></div><a class="btn" href="/lobby">خانه</a></div>
    <div class="card hero store-wallet"><div class="coin-bar"><span class="coin-pill">🪙 <b id="coinBalance">{int(w.get('coins',500) or 0):,}</b> سکه</span><span class="coin-pill">💎 {int(w.get('diamonds',5) or 0)} الماس</span><span class="coin-pill">🔥 {int(w.get('streak',0) or 0)} روز</span></div></div>
    <div class="card coin-pack-card"><div class="coin-pack-icon">🪙</div><h2>۱۰۰۰ سکه</h2><p>۱۰۰٬۰۰۰ تومان</p><div class="coin-pack-cardnum">💳 ۶۲۱۹۸۶۱۸۵۱۱۶۰۰۶۸</div><p>بعد از واریز، رسید را برای پشتیبانی ارسال کن.</p><a class="glow-btn receipt-shop-btn" href="/chat/private/morad">🧾 ارسال رسید</a></div>
    <div class="card"><h2>🎨 شخصی‌سازی</h2><p class="store-section-note">خریدها با سکه انجام می‌شوند و روی حسابت باقی می‌مانند.</p>{cards('custom')}</div>
    <div class="card"><h2>🏆 آیتم‌های مخصوص لیگ</h2><p class="store-section-note">برای خرید باید حداقل جام همان لیگ را داشته باشی.</p>{cards('league')}</div>
    <div id="shopToast" class="shop-toast"></div><script>
    async function buyItem(key){{const card=document.querySelector('[data-item="'+CSS.escape(key)+'"]'),btn=card?.querySelector('.store-buy');if(btn)btn.disabled=true;try{{const r=await fetch('/shop/buy',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{item_key:key}})}});const d=await r.json();if(d.ok){{document.getElementById('coinBalance').textContent=Number(d.wallet.coins||0).toLocaleString('fa-IR');if(card){{card.classList.add('purchased','activate-burst');if(btn){{btn.outerHTML='<button class="store-buy" disabled>✓ فعال</button>'}}const badgeHost=card.querySelector('.grow');if(badgeHost&&!badgeHost.querySelector('.shop-active-badge')){{const b=document.createElement('span');b.className='shop-active-badge';b.textContent='✨ فعال';badgeHost.appendChild(b)}}setTimeout(()=>card.classList.remove('activate-burst'),900)}}toast('✨ آیتم خریداری شد و فعال است');}}else if(d.status==='owned')toast('این آیتم را قبلاً داری.');else if(d.status==='league_locked')toast('🏆 این آیتم برای لیگ تو باز نشده.');else if(d.status==='not_enough')toast('🪙 سکه کافی نیست.');else toast('❌ خرید انجام نشد.')}}catch(e){{toast('❌ خطای ارتباط با فروشگاه.')}}finally{{if(btn&&!card?.classList.contains('purchased'))btn.disabled=false}}}}
    function toast(t){{const x=document.getElementById('shopToast');x.textContent=t;x.classList.add('show');setTimeout(()=>x.classList.remove('show'),2200)}}
    </script>'''
    return page_shell('فروشگاه',body,username)


def chat_private_page(username, other, messages, other_display=None):
    title_id=str(other_display or other)
    initial=_render_messages(messages,username,False)
    receipt=''
    if str(other).lower()=='morad' and username.lower()!='morad':
        receipt='''<div class="receipt-chat-upload"><label class="receipt-btn" for="receiptFile">🧾 ارسال رسید پرداخت</label><input id="receiptFile" type="file" accept="image/jpeg,image/png,image/webp,application/pdf" hidden><span id="receiptStatus" class="report-meta">تصویر یا PDF • حداکثر ۸ مگابایت</span></div>'''
    body=f'''<div class="chat-screen page-enter"><div class="chat-top"><div class="chat-toolbar"><div class="chat-title">💬 @{html.escape(title_id)} <span id="presenceDot" style="font-size:10px;color:#888">● بررسی...</span></div><a class="btn" href="/messages">پیام‌ها</a></div></div><div class="chat-box" id="chatBox">{initial}</div>{receipt}<div class="chat-input-wrap"><div class="chat-input-row"><input type="text" id="msgInput" placeholder="پیامت رو بنوی..." autocomplete="off"><button class="send-btn" onclick="sendMsg()">➤</button></div></div></div><script>
    const wsProto=location.protocol==='https:'?'wss:':'ws:',ws=new WebSocket(wsProto+'//'+location.host+'/ws/chat/private/{quote(other,safe="")}'),box=document.getElementById('chatBox'),me={username!r},dot=document.getElementById('presenceDot');
    function addMsg(d){{if(d.content===undefined)return;const div=document.createElement('div');div.className='msg '+(d.sender===me?'me':'')+((d.owned_items||[]).includes('chat_bubble')?' chat-bubble-owned':'');const s=document.createElement('span');s.className='sender';s.textContent=d.public_username||d.sender;const c=document.createElement('span');c.className='content';c.textContent=d.content;div.append(s,c);if(d.sender!==me){{const b=document.createElement('button');b.className='report-btn';b.textContent='🚩 گزارش';b.onclick=()=>openReportModal(d.sender,d.content,'chat','');div.append(b)}}box.appendChild(div);box.scrollTop=box.scrollHeight}}
    ws.onopen=()=>{{dot.textContent='● آنلاین';dot.style.color='#35df7a'}};ws.onclose=()=>{{dot.textContent='● اتصال قطع شد';dot.style.color='#ff6b8b'}};ws.onmessage=e=>{{const d=JSON.parse(e.data);if(d.type==='blocked'||d.type==='friend_required'){{alert(d.message||'ابتدا درخواست دوستی را قبول کنید.');return}}if(d.content!==undefined)addMsg(d)}};
    function sendMsg(){{const i=document.getElementById('msgInput'),v=i.value.trim();if(!v)return;if(ws.readyState!==1){{alert('⏳ اتصال چت برقرار نیست.');return}}ws.send(JSON.stringify({{content:v}}));i.value=''}}document.getElementById('msgInput').addEventListener('keydown',e=>{{if(e.key==='Enter')sendMsg()}});
    async function presence(){{try{{const d=await (await fetch('/presence/'+encodeURIComponent({other!r}))).json();dot.textContent=d.online?'● آنلاین':'● آفلاین';dot.style.color=d.online?'#35df7a':'#888'}}catch(e){{}}}}presence();setInterval(presence,5000);box.scrollTop=box.scrollHeight;
    const rf=document.getElementById('receiptFile');if(rf)rf.addEventListener('change',async()=>{{const f=rf.files[0];if(!f)return;const st=document.getElementById('receiptStatus');if(f.size>8*1024*1024){{st.textContent='❌ فایل بیشتر از ۸ مگابایت است.';rf.value='';return}}st.textContent='⏳ در حال ارسال...';const fd=new FormData();fd.append('receipt',f);try{{const r=await fetch('/support/receipt',{{method:'POST',body:fd}});const d=await r.json();st.textContent=d.ok?'✅ رسید برای پشتیبانی ارسال شد.':'❌ '+(d.message||'ارسال نشد.');if(d.ok)rf.value=''}}catch(e){{st.textContent='❌ خطای ارتباط با سرور.'}}}});</script>'''
    return page_shell(f'چت با {title_id}',body,username)

BASE_CSS += """
/* V4.2 working store, report media and customization */
.store-item{display:flex;align-items:center;gap:9px;padding:11px;margin:7px 0;border-radius:16px;background:linear-gradient(145deg,#17102f,#0d0a20);border:1px solid #3c2b67;transition:.18s}.store-item:hover{transform:translateY(-1px);border-color:#7d4fe0}.store-item.purchased{border-color:#27d8ad;box-shadow:0 0 18px rgba(39,216,173,.12)}.store-item-icon{width:42px;height:42px;display:grid;place-items:center;border-radius:13px;background:#24144a;font-size:24px;flex:0 0 42px}.store-desc{font-size:10px;color:#a49cbd;margin-top:3px}.store-item .price{white-space:nowrap;color:#ffd85c;font-weight:950;font-size:11px}.store-item button{padding:8px 11px;border-radius:11px;background:linear-gradient(135deg,#00cfff,#7850ff);color:#fff;border:0;font-weight:900;white-space:nowrap}.store-item button:disabled{opacity:.65}.store-section-note{color:#a9a1bd;font-size:11px}.shop-toast{position:fixed;left:50%;bottom:25px;transform:translate(-50%,20px);opacity:0;pointer-events:none;z-index:9999;background:#15102c;color:#fff;border:1px solid #6c42bc;border-radius:14px;padding:11px 16px;box-shadow:0 10px 30px rgba(0,0,0,.35);transition:.2s}.shop-toast.show{opacity:1;transform:translate(-50%,0)}.has-frame{box-shadow:0 0 0 2px rgba(255,205,90,.35),0 0 28px rgba(255,92,210,.12)!important}.name-glow h1,.name-effect-owned{animation:shopNameGlow 1.8s ease-in-out infinite alternate}.chat-bubble-owned{border-color:#6f50d9!important;box-shadow:0 6px 18px rgba(111,80,217,.18)!important}.shop-board-glow{border-color:#ff52d2!important;box-shadow:0 0 30px rgba(255,82,210,.30),0 0 65px rgba(50,217,208,.12)!important}.shop-badge{display:inline-block;margin-top:5px;padding:3px 8px;border-radius:999px;background:linear-gradient(135deg,#ffd75a,#ff8a4c);color:#2a1230;font-size:10px;font-weight:1000}.report-media-video{display:block;width:100%;max-height:520px;object-fit:contain;background:#05050d;border-radius:14px}@keyframes shopNameGlow{from{text-shadow:0 0 4px rgba(103,234,255,.2)}to{text-shadow:0 0 16px rgba(255,83,211,.65)}}@media(max-width:600px){.store-item{padding:9px;gap:7px}.store-item-icon{width:38px;height:38px;flex-basis:38px;font-size:21px}.store-item .price{font-size:9px}.store-item button{padding:7px 8px;font-size:10px}}
"""

BASE_CSS += """
.victory-owned{animation:victoryPulse .8s ease-in-out infinite alternate!important;border-color:#ffd75a!important;box-shadow:0 0 30px rgba(255,215,90,.28),0 0 70px rgba(255,72,203,.12)!important}@keyframes victoryPulse{from{transform:scale(1)}to{transform:scale(1.012)}}
"""

BASE_CSS += """
/* V5 — leaderboard avatar fix (top-3 circular, rest rounded-square) + shop activation polish */
.leader-avatar-fallback{display:flex!important;align-items:center;justify-content:center;background:linear-gradient(145deg,#2b2052,#14102d);color:#7d70b8;font-size:16px}
.leader-podium-card .leader-avatar,.leader-podium-card .leader-avatar-fallback{width:82px;height:82px;margin:auto;border-radius:50%;object-fit:cover;border:3px solid #fff;box-shadow:0 0 18px rgba(255,255,255,.22);display:flex}
.leader-podium-card.rank-1 .leader-avatar,.leader-podium-card.rank-1 .leader-avatar-fallback{width:104px;height:104px;border-color:#ff8be5;box-shadow:0 0 25px rgba(255,79,216,.55);font-size:22px}
.leader-list-avatar{width:34px;height:34px;flex:0 0 34px}
.leader-list-avatar .leader-avatar,.leader-list-avatar .leader-avatar-fallback{width:34px;height:34px;border-radius:10px!important;object-fit:cover;border:1px solid #6c55b0;display:flex}
.leader-row{overflow:hidden}
.leader-podium-card.league-bronze{border-color:#cd7f32}.leader-podium-card.league-davinci{border-color:#32d9d0}.leader-podium-card.league-picasso{border-color:#ff4a4a}
@media(max-width:600px){.leader-list-avatar,.leader-list-avatar .leader-avatar,.leader-list-avatar .leader-avatar-fallback{width:30px;height:30px;flex-basis:30px}}
.store-item{position:relative;overflow:hidden}
.store-item .grow{position:relative;z-index:1}
.shop-active-badge{display:inline-block;margin-top:4px;padding:2px 8px;border-radius:999px;background:linear-gradient(135deg,#27d8ad,#19b8ff);color:#04231c;font-size:9px;font-weight:1000;animation:shopActivePulse 1.6s ease-in-out infinite}
@keyframes shopActivePulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.75;transform:scale(1.05)}}
.store-item.purchased{border:1px solid transparent;background:linear-gradient(145deg,#17102f,#0d0a20) padding-box,conic-gradient(from 0deg,#27d8ad,#19b8ff,#ff52d2,#ffd75a,#27d8ad) border-box;animation:shopFrameSpin 4s linear infinite}
.store-item.purchased .store-item-icon{background:linear-gradient(145deg,#0f3d33,#0d0a20);box-shadow:0 0 14px rgba(39,216,173,.35)}
.store-item.purchased .store-buy{background:linear-gradient(135deg,#27d8ad,#19b8ff)!important;opacity:1!important;cursor:default}
@keyframes shopFrameSpin{to{filter:hue-rotate(360deg)}}
.store-item.activate-burst{animation:shopFrameSpin 4s linear infinite,shopBurst .7s ease-out}
@keyframes shopBurst{0%{box-shadow:0 0 0 0 rgba(39,216,173,.55),0 0 0 0 rgba(25,184,255,.35);transform:scale(1)}40%{transform:scale(1.035)}100%{box-shadow:0 0 0 18px rgba(39,216,173,0),0 0 0 30px rgba(25,184,255,0);transform:scale(1)}}
"""

BASE_CSS += """
/* V6 — real shop item activation */
.frame-premium{border:2px solid transparent!important;background:linear-gradient(var(--surface),var(--surface)) padding-box,conic-gradient(from 0deg,#00e5ff,#7c4dff,#ff4fd8,#ffd54a,#00e5ff) border-box!important;box-shadow:0 0 22px rgba(124,77,255,.28),inset 0 0 22px rgba(0,229,255,.06)!important;animation:premiumFrameSpin 5s linear infinite}
.frame-bronze{border:2px solid #cd7f32!important;box-shadow:0 0 22px rgba(205,127,50,.38),inset 0 0 20px rgba(205,127,50,.08)!important}
.frame-davinci{border:2px solid #32d9d0!important;box-shadow:0 0 25px rgba(50,217,208,.48),inset 0 0 24px rgba(50,217,208,.09)!important;animation:davinciPulse 1.8s ease-in-out infinite alternate}
.frame-picasso{border:2px solid #ff4a4a!important;box-shadow:0 0 25px rgba(255,74,74,.45),0 0 50px rgba(255,82,210,.12)!important;animation:picassoPulse 1.6s ease-in-out infinite alternate}
.frame-gold{border:2px solid #ffd75a!important;box-shadow:0 0 25px rgba(255,215,90,.5),0 0 55px rgba(255,170,20,.16)!important;animation:goldFramePulse 1.8s ease-in-out infinite alternate}
.frame-ice{border:2px solid #52d6ff!important;box-shadow:0 0 25px rgba(82,214,255,.5),0 0 55px rgba(120,220,255,.16)!important;animation:iceFramePulse 1.8s ease-in-out infinite alternate}
@keyframes goldFramePulse{from{box-shadow:0 0 14px rgba(255,215,90,.3)}to{box-shadow:0 0 34px rgba(255,215,90,.65)}}
@keyframes iceFramePulse{from{box-shadow:0 0 14px rgba(82,214,255,.3)}to{box-shadow:0 0 34px rgba(82,214,255,.65)}}
.has-img-frame{position:relative!important;overflow:visible!important}
.avatar-frame-img,.profile-head>div:first-child img.avatar-frame-img,.has-img-frame img.avatar-frame-img{position:absolute!important;top:50%!important;left:50%!important;transform:translate(-50%,-50%)!important;max-width:none!important;max-height:none!important;pointer-events:none;z-index:5;object-fit:contain!important;border-radius:0!important;width:170%!important;height:170%!important;filter:drop-shadow(0 0 6px rgba(0,0,0,.25))}
.frame-img-gold,.profile-head>div:first-child img.frame-img-gold,.has-img-frame img.frame-img-gold{width:172%!important;height:172%!important}
.frame-img-ice,.profile-head>div:first-child img.frame-img-ice,.has-img-frame img.frame-img-ice{width:163%!important;height:163%!important}
.store-item-icon-img{width:100%;height:100%;object-fit:contain}
.shop-badge.gold-owned{background:linear-gradient(135deg,#ffe58a,#ffb02e);color:#3a2400}
.shop-badge.ice-owned{background:linear-gradient(135deg,#bdf3ff,#4fc7ff);color:#04283b}
@media(max-width:600px){.avatar-frame-img{filter:none}}
.gold-spark{position:absolute;width:5px;height:5px;border-radius:50%;background:radial-gradient(circle,#fff8e0,#ffd75a 55%,transparent 75%);opacity:0;pointer-events:none;z-index:6;animation:goldSparkTwinkle 2.2s ease-in-out infinite}
.gold-spark-1{top:6%;left:20%;animation-delay:0s}
.gold-spark-2{top:12%;left:76%;animation-delay:.6s}
.gold-spark-3{top:80%;left:14%;animation-delay:1.2s}
.gold-spark-4{top:84%;left:82%;animation-delay:1.7s}
@keyframes goldSparkTwinkle{0%,100%{opacity:0;transform:scale(.3) translateY(0)}45%{opacity:1;transform:scale(1.3) translateY(-2px)}70%{opacity:.5;transform:scale(.8) translateY(0)}}
.ice-shard{position:absolute;width:3px;height:9px;background:linear-gradient(180deg,#eafcff,#4fd1ff);border-radius:2px;opacity:0;pointer-events:none;z-index:6;animation:iceShardFall 2.8s ease-in infinite;box-shadow:0 0 4px rgba(120,220,255,.8)}
.ice-shard-1{top:4%;left:16%;animation-delay:.1s}
.ice-shard-2{top:2%;left:80%;animation-delay:1s}
.ice-shard-3{top:88%;left:30%;animation-delay:1.8s}
.ice-shard-4{top:90%;left:68%;animation-delay:2.3s}
@keyframes iceShardFall{0%{opacity:0;transform:translateY(-4px) scale(.6) rotate(0deg)}18%{opacity:1}65%{opacity:.7}100%{opacity:0;transform:translateY(16px) scale(.85) rotate(12deg)}}
@media(prefers-reduced-motion:reduce){.gold-spark,.ice-shard{animation:none;opacity:0}}
.effect-davinci{position:relative;box-shadow:0 0 30px rgba(50,217,208,.35),inset 0 0 35px rgba(50,217,208,.06)!important}
.effect-picasso{position:relative;box-shadow:0 0 30px rgba(255,74,74,.32),0 0 65px rgba(255,82,210,.16),inset 0 0 35px rgba(255,74,74,.06)!important}
.effect-davinci::after,.effect-picasso::after{content:"";position:absolute;inset:6px;border-radius:inherit;pointer-events:none;opacity:.55;animation:itemAura 1.5s ease-in-out infinite alternate}
.effect-davinci::after{border:1px solid rgba(50,217,208,.55)}
.effect-picasso::after{border:1px solid rgba(255,74,74,.55)}
.crown-owned{animation:crownBounce 1.4s ease-in-out infinite alternate}
.bronze-owned{background:linear-gradient(135deg,#cd7f32,#7a3f17)!important;color:#fff!important}
.davinci-owned{background:linear-gradient(135deg,#32d9d0,#157f8b)!important;color:#041b20!important}
.picasso-owned{background:linear-gradient(135deg,#ff5a5a,#a51e63)!important;color:#fff!important}
.neon-pen-store{box-shadow:0 0 18px rgba(0,229,255,.35)!important}
.store-item[data-item="neon_pen"] .store-item-icon{filter:drop-shadow(0 0 7px rgba(0,229,255,.65))}
.store-item[data-item="davinci_frame"] .store-item-icon,.store-item[data-item="davinci_effect"] .store-item-icon{filter:drop-shadow(0 0 8px rgba(50,217,208,.75))}
.store-item[data-item="picasso_frame"] .store-item-icon,.store-item[data-item="picasso_effect"] .store-item-icon{filter:drop-shadow(0 0 8px rgba(255,74,74,.75))}
.store-item[data-item="victory_fx"] .store-item-icon{animation:crownBounce 1s ease-in-out infinite alternate}
@keyframes premiumFrameSpin{to{filter:hue-rotate(360deg)}}
@keyframes davinciPulse{from{box-shadow:0 0 14px rgba(50,217,208,.25)}to{box-shadow:0 0 34px rgba(50,217,208,.58)}}
@keyframes picassoPulse{from{box-shadow:0 0 14px rgba(255,74,74,.22)}to{box-shadow:0 0 34px rgba(255,74,74,.52)}}
@keyframes itemAura{from{transform:scale(.985);opacity:.25}to{transform:scale(1);opacity:.8}}
@keyframes crownBounce{from{transform:translateY(0) rotate(-2deg)}to{transform:translateY(-2px) rotate(2deg)}}
"""

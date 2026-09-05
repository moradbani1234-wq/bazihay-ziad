import asyncio
import io
import os
import secrets
import time
from urllib.parse import quote

from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from starlette.middleware.sessions import SessionMiddleware

import auth
import database as db
import templates as tpl
import words_draw

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "change-this-secret-in-production"),
)


# ============================================================
#                        STARTUP
# ============================================================

@app.on_event("startup")
async def on_startup():
    await db.init_db()
    # حساب پشتیبانی را در هر Deploy تضمین و رمز آن را همگام می‌کنیم.
    # حساب پشتیبانی از تمام محرومیت‌های کاربری مستثناست.
    pwd_hash, salt = auth.hash_password("moradzarifiqpmoradzarifiqp")
    await db.ensure_support_account("morad", pwd_hash, salt)


# ============================================================
#                    AUTH: SIGNUP / LOGIN
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if request.session.get("username"):
        return RedirectResponse("/lobby")
    return RedirectResponse("/login")


@app.get("/signup", response_class=HTMLResponse)
async def signup_get():
    return tpl.signup_page()


@app.post("/signup", response_class=HTMLResponse)
async def signup_post(request: Request, username: str = Form(...), password: str = Form(...)):
    username = username.strip()
    if len(username) < 3:
        return tpl.signup_page("نام کاربری باید حداقل ۳ حرف باشد.")
    if len(password) < 4:
        return tpl.signup_page("رمز عبور باید حداقل ۴ حرف باشد.")

    pwd_hash, salt = auth.hash_password(password)
    ok = await db.create_user(username, pwd_hash, salt)
    if not ok:
        return tpl.signup_page("این نام کاربری قبلاً گرفته شده.")

    request.session["username"] = username
    return RedirectResponse("/lobby", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_get():
    return tpl.login_page()


@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    username = username.strip()
    user = await db.get_user(username)
    if not user or not auth.verify_password(password, user["salt"], user["password_hash"]):
        return tpl.login_page("نام کاربری یا رمز عبور اشتباه است.")

    request.session["username"] = username
    return RedirectResponse("/lobby", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


def _require_login(request: Request) -> str | None:
    return request.session.get("username")



GAME_SCOPE = "games"
CHAT_SCOPE = "chat"
DRAW_SCOPE = "drawing"
TTT_SCOPE = "tictactoe"

async def _ban_for(username: str, scope: str):
    return await db.get_active_ban(username, scope)

def _is_support(username: str) -> bool:
    return username == "morad"

async def _require_scope(request: Request, scope: str):
    username = _require_login(request)
    if not username:
        return None, RedirectResponse("/login")
    if _is_support(username):
        return username, None
    ban = await _ban_for(username, scope)
    if ban:
        remaining = max(0, ban["until_ts"] - int(time.time()))
        return None, tpl.banned_page(username, ban["scope"], remaining, ban.get("reason", ""))
    return username, None

async def _require_game_scope(request: Request, game_scope: str):
    username = _require_login(request)
    if not username:
        return None, RedirectResponse("/login")
    if _is_support(username):
        return username, None
    for scope in (game_scope, "games"):
        ban = await _ban_for(username, scope)
        if ban:
            remaining = max(0, ban["until_ts"] - int(time.time()))
            return None, tpl.banned_page(username, ban["scope"], remaining, ban.get("reason", ""))
    return username, None

@app.post("/report")
async def report_content(request: Request):
    username = _require_login(request)
    if not username:
        return {"ok": False, "error": "login_required"}
    try:
        data = await request.json()
    except Exception:
        return {"ok": False, "error": "bad_request"}
    target = str(data.get("target") or "").strip()[:64]
    content = str(data.get("content") or "").strip()[:500]
    context = str(data.get("context") or "chat")[:32]
    attachment = str(data.get("attachment") or "")
    if attachment and len(attachment) > 350000:
        attachment = ""
    if not target or target == username or not content:
        return {"ok": False, "error": "invalid"}
    if not await db.get_user(target):
        return {"ok": False, "error": "user_not_found"}
    await db.create_report(username, target, context, content, attachment or None)
    return {"ok": True}

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    rows = await db.leaderboard()
    return tpl.leaderboard_page(username, rows)

@app.post("/game/leave")
async def game_leave(request: Request):
    username = _require_login(request)
    if not username:
        return {"ok": False}
    # بازگشت به لابی محرومیت ندارد؛ اگر حریف هنوز داخل بازی باشد، همان حریف
    # برنده اعلام می‌شود و امتیاز برد می‌گیرد.
    await ttt_manager.leave(username)
    await drawing_manager.leave(username)
    return {"ok": True, "redirect": "/lobby"}

@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    username = _require_login(request)
    if not username or not _is_support(username):
        return RedirectResponse("/lobby")
    return tpl.support_page(username, await db.get_reports(), await db.get_active_bans(), await db.get_support_tickets())

@app.post("/support/ban")
async def support_ban(request: Request):
    username = _require_login(request)
    if not username or not _is_support(username):
        return {"ok": False, "error": "forbidden"}
    data = await request.json()
    target = str(data.get("target") or "").strip()[:64]
    scope = str(data.get("scope") or "games")
    # مدت محرومیت می‌تواند به‌صورت ساعت (hours) و/یا دقیقه (minutes) ارسال شود؛
    # این دو با هم جمع می‌شوند تا هم محرومیت چند دقیقه‌ای هم چند ساعته ممکن باشد.
    hours = float(data.get("hours") or 0) + float(data.get("minutes") or 0) / 60.0
    reason = str(data.get("reason") or "نقض قوانین")[:300]
    allowed = {"games","chat","drawing","tictactoe","all"}
    if not target or target == "morad" or scope not in allowed or hours <= 0 or hours > 168:
        return {"ok": False, "error": "invalid"}
    until = await db.ban_user(target, scope, hours, reason)
    if data.get("report_id"):
        await db.resolve_report(int(data["report_id"]))
    return {"ok": True, "until": until}

@app.post("/support/unban")
async def support_unban(request: Request):
    username = _require_login(request)
    if not username or not _is_support(username):
        return {"ok": False, "error": "forbidden"}
    data = await request.json()
    target = str(data.get("target") or "").strip()[:64]
    scope = str(data.get("scope") or "all")
    allowed = {"games","chat","drawing","tictactoe","all"}
    if not target or scope not in allowed:
        return {"ok": False, "error": "invalid"}
    await db.unban_user(target, scope)
    return {"ok": True}

@app.get("/profile", response_class=HTMLResponse)
async def profile_query_page(request: Request, u: str = ""):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    target = str(u or "").strip()
    if target.startswith("@"):
        target = target[1:]
    if not target:
        target = username
    prof = await db.profile(target)
    if not prof:
        return HTMLResponse("کاربر پیدا نشد.", status_code=404)
    return tpl.profile_page(username, prof)


@app.get("/profile/{target}", response_class=HTMLResponse)
async def profile_page(request: Request, target: str):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    prof = await db.profile(target)
    if not prof:
        return HTMLResponse("کاربر پیدا نشد.", status_code=404)
    return tpl.profile_page(username, prof)

@app.post("/friends/request")
async def friends_request(request: Request):
    username = _require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); target=str(data.get("target") or "").strip()
    ok, status=await db.send_friend_request(username,target)
    return {"ok":ok,"status":status}

@app.post("/friends/request/form")
async def friends_request_form(request: Request, target: str = Form(...)):
    username=_require_login(request)
    if not username: return RedirectResponse('/login')
    ok,status=await db.send_friend_request(username,target.strip())
    return RedirectResponse('/profile?u='+quote(target.strip(),safe=''),status_code=303)

@app.post("/friends/respond")
async def friends_respond(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); sender=str(data.get("sender") or "").strip(); accept=bool(data.get("accept"))
    ok=await db.respond_friend_request(sender,username,accept)
    return {"ok":ok}

@app.get("/friends")
async def friends_data(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    return {"ok":True,"friends":await db.friends_for(username),"requests":await db.friend_requests_for(username)}

@app.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    username=_require_login(request)
    if not username: return RedirectResponse("/login")
    return tpl.messages_page(username, await db.friends_for(username), await db.friend_requests_for(username))

@app.get("/support/ticket", response_class=HTMLResponse)
async def support_ticket_page(request: Request):
    username, blocked = await _require_scope(request, "chat")
    if blocked: return blocked
    return tpl.support_ticket_page(username)

@app.post("/support/ticket")
async def support_ticket_post(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); subject=str(data.get("subject") or "").strip(); content=str(data.get("content") or "").strip()
    if not subject or not content: return {"ok":False,"error":"empty"}
    tid=await db.create_support_ticket(username,subject,content)
    # Also place it in the existing support report stream for backward compatibility.
    await db.create_report(username,"morad","support_ticket",f"[{subject}]\n{content}")
    return {"ok":True,"ticket_id":tid}

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    return tpl.settings_page(username, await db.profile(username))

@app.post("/settings/profile")
async def settings_profile(request: Request):
    username = _require_login(request)
    if not username:
        return {"ok": False, "error": "login_required"}
    data = await request.json()
    avatar = str(data.get("avatar") or "🎮")
    if avatar.startswith("data:image/") and len(avatar) > 180000:
        return {"ok": False, "error": "image_too_large"}
    if avatar.startswith("data:") and not avatar.startswith("data:image/"):
        return {"ok": False, "error": "bad_image"}
    await db.update_profile(username, str(data.get("display_name") or username), str(data.get("bio") or ""), avatar)
    return {"ok": True}

@app.post("/settings/password")
async def settings_password(request: Request):
    username = _require_login(request)
    if not username:
        return {"ok": False, "error": "login_required"}
    data = await request.json()
    old = str(data.get("old_password") or "")
    new = str(data.get("new_password") or "")
    user = await db.get_user(username)
    if not user or not auth.verify_password(old, user["salt"], user["password_hash"]):
        return {"ok": False, "error": "old_password"}
    if len(new) < 4:
        return {"ok": False, "error": "short_password"}
    h, salt = auth.hash_password(new)
    await db.update_password(username, h, salt)
    return {"ok": True}

# ============================================================
#                          LOBBY
# ============================================================

@app.get("/lobby", response_class=HTMLResponse)
async def lobby(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    return tpl.lobby_page(username)

@app.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request):
    username=_require_login(request)
    if not username: return RedirectResponse("/login")
    return tpl.shop_page(username)

@app.get("/games", response_class=HTMLResponse)
async def games_page(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    # صفحه انتخاب حالت؛ محرومیت بازی همچنان در خود اتصال بازی بررسی می‌شود.
    return tpl.games_page(username)


@app.post("/chat/private/start")
async def start_private_chat(request: Request, other: str = Form(...)):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    other = other.strip()
    if not other or other == username or not await db.get_user(other):
        return RedirectResponse("/lobby", status_code=303)
    return RedirectResponse(f"/chat/private/{other}", status_code=303)


# ============================================================
#                       PUBLIC CHAT
# ============================================================

@app.get("/chat/public", response_class=HTMLResponse)
async def chat_public(request: Request):
    username, blocked = await _require_scope(request, "chat")
    if blocked: return blocked
    history = await db.get_recent_messages("public")
    return tpl.chat_public_page(username, history)


class ChatManager:
    def __init__(self):
        self.public_conns: set[WebSocket] = set()
        self.private_conns: dict[str, set[WebSocket]] = {}

    async def connect_public(self, ws: WebSocket):
        await ws.accept()
        self.public_conns.add(ws)

    def disconnect_public(self, ws: WebSocket):
        self.public_conns.discard(ws)

    async def broadcast_public(self, sender: str, content: str, reply_to_id=None):
        mid = await db.save_message("public", sender, content, reply_to_id)
        prof = await db.profile(sender)
        payload = {"id": mid, "sender": sender, "content": content, "reply_to_id": reply_to_id, "created_at": int(time.time()), "avatar": (prof or {}).get("avatar", "🎮"), "display_name": (prof or {}).get("display_name", sender)}
        dead = []
        for ws in self.public_conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.public_conns.discard(ws)

    async def connect_private(self, room: str, ws: WebSocket):
        await ws.accept()
        self.private_conns.setdefault(room, set()).add(ws)

    def disconnect_private(self, room: str, ws: WebSocket):
        if room in self.private_conns:
            self.private_conns[room].discard(ws)

    async def broadcast_private(self, room: str, sender: str, content: str, reply_to_id=None):
        mid = await db.save_message(room, sender, content, reply_to_id)
        prof = await db.profile(sender)
        payload = {"id": mid, "sender": sender, "content": content, "reply_to_id": reply_to_id, "created_at": int(time.time()), "avatar": (prof or {}).get("avatar", "🎮"), "display_name": (prof or {}).get("display_name", sender)}
        for ws in list(self.private_conns.get(room, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                pass


chat_manager = ChatManager()


@app.websocket("/ws/chat/public")
async def ws_chat_public(websocket: WebSocket):
    username = websocket.session.get("username")
    if not username:
        await websocket.close(code=4001)
        return
    if not _is_support(username) and await _ban_for(username, "chat"):
        await websocket.close(code=4003)
        return
    await chat_manager.connect_public(websocket)
    websocket._drawbattle_username = username
    music_manager.add(websocket)
    current_music = await db.get_room_music("public")
    if current_music and (not current_music.get("target_user") or current_music.get("target_user") == username):
        await websocket.send_json({"type":"music", "music":current_music})
    try:
        while True:
            data = await websocket.receive_json()
            content = (data.get("content") or "").strip()
            if content:
                if not _is_support(username) and await _ban_for(username, "chat"):
                    await websocket.send_json({"type":"banned","message":"دسترسی چت شما موقتاً محدود است."})
                    continue
                await chat_manager.broadcast_public(username, content[:500], data.get("reply_to_id"))
    except WebSocketDisconnect:
        chat_manager.disconnect_public(websocket)
        music_manager.remove(websocket)


@app.get("/chat/public/messages")
async def chat_public_messages(request: Request, after: int = 0):
    username, blocked = await _require_scope(request, "chat")
    if blocked: return {"ok": False, "error": "blocked"}
    rows = await db.get_messages_after("public", max(0, after))
    return {"ok": True, "messages": rows}

@app.get("/chat/public/music")
async def chat_public_music(request: Request):
    username, blocked = await _require_scope(request, "chat")
    if blocked: return {"ok": False, "error": "blocked"}
    return {"ok": True, "music": await db.get_room_music("public")}

class MusicManager:
    def __init__(self):
        self.conns: set[WebSocket] = set()
    def add(self, ws): self.conns.add(ws)
    def remove(self, ws): self.conns.discard(ws)
    async def broadcast(self, payload, target_user=None):
        dead=[]
        for ws in list(self.conns):
            try:
                # Targeted music is metadata-only for everyone else: it never auto-starts.
                if target_user:
                    owner = getattr(ws, "_drawbattle_username", None)
                    if owner != target_user: continue
                await ws.send_json(payload)
            except Exception: dead.append(ws)
        for ws in dead: self.conns.discard(ws)

music_manager = MusicManager()

@app.post("/support/music")
async def support_music(request: Request, music: UploadFile = File(...)):
    username = _require_login(request)
    if not username or not _is_support(username):
        return {"ok": False, "error": "forbidden"}
    title = (str(request.query_params.get("title") or music.filename or "آهنگ چت روم").strip()[:120])
    target = str(request.query_params.get("target_user") or "").strip()[:64]
    if target and not await db.get_user(target):
        return {"ok": False, "error": "user_not_found"}
    allowed = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/ogg", "audio/webm", "audio/mp4", "audio/x-m4a", "audio/aac"}
    mime = (music.content_type or "audio/mpeg").lower()
    if mime not in allowed and not (mime.startswith("audio/")):
        return {"ok": False, "error": "bad_audio"}
    blob = await music.read()
    if not blob:
        return {"ok": False, "error": "empty_audio"}
    if len(blob) > 15 * 1024 * 1024:
        return {"ok": False, "error": "audio_too_large"}
    await db.set_room_music_file("public", title, blob, mime, music.filename or "music", username, target)
    music_info = await db.get_room_music("public")
    await music_manager.broadcast({"type":"music","music":music_info}, target_user=target or None)
    return {"ok": True, "music": music_info}

@app.get("/chat/public/audio")
async def public_music_audio(request: Request):
    username, blocked = await _require_scope(request, "chat")
    if blocked:
        return blocked
    item = await db.get_room_music_audio("public")
    if not item or not item.get("audio_blob"):
        return HTMLResponse("آهنگی فعال نیست.", status_code=404)
    blob = item["audio_blob"]
    mime = item.get("mime_type") or "audio/mpeg"
    # ارسال مستقیم بایت‌ها برای سازگاری بهتر با پلیر موبایل و Railway.
    return Response(content=blob, media_type=mime, headers={
        "Content-Length": str(len(blob)),
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-store",
    })

@app.post("/support/music/clear")
async def support_music_clear(request: Request):
    username = _require_login(request)
    if not username or not _is_support(username):
        return {"ok": False, "error": "forbidden"}
    await db.clear_room_music("public")
    await music_manager.broadcast({"type":"music_clear"})
    return {"ok": True}

# ============================================================
#                       PRIVATE CHAT
# ============================================================

@app.get("/chat/private/{other}", response_class=HTMLResponse)
async def chat_private(request: Request, other: str):
    username, blocked = await _require_scope(request, "chat")
    if blocked: return blocked
    room = ":".join(sorted([username, other]))
    history = await db.get_recent_messages(room)
    return tpl.chat_private_page(username, other, history)


@app.websocket("/ws/chat/private/{other}")
async def ws_chat_private(websocket: WebSocket, other: str):
    username = websocket.session.get("username")
    if not username:
        await websocket.close(code=4001)
        return
    if not _is_support(username) and await _ban_for(username, "chat"):
        await websocket.close(code=4003)
        return
    room = ":".join(sorted([username, other]))
    await chat_manager.connect_private(room, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = (data.get("content") or "").strip()
            if content:
                if not _is_support(username) and await _ban_for(username, "chat"):
                    await websocket.send_json({"type":"banned","message":"دسترسی چت شما موقتاً محدود است."})
                    continue
                await chat_manager.broadcast_private(room, username, content[:500], data.get("reply_to_id"))
    except WebSocketDisconnect:
        chat_manager.disconnect_private(room, websocket)


# ============================================================
#                    TIC-TAC-TOE (دوز)
# ============================================================

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def check_winner(board: list[str]) -> str | None:
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


class TicTacToeManager:
    def __init__(self):
        self.waiting: tuple[str, WebSocket] | None = None
        self.games: dict[str, dict] = {}
        self.player_game: dict[str, str] = {}

    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()

        # اگر بازیکن از قبل توی یه بازی فعال بود (مثلاً رفرش کرده)، دوباره وصلش کن.
        game_id = self.player_game.get(username)
        if game_id and game_id in self.games:
            self.games[game_id]["sockets"][username] = ws
            await self.send_state(game_id)
            return

        if self.waiting is None:
            self.waiting = (username, ws)
            await ws.send_json({"type": "waiting"})
            asyncio.create_task(self._queue_timeout(username, ws))
            return

        other_username, other_ws = self.waiting
        if other_username == username:
            # همون کاربر دو تب باز کرده؛ فقط جایگزین کن.
            self.waiting = (username, ws)
            await ws.send_json({"type": "waiting"})
            return

        self.waiting = None
        game_id = secrets.token_hex(6)
        self.games[game_id] = {
            "board": [""] * 9,
            "players": {"X": other_username, "O": username},
            "turn": "X",
            "sockets": {other_username: other_ws, username: ws},
            "winner": None,
        }
        self.player_game[other_username] = game_id
        self.player_game[username] = game_id
        await self.send_state(game_id)

    async def _queue_timeout(self, username, ws):
        await asyncio.sleep(30)
        if self.waiting and self.waiting[0] == username and self.waiting[1] is ws:
            self.waiting = None
            try: await ws.send_json({"type":"queue_timeout"})
            except Exception: pass

    async def send_state(self, game_id: str):
        game = self.games.get(game_id)
        if not game:
            return
        for symbol, uname in game["players"].items():
            ws = game["sockets"].get(uname)
            if not ws:
                continue
            opponent_symbol = "O" if symbol == "X" else "X"
            try:
                await ws.send_json({
                    "type": "state",
                    "board": game["board"],
                    "your_symbol": symbol,
                    "turn": game["turn"],
                    "winner": game["winner"],
                    "opponent": game["players"][opponent_symbol],
                })
            except Exception:
                pass

    async def move(self, username: str, cell):
        game_id = self.player_game.get(username)
        if not game_id or game_id not in self.games:
            return
        game = self.games[game_id]
        if game["winner"] is not None:
            return
        symbol = "X" if game["players"]["X"] == username else "O"
        if game["turn"] != symbol:
            return
        if not isinstance(cell, int) or not (0 <= cell < 9) or game["board"][cell]:
            return

        game["board"][cell] = symbol
        winner = check_winner(game["board"])
        if winner:
            game["winner"] = winner
            winner_user = game["players"][winner]
            loser_user = game["players"]["O" if winner == "X" else "X"]
            await db.update_stats(winner_user, wins=1, points=3)
            await db.update_stats(loser_user, losses=1)
        elif "" not in game["board"]:
            game["winner"] = "draw"
            for u in game["players"].values():
                await db.update_stats(u, draws=1, points=1)
        else:
            game["turn"] = "O" if symbol == "X" else "X"

        await self.send_state(game_id)

    async def _forfeit(self, game_id: str, leaving: str):
        game = self.games.get(game_id)
        if not game or game.get("winner") is not None:
            return
        winner = next((u for u in game["players"].values() if u != leaving), None)
        game["winner"] = "forfeit"
        if winner:
            await db.update_stats(winner, wins=1, points=3)
            await self._send(game, winner, {"type":"game_won", "reason":"حریف از بازی خارج شد.", "winner":winner})
            await self._send(game, winner, {"type":"opponent_left", "winner":winner})
        self.games.pop(game_id, None)
        for u in game["players"].values():
            self.player_game.pop(u, None)

    async def leave(self, username: str):
        if self.waiting and self.waiting[0] == username:
            self.waiting = None
        game_id = self.player_game.get(username)
        if game_id and game_id in self.games:
            await self._forfeit(game_id, username)

    async def disconnect(self, username: str):
        if self.waiting and self.waiting[0] == username:
            self.waiting = None
        game_id = self.player_game.get(username)
        if game_id and game_id in self.games:
            await self._forfeit(game_id, username)


ttt_manager = TicTacToeManager()



@app.get("/game/tictactoe", response_class=HTMLResponse)
async def tictactoe_page(request: Request):
    username, blocked = await _require_game_scope(request, "tictactoe")
    if blocked: return blocked
    return tpl.tictactoe_page(username)


@app.websocket("/ws/tictactoe")
async def ws_tictactoe(websocket: WebSocket):
    username = websocket.session.get("username")
    if not username:
        await websocket.close(code=4001)
        return
    if not _is_support(username) and (await _ban_for(username, "games") or await _ban_for(username, "tictactoe")):
        await websocket.close(code=4003)
        return
    await ttt_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "move":
                await ttt_manager.move(username, data.get("cell"))
    except WebSocketDisconnect:
        await ttt_manager.disconnect(username)


# ============================================================
#                 DRAWING GAME (نقاشی حدسی دو نفره)
# ============================================================

DRAW_ROUND_SECONDS = 30
DRAW_SCOREBOARD_SECONDS = 5
DRAW_FINAL_RESULT_SECONDS = 7
DRAW_TOTAL_ROUNDS = 4
DRAW_OPTIONS_COUNT = 12


class DrawingGameManager:
    def __init__(self):
        self.waiting: tuple[str, WebSocket] | None = None
        self.games: dict[str, dict] = {}
        self.player_game: dict[str, str] = {}
        self.lock = asyncio.Lock()

    # ---------------------------------------------------------- matchmaking
    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        async with self.lock:
            game_id = self.player_game.get(username)
            if game_id and game_id in self.games:
                game = self.games[game_id]
                game["sockets"][username] = ws
                await self._send(game, username, self._round_start_payload(game, username))
                return

            # Matchmaking is atomic: simultaneous requests cannot both become
            # the waiting player. A stale socket is replaced only for the same user.
            if self.waiting is not None and self.waiting[0] == username:
                old_ws = self.waiting[1]
                self.waiting = (username, ws)
                try:
                    await old_ws.close(code=4000)
                except Exception:
                    pass
                await ws.send_json({"type": "waiting", "timeout": 30})
                asyncio.create_task(self._queue_timeout(username, ws))
                return

            if self.waiting is None:
                self.waiting = (username, ws)
                await ws.send_json({"type": "waiting", "timeout": 30})
                asyncio.create_task(self._queue_timeout(username, ws))
                return

            other_username, other_ws = self.waiting
            self.waiting = None
            game_id = secrets.token_hex(6)
            game = {
                "id": game_id,
                "players": [other_username, username],
                "sockets": {other_username: other_ws, username: ws},
                "scores": {other_username: 0, username: 0},
                "round": 0, "drawer": None, "guesser": None,
                "word": None, "options": [], "wrong_words": set(),
                "round_active": False, "round_deadline": 0.0,
            }
            self.games[game_id] = game
            self.player_game[other_username] = game_id
            self.player_game[username] = game_id

        # Do not hold the matchmaking lock while sending the round.
        await self._next_round(game_id)

    async def _queue_timeout(self, username, ws):
        await asyncio.sleep(30)
        if self.waiting and self.waiting[0] == username and self.waiting[1] is ws:
            self.waiting = None
            try: await ws.send_json({"type":"queue_timeout"})
            except Exception: pass

    async def _send(self, game: dict, username: str, payload: dict):
        ws = game["sockets"].get(username)
        if not ws:
            return
        try:
            await ws.send_json(payload)
        except Exception:
            pass

    async def _broadcast(self, game: dict, payload: dict):
        for username in game["players"]:
            await self._send(game, username, payload)

    def _round_start_payload(self, game: dict, username: str) -> dict:
        base = {
            "type": "round_start",
            "round": game["round"],
            "total_rounds": DRAW_TOTAL_ROUNDS,
            "duration": DRAW_ROUND_SECONDS,
            "scores": game["scores"],
        }
        if username == game["drawer"]:
            base["role"] = "drawer"
            base["word"] = game["word"]
            base["colors"] = words_draw.COLORS
            base["opponent"] = game["guesser"]
        else:
            base["role"] = "guesser"
            base["options"] = game["options"]
            base["opponent"] = game["drawer"]
        return base

    # ---------------------------------------------------------------- rounds
    async def _next_round(self, game_id: str):
        game = self.games.get(game_id)
        if not game:
            return

        game["round"] += 1
        if game["round"] > DRAW_TOTAL_ROUNDS:
            await self._finish_game(game_id)
            return

        players = game["players"]
        drawer = players[(game["round"] - 1) % 2]
        guesser = players[game["round"] % 2]
        target, options = words_draw.pick_round_words(DRAW_OPTIONS_COUNT)

        game.update({
            "drawer": drawer,
            "guesser": guesser,
            "word": target,
            "options": options,
            "wrong_words": set(),
            "round_active": True,
            "round_deadline": time.monotonic() + DRAW_ROUND_SECONDS,
        })

        for username in players:
            await self._send(game, username, self._round_start_payload(game, username))

        asyncio.create_task(self._round_timeout(game_id, game["round"]))

    async def _round_timeout(self, game_id: str, round_number: int):
        await asyncio.sleep(DRAW_ROUND_SECONDS)
        game = self.games.get(game_id)
        if game and game["round_active"] and game["round"] == round_number:
            await self._end_round(game_id, correct=False)

    async def handle_draw(self, username: str, data: dict):
        game_id = self.player_game.get(username)
        game = self.games.get(game_id) if game_id else None
        if not game or not game["round_active"] or username != game["drawer"]:
            return
        other = game["guesser"]
        msg_type = data.get("type")
        if msg_type == "draw":
            await self._send(game, other, {
                "type": "draw",
                "x0": data.get("x0"), "y0": data.get("y0"),
                "x1": data.get("x1"), "y1": data.get("y1"),
                "color": data.get("color"),
                "size": max(1, min(30, float(data.get("size") or 4))),
            })
        elif msg_type == "clear":
            await self._send(game, other, {"type": "clear"})

    async def handle_guess(self, username: str, word: str):
        game_id = self.player_game.get(username)
        game = self.games.get(game_id) if game_id else None
        if not game or not game["round_active"] or username != game["guesser"]:
            return
        word = (word or "").strip()
        if not word or word in game["wrong_words"]:
            return

        if word == game["word"]:
            await db.update_stats(username, correct_guesses=1)
            await self._end_round(game_id, correct=True)
        else:
            game["wrong_words"].add(word)
            await db.update_stats(username, wrong_guesses=1)
            await self._send(game, username, {"type": "guess_wrong", "word": word})

    async def _end_round(self, game_id: str, correct: bool):
        game = self.games.get(game_id)
        if not game or not game["round_active"]:
            return
        game["round_active"] = False

        points_guesser = 0
        points_drawer = 0
        if correct:
            remaining = max(0.0, game["round_deadline"] - time.monotonic())
            ratio = remaining / DRAW_ROUND_SECONDS
            raw_points = round(ratio * 100) - 10 * len(game["wrong_words"])
            points_guesser = max(10, raw_points)
            points_drawer = 50
            game["scores"][game["guesser"]] += points_guesser
            game["scores"][game["drawer"]] += points_drawer

        is_last = game["round"] >= DRAW_TOTAL_ROUNDS
        await self._broadcast(game, {
            "type": "round_result",
            "round": game["round"],
            "total_rounds": DRAW_TOTAL_ROUNDS,
            "correct": correct,
            "word": game["word"],
            "drawer": game["drawer"],
            "guesser": game["guesser"],
            "points_guesser": points_guesser,
            "points_drawer": points_drawer,
            "scores": game["scores"],
            "is_last": is_last,
            "break_seconds": DRAW_FINAL_RESULT_SECONDS if is_last else DRAW_SCOREBOARD_SECONDS,
        })

        delay = DRAW_FINAL_RESULT_SECONDS if is_last else DRAW_SCOREBOARD_SECONDS
        asyncio.create_task(self._advance_after_delay(game_id, delay))

    async def _advance_after_delay(self, game_id: str, delay: float):
        await asyncio.sleep(delay)
        game = self.games.get(game_id)
        if not game:
            return
        if game["round"] >= DRAW_TOTAL_ROUNDS:
            await self._finish_game(game_id)
        else:
            await self._next_round(game_id)

    async def _finish_game(self, game_id: str):
        game = self.games.get(game_id)
        if not game:
            return
        scores = game["scores"]
        best = max(scores.values())
        winners = [u for u, s in scores.items() if s == best]
        winner = winners[0] if len(winners) == 1 else None
        await self._broadcast(game, {
            "type": "game_over",
            "scores": scores,
            "winner": winner,
        })
        if winner:
            loser = next(u for u in game["players"] if u != winner)
            await db.update_stats(winner, wins=1, points=scores[winner])
            await db.update_stats(loser, losses=1, points=scores[loser])
        else:
            for u in game["players"]:
                await db.update_stats(u, draws=1, points=scores[u])
        for username in game["players"]:
            self.player_game.pop(username, None)
        self.games.pop(game_id, None)

    async def _forfeit(self, game_id: str, leaving: str):
        game = self.games.get(game_id)
        if not game:
            return
        game["round_active"] = False
        winner = next((u for u in game["players"] if u != leaving), None)
        if winner:
            await db.update_stats(winner, wins=1, points=max(1, game["scores"].get(winner, 0)))
            await self._send(game, winner, {"type":"game_won", "winner":winner, "reason":"حریف از بازی خارج شد."})
        for u in game["players"]:
            self.player_game.pop(u, None)
        self.games.pop(game_id, None)

    async def leave(self, username: str):
        if self.waiting and self.waiting[0] == username:
            self.waiting = None
        game_id = self.player_game.get(username)
        if game_id and game_id in self.games:
            await self._forfeit(game_id, username)

    # ------------------------------------------------------------- lifecycle
    async def disconnect(self, username: str):
        if self.waiting and self.waiting[0] == username:
            self.waiting = None
        game_id = self.player_game.get(username)
        if game_id and game_id in self.games:
            await self._forfeit(game_id, username)


drawing_manager = DrawingGameManager()


@app.get("/game/drawing", response_class=HTMLResponse)
async def drawing_page(request: Request):
    username, blocked = await _require_game_scope(request, "drawing")
    if blocked: return blocked
    return tpl.drawing_page(username)


@app.websocket("/ws/drawing")
async def ws_drawing(websocket: WebSocket):
    username = websocket.session.get("username")
    if not username:
        await websocket.close(code=4001)
        return
    if not _is_support(username) and (await _ban_for(username, "games") or await _ban_for(username, "drawing")):
        await websocket.close(code=4003)
        return
    await drawing_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type in ("draw", "clear"):
                await drawing_manager.handle_draw(username, data)
            elif msg_type == "guess":
                await drawing_manager.handle_guess(username, data.get("word"))
    except WebSocketDisconnect:
        await drawing_manager.disconnect(username)

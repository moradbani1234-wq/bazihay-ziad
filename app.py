import asyncio
import io
import os
import secrets
import time
import re
from urllib.parse import quote

from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from starlette.middleware.sessions import SessionMiddleware

import auth
import database as db
import templates as tpl
import words_draw
import aiosqlite

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
        return tpl.signup_page("آیدی باید حداقل ۳ کاراکتر باشد.")
    if not re.fullmatch(r"[a-z0-9]+", username):
        return tpl.signup_page("آیدی فقط می‌تواند شامل حروف کوچک انگلیسی (a-z) و عدد (0-9) باشد.")
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
    if username != "morad":
        ban = await db.get_active_ban(username, "username")
        if ban:
            remaining = max(0, ban["until_ts"] - int(time.time()))
            return tpl.banned_page(username, "username", remaining, ban.get("reason", ""))

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
    category = str(data.get("category") or "other").strip()[:32]
    allowed_categories = {"collusion","profile","username","spam","chat","bio","other"}
    if category not in allowed_categories:
        return {"ok": False, "error": "bad_category"}
    attachment = str(data.get("attachment") or "")
    if attachment and len(attachment) > 350000:
        attachment = ""
    if not target or target == username or not content:
        return {"ok": False, "error": "invalid"}
    if not await db.get_user(target):
        return {"ok": False, "error": "user_not_found"}
    await db.create_report(username, target, context, content, attachment or None, category)
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
    await drawing_manager.leave(username)
    return {"ok": True, "redirect": "/lobby"}

@app.get("/wallet")
async def wallet_data(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    return {"ok":True,"wallet":await db.wallet_for(username)}

@app.post("/daily/claim")
async def daily_claim(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    ok,w=await db.claim_daily(username)
    return {"ok":ok,"wallet":w,"message":"جایزه امروز قبلاً گرفته شده." if not ok else f"🎁 +{w.get('reward',0)} سکه"}

@app.post("/shop/buy")
async def shop_buy(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); key=str(data.get("item_key") or "").strip(); cost=int(data.get("cost") or 0)
    catalog={"neon_pen":250,"profile_frame":400,"victory_fx":650,"crown_badge":900}
    if key not in catalog or cost!=catalog[key]: return {"ok":False,"error":"invalid_item"}
    ok,status,w=await db.buy_item(username,key,cost)
    return {"ok":ok,"status":status,"wallet":w}

@app.post("/game/invite")
async def game_invite(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); receiver=str(data.get("receiver") or "").strip(); mode=str(data.get("mode") or "drawing4")
    if receiver==username or not await db.get_user(receiver) or mode not in {"drawing4"}: return {"ok":False,"error":"invalid"}
    async with aiosqlite.connect(db.DB_PATH) as conn:
        await conn.execute("INSERT INTO game_invites(sender,receiver,mode,status,created_at) VALUES(?,?,?,?,?)",(username,receiver,mode,"pending",int(time.time())))
        await conn.commit()
    return {"ok":True}

@app.get("/notifications")
async def notifications(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    reqs=await db.friend_requests_for(username)
    async with aiosqlite.connect(db.DB_PATH) as conn:
        conn.row_factory=aiosqlite.Row
        cur=await conn.execute("SELECT id,sender,mode,created_at FROM game_invites WHERE receiver=? AND status='pending' AND mode='drawing4' ORDER BY id DESC LIMIT 20",(username,))
        inv=[dict(r) for r in await cur.fetchall()]
    return {"ok":True,"friend_requests":reqs,"invites":inv,"count":len(reqs)+len(inv)}

@app.post("/game/invite/respond")
async def game_invite_respond(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); iid=int(data.get("id") or 0); accept=bool(data.get("accept"))
    async with aiosqlite.connect(db.DB_PATH) as conn:
        conn.row_factory=aiosqlite.Row
        cur=await conn.execute("SELECT * FROM game_invites WHERE id=? AND receiver=? AND status='pending'",(iid,username)); row=await cur.fetchone()
        if not row: return {"ok":False,"error":"not_found"}
        await conn.execute("UPDATE game_invites SET status=? WHERE id=?",("accepted" if accept else "rejected",iid)); await conn.commit()
    return {"ok":True,"mode":row["mode"] if accept else None}

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
    allowed = {"games","chat","drawing","profile","bio","username","all"}
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
    allowed = {"games","chat","drawing","profile","bio","username","all"}
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
    prof["profile_banned"] = bool(await db.get_active_ban(prof["username"], "profile"))
    prof["bio_banned"] = bool(await db.get_active_ban(prof["username"], "bio"))
    return tpl.profile_page(username, prof)


@app.get("/profile/{target}", response_class=HTMLResponse)
async def profile_page(request: Request, target: str):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    prof = await db.profile(target)
    if not prof:
        return HTMLResponse("کاربر پیدا نشد.", status_code=404)
    prof["profile_banned"] = bool(await db.get_active_ban(prof["username"], "profile"))
    prof["bio_banned"] = bool(await db.get_active_ban(prof["username"], "bio"))
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
    current = await db.profile(username) or {}
    avatar_value = data.get("avatar")
    avatar_changed = avatar_value not in (None, "")
    avatar = str(avatar_value) if avatar_changed else (current.get("avatar") or "🎮")
    bio = str(data.get("bio") or "").strip()
    try:
        age = int(data.get("age") or 18)
    except (TypeError, ValueError):
        return {"ok": False, "error": "bad_age"}
    if not 1 <= age <= 90:
        return {"ok": False, "error": "bad_age"}
    if len(bio) > 70:
        return {"ok": False, "error": "bio_too_long"}
    if avatar_changed and avatar.startswith("data:image/") and len(avatar) > 350000:
        return {"ok": False, "error": "image_too_large"}
    if avatar.startswith("data:") and not avatar.startswith("data:image/"):
        return {"ok": False, "error": "bad_image"}
    if not _is_support(username):
        if await db.get_active_ban(username, "profile"):
            current = await db.profile(username) or {}
            avatar = current.get("avatar") or "🎮"
        if await db.get_active_ban(username, "bio"):
            current = await db.profile(username) or {}
            bio = current.get("bio") or ""
    await db.update_profile(username, bio, avatar, age)
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
    return tpl.lobby_page(username, await db.profile(username), await db.wallet_for(username))

@app.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request):
    username=_require_login(request)
    if not username: return RedirectResponse("/login")
    return tpl.shop_page(username, await db.wallet_for(username))

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

    async def broadcast_typing(self, room, sender, typing):
        for ws in list(self.public_conns if room=="public" else self.private_conns.get(room, set())):
            try:
                await ws.send_json({"type":"typing","sender":sender,"typing":bool(typing)})
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
            if data.get("type")=="typing":
                await chat_manager.broadcast_typing("public", username, data.get("typing")); continue
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
            if data.get("type")=="typing":
                await chat_manager.broadcast_typing(room, username, data.get("typing")); continue
            content = (data.get("content") or "").strip()
            if content:
                if not _is_support(username) and await _ban_for(username, "chat"):
                    await websocket.send_json({"type":"banned","message":"دسترسی چت شما موقتاً محدود است."})
                    continue
                await chat_manager.broadcast_private(room, username, content[:500], data.get("reply_to_id"))
    except WebSocketDisconnect:
        chat_manager.disconnect_private(room, websocket)


# ============================================================
#                 DRAWING GAME (نقاشی حدسی دو نفره)
# ============================================================

DRAW_ROUND_SECONDS = 30
DRAW_SCOREBOARD_SECONDS = 5
DRAW_FINAL_RESULT_SECONDS = 7
DRAW_TOTAL_ROUNDS = 6
DRAW_OPTIONS_COUNT = 12


class MultiplayerDrawingManager:
    def __init__(self):
        self.waiting={4:[]}; self.games={}; self.player_game={}; self.lock=asyncio.Lock()
    async def connect(self, username, ws, mode):
        await ws.accept()
        async with self.lock:
            gid=self.player_game.get(username)
            if gid in self.games and self.games[gid]["mode"]==mode:
                self.games[gid]["sockets"][username]=ws; await self._send_state(self.games[gid],username); return
            queue=self.waiting[mode]
            queue[:]=[(u,s) for u,s in queue if u!=username]
            queue.append((username,ws))
            if len(queue)<mode:
                await ws.send_json({"type":"waiting","needed":mode,"count":len(queue)}); return
            picked=queue[:mode]; del queue[:mode]
            gid=secrets.token_hex(7); players=[u for u,_ in picked]
            g={"id":gid,"mode":mode,"players":players,"active":players[:],"sockets":{u:s for u,s in picked},"scores":{u:0 for u in players},"round":0,"drawer":None,"word":None,"options":[],"guesses":{},"wrong":{u:set() for u in players},"round_active":False,"deadline":0.0,"strokes":[]}
            self.games[gid]=g
            for u in players:self.player_game[u]=gid
        await self._next_round(gid)
    async def _send(self,g,u,p):
        ws=g["sockets"].get(u)
        if ws:
            try: await ws.send_json(p)
            except Exception: pass
    async def _broadcast(self,g,p):
        for u in g["active"]: await self._send(g,u,p)
    async def _send_state(self,g,u):
        await self._send(g,u,{"type":"rejoin","round":g["round"],"total_rounds":g["mode"],"drawer":g["drawer"],"role":"drawer" if u==g["drawer"] else "guesser","word":g["word"] if u==g["drawer"] else None,"options":g["options"] if u!=g["drawer"] else [],"active":g["active"],"scores":g["scores"],"strokes":g["strokes"],"remaining":max(1,round(g["deadline"]-time.monotonic()))})
    async def _next_round(self,gid):
        g=self.games.get(gid)
        if not g:return
        g["round"]+=1
        if g["round"]>g["mode"]: return await self._finish(gid)
        if not g["active"]: return await self._finish(gid)
        drawer=g["active"][(g["round"]-1)%len(g["active"])]
        word,options=words_draw.pick_round_words(min(12,max(8,len(g["active"])*2)))
        g.update({"drawer":drawer,"word":word,"options":options,"guesses":{},"wrong":{u:set() for u in g["active"]},"round_active":True,"deadline":time.monotonic()+DRAW_ROUND_SECONDS,"strokes":[]})
        for u in g["active"]:
            await self._send(g,u,{"type":"round_start","round":g["round"],"total_rounds":g["mode"],"duration":DRAW_ROUND_SECONDS,"role":"drawer" if u==drawer else "guesser","word":word if u==drawer else None,"options":options if u!=drawer else [],"drawer":drawer,"active":g["active"],"scores":g["scores"]})
        asyncio.create_task(self._timeout(gid,g["round"]))
    async def _timeout(self,gid,r):
        await asyncio.sleep(DRAW_ROUND_SECONDS)
        g=self.games.get(gid)
        if g and g["round_active"] and g["round"]==r: await self._end_round(gid,False)
    async def draw(self,username,data):
        gid=self.player_game.get(username); g=self.games.get(gid) if gid else None
        if not g or not g["round_active"] or username!=g["drawer"]:return
        if data.get("type")=="clear":g["strokes"]=[]; await self._broadcast(g,{"type":"clear"}); return
        if data.get("type")=="draw_batch":
            segs=(data.get("segments") or [])[:200]
            clean=[{"x0":s.get("x0"),"y0":s.get("y0"),"x1":s.get("x1"),"y1":s.get("y1"),"color":s.get("color","#111"),"size":max(1,min(30,float(s.get("size") or 4)))} for s in segs]
            if clean:
                g["strokes"].extend({"type":"draw",**s} for s in clean)
                await self._broadcast(g,{"type":"draw_batch","segments":clean})
            return
        if data.get("type")!="draw":return
        stroke={"type":"draw","x0":data.get("x0"),"y0":data.get("y0"),"x1":data.get("x1"),"y1":data.get("y1"),"color":data.get("color","#111"),"size":max(1,min(30,float(data.get("size") or 4)))}
        g["strokes"].append(stroke); await self._broadcast(g,stroke)
    async def guess(self,username,word):
        gid=self.player_game.get(username); g=self.games.get(gid) if gid else None
        if not g or not g["round_active"] or username==g["drawer"] or username not in g["active"]:return
        word=(word or '').strip()
        if not word or username in g["guesses"] or word in g["wrong"].setdefault(username,set()):return
        if word==g["word"]:
            now=time.monotonic(); g["guesses"][username]=now; pts=max(10,round(max(0,g["deadline"]-now)/DRAW_ROUND_SECONDS*100)); g["scores"][username]+=pts; await db.update_stats(username,correct_guesses=1,points=pts); await self._send(g,username,{"type":"correct","points":pts})
            if len(g["guesses"])>=max(1,len(g["active"])-1): await self._end_round(gid,True)
        else:
            g["wrong"].setdefault(username,set()).add(word); await db.update_stats(username,wrong_guesses=1); await self._send(g,username,{"type":"guess_wrong","word":word})
    async def _end_round(self,gid,correct):
        g=self.games.get(gid)
        if not g or not g["round_active"]:return
        g["round_active"]=False; eliminated=None
        if g["mode"]==6 and g["round"] < 6 and len(g["active"])>1:
            candidates=[u for u in g["active"] if u!=g["drawer"]]
            if candidates:
                eliminated=max(candidates,key=lambda u:g["guesses"].get(u,float('inf'))); g["active"].remove(eliminated); await db.update_stats(eliminated,losses=1)
        await self._broadcast(g,{"type":"round_result","round":g["round"],"total_rounds":g["mode"],"word":g["word"],"scores":g["scores"],"eliminated":eliminated,"active":g["active"],"is_last":g["round"]>=g["mode"],"break_seconds":5})
        asyncio.create_task(self._advance(gid))
    async def _advance(self,gid):
        await asyncio.sleep(5); g=self.games.get(gid)
        if not g:return
        if g["round"]>=g["mode"] or len(g["active"])<=1:return await self._finish(gid)
        await self._next_round(gid)
    async def _finish(self,gid):
        g=self.games.pop(gid,None)
        if not g:return
        winner=max(g["active"],key=lambda u:g["scores"].get(u,0)) if g["active"] else None
        if winner: await db.update_stats(winner,wins=1,points=g["scores"].get(winner,0))
        await self._broadcast(g,{"type":"game_over","winner":winner,"scores":g["scores"],"active":g["active"]})
        for u in g["players"]:self.player_game.pop(u,None)
    async def leave(self,username):
        gid=self.player_game.get(username); g=self.games.get(gid) if gid else None
        if not g:return
        if username in g["active"]:g["active"].remove(username)
        self.player_game.pop(username,None)
        if len(g["active"])<=1: await self._finish(gid)
        else: await self._broadcast(g,{"type":"player_left","username":username,"active":g["active"]})
    async def disconnect(self,username):
        gid=self.player_game.get(username); g=self.games.get(gid) if gid else None
        if g:g["sockets"].pop(username,None)

multiplayer_drawing_manager=MultiplayerDrawingManager()

@app.websocket("/ws/drawing-multi/{mode}")
async def ws_drawing_multi(websocket: WebSocket, mode: int):
    username=websocket.session.get("username")
    if not username or mode != 4: await websocket.close(code=4001); return
    if not _is_support(username) and (await _ban_for(username,"games") or await _ban_for(username,"drawing")): await websocket.close(code=4003); return
    await multiplayer_drawing_manager.connect(username,websocket,mode)
    try:
        while True:
            data=await websocket.receive_json(); typ=data.get("type")
            if typ in ("draw","draw_batch","clear"): await multiplayer_drawing_manager.draw(username,data)
            elif typ=="guess": await multiplayer_drawing_manager.guess(username,data.get("word"))
    except WebSocketDisconnect: await multiplayer_drawing_manager.disconnect(username)


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
                await ws.send_json({"type": "waiting", "timeout": 30, "count": 1, "needed": 2})
                asyncio.create_task(self._queue_timeout(username, ws))
                return

            if self.waiting is None:
                self.waiting = (username, ws)
                await ws.send_json({"type": "waiting", "timeout": 30, "count": 1, "needed": 2})
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
        elif msg_type == "draw_batch":
            segments = data.get("segments") or []
            clean = [{
                "x0": s.get("x0"), "y0": s.get("y0"),
                "x1": s.get("x1"), "y1": s.get("y1"),
                "color": s.get("color"),
                "size": max(1, min(30, float(s.get("size") or 4))),
            } for s in segments[:200]]
            if clean:
                await self._send(game, other, {"type": "draw_batch", "segments": clean})
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


@app.get("/game/drawing4", response_class=HTMLResponse)
async def drawing4_page(request: Request):
    username, blocked = await _require_game_scope(request, "drawing")
    if blocked: return blocked
    return tpl.multiplayer_drawing_page(username, 4)


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
            if msg_type in ("draw", "draw_batch", "clear"):
                await drawing_manager.handle_draw(username, data)
            elif msg_type == "guess":
                await drawing_manager.handle_guess(username, data.get("word"))
    except WebSocketDisconnect:
        await drawing_manager.disconnect(username)

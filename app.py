import os
import random
import secrets

from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

import auth
import database as db
import templates as tpl
import words_fa

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


# ============================================================
#                          LOBBY
# ============================================================

@app.get("/lobby", response_class=HTMLResponse)
async def lobby(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    return tpl.lobby_page(username)


@app.post("/chat/private/start")
async def start_private_chat(request: Request, other: str = Form(...)):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    other = other.strip()
    if not other or other == username:
        return RedirectResponse("/lobby", status_code=303)
    return RedirectResponse(f"/chat/private/{other}", status_code=303)


# ============================================================
#                       PUBLIC CHAT
# ============================================================

@app.get("/chat/public", response_class=HTMLResponse)
async def chat_public(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
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

    async def broadcast_public(self, sender: str, content: str):
        await db.save_message("public", sender, content)
        payload = {"sender": sender, "content": content}
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

    async def broadcast_private(self, room: str, sender: str, content: str):
        await db.save_message(room, sender, content)
        payload = {"sender": sender, "content": content}
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
    await chat_manager.connect_public(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = (data.get("content") or "").strip()
            if content:
                await chat_manager.broadcast_public(username, content[:500])
    except WebSocketDisconnect:
        chat_manager.disconnect_public(websocket)


# ============================================================
#                       PRIVATE CHAT
# ============================================================

@app.get("/chat/private/{other}", response_class=HTMLResponse)
async def chat_private(request: Request, other: str):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    room = ":".join(sorted([username, other]))
    history = await db.get_recent_messages(room)
    return tpl.chat_private_page(username, other, history)


@app.websocket("/ws/chat/private/{other}")
async def ws_chat_private(websocket: WebSocket, other: str):
    username = websocket.session.get("username")
    if not username:
        await websocket.close(code=4001)
        return
    room = ":".join(sorted([username, other]))
    await chat_manager.connect_private(room, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            content = (data.get("content") or "").strip()
            if content:
                await chat_manager.broadcast_private(room, username, content[:500])
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
        elif "" not in game["board"]:
            game["winner"] = "draw"
        else:
            game["turn"] = "O" if symbol == "X" else "X"

        await self.send_state(game_id)

    async def disconnect(self, username: str):
        if self.waiting and self.waiting[0] == username:
            self.waiting = None

        game_id = self.player_game.pop(username, None)
        if game_id and game_id in self.games:
            game = self.games[game_id]
            game["sockets"].pop(username, None)
            for uname, ws in list(game["sockets"].items()):
                try:
                    await ws.send_json({"type": "opponent_left"})
                except Exception:
                    pass
            if not game["sockets"]:
                self.games.pop(game_id, None)


ttt_manager = TicTacToeManager()


@app.get("/game/tictactoe", response_class=HTMLResponse)
async def tictactoe_page(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    return tpl.tictactoe_page(username)


@app.websocket("/ws/tictactoe")
async def ws_tictactoe(websocket: WebSocket):
    username = websocket.session.get("username")
    if not username:
        await websocket.close(code=4001)
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
#                  WORD GAME (حدس کلمه فارسی)
# ============================================================

WORDGAME_SESSIONS: dict[str, dict] = {}


@app.get("/game/wordgame", response_class=HTMLResponse)
async def wordgame_page(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    return tpl.wordgame_page(username)


@app.post("/api/wordgame/start")
async def wordgame_start(request: Request):
    username = _require_login(request)
    if not username:
        raise HTTPException(401, "لطفاً وارد شوید.")
    word = words_fa.normalize(random.choice(words_fa.WORDS))
    WORDGAME_SESSIONS[username] = {"word": word, "guesses": [], "finished": False}
    return JSONResponse({"length": len(word), "max_attempts": 6})


@app.post("/api/wordgame/guess")
async def wordgame_guess(request: Request):
    username = _require_login(request)
    if not username:
        raise HTTPException(401, "لطفاً وارد شوید.")

    body = await request.json()
    guess = words_fa.normalize((body.get("guess") or ""))

    session = WORDGAME_SESSIONS.get(username)
    if not session or session["finished"]:
        raise HTTPException(400, "یک بازی جدید شروع کن.")

    target = session["word"]
    if len(guess) != len(target):
        raise HTTPException(400, f"کلمه باید {len(target)} حرف باشد.")

    feedback = words_fa.evaluate_guess(guess, target)
    session["guesses"].append({"guess": guess, "feedback": feedback})

    won = guess == target
    lost = (not won) and len(session["guesses"]) >= 6
    if won or lost:
        session["finished"] = True

    return JSONResponse({
        "feedback": feedback,
        "won": won,
        "lost": lost,
        "attempts": len(session["guesses"]),
        "target": target if (won or lost) else None,
    })

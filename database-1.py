import time
import aiosqlite

DB_PATH = "webgame.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at INTEGER NOT NULL,
            is_support INTEGER NOT NULL DEFAULT 0,
            display_name TEXT NOT NULL DEFAULT '', bio TEXT NOT NULL DEFAULT '', avatar TEXT NOT NULL DEFAULT '🎮')""")
        # Migration for databases created by older versions.
        try:
            await db.execute("ALTER TABLE users ADD COLUMN is_support INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        for col, definition in [("display_name", "TEXT NOT NULL DEFAULT ''"), ("bio", "TEXT NOT NULL DEFAULT ''"), ("avatar", "TEXT NOT NULL DEFAULT '🎮'")]:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
            except Exception:
                pass
        await db.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL, sender TEXT NOT NULL,
            content TEXT NOT NULL, reply_to_id INTEGER, created_at INTEGER NOT NULL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, reporter TEXT NOT NULL, target TEXT NOT NULL,
            context TEXT NOT NULL, content TEXT NOT NULL, created_at INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'open', attachment TEXT)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS bans (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, scope TEXT NOT NULL,
            until_ts INTEGER NOT NULL, reason TEXT NOT NULL, created_at INTEGER NOT NULL,
            active INTEGER NOT NULL DEFAULT 1)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS stats (
            username TEXT PRIMARY KEY, wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0, draws INTEGER NOT NULL DEFAULT 0,
            points INTEGER NOT NULL DEFAULT 0, correct_guesses INTEGER NOT NULL DEFAULT 0, wrong_guesses INTEGER NOT NULL DEFAULT 0)""")
        try:
            await db.execute("ALTER TABLE messages ADD COLUMN reply_to_id INTEGER")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE reports ADD COLUMN attachment TEXT")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE stats ADD COLUMN correct_guesses INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE stats ADD COLUMN wrong_guesses INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        await db.execute("""CREATE TABLE IF NOT EXISTS room_music (
            room TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL DEFAULT '',
            added_by TEXT NOT NULL, target_user TEXT NOT NULL DEFAULT '',
            created_at INTEGER NOT NULL, active INTEGER NOT NULL DEFAULT 1,
            audio_blob BLOB, mime_type TEXT NOT NULL DEFAULT 'audio/mpeg', filename TEXT NOT NULL DEFAULT '')""")
        for col, definition in [("audio_blob", "BLOB"), ("mime_type", "TEXT NOT NULL DEFAULT 'audio/mpeg'"), ("filename", "TEXT NOT NULL DEFAULT ''")]:
            try:
                await db.execute(f"ALTER TABLE room_music ADD COLUMN {col} {definition}")
            except Exception:
                pass
        await db.execute("""CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, requester TEXT NOT NULL, addressee TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', created_at INTEGER NOT NULL, responded_at INTEGER)""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_friend_req_addressee ON friend_requests(addressee, status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_friend_req_requester ON friend_requests(requester, status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_bans_user ON bans(username, scope, until_ts)")
        await db.commit()

async def create_user(username, password_hash, salt, is_support=False):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO users (username,password_hash,salt,created_at,is_support) VALUES (?,?,?,?,?)",
                             (username,password_hash,salt,int(time.time()),1 if is_support else 0))
            await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)", (username,))
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False

async def ensure_support_account(username, password_hash, salt):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO users(username,password_hash,salt,created_at,is_support)
                           VALUES(?,?,?,?,1)
                           ON CONFLICT(username) DO UPDATE SET
                           password_hash=excluded.password_hash, salt=excluded.salt, is_support=1""",
                       (username,password_hash,salt,int(time.time())))
        await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)", (username,))
        await db.commit()

async def get_user(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT * FROM users WHERE username=?", (username,))
        row=await cur.fetchone()
        return dict(row) if row else None

async def save_message(room,sender,content,reply_to_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("INSERT INTO messages(room,sender,content,reply_to_id,created_at) VALUES(?,?,?,?,?)",
                         (room,sender,content,reply_to_id,int(time.time())))
        await db.commit()
        return cur.lastrowid

async def get_recent_messages(room,limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT m.id,m.sender,m.content,m.reply_to_id,m.created_at,COALESCE(u.avatar,'🎮') avatar,COALESCE(u.display_name,m.sender) display_name
                             FROM messages m LEFT JOIN users u ON u.username=m.sender WHERE m.room=? ORDER BY m.id DESC LIMIT ?""", (room,limit))
        return [dict(r) for r in reversed(await cur.fetchall())]

async def ensure_stats(username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)",(username,))
        await db.commit()

async def update_stats(username, *, wins=0, losses=0, draws=0, points=0, correct_guesses=0, wrong_guesses=0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)",(username,))
        await db.execute("""UPDATE stats SET wins=wins+?, losses=losses+?, draws=draws+?, points=points+?, correct_guesses=correct_guesses+?, wrong_guesses=wrong_guesses+?
                            WHERE username=?""",(wins,losses,draws,points,correct_guesses,wrong_guesses,username))
        await db.commit()

async def leaderboard(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT username,wins,losses,draws,points,
                                (wins*3+draws) AS rating FROM stats
                                ORDER BY rating DESC, points DESC, wins DESC LIMIT ?""",(limit,))
        return [dict(r) for r in await cur.fetchall()]

async def create_report(reporter,target,context,content,attachment=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO reports(reporter,target,context,content,created_at,attachment)
                            VALUES(?,?,?,?,?,?)""",(reporter,target,context,content,int(time.time()),attachment))
        await db.commit()

async def get_reports(limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT * FROM reports ORDER BY id DESC LIMIT ?""",(limit,))
        return [dict(r) for r in await cur.fetchall()]

async def resolve_report(report_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE reports SET status='resolved' WHERE id=?",(report_id,))
        await db.commit()

async def ban_user(username,scope,hours,reason):
    # نکته: قبلاً اینجا max(1,hours)*3600 بود که هر محرومیت زیر یک ساعت
    # (مثلاً محرومیت‌های چند دقیقه‌ای) را به‌اشتباه به یک ساعت کامل تبدیل می‌کرد.
    # حالا حداقلِ واقعی فقط ۱ ثانیه است تا محرومیت‌های دقیقه‌ای هم درست کار کنند.
    until=int(time.time()+max(1,hours*3600))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO bans(username,scope,until_ts,reason,created_at,active)
                            VALUES(?,?,?,?,?,1)""",(username,scope,until,reason,int(time.time())))
        await db.commit()
    return until

async def get_active_ban(username,scope):
    now=int(time.time())
    scopes=(scope,"all")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT * FROM bans
                                WHERE username=? AND active=1 AND until_ts>? AND scope IN (?,?)
                                ORDER BY until_ts DESC LIMIT 1""",(username,now,*scopes))
        row=await cur.fetchone()
        return dict(row) if row else None

async def unban_user(username,scope):
    """محرومیت‌های فعالِ یک کاربر را غیرفعال می‌کند.
    scope='all' یعنی همه محرومیت‌های آن کاربر (در هر بخشی) پاک شوند؛
    در غیر این صورت فقط محرومیت‌های همان بخش + محرومیت‌های عمومی 'all' پاک می‌شوند."""
    async with aiosqlite.connect(DB_PATH) as db:
        if scope == "all":
            await db.execute("UPDATE bans SET active=0 WHERE username=? AND active=1",(username,))
        else:
            await db.execute("UPDATE bans SET active=0 WHERE username=? AND active=1 AND scope IN (?,'all')",
                             (username,scope))
        await db.commit()

async def get_active_bans(limit=200):
    now=int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT * FROM bans WHERE active=1 AND until_ts>?
                                ORDER BY until_ts DESC LIMIT ?""",(now,limit))
        return [dict(r) for r in await cur.fetchall()]


async def update_profile(username, display_name, bio, avatar):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET display_name=?, bio=?, avatar=? WHERE username=?", (display_name[:40], bio[:300], avatar[:180000], username))
        await db.commit()

async def update_password(username, password_hash, salt):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET password_hash=?, salt=? WHERE username=?", (password_hash, salt, username))
        await db.commit()

async def profile(username):
    # Profile lookup is case-insensitive so links from chat never fail just
    # because the browser/user typed a different letter case.
    username = str(username or '').strip()
    if not username:
        return None
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT u.username,u.display_name,u.bio,u.avatar,
                                      COALESCE(s.wins,0) wins,COALESCE(s.losses,0) losses,COALESCE(s.draws,0) draws,COALESCE(s.points,0) points,
                                      COALESCE(s.correct_guesses,0) correct_guesses,COALESCE(s.wrong_guesses,0) wrong_guesses
                               FROM users u LEFT JOIN stats s ON s.username=u.username
                               WHERE u.username=? OR lower(u.username)=lower(?) LIMIT 1""", (username, username))
        r=await cur.fetchone()
        return dict(r) if r else None


async def get_messages_after(room, after_id=0, limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur = await db.execute("""SELECT m.id,m.sender,m.content,m.reply_to_id,m.created_at,COALESCE(u.avatar,'🎮') avatar,COALESCE(u.display_name,m.sender) display_name
                              FROM messages m LEFT JOIN users u ON u.username=m.sender WHERE m.room=? AND m.id>? ORDER BY m.id ASC LIMIT ?""", (room, int(after_id), limit))
        return [dict(r) for r in await cur.fetchall()]

async def set_room_music_file(room, title, audio_blob, mime_type, filename, added_by, target_user=''):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO room_music(room,title,url,added_by,target_user,created_at,active,audio_blob,mime_type,filename)
                           VALUES(?,?, '', ?,?,?,1,?,?,?)
                           ON CONFLICT(room) DO UPDATE SET title=excluded.title,url='',added_by=excluded.added_by,
                           target_user=excluded.target_user,created_at=excluded.created_at,active=1,
                           audio_blob=excluded.audio_blob,mime_type=excluded.mime_type,filename=excluded.filename""",
                       (room, title[:120], added_by, target_user[:64], int(time.time()), audio_blob, mime_type[:100], filename[:180]))
        await db.commit()

async def get_room_music(room):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT room,title,added_by,target_user,created_at,active,filename,mime_type FROM room_music WHERE room=? AND active=1", (room,))
        r=await cur.fetchone()
        if not r:
            return None
        data=dict(r)
        # نسخه‌دار کردن آدرس فایل صوتی با created_at باعث می‌شود مرورگر با هر
        # آهنگ جدید، آدرس متفاوتی ببیند و بافر/کشِ قدیمی را با فایل تازه قاطی نکند
        # (همان چیزی که باعث می‌شد صدا برای بقیه پخش نشود یا مثل رادیوی خش‌دار بشنود).
        data["url"] = f"/chat/public/audio?v={data['created_at']}" if room == "public" else ""
        return data

async def get_room_music_audio(room):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT audio_blob,mime_type,filename FROM room_music WHERE room=? AND active=1", (room,))
        r=await cur.fetchone()
        return dict(r) if r else None

async def clear_room_music(room):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE room_music SET active=0 WHERE room=?", (room,))
        await db.commit()


# ============================================================
#                    FRIENDS / INBOX
# ============================================================

async def _friend_edge(user_a, user_b):
    """آخرین رکورد درخواست دوستی بین دو کاربر (در هر جهتی) را برمی‌گرداند."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""SELECT * FROM friend_requests
                                   WHERE (requester=? AND addressee=?) OR (requester=? AND addressee=?)
                                   ORDER BY id DESC LIMIT 1""", (user_a, user_b, user_b, user_a))
        row = await cur.fetchone()
        return dict(row) if row else None


async def friendship_info(user_a, user_b):
    """وضعیت دوستی بین دو کاربر را برمی‌گرداند: none/pending_outgoing/pending_incoming/friends/self."""
    if user_a == user_b:
        return {"status": "self", "request_id": None}
    edge = await _friend_edge(user_a, user_b)
    if not edge:
        return {"status": "none", "request_id": None}
    if edge["status"] == "accepted":
        return {"status": "friends", "request_id": edge["id"]}
    if edge["status"] == "pending":
        if edge["requester"] == user_a:
            return {"status": "pending_outgoing", "request_id": edge["id"]}
        return {"status": "pending_incoming", "request_id": edge["id"]}
    return {"status": "none", "request_id": None}


async def send_friend_request(requester, addressee):
    info = await friendship_info(requester, addressee)
    if info["status"] == "friends":
        return {"status": "friends"}
    if info["status"] == "pending_outgoing":
        return {"status": "pending_outgoing"}
    if info["status"] == "pending_incoming":
        # طرف مقابل قبلاً برای من درخواست فرستاده؛ پس درخواست او را قبول می‌کنیم.
        await respond_friend_request(info["request_id"], requester, True)
        return {"status": "friends"}
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO friend_requests(requester,addressee,status,created_at)
                             VALUES(?,?,'pending',?)""", (requester, addressee, int(time.time())))
        await db.commit()
    return {"status": "pending_outgoing"}


async def respond_friend_request(request_id, responder, accept):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM friend_requests WHERE id=? AND addressee=? AND status='pending'",
                                (request_id, responder))
        row = await cur.fetchone()
        if not row:
            return False
        status = "accepted" if accept else "declined"
        await db.execute("UPDATE friend_requests SET status=?, responded_at=? WHERE id=?",
                          (status, int(time.time()), request_id))
        await db.commit()
        return True


async def incoming_requests(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""SELECT fr.id, fr.requester, fr.created_at,
                                          COALESCE(u.avatar,'🎮') avatar, COALESCE(u.display_name,fr.requester) display_name
                                   FROM friend_requests fr LEFT JOIN users u ON u.username=fr.requester
                                   WHERE fr.addressee=? AND fr.status='pending' ORDER BY fr.id DESC""", (username,))
        return [dict(r) for r in await cur.fetchall()]


async def friends_list(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""SELECT CASE WHEN requester=? THEN addressee ELSE requester END AS friend_username,
                                          responded_at
                                   FROM friend_requests
                                   WHERE status='accepted' AND (requester=? OR addressee=?)
                                   ORDER BY responded_at DESC""", (username, username, username))
        rows = [dict(r) for r in await cur.fetchall()]
    result = []
    for r in rows:
        prof = await profile(r["friend_username"])
        if prof:
            result.append(prof)
    return result


async def search_users(query, exclude, limit=10):
    q = f"%{query.strip()}%"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""SELECT username, display_name, avatar FROM users
                                   WHERE username LIKE ? AND username != ? ORDER BY username LIMIT ?""",
                                (q, exclude, limit))
        return [dict(r) for r in await cur.fetchall()]


async def list_conversations(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""SELECT room, MAX(id) as last_id FROM messages
                                   WHERE room != 'public' AND (room LIKE ? OR room LIKE ?)
                                   GROUP BY room ORDER BY last_id DESC""",
                                (f"{username}:%", f"%:{username}"))
        rooms = [dict(r) for r in await cur.fetchall()]
        result = []
        for room_row in rooms:
            room = room_row["room"]
            parts = room.split(":", 1)
            if len(parts) != 2:
                continue
            other = parts[0] if parts[1] == username else parts[1]
            cur2 = await db.execute("""SELECT m.sender, m.content, m.created_at,
                                               COALESCE(u.avatar,'🎮') avatar, COALESCE(u.display_name,?) display_name
                                        FROM messages m LEFT JOIN users u ON u.username=?
                                        WHERE m.id=?""", (other, other, room_row["last_id"]))
            last = await cur2.fetchone()
            if last:
                d = dict(last)
                d["other"] = other
                result.append(d)
        return result

import time
import aiosqlite

DB_PATH = "webgame.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at INTEGER NOT NULL,
            is_support INTEGER NOT NULL DEFAULT 0)""")
        # Migration for databases created by older versions.
        try:
            await db.execute("ALTER TABLE users ADD COLUMN is_support INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        await db.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL, sender TEXT NOT NULL,
            content TEXT NOT NULL, created_at INTEGER NOT NULL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, reporter TEXT NOT NULL, target TEXT NOT NULL,
            context TEXT NOT NULL, content TEXT NOT NULL, created_at INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'open')""")
        await db.execute("""CREATE TABLE IF NOT EXISTS bans (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, scope TEXT NOT NULL,
            until_ts INTEGER NOT NULL, reason TEXT NOT NULL, created_at INTEGER NOT NULL,
            active INTEGER NOT NULL DEFAULT 1)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS stats (
            username TEXT PRIMARY KEY, wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0, draws INTEGER NOT NULL DEFAULT 0,
            points INTEGER NOT NULL DEFAULT 0)""")
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

async def save_message(room,sender,content):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO messages(room,sender,content,created_at) VALUES(?,?,?,?)",
                         (room,sender,content,int(time.time())))
        await db.commit()

async def get_recent_messages(room,limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT sender,content,created_at FROM messages WHERE room=? ORDER BY id DESC LIMIT ?",
                             (room,limit))
        return [dict(r) for r in reversed(await cur.fetchall())]

async def ensure_stats(username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)",(username,))
        await db.commit()

async def update_stats(username, *, wins=0, losses=0, draws=0, points=0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)",(username,))
        await db.execute("""UPDATE stats SET wins=wins+?, losses=losses+?, draws=draws+?, points=points+?
                            WHERE username=?""",(wins,losses,draws,points,username))
        await db.commit()

async def leaderboard(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT username,wins,losses,draws,points,
                                (wins*3+draws) AS rating FROM stats
                                ORDER BY rating DESC, points DESC, wins DESC LIMIT ?""",(limit,))
        return [dict(r) for r in await cur.fetchall()]

async def create_report(reporter,target,context,content):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO reports(reporter,target,context,content,created_at)
                            VALUES(?,?,?,?,?)""",(reporter,target,context,content,int(time.time())))
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

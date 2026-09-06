import time
import re
import aiosqlite

DB_PATH = "webgame.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at INTEGER NOT NULL,
            is_support INTEGER NOT NULL DEFAULT 0,
            display_name TEXT NOT NULL DEFAULT '', public_username TEXT NOT NULL DEFAULT '', bio TEXT NOT NULL DEFAULT '', avatar TEXT NOT NULL DEFAULT '', age INTEGER NOT NULL DEFAULT 18)""")
        # Migration for databases created by older versions.
        try:
            await db.execute("ALTER TABLE users ADD COLUMN is_support INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        for col, definition in [("display_name", "TEXT NOT NULL DEFAULT ''"), ("public_username", "TEXT NOT NULL DEFAULT ''"), ("bio", "TEXT NOT NULL DEFAULT ''"), ("avatar", "TEXT NOT NULL DEFAULT ''"), ("age", "INTEGER NOT NULL DEFAULT 18")]:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
            except Exception:
                pass
        # قاب فعال کاربر؛ فقط یک قاب در هر لحظه فعال است.
        try:
            await db.execute("ALTER TABLE users ADD COLUMN active_frame TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass
        await db.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL, sender TEXT NOT NULL,
            content TEXT NOT NULL, reply_to_id INTEGER, created_at INTEGER NOT NULL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, reporter TEXT NOT NULL, target TEXT NOT NULL,
            context TEXT NOT NULL, content TEXT NOT NULL, created_at INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'open', attachment TEXT, category TEXT NOT NULL DEFAULT 'other')""")
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
            await db.execute("ALTER TABLE reports ADD COLUMN category TEXT NOT NULL DEFAULT 'other'")
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
            id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, receiver TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL,
            UNIQUE(sender, receiver)
        )""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_friend_receiver ON friend_requests(receiver,status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_friend_sender ON friend_requests(sender,status)")
        await db.execute("""CREATE TABLE IF NOT EXISTS friends (
            user1 TEXT NOT NULL, user2 TEXT NOT NULL, created_at INTEGER NOT NULL,
            PRIMARY KEY(user1,user2)
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS user_blocks (
            blocker TEXT NOT NULL, blocked TEXT NOT NULL, created_at INTEGER NOT NULL,
            PRIMARY KEY(blocker, blocked)
        )""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_blocks_blocker ON user_blocks(blocker,blocked)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_blocks_blocked ON user_blocks(blocked,blocker)")
        # پاک‌سازی آواتارهای ایموجی قدیمی؛ از این نسخه فقط تصویر مجاز است.
        await db.execute("UPDATE users SET avatar='' WHERE avatar IS NOT NULL AND avatar!='' AND avatar NOT LIKE 'data:image/%'")
        await db.execute("UPDATE users SET public_username=username WHERE COALESCE(public_username,'')=''")
        await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_public_username ON users(public_username COLLATE NOCASE) WHERE public_username!=''")
        await db.execute("""CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, subject TEXT NOT NULL, content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open', created_at INTEGER NOT NULL
        )""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status)")
        await db.execute("""CREATE TABLE IF NOT EXISTS wallet (
            username TEXT PRIMARY KEY, coins INTEGER NOT NULL DEFAULT 500, diamonds INTEGER NOT NULL DEFAULT 5,
            last_daily INTEGER NOT NULL DEFAULT 0, streak INTEGER NOT NULL DEFAULT 0
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS owned_items (
            username TEXT NOT NULL, item_key TEXT NOT NULL, purchased_at INTEGER NOT NULL,
            PRIMARY KEY(username,item_key)
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS game_invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, receiver TEXT NOT NULL,
            mode TEXT NOT NULL DEFAULT 'drawing4', status TEXT NOT NULL DEFAULT 'pending', created_at INTEGER NOT NULL
        )""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_invites_receiver ON game_invites(receiver,status)")
        # یک‌بار قاب فعال کاربران قدیمی را از آخرین قاب خریداری‌شده مهاجرت کن.
        await db.execute("CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        cur=await db.execute("SELECT value FROM app_meta WHERE key='active_frame_migrated'")
        if not await cur.fetchone():
            await db.execute("""UPDATE users SET active_frame=(SELECT oi.item_key FROM owned_items oi
                WHERE oi.username=users.username AND oi.item_key IN ('fire_frame','lightning_frame','shadow_frame','royal_frame','angel_frame','gold_frame','ice_frame','profile_frame','bronze_frame','davinci_frame','picasso_frame')
                ORDER BY oi.purchased_at DESC LIMIT 1)
                WHERE COALESCE(active_frame,'')='' AND EXISTS(SELECT 1 FROM owned_items oi2 WHERE oi2.username=users.username AND oi2.item_key LIKE '%_frame')""")
            await db.execute("INSERT INTO app_meta(key,value) VALUES('active_frame_migrated','1')")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_bans_user ON bans(username, scope, until_ts)")
        await db.execute("""CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, kind TEXT NOT NULL,
            title TEXT NOT NULL, content TEXT NOT NULL, data TEXT NOT NULL DEFAULT '',
            created_at INTEGER NOT NULL, read INTEGER NOT NULL DEFAULT 0)""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(username,read,id)")
        await db.execute("""CREATE TABLE IF NOT EXISTS pinned_messages (
            message_id INTEGER PRIMARY KEY, room TEXT NOT NULL, pinned_by TEXT NOT NULL, created_at INTEGER NOT NULL)""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_pinned_room ON pinned_messages(room,created_at)")
        await db.execute("""CREATE TABLE IF NOT EXISTS support_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, tag TEXT NOT NULL,
            created_at INTEGER NOT NULL, active INTEGER NOT NULL DEFAULT 1)""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_support_tags_user ON support_tags(username,active,id)")
        await db.execute("""CREATE TABLE IF NOT EXISTS support_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, filename TEXT NOT NULL,
            mime_type TEXT NOT NULL, blob BLOB NOT NULL, amount INTEGER NOT NULL DEFAULT 100000,
            created_at INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'new'
        )""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_support_receipts_status ON support_receipts(status,id)")
        cur=await db.execute("PRAGMA table_info(report_media)")
        media_cols=[r[1] for r in await cur.fetchall()]
        if media_cols and 'id' not in media_cols:
            await db.execute("ALTER TABLE report_media RENAME TO report_media_legacy")
            await db.execute("CREATE TABLE report_media (id INTEGER PRIMARY KEY AUTOINCREMENT, report_id INTEGER NOT NULL, mime_type TEXT NOT NULL, filename TEXT NOT NULL DEFAULT '', blob BLOB NOT NULL, created_at INTEGER NOT NULL)")
            await db.execute("INSERT INTO report_media(report_id,mime_type,filename,blob,created_at) SELECT report_id,mime_type,filename,blob,created_at FROM report_media_legacy")
            await db.execute("DROP TABLE report_media_legacy")
        else:
            await db.execute("CREATE TABLE IF NOT EXISTS report_media (id INTEGER PRIMARY KEY AUTOINCREMENT, report_id INTEGER NOT NULL, mime_type TEXT NOT NULL, filename TEXT NOT NULL DEFAULT '', blob BLOB NOT NULL, created_at INTEGER NOT NULL)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_report_media_report ON report_media(report_id,created_at)")
        await db.commit()

async def create_user(username, password_hash, salt, is_support=False):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO users (username,password_hash,salt,created_at,is_support,public_username) VALUES (?,?,?,?,?,?)",
                             (username,password_hash,salt,int(time.time()),1 if is_support else 0,username))
            await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)", (username,))
            await db.execute("INSERT OR IGNORE INTO wallet(username) VALUES (?)", (username,))
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
        await db.execute("INSERT OR IGNORE INTO wallet(username) VALUES (?)", (username,))
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
        cur=await db.execute("""SELECT m.id,m.sender,m.content,m.reply_to_id,m.created_at,
                                CASE WHEN EXISTS(SELECT 1 FROM bans b WHERE b.username=m.sender AND b.scope IN ('profile','all') AND b.active=1 AND b.until_ts>?) THEN '' ELSE COALESCE(u.avatar,'') END avatar,
                                m.sender display_name,COALESCE(u.public_username,u.username) public_username,
                                COALESCE(u.active_frame,'') AS active_frame,
                                (SELECT group_concat(oi.item_key, ',') FROM owned_items oi WHERE oi.username=m.sender) AS owned_items
                             FROM messages m LEFT JOIN users u ON u.username=m.sender WHERE m.room=? ORDER BY m.id DESC LIMIT ?""", (int(time.time()),room,limit))
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

async def league_for_trophies(trophies):
    t=int(trophies or 0)
    if t >= 1500: return {"key":"picasso","name":"پیکاسو","min":1500,"theme":"league-picasso"}
    if t >= 750: return {"key":"davinci","name":"داوینچی","min":750,"theme":"league-davinci"}
    if t >= 250: return {"key":"bronze","name":"برنزی","min":250,"theme":"league-bronze"}
    return {"key":"starter","name":"مبتدی","min":0,"theme":"league-starter"}

async def leaderboard(limit=50, by="wins"):
    primary = "s.points" if by == "points" else "s.wins"
    secondary = "s.wins" if by == "points" else "s.points"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute(f"""SELECT s.username,s.wins,s.losses,s.draws,s.points,
                                COALESCE(u.public_username,u.username) AS public_username,
                                CASE WHEN EXISTS(SELECT 1 FROM bans b WHERE b.username=s.username AND b.scope IN ('profile','all') AND b.active=1 AND b.until_ts>?) THEN '' ELSE COALESCE(u.avatar,'') END AS avatar,
                                CASE WHEN EXISTS(SELECT 1 FROM bans b WHERE b.username=s.username AND b.scope IN ('profile','all') AND b.active=1 AND b.until_ts>?) THEN 1 ELSE 0 END AS profile_banned,
                                COALESCE(u.age,18) AS age, COALESCE(u.bio,'') AS bio, COALESCE(u.active_frame,'') AS active_frame
                                FROM stats s LEFT JOIN users u ON u.username=s.username
                                ORDER BY {primary} DESC, {secondary} DESC LIMIT ?""",(int(time.time()),int(time.time()),limit))
        rows=[dict(r) for r in await cur.fetchall()]
        for r in rows: r["league"]=await league_for_trophies(r.get("wins",0))
        return rows

async def create_report(reporter,target,context,content,attachment=None,category="other"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO reports(reporter,target,context,content,created_at,attachment,category)
                            VALUES(?,?,?,?,?,?,?)""",(reporter,target,context,content,int(time.time()),attachment,category))
        await db.commit()

async def save_report_media(report_id, mime_type, filename, blob):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO report_media(report_id,mime_type,filename,blob,created_at) VALUES(?,?,?,?,?)",(int(report_id),str(mime_type)[:100],str(filename or '')[:180],blob,int(time.time())))
        await db.commit()

async def get_report_media(report_id, mime_type=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        if mime_type:
            cur=await db.execute("SELECT * FROM report_media WHERE report_id=? AND mime_type=? ORDER BY created_at DESC LIMIT 1",(int(report_id),str(mime_type)))
        else:
            cur=await db.execute("SELECT * FROM report_media WHERE report_id=? ORDER BY CASE WHEN mime_type LIKE 'video/%' THEN 0 ELSE 1 END, created_at DESC LIMIT 1",(int(report_id),))
        r=await cur.fetchone()
        return dict(r) if r else None

async def get_reports(limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT r.*,
                               (SELECT rm.mime_type FROM report_media rm WHERE rm.report_id=r.id AND rm.mime_type LIKE 'video/%' ORDER BY rm.created_at DESC LIMIT 1) AS media_mime,
                               (SELECT rm.filename FROM report_media rm WHERE rm.report_id=r.id AND rm.mime_type LIKE 'video/%' ORDER BY rm.created_at DESC LIMIT 1) AS media_filename,
                               (SELECT rm.mime_type FROM report_media rm WHERE rm.report_id=r.id AND rm.mime_type='application/json' ORDER BY rm.created_at DESC LIMIT 1) AS replay_mime
                              FROM reports r ORDER BY r.id DESC LIMIT ?""",(limit,))
        return [dict(r) for r in await cur.fetchall()]

async def delete_report(report_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM report_media WHERE report_id=?", (int(report_id),))
        await db.execute("DELETE FROM reports WHERE id=?", (int(report_id),))
        await db.commit()
        return True

async def owned_items_for(username):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("SELECT item_key FROM owned_items WHERE username=? ORDER BY purchased_at DESC", (username,))
        return [r[0] for r in await cur.fetchall()]

async def resolve_report(report_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE reports SET status='resolved' WHERE id=?",(report_id,))
        await db.commit()

async def ban_user(username,scope,hours,reason):
    # حساب پشتیبانی هرگز قابل محروم‌سازی نیست.
    if str(username or '').strip().lower() == 'morad':
        return 0
    # نکته: قبلاً اینجا max(1,hours)*3600 بود که هر محرومیت زیر یک ساعت
    # (مثلاً محرومیت‌های چند دقیقه‌ای) را به‌اشتباه به یک ساعت کامل تبدیل می‌کرد.
    # حالا حداقلِ واقعی فقط ۱ ثانیه است تا محرومیت‌های دقیقه‌ای هم درست کار کنند.
    until=int(time.time()+max(1,hours*3600))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""INSERT INTO bans(username,scope,until_ts,reason,created_at,active)
                            VALUES(?,?,?,?,?,1)""",(username,scope,until,reason,int(time.time())))
        await db.commit()
    if scope == "username":
        await make_fake_public_username(username)
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


async def resolve_username(identifier):
    ident=str(identifier or '').strip().lstrip('@')
    if not ident: return None
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT username FROM users WHERE username=? OR lower(public_username)=lower(?) LIMIT 1",(ident,ident))
        r=await cur.fetchone()
        return r[0] if r else None

async def set_public_username(username, public_username):
    public_username=str(public_username or '').strip().lower()
    if not re.fullmatch(r'[a-z0-9]{3,32}', public_username): return False, 'invalid'
    if public_username == 'morad': return False, 'reserved'
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("SELECT username FROM users WHERE lower(public_username)=lower(?) AND username!=? LIMIT 1",(public_username,username))
        if await cur.fetchone(): return False,'taken'
        cur=await db.execute("SELECT username FROM users WHERE lower(username)=lower(?) AND username!=? LIMIT 1",(public_username,username))
        if await cur.fetchone(): return False,'taken'
        await db.execute("UPDATE users SET public_username=? WHERE username=?",(public_username,username))
        await db.commit()
    return True,'ok'

async def make_fake_public_username(username):
    import secrets
    async with aiosqlite.connect(DB_PATH) as db:
        for _ in range(20):
            fake='user'+str(secrets.randbelow(900000)+100000)
            cur=await db.execute("SELECT 1 FROM users WHERE lower(public_username)=lower(?) OR lower(username)=lower(?)",(fake,fake))
            if not await cur.fetchone():
                await db.execute("UPDATE users SET public_username=? WHERE username=?",(fake,username))
                await db.commit()
                return fake
    return None

async def update_profile(username, bio, avatar, age):
    age = max(1, min(90, int(age or 18)))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET bio=?, avatar=?, age=? WHERE username=?", (bio[:70], avatar[:180000], age, username))
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
        cur=await db.execute("""SELECT u.username,COALESCE(u.public_username,u.username) public_username,u.bio,u.avatar,COALESCE(u.age,18) age,
                                      COALESCE(u.active_frame,'') active_frame,
                                      COALESCE(s.wins,0) wins,COALESCE(s.losses,0) losses,COALESCE(s.draws,0) draws,COALESCE(s.points,0) points,
                                      COALESCE(s.correct_guesses,0) correct_guesses,COALESCE(s.wrong_guesses,0) wrong_guesses
                               FROM users u LEFT JOIN stats s ON s.username=u.username
                               WHERE u.username=? OR lower(u.username)=lower(?) LIMIT 1""", (username, username))
        r=await cur.fetchone()
        if not r: return None
        out=dict(r)
        out["league"]=await league_for_trophies(out.get("wins",0))
        cur2=await db.execute("SELECT item_key FROM owned_items WHERE username=? ORDER BY purchased_at DESC", (out["username"],))
        out["owned_items"]=[row[0] for row in await cur2.fetchall()]
        frame_keys={"fire_frame","lightning_frame","shadow_frame","royal_frame","angel_frame","gold_frame","ice_frame","profile_frame","bronze_frame","davinci_frame","picasso_frame"}
        active=str(out.get("active_frame") or "")
        out["active_frame"]=active if active in frame_keys and active in out["owned_items"] else ""
        return out


async def get_messages_after(room, after_id=0, limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur = await db.execute("""SELECT m.id,m.sender,m.content,m.reply_to_id,m.created_at,
                              CASE WHEN EXISTS(SELECT 1 FROM bans b WHERE b.username=m.sender AND b.scope IN ('profile','all') AND b.active=1 AND b.until_ts>?) THEN '' ELSE COALESCE(u.avatar,'') END avatar,
                              m.sender display_name,COALESCE(u.public_username,u.username) public_username,
                              COALESCE(u.active_frame,'') AS active_frame,
                              (SELECT group_concat(oi.item_key, ',') FROM owned_items oi WHERE oi.username=m.sender) AS owned_items
                              FROM messages m LEFT JOIN users u ON u.username=m.sender WHERE m.room=? AND m.id>? ORDER BY m.id ASC LIMIT ?""", (int(time.time()),room, int(after_id), limit))
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
        data["url"] = "/chat/public/audio" if room == "public" else ""
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


async def friend_status(me, other):
    if not me or not other or me == other: return "self"
    a,b=sorted([me,other], key=lambda x:x.lower())
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("SELECT 1 FROM friends WHERE user1=? AND user2=?",(a,b))
        if await cur.fetchone(): return "friends"
        cur=await db.execute("SELECT sender,receiver,status FROM friend_requests WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id DESC LIMIT 1",(me,other,other,me))
        r=await cur.fetchone()
        if not r: return "none"
        sender,receiver,status=r
        if status != 'pending': return status
        return "outgoing" if sender==me else "incoming"

async def send_friend_request(sender, receiver):
    if not sender or not receiver or sender==receiver: return False, "invalid"
    receiver = await resolve_username(receiver) or receiver
    if not await get_user(receiver): return False, "user_not_found"
    if await any_block(sender,receiver): return False, "blocked"
    status=await friend_status(sender,receiver)
    if status=="friends": return False,"already_friends"
    if status=="incoming":
        await respond_friend_request(sender=receiver, receiver=sender, accept=True)
        return True,"accepted"
    if status=="outgoing": return False,"already_sent"
    now=int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM friend_requests WHERE ((sender=? AND receiver=?) OR (sender=? AND receiver=?)) AND status!='pending'",(sender,receiver,receiver,sender))
        try:
            await db.execute("INSERT INTO friend_requests(sender,receiver,status,created_at,updated_at) VALUES(?,?,?,?,?)",(sender,receiver,'pending',now,now))
        except aiosqlite.IntegrityError: return False,"already_sent"
        await db.commit()
    await create_notification(receiver, "friend", "درخواست دوستی جدید", f"@{sender} برای شما درخواست دوستی فرستاد.")
    return True,"sent"

async def respond_friend_request(sender, receiver, accept):
    # sender is original requester; receiver is current user
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("SELECT id FROM friend_requests WHERE sender=? AND receiver=? AND status='pending' ORDER BY id DESC LIMIT 1",(sender,receiver))
        row=await cur.fetchone()
        if not row: return False
        now=int(time.time())
        status='accepted' if accept else 'rejected'
        await db.execute("UPDATE friend_requests SET status=?,updated_at=? WHERE id=?",(status,now,row[0]))
        if accept:
            a,b=sorted([sender,receiver], key=lambda x:x.lower())
            await db.execute("INSERT OR IGNORE INTO friends(user1,user2,created_at) VALUES(?,?,?)",(a,b,now))
        await db.commit()
    if accept:
        await create_notification(sender, "friend", "درخواست دوستی پذیرفته شد", f"@{receiver} درخواست دوستی شما را پذیرفت. حالا می‌توانید چت خصوصی داشته باشید.")
    else:
        await create_notification(sender, "friend", "درخواست دوستی رد شد", f"@{receiver} درخواست دوستی شما را رد کرد.")
    return True

async def friend_requests_for(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT fr.id,fr.sender,fr.receiver,fr.created_at,fr.sender display_name,COALESCE(u.public_username,u.username) public_username,COALESCE(u.avatar,'') avatar, CASE WHEN EXISTS(SELECT 1 FROM bans b WHERE b.username=fr.sender AND b.scope IN ('profile','all') AND b.active=1 AND b.until_ts>?) THEN 1 ELSE 0 END profile_banned FROM friend_requests fr LEFT JOIN users u ON u.username=fr.sender WHERE fr.receiver=? AND fr.status='pending' ORDER BY fr.id DESC",(int(time.time()),username))
        return [dict(r) for r in await cur.fetchall()]

async def friends_for(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT CASE WHEN f.user1=? THEN f.user2 ELSE f.user1 END username,
                               CASE WHEN f.user1=? THEN f.user2 ELSE f.user1 END display_name,
                               COALESCE(u.public_username,u.username) public_username,
                               f.created_at,
                               CASE WHEN EXISTS(SELECT 1 FROM bans b WHERE b.username=(CASE WHEN f.user1=? THEN f.user2 ELSE f.user1 END) AND b.scope IN ('profile','all') AND b.active=1 AND b.until_ts>?) THEN '' ELSE COALESCE(u.avatar,'') END avatar,
                               CASE WHEN EXISTS(SELECT 1 FROM bans b WHERE b.username=(CASE WHEN f.user1=? THEN f.user2 ELSE f.user1 END) AND b.scope IN ('profile','all') AND b.active=1 AND b.until_ts>?) THEN 1 ELSE 0 END profile_banned
                               FROM friends f JOIN users u ON u.username=(CASE WHEN f.user1=? THEN f.user2 ELSE f.user1 END)
                               WHERE f.user1=? OR f.user2=? ORDER BY lower(display_name)""",(username,username,username,int(time.time()),username,int(time.time()),username,username,username))
        return [dict(r) for r in await cur.fetchall()]


async def remove_friend(me, other):
    if not me or not other or me == other:
        return False, "invalid"
    a,b=sorted([me,other], key=lambda x:x.lower())
    async with aiosqlite.connect(DB_PATH) as conn:
        cur=await conn.execute("SELECT created_at FROM friends WHERE user1=? AND user2=?",(a,b))
        row=await cur.fetchone()
        if not row:
            return False, "not_friends"
        if int(time.time()) - int(row[0]) < 5*3600:
            return False, "too_soon"
        await conn.execute("DELETE FROM friends WHERE user1=? AND user2=?",(a,b))
        await conn.commit()
    return True, "removed"

async def block_status(me, other):
    if not me or not other or me == other:
        return False
    async with aiosqlite.connect(DB_PATH) as conn:
        cur=await conn.execute("SELECT 1 FROM user_blocks WHERE blocker=? AND blocked=?",(me,other))
        return bool(await cur.fetchone())

async def toggle_block(me, other):
    me=str(me or '').strip(); other=str(other or '').strip()
    other = await resolve_username(other) or other
    # هیچ کاربری نمی‌تواند حساب پشتیبانی رسمی را بلاک کند و پشتیبانی هم بلاک نمی‌شود.
    if me.lower() == 'morad' or other.lower() == 'morad':
        return False, "support_protected"
    if not me or not other or me == other or not await get_user(other):
        return False, "invalid"
    async with aiosqlite.connect(DB_PATH) as conn:
        cur=await conn.execute("SELECT 1 FROM user_blocks WHERE blocker=? AND blocked=?",(me,other))
        exists=await cur.fetchone()
        if exists:
            await conn.execute("DELETE FROM user_blocks WHERE blocker=? AND blocked=?",(me,other))
            result="unblocked"
        else:
            await conn.execute("INSERT INTO user_blocks(blocker,blocked,created_at) VALUES(?,?,?)",(me,other,int(time.time())))
            result="blocked"
        await conn.commit()
    return True,result

async def any_block(me, other):
    if not me or not other:
        return False
    # پشتیبانی رسمی از سیستم بلاک مستثناست؛ هیچ‌کس نمی‌تواند آن را بلاک کند.
    if str(me).lower() == 'morad' or str(other).lower() == 'morad':
        return False
    return await block_status(me,other) or await block_status(other,me)

async def create_support_ticket(username, subject, content):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("INSERT INTO support_tickets(user,subject,content,created_at) VALUES(?,?,?,?)",(username,subject[:120],content[:3000],int(time.time())))
        await db.commit()
        return cur.lastrowid

async def get_support_tickets(limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT * FROM support_tickets ORDER BY id DESC LIMIT ?",(limit,))
        return [dict(r) for r in await cur.fetchall()]


async def wallet_for(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        await db.execute("INSERT OR IGNORE INTO wallet(username) VALUES (?)", (username,))
        await db.commit()
        cur=await db.execute("SELECT * FROM wallet WHERE username=?", (username,))
        r=await cur.fetchone()
        return dict(r) if r else {"username":username,"coins":500,"diamonds":5,"last_daily":0,"streak":0}

async def claim_daily(username):
    now=int(time.time()); today=now//86400
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        await db.execute("INSERT OR IGNORE INTO wallet(username) VALUES (?)", (username,))
        cur=await db.execute("SELECT * FROM wallet WHERE username=?", (username,))
        w=dict(await cur.fetchone())
        last_day=(w.get("last_daily",0)//86400)
        if last_day==today:
            return False,w
        streak=w.get("streak",0)+1 if last_day==today-1 else 1
        reward=min(1000,200+100*min(streak-1,8))
        await db.execute("UPDATE wallet SET coins=coins+?,last_daily=?,streak=? WHERE username=?",(reward,now,streak,username))
        await db.commit()
        w["coins"]+=reward; w["last_daily"]=now; w["streak"]=streak
        return True,{**w,"reward":reward}

async def buy_item(username,item_key,cost):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        await db.execute("BEGIN IMMEDIATE")
        await db.execute("INSERT OR IGNORE INTO wallet(username) VALUES (?)",(username,))
        cur=await db.execute("SELECT 1 FROM owned_items WHERE username=? AND item_key=?",(username,item_key))
        if await cur.fetchone():
            await db.rollback()
            return False,"owned",None
        cur=await db.execute("UPDATE wallet SET coins=coins-? WHERE username=? AND coins>=?",(cost,username,cost))
        if cur.rowcount != 1:
            await db.rollback()
            return False,"not_enough",None
        await db.execute("INSERT INTO owned_items(username,item_key,purchased_at) VALUES(?,?,?)",(username,item_key,int(time.time())))
        if item_key.endswith('_frame'):
            await db.execute("UPDATE users SET active_frame=? WHERE username=?",(item_key,username))
        await db.commit()
        cur=await db.execute("SELECT * FROM wallet WHERE username=?",(username,)); w=dict(await cur.fetchone())
        return True,"ok",w

async def set_active_frame(username, frame_key):
    frame_key=str(frame_key or '').strip()
    allowed={"fire_frame","lightning_frame","shadow_frame","royal_frame","angel_frame","gold_frame","ice_frame","profile_frame","bronze_frame","davinci_frame","picasso_frame"}
    async with aiosqlite.connect(DB_PATH) as db:
        if frame_key:
            if frame_key not in allowed:
                return False, 'invalid_frame'
            cur=await db.execute("SELECT 1 FROM owned_items WHERE username=? AND item_key=?",(username,frame_key))
            if not await cur.fetchone():
                return False, 'not_owned'
        await db.execute("UPDATE users SET active_frame=? WHERE username=?",(frame_key,username))
        await db.commit()
    return True, 'ok'

async def active_frame_for(username):
    prof=await profile(username)
    return (prof or {}).get('active_frame') or ''


async def create_notification(username, kind, title, content, data=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO notifications(username,kind,title,content,data,created_at,read) VALUES(?,?,?,?,?,?,0)",
                         (username, kind[:40], title[:120], content[:500], data[:500], int(time.time())))
        await db.commit()

async def notifications_for(username, limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT * FROM notifications WHERE username=? ORDER BY id DESC LIMIT ?", (username,limit))
        return [dict(r) for r in await cur.fetchall()]

async def unread_notification_count(username):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("SELECT COUNT(*) FROM notifications WHERE username=? AND read=0", (username,))
        return int((await cur.fetchone())[0])

async def mark_notifications_read(username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE notifications SET read=1 WHERE username=?", (username,))
        await db.commit()

async def pin_message(message_id, room, pinned_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO pinned_messages(message_id,room,pinned_by,created_at) VALUES(?,?,?,?)",
                         (int(message_id), room[:120], pinned_by, int(time.time())))
        await db.commit()

async def unpin_message(message_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM pinned_messages WHERE message_id=?", (int(message_id),))
        await db.commit()

async def get_pinned_messages(room, limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("""SELECT p.*,m.sender,m.content,m.created_at AS message_created_at,COALESCE(u.avatar,'') avatar
                              FROM pinned_messages p JOIN messages m ON m.id=p.message_id
                              LEFT JOIN users u ON u.username=m.sender
                              WHERE p.room=? ORDER BY p.created_at DESC, p.message_id DESC LIMIT ?""", (room,limit))
        return [dict(r) for r in await cur.fetchall()]

async def add_support_tag(username, tag):
    tag=str(tag or '').strip()[:40]
    if not tag: return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO support_tags(username,tag,created_at,active) VALUES(?,?,?,1)",(username,tag,int(time.time())))
        await db.commit()
    return True

async def remove_support_tags(username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE support_tags SET active=0 WHERE username=? AND active=1",(username,))
        await db.commit()

async def tags_for(username):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT id,tag,created_at FROM support_tags WHERE username=? AND active=1 ORDER BY id DESC",(username,))
        return [dict(r) for r in await cur.fetchall()]


async def adjust_wallet(username, coins_delta=0, trophies_delta=0):
    coins_delta=int(coins_delta or 0); trophies_delta=int(trophies_delta or 0)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO wallet(username) VALUES (?)", (username,))
        await db.execute("UPDATE wallet SET coins=MAX(0,coins+?) WHERE username=?", (coins_delta,username))
        await db.execute("INSERT OR IGNORE INTO stats(username) VALUES (?)", (username,))
        await db.execute("UPDATE stats SET wins=MAX(0,wins+?) WHERE username=?", (trophies_delta,username))
        await db.commit()
    return await wallet_for(username), await profile(username)

async def create_support_receipt(username, filename, mime_type, blob, amount=100000):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("INSERT INTO support_receipts(username,filename,mime_type,blob,amount,created_at,status) VALUES(?,?,?,?,?,?,?)",
                             (username,filename[:180],mime_type[:100],blob,int(amount),int(time.time()),'new'))
        await db.commit()
        return cur.lastrowid

async def get_support_receipts(limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT id,username,filename,mime_type,amount,created_at,status FROM support_receipts ORDER BY id DESC LIMIT ?",(limit,))
        return [dict(r) for r in await cur.fetchall()]

async def get_support_receipt(receipt_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory=aiosqlite.Row
        cur=await db.execute("SELECT * FROM support_receipts WHERE id=?",(int(receipt_id),))
        r=await cur.fetchone()
        return dict(r) if r else None

async def mark_support_receipt(receipt_id,status):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("SELECT status FROM support_receipts WHERE id=?",(int(receipt_id),))
        row=await cur.fetchone()
        if not row:
            return False, "not_found"
        current=row[0]
        if current in {"accepted","rejected"} and status != current:
            return False, "finalized"
        if status not in {"new","reviewed","accepted","rejected"}:
            return False, "invalid"
        await db.execute("UPDATE support_receipts SET status=? WHERE id=?",(status,int(receipt_id)))
        await db.commit()
        return True, status

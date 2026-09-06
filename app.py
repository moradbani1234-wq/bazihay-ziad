import asyncio
import io
import os
import secrets
import time
import re
from urllib.parse import quote

from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import auth
import database as db
import templates as tpl
import words_draw
import aiosqlite

app = FastAPI()

# فایل‌های استاتیک فروشگاه (تصاویر قاب‌ها و ...)؛ cache طولانی چون فایل‌ها تغییر نمی‌کنند و لگ ایجاد نمی‌شود.
_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(_STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
app.add_middleware(
    SessionMiddleware,
    # مقدار واقعی را در Railway/AppMint در SESSION_SECRET قرار بده؛ fallback فقط برای اجرای محلی است.
    secret_key=os.environ.get("SESSION_SECRET") or secrets.token_urlsafe(48),
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
    username_input = username.strip()
    username = await db.resolve_username(username_input) or username_input
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
    target_input = str(data.get("target") or "").strip()[:64]
    target = await db.resolve_username(target_input)
    content = str(data.get("content") or "").strip()[:500]
    context = str(data.get("context") or "chat")[:32]
    category = str(data.get("category") or "other").strip()[:32]
    allowed_categories = {"collusion","profile","username","spam","chat","drawing","bio","other"}
    if category not in allowed_categories:
        return {"ok": False, "error": "bad_category"}
    attachment = str(data.get("attachment") or "")
    if attachment and len(attachment) > 350000:
        attachment = ""
    if not target or target == username or not content:
        return {"ok": False, "error": "invalid"}
    if target.lower() == "morad":
        return {"ok": False, "error": "support_protected"}
    if not await db.get_user(target):
        return {"ok": False, "error": "user_not_found"}
    await db.create_report(username, target, context, content, attachment or None, category)
    if context.startswith("drawing") or category == "drawing":
        await db.create_notification(target, "report", "نقاشی شما گزارش شد", f"نقاشی/محتوای نقاشی شما با موضوع «{category}» گزارش شد و توسط پشتیبانی بررسی می‌شود.")
    else:
        await db.create_notification(target, "report", "گزارش برای محتوای شما", f"یک گزارش با موضوع «{category}» برای محتوای شما ثبت شد.")
    return {"ok": True}

@app.post("/report/drawing")
async def report_drawing(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    form=await request.form()
    target_input=str(form.get("target") or "").strip()[:64]
    target=await db.resolve_username(target_input)
    if not target or target==username or target.lower()=="morad": return {"ok":False,"error":"invalid_target"}
    content=str(form.get("content") or "گزارش نقاشی")[:500]
    if not content.strip(): content="گزارش نقاشی"
    rid=await db.create_report(username,target,"drawing",content,None,"drawing")
    saved_video=False
    media=form.get("video")
    if media and hasattr(media,"read"):
        blob=await media.read()
        mime=str(getattr(media,"content_type","") or "video/webm")
        if blob and len(blob)<=16*1024*1024:
            await db.save_report_media(rid,mime,getattr(media,"filename","") or "drawing.webm",blob)
            saved_video=True
    drawing_data=str(form.get("drawing_data") or "")
    if drawing_data and len(drawing_data)<=350000:
        await db.save_report_media(rid,"application/json","drawing-replay.json",drawing_data.encode("utf-8"))
    await db.create_notification("morad","report","🚩 گزارش نقاشی جدید",f"@{username} نقاشی @{target} را گزارش کرده است.",str(rid))
    return {"ok":True,"report_id":rid}

@app.get("/support/report/{report_id}/replay")
async def support_report_replay(request: Request, report_id:int):
    username=_require_login(request)
    if not username or not _is_support(username): return Response(status_code=403)
    media=await db.get_report_media(report_id, mime_type="application/json")
    if not media: return Response(status_code=404)
    return Response(content=media["blob"], media_type="application/json", headers={"Cache-Control":"no-store"})

@app.get("/support/report/{report_id}/media")
async def support_report_media(request: Request, report_id:int):
    username=_require_login(request)
    if not username or not _is_support(username): return Response(status_code=403)
    media=await db.get_report_media(report_id)
    if not media: return Response(status_code=404)
    return Response(content=media["blob"],media_type=media["mime_type"],headers={"Content-Disposition":f'inline; filename="{str(media.get("filename") or "drawing").replace(chr(34),"")}"',"Cache-Control":"no-store"})

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    by = request.query_params.get("by", "wins")
    if by not in ("wins", "points"):
        by = "wins"
    rows = await db.leaderboard(by=by)
    return tpl.leaderboard_page(username, rows, by)

@app.post("/game/leave")
async def game_leave(request: Request):
    username = _require_login(request)
    if not username:
        return {"ok": False}
    await two_player_drawing_manager.leave(username)
    await four_player_drawing_manager.leave(username)
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

SHOP_CATALOG = {
    "neon_pen": {"cost":250, "type":"custom"},
    "profile_frame": {"cost":400, "type":"custom"},
    "victory_fx": {"cost":650, "type":"custom"},
    "crown_badge": {"cost":900, "type":"custom"},
    "chat_bubble": {"cost":300, "type":"custom"},
    "name_effect": {"cost":500, "type":"custom"},
    "draw_glow": {"cost":450, "type":"custom"},
    "bronze_frame": {"cost":550, "type":"league", "min_trophies":250},
    "bronze_badge": {"cost":350, "type":"league", "min_trophies":250},
    "davinci_frame": {"cost":1100, "type":"league", "min_trophies":750},
    "davinci_effect": {"cost":900, "type":"league", "min_trophies":750},
    "picasso_frame": {"cost":1800, "type":"league", "min_trophies":1500},
    "picasso_effect": {"cost":1500, "type":"league", "min_trophies":1500},
    "gold_frame": {"cost":1300, "type":"custom"},
    "ice_frame": {"cost":1300, "type":"custom"},
    "angel_frame": {"cost":1600, "type":"custom"},
    "fire_frame": {"cost":1800, "type":"custom"},
    "lightning_frame": {"cost":2000, "type":"custom"},
    "purple_frame": {"cost":2200, "type":"custom"},
    "king_frame": {"cost":2500, "type":"custom"},
}

@app.post("/shop/buy")
async def shop_buy(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); key=str(data.get("item_key") or "").strip()
    item=SHOP_CATALOG.get(key)
    if not item: return {"ok":False,"error":"invalid_item"}
    cost=int(item["cost"])
    # قیمت فقط از کاتالوگ سرور گرفته می‌شود؛ کلاینت نمی‌تواند قیمت را دستکاری کند.
    if item.get("type")=="league":
        prof=await db.profile(username) or {}
        trophies=int(prof.get("wins",0) or 0)
        if trophies < int(item.get("min_trophies",0)):
            return {"ok":False,"status":"league_locked","message":"این آیتم مخصوص لیگ بالاتر است."}
    ok,status,w=await db.buy_item(username,key,cost)
    return {"ok":ok,"status":status,"wallet":w}

@app.post("/shop/frame/toggle")
async def shop_frame_toggle(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); key=str(data.get("item_key") or "").strip()
    frame_keys={"profile_frame","bronze_frame","davinci_frame","picasso_frame","gold_frame","ice_frame","angel_frame","fire_frame","lightning_frame","purple_frame","king_frame"}
    if key not in frame_keys: return {"ok":False,"status":"invalid_item"}
    prof=await db.profile(username) or {}
    owned=set(prof.get("owned_items") or [])
    if key not in owned: return {"ok":False,"status":"not_owned"}
    if (prof.get("active_frame") or "") == key:
        ok,status=await db.set_active_frame(username,"")
    else:
        ok,status=await db.set_active_frame(username,key)
    prof=await db.profile(username) or {}
    return {"ok":ok,"status":status,"active_frame":prof.get("active_frame") or ""}

@app.get("/notifications")
async def notifications(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    reqs=await db.friend_requests_for(username)
    notes=await db.notifications_for(username)
    return {"ok":True,"friend_requests":reqs,"invites":[],"notifications":notes,"count":len(reqs)+sum(1 for n in notes if not n.get('read'))}

@app.post("/notifications/read")
async def notifications_read(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    await db.mark_notifications_read(username)
    return {"ok":True}

@app.post("/support/message")
async def support_message(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); target=await db.resolve_username(str(data.get("target") or "").strip()[:64]); content=str(data.get("content") or "").strip()[:500]
    if not target or target=="morad" or not await db.get_user(target) or not content: return {"ok":False,"error":"invalid"}
    room=":".join(sorted([username,target]))
    await chat_manager.broadcast_private(room,username,content)
    return {"ok":True}

@app.post("/support/pin")
async def support_pin(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); mid=int(data.get("message_id") or 0); room=str(data.get("room") or "public")
    if not mid or room!="public": return {"ok":False,"error":"invalid"}
    await db.pin_message(mid,room,username)
    pinned=await db.get_pinned_messages(room,20)
    await chat_manager.broadcast_public_event({"type":"pinned_messages","messages":pinned})
    return {"ok":True,"messages":pinned}

@app.post("/support/unpin")
async def support_unpin(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); mid=int(data.get("message_id") or 0)
    if not mid: return {"ok":False,"error":"invalid"}
    await db.unpin_message(mid)
    pinned=await db.get_pinned_messages("public",20)
    await chat_manager.broadcast_public_event({"type":"pinned_messages","messages":pinned})
    return {"ok":True,"messages":pinned}

@app.post("/support/tag")
async def support_tag(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); target=str(data.get("target") or "").strip()[:64]; tag=str(data.get("tag") or "").strip()[:40]
    if not target or target=="morad" or not await db.get_user(target) or not tag: return {"ok":False,"error":"invalid"}
    await db.add_support_tag(target,tag)
    await db.create_notification(target,"tag","تگ جدید از پشتیبانی",f"پشتیبانی یک تگ جدید برای پروفایل شما ثبت کرد: {tag}")
    return {"ok":True,"tags":await db.tags_for(target)}

@app.post("/support/tag/remove")
async def support_tag_remove(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); target=str(data.get("target") or "").strip()[:64]
    if not target or not await db.get_user(target): return {"ok":False,"error":"invalid"}
    await db.remove_support_tags(target)
    return {"ok":True}

@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    username = _require_login(request)
    if not username or not _is_support(username):
        return RedirectResponse("/lobby")
    return tpl.support_page(username, await db.get_reports(), await db.get_active_bans(), await db.get_support_tickets(), await db.get_support_receipts())

@app.post("/support/adjust")
async def support_adjust(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); target=await db.resolve_username(str(data.get("target") or "").strip()[:64])
    if not target or not await db.get_user(target): return {"ok":False,"error":"invalid"}
    if target.lower()=="morad" and username.lower()!="morad": return {"ok":False,"error":"invalid"}
    try: coins=int(data.get("coins") or 0); trophies=int(data.get("trophies") or 0)
    except Exception: return {"ok":False,"error":"invalid"}
    if abs(coins)>100000000 or abs(trophies)>100000: return {"ok":False,"error":"too_large"}
    wallet,prof=await db.adjust_wallet(target,coins,trophies)
    await db.create_notification(target,"support","تغییر موجودی توسط پشتیبانی",f"پشتیبانی موجودی شما را تغییر داد: {coins:+d} سکه و {trophies:+d} جام.")
    return {"ok":True,"wallet":wallet,"profile":prof}

@app.post("/support/receipt")
async def support_receipt(request: Request, receipt: UploadFile = File(...)):
    username=_require_login(request)
    if not username or _is_support(username): return {"ok":False,"error":"forbidden"}
    allowed={"image/jpeg","image/png","image/webp","application/pdf"}
    mime=(receipt.content_type or "application/octet-stream").lower()
    if mime not in allowed: return {"ok":False,"error":"type_not_allowed"}
    blob=await receipt.read()
    if not blob or len(blob)>8*1024*1024: return {"ok":False,"error":"file_too_large"}
    rid=await db.create_support_receipt(username,receipt.filename or "receipt",mime,blob,100000)
    link=f"/support/receipt/{rid}"
    room=":".join(sorted([username,"morad"]))
    await chat_manager.broadcast_private(room,username,f"🧾 رسید پرداخت ۱۰۰۰ سکه ارسال شد • مشاهده رسید: {link}")
    await db.create_notification("morad","support_receipt","🧾 رسید جدید",f"@{username} رسید خرید ۱۰۰۰ سکه را ارسال کرد.",link)
    return {"ok":True,"receipt_id":rid,"message":"رسید با موفقیت به پیوی پشتیبانی ارسال شد."}

@app.get("/support/receipt/{receipt_id}", response_class=HTMLResponse)
async def support_receipt_file(request: Request, receipt_id: int):
    username=_require_login(request)
    if not username or not _is_support(username): return Response(status_code=403)
    r=await db.get_support_receipt(receipt_id)
    if not r: return Response(status_code=404)
    raw_url=f"/support/receipt/{int(receipt_id)}/raw"
    mime=r.get("mime_type") or "application/octet-stream"
    if mime.startswith("image/"):
        viewer=f'<img src="{raw_url}" style="max-width:100%;max-height:80vh;object-fit:contain;border-radius:16px">'
    elif mime=="application/pdf":
        viewer=f'<iframe src="{raw_url}" style="width:100%;height:80vh;border:0;border-radius:16px;background:#fff"></iframe>'
    else:
        viewer=f'<a class="btn" href="{raw_url}">باز کردن فایل</a>'
    body=f'<div style="max-width:900px;margin:20px auto;padding:18px;background:#17112f;color:#fff;border:1px solid #4a2b7d;border-radius:20px;text-align:center"><h2>🧾 رسید @{html.escape(r["username"])}</h2><p>{html.escape(r["filename"])}</p>{viewer}<div style="margin-top:14px"><a class="btn" href="/support">← بازگشت به پنل</a></div></div>'
    return HTMLResponse(f'<!doctype html><html lang="fa" dir="rtl"><meta name="viewport" content="width=device-width,initial-scale=1"><title>رسید</title><body style="margin:0;background:#09051b;font-family:Tahoma,sans-serif">{body}</body></html>')

@app.get("/support/receipt/{receipt_id}/raw")
async def support_receipt_raw(request: Request, receipt_id: int):
    username=_require_login(request)
    if not username or not _is_support(username): return Response(status_code=403)
    r=await db.get_support_receipt(receipt_id)
    if not r: return Response(status_code=404)
    filename=str(r.get("filename") or "receipt").replace('"','')
    headers={"Content-Disposition":f'inline; filename="{filename}"',"Cache-Control":"no-store"}
    return Response(content=r["blob"],media_type=r.get("mime_type") or "application/octet-stream",headers=headers)

@app.post("/support/receipt/status")
async def support_receipt_status(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); rid=int(data.get("id") or 0); status=str(data.get("status") or "reviewed")
    if rid<=0 or status not in {"new","reviewed","accepted","rejected"}: return {"ok":False,"error":"invalid"}
    r=await db.get_support_receipt(rid)
    if not r: return {"ok":False,"error":"not_found"}
    already_accepted=r.get("status")=="accepted"
    already_rejected=r.get("status")=="rejected"
    if status != r.get("status") and (already_accepted or already_rejected):
        return {"ok":False,"error":"finalized","message":"این رسید قبلاً نهایی شده است."}
    ok_mark, mark_status = await db.mark_support_receipt(rid,status)
    if not ok_mark:
        return {"ok":False,"error":mark_status}
    if status=="accepted" and not already_accepted:
        await db.adjust_wallet(r["username"],1000,0)
        await db.create_notification(r["username"],"support_receipt","💰 خرید تأیید شد","رسید شما تأیید شد و ۱۰۰۰ سکه به حساب اضافه شد.")
    elif status=="rejected":
        await db.create_notification(r["username"],"support_receipt","❌ رسید رد شد","رسید پرداخت شما توسط پشتیبانی رد شد.")
    return {"ok":True,"status":status}

@app.post("/support/report/delete")
async def support_report_delete(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); rid=int(data.get("report_id") or 0)
    if rid<=0: return {"ok":False,"error":"invalid"}
    await db.delete_report(rid)
    return {"ok":True}

@app.post("/support/report/review")
async def support_report_review(request: Request):
    username=_require_login(request)
    if not username or not _is_support(username): return {"ok":False,"error":"forbidden"}
    data=await request.json(); rid=int(data.get("report_id") or 0); decision=str(data.get("decision") or "")
    if rid<=0 or decision not in {"valid","invalid"}: return {"ok":False,"error":"invalid"}
    reports=await db.get_reports(200); report=next((r for r in reports if int(r.get("id"))==rid),None)
    if not report: return {"ok":False,"error":"not_found"}
    await db.resolve_report(rid)
    if decision=="invalid":
        await db.create_notification(report["reporter"],"report_review","⚠️ گزارش بی‌اساس",f"گزارش #{rid} بررسی شد و بی‌اساس تشخیص داده شد. در صورت تکرار گزارش‌های بی‌اساس، ممکن است محروم شوید.")
    else:
        await db.create_notification(report["reporter"],"report_review","✅ گزارش بررسی شد",f"گزارش #{rid} بررسی شد و مورد پیگیری قرار گرفت.")
    return {"ok":True,"decision":decision}

@app.post("/support/ban")
async def support_ban(request: Request):
    username = _require_login(request)
    if not username or not _is_support(username):
        return {"ok": False, "error": "forbidden"}
    data = await request.json()
    target = await db.resolve_username(str(data.get("target") or "").strip()[:64])
    scope = str(data.get("scope") or "games")
    # مدت محرومیت می‌تواند به‌صورت ساعت (hours) و/یا دقیقه (minutes) ارسال شود؛
    # این دو با هم جمع می‌شوند تا هم محرومیت چند دقیقه‌ای هم چند ساعته ممکن باشد.
    hours = float(data.get("hours") or 0) + float(data.get("minutes") or 0) / 60.0
    reason = str(data.get("reason") or "نقض قوانین")[:300]
    allowed = {"games","chat","drawing","profile","bio","username","all"}
    if not target or target == "morad" or scope not in allowed or hours <= 0 or hours > 168:
        return {"ok": False, "error": "invalid"}
    until = await db.ban_user(target, scope, hours, reason)
    if target.lower() == "morad" or until == 0:
        return {"ok": False, "error": "support_protected", "message": "حساب پشتیبانی قابل محروم‌سازی نیست."}
    if data.get("report_id"):
        await db.resolve_report(int(data["report_id"]))
    mins=max(1, int(hours*60))
    replacement=None
    if scope=="username":
        p=await db.profile(target) or {}; replacement=p.get("public_username")
    await db.create_notification(target, "ban", "محدودیت دسترسی", f"پشتیبانی دسترسی «{scope}» شما را برای {mins} دقیقه محدود کرد. دلیل: {reason}" + (f" آیدی موقت شما: @{replacement}" if replacement else ""))
    return {"ok": True, "until": until, "replacement_id": replacement}

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
    resolved = await db.resolve_username(target)
    prof = await db.profile(resolved or target)
    if not prof:
        return HTMLResponse("کاربر پیدا نشد.", status_code=404)
    prof["profile_banned"] = bool(await db.get_active_ban(prof["username"], "profile"))
    prof["bio_banned"] = bool(await db.get_active_ban(prof["username"], "bio"))
    prof["support_tags"] = await db.tags_for(prof["username"])
    prof["friend_status"] = await db.friend_status(username, prof["username"])
    prof["blocked_by_me"] = await db.block_status(username, prof["username"])
    prof["blocked_me"] = await db.block_status(prof["username"], username)
    prof["chat_notice"] = "برای شروع چت خصوصی، اول باید درخواست دوستی ارسال و توسط این کاربر پذیرفته شود." if request.query_params.get("chat")=="friend_required" else ""
    prof["game_history"] = await db.game_history(prof["username"], 15)
    return tpl.profile_page(username, prof)


@app.get("/profile/{target}", response_class=HTMLResponse)
async def profile_page(request: Request, target: str):
    username = _require_login(request)
    if not username:
        return RedirectResponse("/login")
    resolved = await db.resolve_username(target)
    prof = await db.profile(resolved or target)
    if not prof:
        return HTMLResponse("کاربر پیدا نشد.", status_code=404)
    prof["profile_banned"] = bool(await db.get_active_ban(prof["username"], "profile"))
    prof["bio_banned"] = bool(await db.get_active_ban(prof["username"], "bio"))
    prof["support_tags"] = await db.tags_for(prof["username"])
    prof["friend_status"] = await db.friend_status(username, prof["username"])
    prof["blocked_by_me"] = await db.block_status(username, prof["username"])
    prof["blocked_me"] = await db.block_status(prof["username"], username)
    prof["game_history"] = await db.game_history(prof["username"], 15)
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

@app.post("/friends/remove")
async def friends_remove(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); target=str(data.get("target") or "").strip()
    ok,status=await db.remove_friend(username,target)
    return {"ok":ok,"status":status}

@app.post("/users/block")
async def users_block(request: Request):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    data=await request.json(); target=str(data.get("target") or "").strip()
    if not target or target==username: return {"ok":False,"error":"invalid"}
    if target.lower() == "morad" or username.lower() == "morad":
        return {"ok":False,"error":"support_protected","message":"حساب پشتیبانی قابل بلاک نیست."}
    ok,status=await db.toggle_block(username,target)
    return {"ok":ok,"status":status}

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
    public_id = str(data.get("public_username") or current.get("public_username") or username).strip().lower()
    if not _is_support(username):
        username_ban = await db.get_active_ban(username, "username")
        if username_ban and public_id != (current.get("public_username") or username):
            return {"ok":False,"error":"username_banned","message":"فعلاً اجازه تغییر آیدی نداری."}
        if public_id != (current.get("public_username") or username):
            ok_id,status_id=await db.set_public_username(username,public_id)
            if not ok_id: return {"ok":False,"error":"username_taken" if status_id=='taken' else "bad_username"}
    avatar_value = data.get("avatar")
    avatar_changed = avatar_value not in (None, "")
    avatar = str(avatar_value) if avatar_changed else (current.get("avatar") or "")
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
    if avatar_changed and not avatar.startswith("data:image/"):
        return {"ok": False, "error": "avatar_must_be_image"}
    if not _is_support(username):
        profile_ban = await db.get_active_ban(username, "profile")
        bio_ban = await db.get_active_ban(username, "bio")
        if profile_ban and avatar_changed:
            return {"ok": False, "error": "profile_banned", "message": "پروفایل شما موقتاً محدود است."}
        if bio_ban and bio != (current.get("bio") or ""):
            return {"ok": False, "error": "bio_banned", "message": "بیوگرافی شما موقتاً محدود است."}
        if profile_ban:
            avatar = current.get("avatar") or ""
        if bio_ban:
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
    prof=await db.profile(username)
    if prof:
        prof["profile_banned"]=bool(await db.get_active_ban(username,"profile"))
    return tpl.lobby_page(username, prof, await db.wallet_for(username))

@app.get("/shop", response_class=HTMLResponse)
async def shop_page(request: Request):
    username=_require_login(request)
    if not username: return RedirectResponse("/login")
    prof=await db.profile(username) or {}
    return tpl.shop_page(username, await db.wallet_for(username), await db.owned_items_for(username), prof.get("active_frame") or "")

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
    other = await db.resolve_username(other.strip()) or other.strip()
    if not other or other == username or not await db.get_user(other):
        return RedirectResponse("/lobby", status_code=303)
    if not _is_support(username):
        if await db.any_block(username, other):
            return RedirectResponse(f"/profile?u={quote(other,safe='')}", status_code=303)
        if await db.friend_status(username, other) != "friends":
            return RedirectResponse(f"/profile?u={quote(other,safe='')}&chat=friend_required", status_code=303)
    return RedirectResponse(f"/chat/private/{other}", status_code=303)


# ============================================================
#                       PUBLIC CHAT
# ============================================================

@app.get("/chat/public", response_class=HTMLResponse)
async def chat_public(request: Request):
    username, blocked = await _require_scope(request, "chat")
    if blocked: return blocked
    history = await db.get_recent_messages("public")
    pinned = await db.get_pinned_messages("public")
    return tpl.chat_public_page(username, history, pinned)


class ChatManager:
    def __init__(self):
        self.public_conns: set[WebSocket] = set()
        self.private_conns: dict[str, set[WebSocket]] = {}
        self.presence: dict[str,int] = {}
    def mark_online(self, username):
        self.presence[username] = self.presence.get(username, 0) + 1
    def mark_offline(self, username):
        n=self.presence.get(username,0)-1
        if n<=0: self.presence.pop(username,None)
        else: self.presence[username]=n
    def is_online(self, username):
        return self.presence.get(username,0)>0

    async def connect_public(self, ws: WebSocket):
        await ws.accept()
        self.public_conns.add(ws)

    def disconnect_public(self, ws: WebSocket):
        self.public_conns.discard(ws)

    async def broadcast_public(self, sender: str, content: str, reply_to_id=None):
        mid = await db.save_message("public", sender, content, reply_to_id)
        prof = await db.profile(sender)
        payload = {"id": mid, "sender": sender, "public_username": (prof or {}).get("public_username", sender), "content": content, "reply_to_id": reply_to_id, "created_at": int(time.time()), "avatar": (prof or {}).get("avatar", ""), "display_name": (prof or {}).get("display_name", sender), "active_frame": (prof or {}).get("active_frame", ""), "owned_items": list((prof or {}).get("owned_items") or [])}
        dead = []
        for ws in self.public_conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.public_conns.discard(ws)

    async def broadcast_public_event(self, payload):
        dead=[]
        for ws in list(self.public_conns):
            try: await ws.send_json(payload)
            except Exception: dead.append(ws)
        for ws in dead: self.public_conns.discard(ws)

    async def connect_private(self, room: str, ws: WebSocket):
        await ws.accept()
        self.private_conns.setdefault(room, set()).add(ws)

    def disconnect_private(self, room: str, ws: WebSocket):
        if room in self.private_conns:
            self.private_conns[room].discard(ws)

    async def broadcast_private(self, room: str, sender: str, content: str, reply_to_id=None):
        mid = await db.save_message(room, sender, content, reply_to_id)
        try:
            a,b=room.split(":",1); receiver=b if sender==a else a
            await db.create_notification(receiver, "message", "پیام خصوصی جدید", f"@{sender}: {content}")
        except Exception:
            pass
        prof = await db.profile(sender)
        payload = {"id": mid, "sender": sender, "public_username": (prof or {}).get("public_username", sender), "content": content, "reply_to_id": reply_to_id, "created_at": int(time.time()), "avatar": (prof or {}).get("avatar", ""), "display_name": (prof or {}).get("display_name", sender), "active_frame": (prof or {}).get("active_frame", ""), "owned_items": list((prof or {}).get("owned_items") or [])}
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
    chat_manager.mark_online(username)
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
        chat_manager.mark_offline(username)
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
    other = await db.resolve_username(other) or other
    if not await db.get_user(other): return HTMLResponse("کاربر پیدا نشد.", status_code=404)
    is_support_chat=(username.lower()=='morad' or other.lower()=='morad')
    if not is_support_chat and not _is_support(username):
        if await db.any_block(username, other):
            return HTMLResponse("این کاربر را بلاک کرده‌ای یا او شما را بلاک کرده است.", status_code=403)
        if await db.friend_status(username, other) != "friends":
            return HTMLResponse("برای شروع چت خصوصی، اول باید درخواست دوستی ارسال و توسط این کاربر پذیرفته شود.", status_code=403)
    room = ":".join(sorted([username, other]))
    history = await db.get_recent_messages(room)
    other_prof=await db.profile(other) or {}
    return tpl.chat_private_page(username, other, history, other_prof.get("public_username") or other)


@app.websocket("/ws/chat/private/{other}")
async def ws_chat_private(websocket: WebSocket, other: str):
    username = websocket.session.get("username")
    if not username:
        await websocket.close(code=4001)
        return
    other = await db.resolve_username(other) or other
    if not await db.get_user(other):
        await websocket.close(code=4004); return
    if not _is_support(username) and await _ban_for(username, "chat"):
        await websocket.close(code=4003)
        return
    is_support_chat=(username.lower()=='morad' or other.lower()=='morad')
    if not is_support_chat and not _is_support(username):
        if await db.any_block(username, other) or await db.friend_status(username, other) != "friends":
            await websocket.close(code=4003)
            return
    room = ":".join(sorted([username, other]))
    await chat_manager.connect_private(room, websocket)
    chat_manager.mark_online(username)
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
                if not is_support_chat and not _is_support(username) and await db.any_block(username, other):
                    await websocket.send_json({"type":"blocked","message":"این گفت‌وگو به‌دلیل بلاک بودن یکی از طرفین در دسترس نیست."})
                    continue
                if not is_support_chat and not _is_support(username) and await db.friend_status(username, other) != "friends":
                    await websocket.send_json({"type":"friend_required","message":"برای پیام دادن اول باید دوست باشید."})
                    continue
                await chat_manager.broadcast_private(room, username, content[:500], data.get("reply_to_id"))
    except WebSocketDisconnect:
        chat_manager.disconnect_private(room, websocket)
        chat_manager.mark_offline(username)


@app.get("/presence/{target}")
async def presence(request: Request, target: str):
    username=_require_login(request)
    if not username: return {"ok":False,"error":"login_required"}
    return {"ok":True,"online":chat_manager.is_online(target)}


# ============================================================
#                 DRAWING GAME — 2P / 4P
# ============================================================

DRAW_PREVIEW_SECONDS = 5
DRAW_BREAK_SECONDS = 10
DRAW_TOTAL_ROUNDS = 6
DRAW_OPTIONS_COUNT = 20
DRAW_MODE_DURATION = {2: 45, 4: 35}


class DrawingBattleManager:
    def __init__(self, mode: int):
        self.mode = mode
        self.duration = DRAW_MODE_DURATION[mode]
        self.waiting = []
        self.games = {}
        self.player_game = {}
        self.lock = asyncio.Lock()

    async def _profiles(self, players):
        out = {}
        for u in players:
            prof = await db.profile(u) or {}
            profile_banned=bool(await db.get_active_ban(u,"profile"))
            out[u] = {
                "username": u,
                "public_username": prof.get("public_username") or u,
                "display_name": prof.get("display_name") or prof.get("public_username") or u,
                "avatar": "" if profile_banned else (prof.get("avatar") or ""),
                "wins": int(prof.get("wins") or 0),
                "points": int(prof.get("points") or 0),
                "league": prof.get("league") or await db.league_for_trophies(prof.get("wins") or 0),
                "owned_items": list(prof.get("owned_items") or []),
                "active_frame": prof.get("active_frame") or "",
            }
        return out

    async def connect(self, username, ws):
        await ws.accept()
        async with self.lock:
            gid = self.player_game.get(username)
            if gid and gid in self.games:
                game = self.games[gid]
                game["sockets"][username] = ws
                await self._send_state(game, username)
                return

            self.waiting = [(u, s) for u, s in self.waiting if u != username]
            self.waiting.append((username, ws))
            if len(self.waiting) < self.mode:
                await self._send(ws, {"type":"waiting", "needed":self.mode, "count":len(self.waiting), "timeout":30})
                asyncio.create_task(self._queue_timeout(username, ws))
                return

            picked = self.waiting[:self.mode]
            del self.waiting[:self.mode]
            players = [u for u, _ in picked]
            gid = secrets.token_hex(7)
            game = {
                "id": gid, "mode": self.mode, "players": players,
                "active": players[:], "sockets": {u:s for u,s in picked},
                "scores": {u:0 for u in players}, "round":0,
                "drawer":None, "guesser":None, "word":None, "options":[],
                "wrong_words": {u:set() for u in players}, "attempted": set(), "guesses": {}, "round_points": {},
                "round_active":False, "phase":"waiting", "deadline":0.0,
                "strokes":[], "profiles": await self._profiles(players), "last_result": None,
            }
            self.games[gid] = game
            for u in players:
                self.player_game[u] = gid

        await self._next_round(gid)

    async def _queue_timeout(self, username, ws):
        await asyncio.sleep(30)
        async with self.lock:
            for i, (u, s) in enumerate(self.waiting):
                if u == username and s is ws:
                    self.waiting.pop(i)
                    try: await ws.send_json({"type":"queue_timeout"})
                    except Exception: pass
                    break

    async def _send(self, ws, payload):
        try:
            await ws.send_json(payload)
        except Exception:
            pass

    async def _to_user(self, game, username, payload):
        ws = game["sockets"].get(username)
        if ws: await self._send(ws, payload)

    async def _broadcast(self, game, payload):
        for u in list(game["active"]):
            await self._to_user(game, u, payload)

    def _base_payload(self, game, username, typ):
        drawer = game["drawer"]
        return {
            "type": typ,
            "round": game["round"],
            "total_rounds": self.mode if self.mode == 4 else DRAW_TOTAL_ROUNDS,
            "duration": self.duration,
            "preview_seconds": DRAW_PREVIEW_SECONDS,
            "role": "drawer" if username == drawer else "guesser",
            "drawer": drawer,
            "opponent": next((u for u in game["active"] if u != username), None),
            "scores": game["scores"],
            "active": game["active"],
            "profiles": game["profiles"],
        }

    async def _send_state(self, game, username):
        if game["phase"] == "preview":
            p = self._base_payload(game, username, "round_preview")
            p["remaining"] = max(0, int(game["deadline"] - time.monotonic() + 0.999))
            p["word"] = game["word"] if username == game["drawer"] else None
            await self._to_user(game, username, p)
            return
        if game["phase"] == "result" and game.get("last_result"):
            await self._to_user(game, username, game["last_result"])
            return
        if game["phase"] == "round":
            p = self._base_payload(game, username, "round_start")
            p["remaining"] = max(0, int(game["deadline"] - time.monotonic() + 0.999))
            p["word"] = game["word"] if username == game["drawer"] else None
            p["options"] = game["options"] if username != game["drawer"] else []
            p["colors"] = words_draw.COLORS if username == game["drawer"] else []
            p["strokes"] = game["strokes"]
            await self._to_user(game, username, p)

    async def _next_round(self, gid):
        game = self.games.get(gid)
        if not game: return
        game["round"] += 1
        total_rounds = self.mode if self.mode == 4 else DRAW_TOTAL_ROUNDS
        if game["round"] > total_rounds or len(game["active"]) <= 1:
            return await self._finish_game(gid)

        players = game["active"]
        drawer = players[(game["round"] - 1) % len(players)]
        target, options = words_draw.pick_round_words(min(DRAW_OPTIONS_COUNT, max(8, len(players)*2)))
        game.update({
            "drawer": drawer, "word": target, "options": options,
            "wrong_words": {u:set() for u in players}, "attempted": set(), "guesses": {}, "round_points": {},
            "round_active": False, "phase":"preview",
            "deadline": time.monotonic() + DRAW_PREVIEW_SECONDS, "strokes":[],
        })
        for u in players:
            p = self._base_payload(game, u, "round_preview")
            p["remaining"] = DRAW_PREVIEW_SECONDS
            p["word"] = target if u == drawer else None
            p["message"] = "موضوع را حفظ کن؛ تا چند ثانیه دیگر شروع می‌شود!"
            await self._to_user(game, u, p)
        asyncio.create_task(self._preview_timeout(gid, game["round"]))

    async def _preview_timeout(self, gid, round_number):
        await asyncio.sleep(DRAW_PREVIEW_SECONDS)
        game = self.games.get(gid)
        if game and game["round"] == round_number and game["phase"] == "preview":
            await self._start_round(gid, round_number)

    async def _start_round(self, gid, round_number):
        game = self.games.get(gid)
        if not game or game["round"] != round_number: return
        game["phase"] = "round"
        game["round_active"] = True
        game["deadline"] = time.monotonic() + self.duration
        for u in list(game["active"]):
            p = self._base_payload(game, u, "round_start")
            p["word"] = game["word"] if u == game["drawer"] else None
            p["options"] = game["options"] if u != game["drawer"] else []
            p["colors"] = words_draw.COLORS if u == game["drawer"] else []
            p["strokes"] = []
            await self._to_user(game, u, p)
        asyncio.create_task(self._round_timeout(gid, round_number))

    async def _round_timeout(self, gid, round_number):
        await asyncio.sleep(self.duration)
        game = self.games.get(gid)
        if game and game["round"] == round_number and game["round_active"]:
            await self._end_round(gid, False)

    async def draw(self, username, data):
        gid = self.player_game.get(username)
        game = self.games.get(gid) if gid else None
        if not game or not game["round_active"] or username != game["drawer"]: return
        if data.get("type") == "clear":
            game["strokes"] = []
            await self._broadcast(game, {"type":"clear"})
            return
        if data.get("type") == "draw_batch":
            segs = data.get("segments") or []
            clean=[]
            for s in segs[:200]:
                try:
                    clean.append({"x0":float(s.get("x0")),"y0":float(s.get("y0")),"x1":float(s.get("x1")),"y1":float(s.get("y1")),"color":str(s.get("color") or "#111")[:20],"size":max(1,min(30,float(s.get("size") or 4)))})
                except Exception: pass
            if clean:
                game["strokes"].extend(clean)
                await self._broadcast(game, {"type":"draw_batch","segments":clean})
            return
        if data.get("type") != "draw": return
        try:
            stroke={"x0":float(data.get("x0")),"y0":float(data.get("y0")),"x1":float(data.get("x1")),"y1":float(data.get("y1")),"color":str(data.get("color") or "#111")[:20],"size":max(1,min(30,float(data.get("size") or 4)))}
        except Exception: return
        game["strokes"].append(stroke)
        await self._broadcast(game, {"type":"draw",**stroke})

    async def guess(self, username, word):
        gid=self.player_game.get(username); game=self.games.get(gid) if gid else None
        if not game or not game["round_active"] or username==game["drawer"] or username not in game["active"]: return
        word=(word or "").strip()
        if not word or username in game.get("attempted",set()) or username in game["guesses"]:
            return
        game.setdefault("attempted",set()).add(username)
        if word == game["word"]:
            now=time.monotonic(); game["guesses"][username]=now
            pts=max(10, round(max(0,game["deadline"]-now)/self.duration*100))
            game["round_points"][username]=pts
            game["scores"][username]+=pts
            await db.update_stats(username, correct_guesses=1)
            await self._to_user(game, username, {"type":"correct","points":pts})
            await self._to_user(game, game["drawer"], {"type":"guess_notice","username":username,"word":word,"correct":True,"message":f"@{username} حدس زد: {word} ✅"})
            needed=max(1,len(game["active"])-1)
            if len(game["guesses"]) >= needed: await self._end_round(gid, True)
        else:
            await db.update_stats(username, wrong_guesses=1)
            await self._to_user(game, username, {"type":"guess_wrong","word":word,"final":True})
            await self._to_user(game, game["drawer"], {"type":"guess_notice","username":username,"word":word,"correct":False,"message":f"@{username} حدس اشتباه زد: {word} ❌"})

    async def _end_round(self, gid, correct):
        game=self.games.get(gid)
        if not game or not game["round_active"]: return
        game["round_active"]=False; game["phase"]="result"
        points_drawer=0
        if correct:
            points_drawer=50
            game["scores"][game["drawer"]]+=points_drawer
        points_map=game.get("round_points",{})
        points_guesser=sum(points_map.values()) if game["mode"]==4 else next(iter(points_map.values()),0)
        total_rounds=self.mode if self.mode==4 else DRAW_TOTAL_ROUNDS
        is_last=game["round"]>=total_rounds
        payload={"type":"round_result","round":game["round"],"total_rounds":total_rounds,"correct":correct,"word":game["word"],"drawer":game["drawer"],"guesser":next(iter(points_map),None),"points_guesser":points_guesser,"points_drawer":points_drawer,"points_map":points_map,"scores":game["scores"],"active":game["active"],"profiles":game["profiles"],"is_last":is_last,"break_seconds":DRAW_BREAK_SECONDS}
        game["last_result"] = payload
        await self._broadcast(game,payload)
        asyncio.create_task(self._advance(gid, game["round"]))

    async def _advance(self,gid,round_number):
        await asyncio.sleep(DRAW_BREAK_SECONDS)
        game=self.games.get(gid)
        if not game or game["round"]!=round_number: return
        total_rounds=self.mode if self.mode==4 else DRAW_TOTAL_ROUNDS
        if round_number>=total_rounds or len(game["active"])<=1: return await self._finish_game(gid)
        await self._next_round(gid)

    async def _finish_game(self,gid):
        game=self.games.pop(gid,None)
        if not game:return
        ranked=sorted(game["players"], key=lambda u:game["scores"].get(u,0), reverse=True)
        winner=ranked[0] if ranked and len([x for x in ranked if game["scores"].get(x,0)==game["scores"].get(ranked[0],0)])==1 else None
        if winner:
            await db.update_stats(winner,wins=5)
            for u in ranked[1:]: await db.update_stats(u,losses=1)
        else:
            for u in ranked: await db.update_stats(u,draws=1)
        ts=int(time.time())
        history_rows=[]
        for u in game["players"]:
            result = "win" if (winner and u==winner) else ("draw" if not winner else "loss")
            opponents = ",".join(game["profiles"].get(o,{}).get("public_username",o) for o in game["players"] if o!=u)
            history_rows.append({"username":u,"result":result,"points":game["scores"].get(u,0),"opponents":opponents,"mode":self.mode,"created_at":ts})
        await db.log_game_history(history_rows)
        await self._broadcast(game,{"type":"game_over","winner":winner,"scores":game["scores"],"active":game["active"],"profiles":game["profiles"]})
        for u in game["players"]: self.player_game.pop(u,None)

    async def leave(self,username):
        self.waiting=[x for x in self.waiting if x[0]!=username]
        gid=self.player_game.get(username); game=self.games.get(gid) if gid else None
        if not game:return
        if username in game["active"]: game["active"].remove(username)
        self.player_game.pop(username,None)
        if len(game["active"])<=1: await self._finish_game(gid)
        else: await self._broadcast(game,{"type":"player_left","username":username,"active":game["active"]})

    async def disconnect(self,username,ws=None):
        # قطع اتصال باید هم صف و هم بازی را تمیز کند تا بازیکن شبحی وارد Match بعدی نشود.
        async with self.lock:
            self.waiting=[(u,s) for u,s in self.waiting if not (u==username and (ws is None or s is ws))]
            gid=self.player_game.get(username); game=self.games.get(gid) if gid else None
            if not game:
                return
            current=game["sockets"].get(username)
            if ws is not None and current is not ws:
                return
            game["sockets"].pop(username,None)
            if username in game["active"]:
                game["active"].remove(username)
            self.player_game.pop(username,None)
            if len(game["active"])<=1:
                await self._finish_game(gid)
            else:
                await self._broadcast(game,{"type":"player_left","username":username,"active":game["active"]})


two_player_drawing_manager=DrawingBattleManager(2)
four_player_drawing_manager=DrawingBattleManager(4)

@app.websocket("/ws/drawing-multi/{mode}")
async def ws_drawing_multi(websocket: WebSocket, mode: int):
    username=websocket.session.get("username")
    if not username or mode != 4: await websocket.close(code=4001); return
    if not _is_support(username) and (await _ban_for(username,"games") or await _ban_for(username,"drawing")): await websocket.close(code=4003); return
    await four_player_drawing_manager.connect(username,websocket)
    try:
        while True:
            data=await websocket.receive_json(); typ=data.get("type")
            if typ in ("draw","draw_batch","clear"): await four_player_drawing_manager.draw(username,data)
            elif typ=="guess": await four_player_drawing_manager.guess(username,data.get("word"))
    except WebSocketDisconnect: await four_player_drawing_manager.disconnect(username, websocket)

@app.websocket("/ws/drawing")
async def ws_drawing(websocket: WebSocket):
    username=websocket.session.get("username")
    if not username: await websocket.close(code=4001); return
    if not _is_support(username) and (await _ban_for(username,"games") or await _ban_for(username,"drawing")): await websocket.close(code=4003); return
    await two_player_drawing_manager.connect(username,websocket)
    try:
        while True:
            data=await websocket.receive_json(); typ=data.get("type")
            if typ in ("draw","draw_batch","clear"): await two_player_drawing_manager.draw(username,data)
            elif typ=="guess": await two_player_drawing_manager.guess(username,data.get("word"))
    except WebSocketDisconnect: await two_player_drawing_manager.disconnect(username, websocket)


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

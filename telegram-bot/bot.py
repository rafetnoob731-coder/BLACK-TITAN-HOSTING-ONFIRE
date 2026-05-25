"""
𝐁𝐋𝐀𝐂𝐊 𝐓𝐈𝐓𝐀𝐍 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐁𝐎𝐓 𝐕𝟒.𝟎
𝐀𝐔𝐓𝐎-𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 & 𝐓𝐈𝐄𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓
𝐂𝐑𝐄𝐃𝐈𝐓𝐒: 𝐁𝐋𝐀𝐂𝐊 𝐓𝐈𝐓𝐀𝐍
"""

import subprocess, sys, os
for mod in ["telebot","psutil","requests","flask","qrcode","Pillow","cryptography"]:
    try:
        __import__(mod)
    except ModuleNotFoundError:
        print(f"Installing {mod}...")
        subprocess.check_call([sys.executable,"-m","pip","install",mod,"--quiet"])

import telebot, zipfile, tempfile, shutil
from telebot import types
import time, uuid
from datetime import datetime, timedelta
import psutil, sqlite3, json, logging, threading, re, atexit, requests
from flask import Flask
from threading import Thread
import qrcode
from io import BytesIO
import random
from collections import defaultdict, deque
from functools import wraps

TOKEN = os.environ.get("BOT_TOKEN", "8792154488:AAHEi2aH2UrHRq_3QfX_J2gxWpmFY7Ptdkw")
OWNER_ID = int(os.environ.get("OWNER_ID", "7892915425"))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7702588711"))
BOT_USERNAME = os.environ.get("BOT_USERNAME", "@VIP_DARK_GOD")
UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/vip_dark_god_primel")
UPDATE_GROUP = os.environ.get("UPDATE_GROUP", "https://t.me/vip_dark_god_chat")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(BASE_DIR, "bt_uploads"))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "bt_data"))
DB_PATH = os.path.join(DATA_DIR, "bt_bot.db")
RUNNING_DB = os.path.join(DATA_DIR, "running_scripts.json")
REFERRAL_DB = os.path.join(DATA_DIR, "referrals.json")
PORT = int(os.environ.get("PORT", 8080))

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
referral_data = {}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

FM = {
    "A":"𝐀","B":"𝐁","C":"𝐂","D":"𝐃","E":"𝐄","F":"𝐅","G":"𝐆",
    "H":"𝐇","I":"𝐈","J":"𝐉","K":"𝐊","L":"𝐋","M":"𝐌","N":"𝐍",
    "O":"𝐎","P":"𝐏","Q":"𝐐","R":"𝐑","S":"𝐒","T":"𝐓","U":"𝐔",
    "V":"𝐕","W":"𝐖","X":"𝐗","Y":"𝐘","Z":"𝐙",
    "a":"𝐚","b":"𝐛","c":"𝐜","d":"𝐝","e":"𝐞","f":"𝐟","g":"𝐠",
    "h":"𝐡","i":"𝐢","j":"𝐣","k":"𝐤","l":"𝐥","m":"𝐦","n":"𝐧",
    "o":"𝐨","p":"𝐩","q":"𝐪","r":"𝐫","s":"𝐬","t":"𝐭","u":"𝐮",
    "v":"𝐯","w":"𝐰","x":"𝐱","y":"𝐲","z":"𝐳",
    "0":"𝟎","1":"𝟏","2":"𝟐","3":"𝟑","4":"𝟒","5":"𝟓","6":"𝟔",
    "7":"𝟕","8":"𝟖","9":"𝟗"
}

def B(t):
    return "".join(FM.get(c, c) for c in str(t))

TIERS = {
    "free": {"name":"𝐅𝐑𝐄𝐄","ul":3,"mfs":50*1024*1024,"icon":"🎫","color":"#2ecc71","ar":False,"rn":3},
    "premium": {"name":"𝐏𝐑𝐄𝐌𝐈𝐔𝐌","ul":10,"mfs":200*1024*1024,"icon":"⭐","color":"#f39c12","ar":True,"rn":0},
    "owner": {"name":"𝐎𝐖𝐍𝐄𝐑","ul":float("inf"),"mfs":float("inf"),"icon":"👑","color":"#e74c3c","ar":True,"rn":0}
}

def get_folder(uid):
    p = os.path.join(UPLOAD_DIR, str(uid))
    os.makedirs(p, exist_ok=True)
    return p

def get_tier(uid):
    if uid == OWNER_ID or uid in admin_ids: return "owner"
    if uid in user_subscriptions:
        s = user_subscriptions[uid]
        if s.get("expiry") and s["expiry"] > datetime.now():
            return s.get("tier", "premium")
    return "free"

def file_limit(uid): return TIERS[get_tier(uid)]["ul"]
def file_count(uid): return len(user_files.get(uid, []))

def is_running(uid, fn):
    k = f"{uid}_{fn}"
    si = bot_scripts.get(k)
    if si and si.get("process"):
        try:
            proc = psutil.Process(si["process"].pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            if k in bot_scripts: del bot_scripts[k]
            return False
    return False

def kill_proc(pi):
    try:
        p = pi.get("process")
        if not p or not hasattr(p, "pid"): return
        try:
            parent = psutil.Process(p.pid)
            for c in parent.children(recursive=True):
                try: c.terminate()
                except: pass
            parent.terminate(); parent.wait(timeout=3)
        except:
            try: parent.kill()
            except: pass
    except: pass

class RateLimit:
    def __init__(self, mx=5, pd=60):
        self.mx, self.pd, self.c = mx, pd, defaultdict(deque)
    def check(self, uid):
        n = time.time()
        while self.c[uid] and self.c[uid][0] < n - self.pd:
            self.c[uid].popleft()
        if len(self.c[uid]) >= self.mx: return False
        self.c[uid].append(n); return True

rlim = RateLimit(10, 60)

class Recovery:
    def __init__(self): self.f = RUNNING_DB
    def save(self, uid, fn, fp, pid):
        try:
            d = json.load(open(self.f)) if os.path.exists(self.f) else {"s":[]}
            d["s"] = [x for x in d["s"] if not (x["u"]==uid and x["f"]==fn)]
            d["s"].append({"u":uid,"f":fn,"fp":fp,"p":pid,"t":datetime.now().isoformat()})
            json.dump(d, open(self.f,"w"), indent=4)
        except Exception as e: logger.error(f"Save err: {e}")
    def remove(self, uid, fn):
        try:
            if not os.path.exists(self.f): return
            d = json.load(open(self.f))
            d["s"] = [x for x in d["s"] if not (x["u"]==uid and x["f"]==fn)]
            json.dump(d, open(self.f,"w"), indent=4)
        except Exception as e: logger.error(f"Remove err: {e}")
    def recover_all(self):
        try:
            if not os.path.exists(self.f): return []
            d = json.load(open(self.f))
            rv = []
            for s in d.get("s",[]):
                try:
                    uid, fn, fp = s["u"], s["f"], s["fp"]
                    if not os.path.exists(fp): continue
                    tier = get_tier(uid)
                    ar = TIERS[tier]["ar"]
                    if tier == "free": ar = refsys.is_auto(uid)
                    if not ar: continue
                    fo = get_folder(uid)
                    ext = os.path.splitext(fn)[1].lower()
                    if ext == ".py":
                        threading.Thread(target=self._restart_py, args=(uid, fp, fo, fn)).start()
                    elif ext == ".js":
                        threading.Thread(target=self._restart_js, args=(uid, fp, fo, fn)).start()
                    rv.append({"uid":uid,"fn":fn})
                    time.sleep(1)
                except: pass
            return rv
        except: return []
    def _restart_py(self, uid, fp, fo, fn):
        k = f"{uid}_{fn}"
        if k in bot_scripts: return
        lf = open(os.path.join(fo,f"{os.path.splitext(fn)[0]}.log"),"a",encoding="utf-8",errors="ignore")
        sinfo = None
        if os.name=="nt":
            sinfo = subprocess.STARTUPINFO(); sinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow=subprocess.SW_HIDE
        proc = subprocess.Popen([sys.executable,fp],cwd=fo,stdout=lf,stderr=lf,stdin=subprocess.PIPE,startupinfo=sinfo,encoding="utf-8",errors="ignore")
        bot_scripts[k] = {"process":proc,"lf":lf,"fn":fn,"uid":uid,"st":datetime.now(),"tp":"py","sk":k}
        self.save(uid,fn,fp,proc.pid)
    def _restart_js(self, uid, fp, fo, fn):
        k = f"{uid}_{fn}"
        if k in bot_scripts: return
        lf = open(os.path.join(fo,f"{os.path.splitext(fn)[0]}.log"),"a",encoding="utf-8",errors="ignore")
        sinfo = None
        if os.name=="nt":
            sinfo = subprocess.STARTUPINFO(); sinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow=subprocess.SW_HIDE
        proc = subprocess.Popen(["node",fp],cwd=fo,stdout=lf,stderr=lf,stdin=subprocess.PIPE,startupinfo=sinfo,encoding="utf-8",errors="ignore")
        bot_scripts[k] = {"process":proc,"lf":lf,"fn":fn,"uid":uid,"st":datetime.now(),"tp":"js","sk":k}
        self.save(uid,fn,fp,proc.pid)
    def count(self):
        try:
            if os.path.exists(self.f): return len(json.load(open(self.f)).get("s",[]))
            return 0
        except: return 0

rec = Recovery()

class RefSys:
    def __init__(self): self.f = REFERRAL_DB
    def load(self):
        global referral_data
        try: referral_data = json.load(open(self.f)) if os.path.exists(self.f) else {}
        except: referral_data = {}
    def save(self):
        try: json.dump(referral_data, open(self.f,"w"), indent=4)
        except: pass
    def gen(self, uid):
        c = f"BT{uid}{random.randint(1000,9999)}"
        if uid not in referral_data:
            referral_data[uid] = {"code":c,"r":[],"cnt":0,"ar":False,"t":datetime.now().isoformat(),"u":""}
        else: referral_data[uid]["code"] = c
        self.save(); return c
    def get_code(self, uid):
        if uid in referral_data: return referral_data[uid].get("code")
        return self.gen(uid)
    def add(self, rid, uid, un=None):
        if rid == uid: return False
        if rid not in referral_data: self.gen(rid)
        if "u" not in referral_data[rid]: referral_data[rid]["u"] = ""
        if uid not in [x["uid"] for x in referral_data[rid].get("r",[])]:
            referral_data[rid].setdefault("r",[]).append({"uid":uid,"un":un or "","jt":datetime.now().isoformat()})
            referral_data[rid]["cnt"] = len(referral_data[rid]["r"])
            if referral_data[rid]["cnt"] >= TIERS["free"]["rn"]:
                referral_data[rid]["ar"] = True
            self.save(); return True
        return False
    def count(self, uid): return referral_data.get(uid,{}).get("cnt",0)
    def is_auto(self, uid): return referral_data.get(uid,{}).get("ar",False)
    def top(self, lim=10):
        r = []
        for uid,d in referral_data.items():
            if d.get("cnt",0)>0: r.append({"uid":uid,"un":d.get("u",""),"cnt":d["cnt"],"ar":d.get("ar",False)})
        r.sort(key=lambda x:x["cnt"],reverse=True)
        return r[:lim]
    def info(self, uid):
        if uid not in referral_data: return None
        d = referral_data[uid].copy()
        d["rank"] = self.rank(uid)
        return d
    def rank(self, uid):
        for i,r in enumerate(self.top(1000),1):
            if r["uid"]==uid: return i
        return None
    def update_un(self, uid, un):
        if uid in referral_data:
            referral_data[uid]["u"] = un or ""
            self.save()

refsys = RefSys()
refsys.load()

ANIM_EXEC = [
    B("𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▱▱▱▱▱▱▱▱▱▱] 0%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▱▱▱▱▱▱▱▱▱] 10%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▱▱▱▱▱▱▱▱] 20%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▰▱▱▱▱▱▱▱] 30%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▰▰▱▱▱▱▱▱] 40%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▰▰▰▱▱▱▱▱] 50%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▰▰▰▰▱▱▱▱] 60%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▰▰▰▰▰▱▱▱] 70%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▰▰▰▰▰▰▱▱] 80%"),
    B("⚡ 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐧𝐠: [▰▰▰▰▰▰▰▰▰▱] 90%"),
    B("✅ 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞: [▰▰▰▰▰▰▰▰▰▰] 100%")
]
ANIM_UPLD = [
    B("📤 𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠: [▱▱▱▱▱▱▱▱▱▱] 0%"),
    B("📤 𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠: [▰▱▱▱▱▱▱▱▱▱] 25%"),
    B("📤 𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠: [▰▰▰▱▱▱▱▱▱▱] 50%"),
    B("📤 𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠: [▰▰▰▰▰▰▱▱▱▱] 75%"),
    B("✅ 𝐔𝐩𝐥𝐨𝐚𝐝𝐞𝐝: [▰▰▰▰▰▰▰▰▰▰] 100%")
]
ANIM_RECV = [
    B("🔄 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐲: [▱▱▱▱▱▱▱▱▱▱] 0%"),
    B("🔄 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐲: [▰▰▱▱▱▱▱▱▱▱] 20%"),
    B("🔄 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐲: [▰▰▰▰▱▱▱▱▱▱] 40%"),
    B("🔄 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐲: [▰▰▰▰▰▰▱▱▱▱] 60%"),
    B("🔄 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐲: [▰▰▰▰▰▰▰▰▱▱] 80%"),
    B("✅ 𝐑𝐞𝐜𝐨𝐯𝐞𝐫𝐞𝐝: [▰▰▰▰▰▰▰▰▰▰] 100%")
]
ANIM_REST = [
    B("🔄 𝐁𝐨𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭: [▱▱▱▱▱▱▱▱▱▱] 0%"),
    B("🔄 𝐁𝐨𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭: [▰▰▱▱▱▱▱▱▱▱] 20%"),
    B("🔄 𝐁𝐨𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭: [▰▰▰▰▱▱▱▱▱▱] 40%"),
    B("🔄 𝐁𝐨𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭: [▰▰▰▰▰▰▱▱▱▱] 60%"),
    B("🔄 𝐁𝐨𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭: [▰▰▰▰▰▰▰▰▱▱] 80%"),
    B("✅ 𝐁𝐨𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭𝐞𝐝: [▰▰▰▰▰▰▰▰▰▰] 100%")
]

def animate(msg, frames):
    m = bot.reply_to(msg, frames[0])
    for f in frames:
        try:
            bot.edit_message_text(f, msg.chat.id, m.message_id)
            time.sleep(0.3)
        except: pass
    return m

DBL = threading.Lock()

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS subs(uid INTEGER PRIMARY KEY,exp TEXT,tier TEXT,created TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS uf(uid INTEGER,fn TEXT,ft TEXT,project TEXT,up TEXT,PRIMARY KEY(uid,fn))")
        try: c.execute("ALTER TABLE uf ADD COLUMN project TEXT DEFAULT ''")
        except: pass
        c.execute("CREATE TABLE IF NOT EXISTS au(uid INTEGER PRIMARY KEY,un TEXT,fj TEXT,ls TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS adm(uid INTEGER PRIMARY KEY,ab INTEGER,at TEXT)")
        c.execute("INSERT OR IGNORE INTO adm VALUES(?,?,?)", (OWNER_ID, OWNER_ID, datetime.now().isoformat()))
        if ADMIN_ID != OWNER_ID:
            c.execute("INSERT OR IGNORE INTO adm VALUES(?,?,?)", (ADMIN_ID, OWNER_ID, datetime.now().isoformat()))
        conn.commit(); conn.close()
    except Exception as e: logger.error(f"DB init: {e}")

def load_data():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False); c = conn.cursor()
        for uid,exp,tier in c.execute("SELECT uid,exp,tier FROM subs"):
            try: user_subscriptions[uid] = {"expiry":datetime.fromisoformat(exp) if exp else None,"tier":tier or "free"}
            except: pass
        try:
            for row in c.execute("SELECT uid,fn,ft,project FROM uf"):
                uid,fn,ft,proj = row
                user_files.setdefault(uid,[]).append((fn,ft,proj))
        except:
            for uid,fn,ft in c.execute("SELECT uid,fn,ft FROM uf"):
                user_files.setdefault(uid,[]).append((fn,ft,""))
        active_users.update(uid for uid, in c.execute("SELECT uid FROM au"))
        admin_ids.update(uid for uid, in c.execute("SELECT uid FROM adm"))
        conn.close()
    except Exception as e: logger.error(f"Load data: {e}")

init_db(); load_data()

def save_file(uid, fn, ft="py", project=""):
    with DBL:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False); c = conn.cursor()
        try:
            c.execute("INSERT OR REPLACE INTO uf VALUES(?,?,?,?,?)", (uid,fn,ft,project,datetime.now().isoformat()))
            conn.commit()
            if uid not in user_files: user_files[uid]=[]
            user_files[uid] = [(x,y,z) for x,y,z in user_files[uid] if x!=fn]
            user_files[uid].append((fn,ft,project))
        except Exception as e: logger.error(f"Save file: {e}")
        finally: conn.close()

def del_file(uid, fn):
    with DBL:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False); c = conn.cursor()
        try:
            c.execute("DELETE FROM uf WHERE uid=? AND fn=?", (uid,fn))
            conn.commit()
            if uid in user_files:
                user_files[uid] = [x for x in user_files[uid] if x[0]!=fn]
                if not user_files[uid]: del user_files[uid]
            rec.remove(uid,fn)
        except Exception as e: logger.error(f"Del file: {e}")
        finally: conn.close()

def add_user(uid, un=None):
    active_users.add(uid)
    with DBL:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False); c = conn.cursor()
        try:
            c.execute("INSERT OR REPLACE INTO au VALUES(?,?,COALESCE((SELECT fj FROM au WHERE uid=?),?),?)",
                      (uid,un,uid,datetime.now().isoformat(),datetime.now().isoformat()))
            conn.commit()
        except: pass
        finally: conn.close()

def save_sub(uid, exp, tier="premium"):
    with DBL:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False); c = conn.cursor()
        try:
            es = exp.isoformat() if exp else None
            c.execute("INSERT OR REPLACE INTO subs VALUES(?,?,?,?)", (uid,es,tier,datetime.now().isoformat()))
            conn.commit()
            user_subscriptions[uid] = {"expiry":exp,"tier":tier}
        except: pass
        finally: conn.close()

def rem_sub(uid):
    with DBL:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False); c = conn.cursor()
        try:
            c.execute("DELETE FROM subs WHERE uid=?", (uid,))
            conn.commit()
            if uid in user_subscriptions: del user_subscriptions[uid]
        except: pass
        finally: conn.close()

# Flask keep-alive
flask_app = Flask(__name__)

PAGE_HTML = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BLACK TITAN HOSTING</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<style>
body{{background:#0a0a0f;color:#e0e0e0;font-family:'Segoe UI',sans-serif}}
.sidebar{{background:#12121a;min-height:100vh;border-right:1px solid #2a2a3a}}
.sidebar .nav-link{{color:#aaa;padding:12px 20px;border-radius:8px;margin:2px 8px}}
.sidebar .nav-link:hover,.sidebar .nav-link.active{{background:#1e1e30;color:#fff}}
.card{{background:#12121a;border:1px solid #2a2a3a;border-radius:12px}}
.stat-card{{text-align:center;padding:20px}}
.stat-card .icon{{font-size:2rem;margin-bottom:8px}}
.stat-card .value{{font-size:1.8rem;font-weight:700;color:#fff}}
.stat-card .label{{color:#888;font-size:.85rem}}
.uptime-dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}}
.table{{color:#e0e0e0;font-size:.9rem}}
.table th{{border-color:#2a2a3a;color:#888}}
.table td{{border-color:#2a2a3a;vertical-align:middle}}
.badge-tg{{background:#1e1e30;color:#aaa;padding:2px 10px;border-radius:20px;font-size:.75rem}}
footer{{color:#555;text-align:center;padding:20px;font-size:.8rem}}
</style></head><body>
<div class="container-fluid"><div class="row">
<div class="col-md-2 sidebar p-3">
<h4 class="text-white mb-4 mt-2"><i class="bi bi-shield-shaded me-2"></i>BLACK TITAN</h4>
<nav class="nav flex-column">
<a class="nav-link active" href="/"><i class="bi bi-speedometer2 me-2"></i>Dashboard</a>
<a class="nav-link" href="/users"><i class="bi bi-people me-2"></i>Users</a>
<a class="nav-link" href="/files"><i class="bi bi-file-code me-2"></i>Files</a>
<a class="nav-link" href="/scripts"><i class="bi bi-terminal me-2"></i>Scripts</a>
<a class="nav-link" href="/referrals"><i class="bi bi-link-45deg me-2"></i>Referrals</a>
</nav></div>
<div class="col-md-10 p-4">
<div class="d-flex justify-content-between align-items-center mb-4">
<h3><i class="bi bi-speedometer2 me-2"></i>Management Dashboard</h3>
<span class="badge-tg"><i class="bi bi-telegram me-1"></i>{bu}</span>
</div>
<div class="row g-3 mb-4">
<div class="col-md-3"><div class="card stat-card">
<div class="icon">👥</div><div class="value">{tu}</div><div class="label">Total Users</div></div></div>
<div class="col-md-3"><div class="card stat-card">
<div class="icon">📁</div><div class="value">{tf}</div><div class="label">Files</div></div></div>
<div class="col-md-3"><div class="card stat-card">
<div class="icon">🟢</div><div class="value">{rs}</div><div class="label">Running</div></div></div>
<div class="col-md-3"><div class="card stat-card">
<div class="icon">💾</div><div class="value">{ruc}</div><div class="label">Recovery</div></div></div>
</div>
<div class="row g-3 mb-4">
<div class="col-md-4"><div class="card p-3"><h6><i class="bi bi-tag me-2"></i>Tier Distribution</h6>
<div class="mt-2"><div>FREE: <strong>{free_c}</strong></div><div>PREMIUM: <strong>{prem_c}</strong></div><div>OWNER: <strong>{own_c}</strong></div></div></div></div>
<div class="col-md-4"><div class="card p-3"><h6><i class="bi bi-link me-2"></i>Referral Stats</h6>
<div class="mt-2"><div>Referring: <strong>{ru}</strong></div><div>Auto-Restart: <strong>{are}</strong></div><div>Top: <strong>{top_ref} refs</strong></div></div></div></div>
<div class="col-md-4"><div class="card p-3"><h6><i class="bi bi-cpu me-2"></i>System</h6>
<div class="mt-2"><div>CPU: <strong>{cpu}%</strong></div><div>RAM: <strong>{ram_p}% ({ram_u}/{ram_t}GB)</strong></div><div>Bot: <span class="uptime-dot" style="background:{bot_color}"></span>{bot_status}</div></div></div></div>
</div>
<div class="card p-3"><h6><i class="bi bi-activity me-2"></i>Active Users</h6>
<div class="table-responsive mt-2"><table class="table table-dark table-hover"><thead><tr>
<th>ID</th><th>Username</th><th>Tier</th><th>Files</th><th>Running</th><th>Referrals</th></tr></thead><tbody>{user_rows}</tbody></table></div></div>
<footer>BLACK TITAN HOSTING BOT V4.0 | <a href="https://t.me/{bu_clean}" class="text-white-50">@{bu_clean}</a></footer>
</div></div></div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script></body></html>"""

@flask_app.route("/")
def web_dashboard():
    tu = len(active_users); tf = sum(len(f) for f in user_files.values())
    rs = sum(1 for k,v in bot_scripts.items() if is_running(v["uid"],v["fn"]))
    ruc = rec.count(); ru = sum(1 for u in active_users if refsys.count(u)>0)
    are = sum(1 for u in active_users if refsys.is_auto(u))
    top = refsys.top(1); top_ref = top[0]["cnt"] if top else 0
    free_c = sum(1 for u in active_users if get_tier(u)=="free")
    prem_c = sum(1 for u in active_users if get_tier(u)=="premium")
    own_c = sum(1 for u in active_users if get_tier(u)=="owner")
    cpu = psutil.cpu_percent(interval=0.05); mem = psutil.virtual_memory()
    ram_u = round(mem.used/1024**3,1); ram_t = round(mem.total/1024**3,1); ram_p = mem.percent
    user_rows = ""
    for uid in sorted(active_users)[:20]:
        try:
            un = bot.get_chat(uid).username or str(uid)
        except: un = str(uid)
        t = get_tier(uid); fc = file_count(uid); rc = refsys.count(uid)
        rn = sum(1 for f in user_files.get(uid,[]) if is_running(uid,f[0]))
        user_rows += f"<tr><td><code>{uid}</code></td><td>{un}</td><td>{t}</td><td>{fc}</td><td>{rn}</td><td>{rc}</td></tr>"
    if not user_rows: user_rows = "<tr><td colspan='6' class='text-muted'>No users</td></tr>"
    bu = BOT_USERNAME; bu_clean = BOT_USERNAME.replace("@","")
    bot_color = "#e74c3c" if bot_locked else "#2ecc71"
    bot_status = "Locked" if bot_locked else "Unlocked"
    return PAGE_HTML.format(tu=tu,tf=tf,rs=rs,ruc=ruc,ru=ru,are=are,top_ref=top_ref,
            free_c=free_c,prem_c=prem_c,own_c=own_c,cpu=cpu,ram_u=ram_u,ram_t=ram_t,ram_p=ram_p,
            bot_color=bot_color,bot_status=bot_status,user_rows=user_rows,bu=bu,bu_clean=bu_clean)

@flask_app.route("/health")
def health():
    return json.dumps({"status":"running","users":len(active_users),"scripts":len(bot_scripts),"uptime":str(datetime.now()-startup_time)})

USER_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Users - BLACK TITAN</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:#0a0a0f;color:#e0e0e0}.card{background:#12121a;border:1px solid #2a2a3a;border-radius:12px}.table{color:#e0e0e0}</style></head><body>
<div class="container p-4">
<h3 class="mb-4"><i class="bi bi-people me-2"></i>Users</h3>
<div class="card p-3"><table class="table table-dark"><thead><tr>
<th>ID</th><th>Username</th><th>Tier</th><th>Files</th><th>Running</th><th>Referrals</th><th>Auto-Restart</th></tr></thead><tbody>{rows}</tbody></table></div>
<a href="/" class="btn btn-outline-light mt-3">Back</a>
</div></body></html>"""

@flask_app.route("/users")
def web_users():
    rows = ""
    for uid in sorted(active_users):
        try: un = bot.get_chat(uid).username or str(uid)
        except: un = str(uid)
        t = get_tier(uid); fc = file_count(uid); rc = refsys.count(uid)
        rn = sum(1 for f in user_files.get(uid,[]) if is_running(uid,f[0]))
        ar = "✅" if refsys.is_auto(uid) else "❌"
        rows += f"<tr><td><code>{uid}</code></td><td>{un}</td><td>{t}</td><td>{fc}</td><td>{rn}</td><td>{rc}</td><td>{ar}</td></tr>"
    if not rows: rows = "<tr><td colspan='7' class='text-muted'>No users</td></tr>"
    return USER_PAGE.format(rows=rows)

FILES_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Files - BLACK TITAN</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:#0a0a0f;color:#e0e0e0}.card{background:#12121a;border:1px solid #2a2a3a;border-radius:12px}.table{color:#e0e0e0}</style></head><body>
<div class="container p-4">
<h3 class="mb-4"><i class="bi bi-file-code me-2"></i>Files</h3>
<div class="card p-3"><table class="table table-dark"><thead><tr>
<th>User ID</th><th>File Name</th><th>Type</th><th>Project</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
<a href="/" class="btn btn-outline-light mt-3">Back</a>
</div></body></html>"""

@flask_app.route("/files")
def web_files():
    rows = ""
    for uid, files in user_files.items():
        for entry in files:
            fn, ft = entry[0], entry[1]
            proj = entry[2] if len(entry)==3 else ""
            st = "🟢 Running" if is_running(uid,fn) else "🔴 Stopped"
            rows += f"<tr><td><code>{uid}</code></td><td>{fn}</td><td>{ft}</td><td>{proj or '-'}</td><td>{st}</td></tr>"
    if not rows: rows = "<tr><td colspan='5' class='text-muted'>No files</td></tr>"
    return FILES_PAGE.format(rows=rows)

SCRIPTS_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scripts - BLACK TITAN</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:#0a0a0f;color:#e0e0e0}.card{background:#12121a;border:1px solid #2a2a3a;border-radius:12px}.table{color:#e0e0e0}</style></head><body>
<div class="container p-4">
<h3 class="mb-4"><i class="bi bi-terminal me-2"></i>Running Scripts</h3>
<div class="card p-3"><table class="table table-dark"><thead><tr>
<th>User ID</th><th>File</th><th>Type</th><th>Started</th><th>PID</th></tr></thead><tbody>{rows}</tbody></table></div>
<a href="/" class="btn btn-outline-light mt-3">Back</a>
</div></body></html>"""

@flask_app.route("/scripts")
def web_scripts():
    rows = ""
    for k, v in bot_scripts.items():
        uid = v["uid"]; fn = v["fn"]; tp = v["tp"]; pid = v["process"].pid if v.get("process") else "?"
        st = v.get("st","")
        rows += f"<tr><td><code>{uid}</code></td><td>{fn}</td><td>{tp}</td><td>{st}</td><td>{pid}</td></tr>"
    if not rows: rows = "<tr><td colspan='5' class='text-muted'>No running scripts</td></tr>"
    return SCRIPTS_PAGE.format(rows=rows)

REFS_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Referrals - BLACK TITAN</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:#0a0a0f;color:#e0e0e0}.card{background:#12121a;border:1px solid #2a2a3a;border-radius:12px}.table{color:#e0e0e0}</style></head><body>
<div class="container p-4">
<h3 class="mb-4"><i class="bi bi-link-45deg me-2"></i>Referral Leaderboard</h3>
<div class="card p-3"><table class="table table-dark"><thead><tr>
<th>#</th><th>User</th><th>Referrals</th><th>Auto-Restart</th></tr></thead><tbody>{rows}</tbody></table></div>
<a href="/" class="btn btn-outline-light mt-3">Back</a>
</div></body></html>"""

@flask_app.route("/referrals")
def web_refs():
    top = refsys.top(50); rows = ""
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    for i, r in enumerate(top, 1):
        un = r["un"] or f"User {r['uid']}"
        m = medals[i-1] if i<=10 else f"{i}."
        ar = "✅" if r["ar"] else "❌"
        rows += f"<tr><td>{m}</td><td>{un}</td><td>{r['cnt']}</td><td>{ar}</td></tr>"
    if not rows: rows = "<tr><td colspan='4' class='text-muted'>No referrals yet</td></tr>"
    return REFS_PAGE.format(rows=rows)

startup_time = datetime.now()

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

Thread(target=run_flask, daemon=True).start()
print("✅ Management Dashboard started.")

# ====== BUTTONS ======
def main_markup(uid):
    mk = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton(B("📢 Updates"), url=UPDATE_CHANNEL),
        types.InlineKeyboardButton(B("👥 Group"), url=UPDATE_GROUP),
        types.InlineKeyboardButton(B("📤 Upload"), callback_data="upload"),
        types.InlineKeyboardButton(B("📂 My Files"), callback_data="check_files"),
        types.InlineKeyboardButton(B("⚡ Speed"), callback_data="speed"),
        types.InlineKeyboardButton(B("📊 Stats"), callback_data="stats"),
        types.InlineKeyboardButton(B("👤 Profile"), callback_data="profile"),
        types.InlineKeyboardButton(B("🤝 Refer"), callback_data="refer"),
        types.InlineKeyboardButton(B("🏆 Leaderboard"), callback_data="leaderboard"),
        types.InlineKeyboardButton(B("🔄 Restart All"), callback_data="restart_all"),
        types.InlineKeyboardButton(B("📞 Contact"), url=f"https://t.me/{BOT_USERNAME.replace('@','')}")
    ]
    if uid in admin_ids:
        ab = [
            types.InlineKeyboardButton(B("👑 Admin"), callback_data="admin_panel"),
            types.InlineKeyboardButton(B("💳 Subs"), callback_data="subscription"),
            types.InlineKeyboardButton(B("📢 Broadcast"), callback_data="broadcast"),
            types.InlineKeyboardButton(B("🔒 Lock") if not bot_locked else B("🔓 Unlock"),
                                       callback_data="lock_bot" if not bot_locked else "unlock_bot"),
            types.InlineKeyboardButton(B("🔄 Recover"), callback_data="recover_all"),
            types.InlineKeyboardButton(B("📈 Analytics"), callback_data="analytics"),
            types.InlineKeyboardButton(B("🚀 Restart Bot"), callback_data="restart_bot")
        ]
        mk.add(btns[0],btns[1]); mk.add(btns[2],btns[3]); mk.add(btns[4],ab[0])
        mk.add(ab[1],ab[2]); mk.add(ab[3],ab[4]); mk.add(btns[6],btns[7])
        mk.add(ab[6],ab[5]); mk.add(btns[8],btns[5]); mk.add(btns[9],btns[10])
    else:
        mk.add(btns[0],btns[1]); mk.add(btns[2],btns[3]); mk.add(btns[4],btns[5])
        mk.add(btns[6],btns[7]); mk.add(btns[8],btns[9]); mk.add(btns[10])
    return mk

def reply_kb(uid):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if uid in admin_ids:
        b = [B(x) for x in ["📢 Updates","👥 Group","📤 Upload","📂 My Files","⚡ Speed","📊 Stats",
             "👤 Profile","🤝 Refer","🏆 Leaderboard","👑 Admin","💳 Subs","📢 Broadcast",
             "🔄 Recover","🔄 Restart All","🚀 Restart Bot","📞 Contact"]]
    else:
        b = [B(x) for x in ["📢 Updates","👥 Group","📤 Upload","📂 My Files","⚡ Speed","📊 Stats",
             "👤 Profile","🤝 Refer","🏆 Leaderboard","🔄 Restart All","📞 Contact"]]
    for i in range(0, len(b), 2):
        mk.add(*[types.KeyboardButton(t) for t in b[i:i+2]])
    return mk

def ctrl_btns(uid, fn, running=True):
    mk = types.InlineKeyboardMarkup(row_width=2)
    if running:
        mk.row(types.InlineKeyboardButton(B("🔴 Stop"), callback_data=f"stp_{uid}_{fn}"),
               types.InlineKeyboardButton(B("🔄 Restart"), callback_data=f"rst_{uid}_{fn}"))
        mk.row(types.InlineKeyboardButton(B("🗑️ Delete"), callback_data=f"del_{uid}_{fn}"),
               types.InlineKeyboardButton(B("📜 Logs"), callback_data=f"log_{uid}_{fn}"))
    else:
        mk.row(types.InlineKeyboardButton(B("🟢 Start"), callback_data=f"sta_{uid}_{fn}"),
               types.InlineKeyboardButton(B("🗑️ Delete"), callback_data=f"del_{uid}_{fn}"))
        mk.row(types.InlineKeyboardButton(B("📜 Logs"), callback_data=f"log_{uid}_{fn}"))
    mk.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data="check_files"))
    return mk

def admin_mk():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.row(types.InlineKeyboardButton(B("➕ Add Admin"), callback_data="add_adm"),
           types.InlineKeyboardButton(B("➖ Remove Admin"), callback_data="rm_adm"))
    mk.row(types.InlineKeyboardButton(B("📋 List Admins"), callback_data="list_adm"),
           types.InlineKeyboardButton(B("📊 System Stats"), callback_data="sys_stats"))
    mk.row(types.InlineKeyboardButton(B("🔙 Back"), callback_data="back"))
    return mk

def sub_mk():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.row(types.InlineKeyboardButton(B("➕ Add Sub"), callback_data="add_sub"),
           types.InlineKeyboardButton(B("➖ Remove Sub"), callback_data="rm_sub"))
    mk.row(types.InlineKeyboardButton(B("🔍 Check Sub"), callback_data="chk_sub"))
    mk.row(types.InlineKeyboardButton(B("🔙 Back"), callback_data="back"))
    return mk

def ref_mk(uid):
    mk = types.InlineKeyboardMarkup(row_width=2)
    c = refsys.get_code(uid)
    mk.add(types.InlineKeyboardButton(B("🔗 Copy Link"), callback_data=f"cpy_{uid}"))
    mk.add(types.InlineKeyboardButton(B("📊 My Referrals"), callback_data=f"myr_{uid}"))
    mk.add(types.InlineKeyboardButton(B("🏆 Leaderboard"), callback_data="leaderboard"))
    mk.add(types.InlineKeyboardButton(B("📋 QR Code"), callback_data=f"qr_{uid}"))
    mk.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data="back"))
    return mk

def lb_mk():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(types.InlineKeyboardButton(B("🔄 Refresh"), callback_data="rflb"))
    mk.add(types.InlineKeyboardButton(B("🏆 My Rank"), callback_data="myrk"))
    mk.add(types.InlineKeyboardButton(B("🤝 Refer"), callback_data="refer"))
    mk.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data="back"))
    return mk

# ====== SCRIPT RUNNER ======
MODS = {
    "telebot":"pyTelegramBotAPI","telegram":"python-telegram-bot",
    "aiogram":"aiogram==2.25.1","aiogram.contrib":"aiogram==2.25.1",
    "pyrogram":"pyrogram","telethon":"telethon","requests":"requests","flask":"Flask",
    "psutil":"psutil","qrcode":"qrcode","pillow":"Pillow","cryptography":"cryptography",
    "bs4":"beautifulsoup4","pandas":"pandas","numpy":"numpy"
}

def install_mod(name, msg):
    root = name.split(".")[0]
    pkg = MODS.get(root.lower(), root)
    try:
        bot.reply_to(msg, B(f"🐍 Installing `{root}`..."))
        r = subprocess.run([sys.executable,"-m","pip","install",pkg,"--quiet"], capture_output=True, text=True)
        if r.returncode==0:
            bot.reply_to(msg, B(f"✅ `{pkg}` installed.")); return True
        else:
            bot.reply_to(msg, B(f"❌ Failed `{pkg}`.")); return False
    except Exception as e:
        bot.reply_to(msg, B(f"❌ {e}")); return False

def run_py(script_path, uid, folder, fn, msg):
    try:
        animate(msg, ANIM_EXEC)
        if not os.path.exists(script_path): return
        try:
            proc = subprocess.Popen([sys.executable,script_path], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
            out, err = proc.communicate(timeout=5)
            if err:
                m = re.search(r"ModuleNotFoundError: No module named '(.+?)'", err)
                if m and install_mod(m.group(1), msg):
                    time.sleep(2); run_py(script_path, uid, folder, fn, msg); return
        except subprocess.TimeoutExpired:
            if proc: proc.kill()
        lf = open(os.path.join(folder,f"{os.path.splitext(fn)[0]}.log"),"w",encoding="utf-8",errors="ignore")
        sinfo = None
        if os.name=="nt":
            sinfo=subprocess.STARTUPINFO(); sinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow=subprocess.SW_HIDE
        proc = subprocess.Popen([sys.executable,script_path],cwd=folder,stdout=lf,stderr=lf,stdin=subprocess.PIPE,startupinfo=sinfo,encoding="utf-8",errors="ignore")
        k = f"{uid}_{fn}"
        bot_scripts[k] = {"process":proc,"lf":lf,"fn":fn,"uid":uid,"st":datetime.now(),"tp":"py","sk":k}
        rec.save(uid,fn,script_path,proc.pid)
        bot.send_message(msg.chat.id, B(f"✅ `{fn}` started! PID: {proc.pid}"))
    except Exception as e:
        bot.reply_to(msg, B(f"❌ {e}"))

def run_js(script_path, uid, folder, fn, msg):
    try:
        animate(msg, ANIM_EXEC)
        if not os.path.exists(script_path): return
        try:
            proc = subprocess.Popen(["node",script_path], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
            out, err = proc.communicate(timeout=5)
            if err and "Cannot find module" in err:
                m = re.search(r"Cannot find module '(.+?)'", err)
                if m:
                    bot.reply_to(msg, B(f"📦 Installing `{m.group(1)}`..."))
                    subprocess.run(["npm","install",m.group(1)], cwd=folder, capture_output=True)
                    time.sleep(2); run_js(script_path, uid, folder, fn, msg); return
        except subprocess.TimeoutExpired:
            if proc: proc.kill()
        lf = open(os.path.join(folder,f"{os.path.splitext(fn)[0]}.log"),"w",encoding="utf-8",errors="ignore")
        sinfo = None
        if os.name=="nt":
            sinfo=subprocess.STARTUPINFO(); sinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow=subprocess.SW_HIDE
        proc = subprocess.Popen(["node",script_path],cwd=folder,stdout=lf,stderr=lf,stdin=subprocess.PIPE,startupinfo=sinfo,encoding="utf-8",errors="ignore")
        k = f"{uid}_{fn}"
        bot_scripts[k] = {"process":proc,"lf":lf,"fn":fn,"uid":uid,"st":datetime.now(),"tp":"js","sk":k}
        rec.save(uid,fn,script_path,proc.pid)
        bot.send_message(msg.chat.id, B(f"✅ `{fn}` started! PID: {proc.pid}"))
    except Exception as e:
        bot.reply_to(msg, B(f"❌ {e}"))

def handle_zip(content, fn, uid, folder, msg, project=""):
    td = None
    try:
        td = tempfile.mkdtemp()
        with open(os.path.join(td,fn),"wb") as f: f.write(content)
        with zipfile.ZipFile(os.path.join(td,fn)) as z: z.extractall(td)
        files = os.listdir(td)
        py = [f for f in files if f.endswith(".py")]
        js = [f for f in files if f.endswith(".js")]
        main = None; ft = None
        for n in ["main.py","bot.py","app.py"]:
            if n in py: main=n; ft="py"; break
        if not main and py: main=py[0]; ft="py"
        elif not main and js:
            for n in ["index.js","main.js","bot.js"]:
                if n in js: main=n; ft="js"; break
            if not main and js: main=js[0]; ft="js"
        if not main: bot.reply_to(msg, B("❌ No .py/.js in ZIP.")); return
        for item in os.listdir(td):
            s=os.path.join(td,item); d=os.path.join(folder,item)
            if os.path.isdir(s): shutil.copytree(s,d,dirs_exist_ok=True)
            else: shutil.copy2(s,d)
        save_file(uid,main,ft,project)
        fp = os.path.join(folder,main)
        if ft=="py": threading.Thread(target=run_py, args=(fp,uid,folder,main,msg)).start()
        else: threading.Thread(target=run_js, args=(fp,uid,folder,main,msg)).start()
    except Exception as e: bot.reply_to(msg, B(f"❌ ZIP error: {e}"))
    finally:
        if td and os.path.exists(td): shutil.rmtree(td)

# ====== PROJECT SYSTEM ======
user_state = {}  # {uid: {"action":"upload","project":"..."}}

def get_project_folder(uid, project):
    b = os.path.join(BASE_DIR, "bt_uploads", str(uid), project)
    os.makedirs(b, exist_ok=True); return b

def get_user_projects(uid):
    pdir = os.path.join(BASE_DIR, "bt_uploads", str(uid))
    if not os.path.exists(pdir): return []
    return sorted([d for d in os.listdir(pdir) if os.path.isdir(os.path.join(pdir,d))])

def project_files(uid, project):
    pdir = get_project_folder(uid, project)
    if not os.path.exists(pdir): return []
    return sorted(os.listdir(pdir))

def del_project(uid, project):
    pdir = os.path.join(BASE_DIR, "bt_uploads", str(uid), project)
    if os.path.exists(pdir): shutil.rmtree(pdir)
    # remove from user_files
    if uid in user_files:
        user_files[uid] = [x for x in user_files[uid] if x[0] != project]

@bot.message_handler(func=lambda m: user_state.get(m.from_user.id,{}).get("action")=="await_project" and m.text)
def handle_project_name(msg):
    uid = msg.from_user.id; pn = msg.text.strip().replace("/","_").replace(" ","_")[:30]
    if not pn: bot.reply_to(msg, B("⚠️ Invalid project name.")); return
    get_project_folder(uid, pn)
    user_state[uid] = {"action":"upload","project":pn}
    bot.reply_to(msg, B(f"📁 Project `{pn}` set. Send .py, .js, or .zip files."),
                 reply_markup=types.ForceReply(selective=False))

# ====== COMMANDS ======
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    uid = msg.from_user.id; un = msg.from_user.username
    add_user(uid, un); refsys.update_un(uid, un)
    rc = None
    if len(msg.text.split())>1: rc = msg.text.split()[1].strip()
    if rc and rc.startswith("BT"):
        try:
            rid = int(rc[2:-4])
            if rid != uid and refsys.add(rid, uid, un):
                bot.reply_to(msg, B(f"🎉 Referred by `{rid}`"))
        except: pass
    tier = get_tier(uid); ti = TIERS[tier]; rc2 = refsys.count(uid); ar = refsys.is_auto(uid) if tier=="free" else True; rk = refsys.rank(uid)
    wt = B(f"""
╔══ 𝐁𝐋𝐀𝐂𝐊 𝐓𝐈𝐓𝐀𝐍 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 ══╗
║         𝐕𝐄𝐑𝐒𝐈𝐎𝐍 𝟒.𝟎           ║
╚═══════════════════════════════╝

👤 Welcome, {msg.from_user.first_name}!
🆔 `{uid}`
🎫 {ti["icon"]} {ti["name"]}
📁 {file_count(uid)}/{file_limit(uid)}

📊 Referrals: {rc2}/{TIERS["free"]["rn"]}
🏆 Rank: #{rk if rk else "-"}
🔄 Auto-Restart: {'✅' if ar else '❌'}

📢 {UPDATE_CHANNEL}
👥 {UPDATE_GROUP}

Features:
• Auto-Recovery System
• Tier-Based Hosting
• Python/JS Support
• Real-Time Monitoring
• 🏆 Referral Leaderboard
""")
    try:
        pp = bot.get_user_profile_photos(uid, limit=1)
        if pp.total_count>0:
            bot.send_photo(msg.chat.id, pp.photos[0][-1].file_id, caption=wt, reply_markup=reply_kb(uid), parse_mode="Markdown")
        else:
            bot.send_message(msg.chat.id, wt, reply_markup=reply_kb(uid), parse_mode="Markdown")
    except:
        bot.send_message(msg.chat.id, wt, reply_markup=reply_kb(uid), parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def cmd_help(msg):
    bot.reply_to(msg, B(f"""
🤖 BLACK TITAN HELP

Commands:
/start - Start
/help - Help
/refer - Referral link
/leaderboard - Top referrers
/stats - Statistics

Upload .py, .js, or .zip files.
Auto-installs dependencies.

Auto-Restart:
• Premium/Owner: ✅ Always
• Free: 3 referrals needed

Referral:
1. /refer -> get link
2. Share with friends
3. Get auto-restart after 3

Support:
📢 {UPDATE_CHANNEL}
👥 {UPDATE_GROUP}
👤 {BOT_USERNAME}
"""), parse_mode="Markdown")

@bot.message_handler(commands=["refer"])
def cmd_refer(msg):
    uid = msg.from_user.id; tier = get_tier(uid)
    rc = refsys.count(uid); ar = refsys.is_auto(uid) if tier=="free" else True
    mk, link = None, None
    c = refsys.get_code(uid)
    bu = bot.get_me().username
    link = f"https://t.me/{bu}?start={c}"
    bot.reply_to(msg, B(f"""
🤝 *REFERRAL SYSTEM*

👤 `{uid}`
📊 {rc}/{TIERS["free"]["rn"]}
🔄 {'✅' if ar else '❌'}

🔗 Link:
`{link}`

Share with friends!
3 referrals = Auto-Restart!
"""), parse_mode="Markdown", reply_markup=ref_mk(uid))

@bot.message_handler(commands=["leaderboard","topref"])
def cmd_lb(msg):
    top = refsys.top(10)
    if not top: bot.reply_to(msg, B("🏆 No referrals yet!")); return
    t = B("""🏆 *LEADERBOARD*
━━━━━━━━━━━━━━━━━━━
""")
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    for i, r in enumerate(top):
        un = r["un"] or f"User {r['uid']}"
        m = medals[i] if i<len(medals) else f"{i+1}."
        t += B(f"\n{m} *{un}*\n   👥 `{r['cnt']}` | {'✅' if r['ar'] else '❌'}\n")
    uid = msg.from_user.id; rk = refsys.rank(uid); rc = refsys.count(uid)
    t += B(f"\n━━━━━━━━━━━━━━━━━━━\n")
    t += B(f"👤 You: #{rk if rk else '-'} | {rc}/{TIERS['free']['rn']}")
    bot.reply_to(msg, t, parse_mode="Markdown", reply_markup=lb_mk())

@bot.message_handler(commands=["stats"])
def cmd_stats(msg):
    tu = len(active_users); tf = sum(len(f) for f in user_files.values())
    rs = sum(1 for k,v in bot_scripts.items() if is_running(v["uid"], v["fn"]))
    ruc = rec.count()
    ru = sum(1 for u in active_users if refsys.count(u)>0)
    are = sum(1 for u in active_users if refsys.is_auto(u))
    bot.reply_to(msg, B(f"""
📊 STATISTICS

👥 Users: {tu}
📁 Files: {tf}
🟢 Running: {rs}
💾 Recovery: {ruc}
🔒 {'Locked' if bot_locked else 'Unlocked'}

🎫 Tiers:
• FREE: {sum(1 for u in active_users if get_tier(u)=='free')}
• PREMIUM: {sum(1 for u in active_users if get_tier(u)=='premium')}
• OWNER: {sum(1 for u in active_users if get_tier(u)=='owner')}

🤝 Referrals:
• Referring: {ru}
• Auto-Restart: {are}
"""), parse_mode="Markdown")

@bot.message_handler(commands=["restartall","recover"])
def cmd_ra(msg):
    if msg.from_user.id not in admin_ids:
        bot.reply_to(msg, B("⚠️ Admin only.")); return
    if msg.text.startswith("/recover"):
        animate(msg, ANIM_RECV)
        rv = rec.recover_all()
        bot.reply_to(msg, B(f"✅ Recovered {len(rv)} scripts.") if rv else B("📭 Nothing to recover."))
    else:
        animate(msg, ANIM_EXEC)
        r = 0
        for uid,files in user_files.items():
            for fn,ft in files:
                if is_running(uid,fn):
                    k=f"{uid}_{fn}"
                    if k in bot_scripts: kill_proc(bot_scripts[k]); del bot_scripts[k]
                fo=get_folder(uid); fp=os.path.join(fo,fn)
                if os.path.exists(fp):
                    if ft=="py": threading.Thread(target=run_py, args=(fp,uid,fo,fn,msg)).start()
                    else: threading.Thread(target=run_js, args=(fp,uid,fo,fn,msg)).start()
                    r+=1; time.sleep(0.5)
        bot.reply_to(msg, B(f"✅ Restarted {r} scripts."))

@bot.message_handler(commands=["restartbot"])
def cmd_rb(msg):
    if msg.from_user.id not in admin_ids: bot.reply_to(msg, B("⚠️ Admin only.")); return
    bot.reply_to(msg, B("🚀 Sending notifications..."))
    threading.Thread(target=lambda: [bot.send_message(u, B("🔄 Bot restarting..."), parse_mode="Markdown") and time.sleep(0.1) for u in list(active_users)]).start()
    animate(msg, ANIM_REST)
    time.sleep(5)
    os.execv(sys.executable, ["python"]+sys.argv)

# ====== FILE HANDLER ======
def start_upload(msg):
    uid = msg.from_user.id
    st = user_state.get(uid,{})
    if st.get("action")=="upload" and st.get("project"):
        bot.reply_to(msg, B(f"📁 Send file for project `{st['project']}` (.py, .js, .zip)"))
        return
    projects = get_user_projects(uid)
    if projects:
        mk = types.InlineKeyboardMarkup(row_width=2)
        for p in projects[:10]:
            mk.add(types.InlineKeyboardButton(B(f"📁 {p}"), callback_data=f"useproj_{p}"))
        mk.add(types.InlineKeyboardButton(B("➕ New Project"), callback_data="newproj"))
        mk.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data="back"))
        bot.reply_to(msg, B("📁 Select project or create new:"), reply_markup=mk)
    else:
        user_state[uid] = {"action":"await_project"}
        bot.reply_to(msg, B("📝 Send a project name to start:"))

@bot.message_handler(content_types=["document"])
def handle_file(msg):
    uid = msg.from_user.id
    if not rlim.check(uid): bot.reply_to(msg, B("⚠️ Rate limit. Wait 60s.")); return
    if bot_locked and uid not in admin_ids: bot.reply_to(msg, B("⚠️ Bot locked.")); return
    if file_count(uid) >= file_limit(uid):
        bot.reply_to(msg, B(f"⚠️ Limit ({file_count(uid)}/{file_limit(uid)}).")); return
    st = user_state.get(uid,{})
    proj = st.get("project","") if st.get("action")=="upload" else ""
    if not proj:
        bot.reply_to(msg, B("⚠️ First select a project via 📤 Upload.")); return
    doc = msg.document
    if not doc.file_name: bot.reply_to(msg, B("⚠️ No file name.")); return
    ext = os.path.splitext(doc.file_name)[1].lower()
    if ext not in [".py",".js",".zip"]: bot.reply_to(msg, B("⚠️ Use .py, .js, or .zip")); return
    animate(msg, ANIM_UPLD)
    try:
        fi = bot.get_file(doc.file_id); dl = bot.download_file(fi.file_path)
        folder = get_project_folder(uid, proj); fp = os.path.join(folder, doc.file_name)
        with open(fp,"wb") as f: f.write(dl)
        if ext==".zip":
            save_file(uid, doc.file_name, "zip", proj)
            handle_zip(dl, doc.file_name, uid, folder, msg, proj)
        elif ext==".py":
            save_file(uid, doc.file_name, "py", proj)
            threading.Thread(target=run_py, args=(fp,uid,folder,doc.file_name,msg)).start()
        elif ext==".js":
            save_file(uid, doc.file_name, "js", proj)
            threading.Thread(target=run_js, args=(fp,uid,folder,doc.file_name,msg)).start()
    except Exception as e:
        bot.reply_to(msg, B(f"❌ Upload error: {e}"))

# ====== TEXT HANDLERS ======
H = {}
def reg_handlers():
    global H
    H = {
        B("📢 Updates"): lambda m: bot.reply_to(m, f"📢 {UPDATE_CHANNEL}\n👥 {UPDATE_GROUP}"),
        B("👥 Group"): lambda m: bot.reply_to(m, f"👥 {UPDATE_GROUP}"),
        B("📤 Upload"): lambda m: start_upload(m),
        B("📂 My Files"): lambda m: show_files(m),
        B("⚡ Speed"): lambda m: check_sp(m),
        B("📊 Stats"): lambda m: cmd_stats(m),
        B("👤 Profile"): lambda m: show_profile(m),
        B("🤝 Refer"): lambda m: cmd_refer(m),
        B("🏆 Leaderboard"): lambda m: cmd_lb(m),
        B("🔄 Restart All"): lambda m: cmd_ra(m),
        B("👑 Admin"): lambda m: show_admin(m),
        B("💳 Subs"): lambda m: show_subs(m),
        B("📢 Broadcast"): lambda m: start_bc(m),
        B("🔄 Recover"): lambda m: cmd_ra(m),
        B("🚀 Restart Bot"): lambda m: cmd_rb(m),
        B("📞 Contact"): lambda m: bot.reply_to(m, B(f"📞 {BOT_USERNAME}"))
    }
reg_handlers()

@bot.message_handler(func=lambda m: m.text in H)
def handle_btn(m): H[m.text](m)

def show_files(msg):
    uid = msg.from_user.id; files = user_files.get(uid,[])
    if not files: bot.reply_to(msg, B("📭 No files.")); return
    projects = {}
    for entry in files:
        fn, ft, proj = entry if len(entry)==3 else (entry[0], entry[1], "")
        projects.setdefault(proj,[]).append((fn,ft))
    mk = types.InlineKeyboardMarkup(row_width=1)
    for proj in sorted(projects):
        pf = projects[proj]
        label = f"📁 {proj} ({len(pf)} files)" if proj else f"📂 General ({len(pf)} files)"
        mk.add(types.InlineKeyboardButton(B(label), callback_data=f"proj_{uid}_{proj or '_'}"))
    bot.reply_to(msg, B("📂 Your Projects:"), reply_markup=mk)

def check_sp(msg):
    s = time.time(); m = bot.reply_to(msg, B("🏃 Checking..."))
    l = round((time.time()-s)*1000, 2)
    bot.edit_message_text(B(f"⚡ Speed\n⏱️ {l}ms\n🔒 {'Locked' if bot_locked else 'Unlocked'}"), msg.chat.id, m.message_id)

def show_profile(msg):
    uid = msg.from_user.id; tier = get_tier(uid); ti = TIERS[tier]
    rc = refsys.count(uid); ar = refsys.is_auto(uid) if tier=="free" else True; rk = refsys.rank(uid)
    bot.reply_to(msg, B(f"""
👤 PROFILE

🆔 `{uid}`
👤 {msg.from_user.first_name}
🎫 {ti["icon"]} {ti["name"]}
📁 {file_count(uid)}/{file_limit(uid)}
🟢 Running: {sum(1 for f in user_files.get(uid,[]) if is_running(uid,f[0]))}

🤝 {rc}/{TIERS["free"]["rn"]}
🏆 #{rk if rk else "-"}
🔄 {'Enabled' if ar else 'Disabled'}

Auto-Restart:
• Premium/Owner: ✅ Always
• Free: Refer 3 friends
"""), parse_mode="Markdown")

def show_admin(msg):
    if msg.from_user.id not in admin_ids: return
    bot.reply_to(msg, B("👑 ADMIN PANEL"), reply_markup=admin_mk())

def show_subs(msg):
    if msg.from_user.id not in admin_ids: return
    bot.reply_to(msg, B("💳 SUBSCRIPTIONS"), reply_markup=sub_mk())

def start_bc(msg):
    if msg.from_user.id not in admin_ids: return
    bot.reply_to(msg, B("📢 Send message to broadcast."))
    bot.register_next_step_handler(msg, process_bc)

def process_bc(msg):
    if msg.from_user.id not in admin_ids: return
    text = msg.text or msg.caption
    if not text: bot.reply_to(msg, B("⚠️ No message.")); return
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton(B("✅ Confirm"), callback_data=f"bcc_{msg.message_id}"),
           types.InlineKeyboardButton(B("❌ Cancel"), callback_data="bccx"))
    bot.reply_to(msg, B(f"📢 Broadcast to {len(active_users)} users?\n\n{(text[:1000] if text else '(media)')}"), reply_markup=mk)

# ====== CALLBACKS ======
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    d = c.data; uid = c.from_user.id
    try:
        if d=="upload":
            if file_count(uid)>=file_limit(uid): bot.answer_callback_query(c.id, B("⚠️ Limit reached"), show_alert=True); return
            bot.answer_callback_query(c.id); start_upload(c.message)
        elif d.startswith("proj_"): cb_proj_files(c)
        elif d.startswith("useproj_"): cb_use_proj(c)
        elif d=="newproj":
            user_state[uid] = {"action":"await_project"}
            bot.answer_callback_query(c.id); bot.send_message(c.message.chat.id, B("📝 Send a project name:"))
        elif d=="check_files": cb_files(c)
        elif d.startswith("fil_"): cb_file_ctrl(c)
        elif d.startswith("sta_"): cb_start(c)
        elif d.startswith("stp_"): cb_stop(c)
        elif d.startswith("rst_"): cb_rst(c)
        elif d.startswith("del_"): cb_del(c)
        elif d.startswith("log_"): cb_log(c)
        elif d in ("speed","stats","profile","refer"): {"speed":cb_sp,"stats":cb_stats,"profile":cb_profile,"refer":cb_refer}[d](c)
        elif d=="leaderboard": cmd_lb(c.message); bot.answer_callback_query(c.id)
        elif d=="rflb": cmd_lb(c.message); bot.answer_callback_query(c.id)
        elif d=="myrk": cb_myrk(c)
        elif d.startswith("cpy_"): cb_cpy(c)
        elif d.startswith("qr_"): cb_qr(c)
        elif d.startswith("myr_"): cb_myr(c)
        elif d=="restart_all": cb_ra(c)
        elif d=="admin_panel": cb_admin(c)
        elif d=="subscription": cb_sub(c)
        elif d=="broadcast": cb_bc(c)
        elif d in ("lock_bot","unlock_bot"): cb_lock(c, d=="lock_bot")
        elif d=="recover_all": cb_rec(c)
        elif d=="analytics": cb_an(c)
        elif d in ("add_adm","rm_adm"): cb_addrm_adm(c)
        elif d=="list_adm": cb_list_adm(c)
        elif d=="sys_stats": cb_sys(c)
        elif d in ("add_sub","rm_sub","chk_sub"): cb_sub_ops(c)
        elif d.startswith("bcc_"): cb_bcc(c)
        elif d=="bccx": bot.answer_callback_query(c.id,"❌ Cancelled"); bot.delete_message(c.message.chat.id,c.message.message_id)
        elif d=="restart_bot": cmd_rb(c.message)
        elif d=="back": cb_back(c)
        else: bot.answer_callback_query(c.id,"❌ Unknown")
    except Exception as e: logger.error(f"CB err: {e}"); bot.answer_callback_query(c.id,"❌ Error")

def cb_proj_files(c):
    try:
        p = c.data.split("_", 2); uid = int(p[1]); proj = p[2].replace("_","")
        if c.from_user.id != uid and c.from_user.id not in admin_ids:
            bot.answer_callback_query(c.id, B("⚠️ Denied"), show_alert=True); return
        files = user_files.get(uid,[])
        pfiles = [x for x in files if (x[2] if len(x)==3 else "")==proj or (not proj and len(x)==2)]
        mk = types.InlineKeyboardMarkup(row_width=1)
        for entry in pfiles:
            fn, ft = entry[0], entry[1]
            ir = is_running(uid, fn)
            mk.add(types.InlineKeyboardButton(B(f"{'🟢' if ir else '🔴'} {fn} ({ft})"), callback_data=f"fil_{uid}_{fn}"))
        mk.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data="check_files"))
        bot.answer_callback_query(c.id)
        bot.edit_message_text(B(f"📁 {proj or 'General'}:"), c.message.chat.id, c.message.message_id, reply_markup=mk)
    except Exception as e: logger.error(f"Proj files err: {e}")

def cb_use_proj(c):
    try:
        proj = c.data.split("_", 1)[1]
        uid = c.from_user.id
        user_state[uid] = {"action":"upload","project":proj}
        bot.answer_callback_query(c.id, B(f"✅ Project: {proj}"), show_alert=True)
        bot.send_message(c.message.chat.id, B(f"📁 Project `{proj}` set. Send .py, .js, or .zip."))
    except Exception as e: logger.error(f"Use proj err: {e}")

def cb_files(c):
    uid = c.from_user.id; files = user_files.get(uid,[])
    if not files: bot.answer_callback_query(c.id,B("📭 No files"),show_alert=True); return
    projects = {}
    for entry in files:
        fn, ft, proj = entry if len(entry)==3 else (entry[0], entry[1], "")
        projects.setdefault(proj,[]).append((fn,ft))
    mk = types.InlineKeyboardMarkup(row_width=1)
    for proj in sorted(projects):
        pf = projects[proj]
        label = f"📁 {proj} ({len(pf)} files)" if proj else f"📂 General ({len(pf)} files)"
        mk.add(types.InlineKeyboardButton(B(label), callback_data=f"proj_{uid}_{proj or '_'}"))
    mk.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data="back"))
    bot.answer_callback_query(c.id); bot.edit_message_text(B("📂 Your Projects:"), c.message.chat.id, c.message.message_id, reply_markup=mk)

def cb_file_ctrl(c):
    try:
        p=c.data.split("_"); uid=int(p[1]); fn="_".join(p[2:])
        if c.from_user.id!=uid and c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        fi=None
        for entry in user_files.get(uid,[]):
            f,ft = entry[0], entry[1]
            if f==fn: fi=(f,ft); break
        if not fi: bot.answer_callback_query(c.id,B("❌ Not found"),show_alert=True); return
        ir=is_running(uid,fn)
        bot.answer_callback_query(c.id)
        bot.edit_message_text(B(f"⚙️ `{fn}`\n📁 {fi[1]}\n📊 {'🟢 Running' if ir else '🔴 Stopped'}"), c.message.chat.id, c.message.message_id, reply_markup=ctrl_btns(uid,fn,ir), parse_mode="Markdown")
    except Exception as e: logger.error(f"File ctrl: {e}")

def cb_start(c):
    try:
        p=c.data.split("_"); uid=int(p[1]); fn="_".join(p[2:])
        if c.from_user.id!=uid and c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        if is_running(uid,fn): bot.answer_callback_query(c.id,B("✅ Already running"),show_alert=True); return
        proj=""; ft="py"
        for entry in user_files.get(uid,[]):
            f,ft2 = entry[0], entry[1]
            if entry[2] if len(entry)==3 else "": proj=entry[2]
            if f==fn: ft=ft2; break
        fo = get_project_folder(uid, proj) if proj else get_folder(uid)
        fp=os.path.join(fo,fn)
        if not os.path.exists(fp): bot.answer_callback_query(c.id,B("❌ Not found"),show_alert=True); return
        bot.answer_callback_query(c.id,B("🚀 Starting..."))
        if ft=="py": threading.Thread(target=run_py,args=(fp,uid,fo,fn,c.message)).start()
        else: threading.Thread(target=run_js,args=(fp,uid,fo,fn,c.message)).start()
    except Exception as e: logger.error(f"Start err: {e}")

def cb_stop(c):
    try:
        p=c.data.split("_"); uid=int(p[1]); fn="_".join(p[2:])
        if c.from_user.id!=uid and c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        if not is_running(uid,fn): bot.answer_callback_query(c.id,B("✅ Already stopped"),show_alert=True); return
        k=f"{uid}_{fn}"
        if k in bot_scripts: kill_proc(bot_scripts[k]); del bot_scripts[k]
        bot.answer_callback_query(c.id,B("🛑 Stopped"))
        bot.edit_message_reply_markup(c.message.chat.id,c.message.message_id,reply_markup=ctrl_btns(uid,fn,False))
    except Exception as e: logger.error(f"Stop err: {e}")

def _get_proj_for_file(uid, fn):
    for entry in user_files.get(uid,[]):
        if entry[0]==fn:
            return entry[2] if len(entry)==3 else ""
    return ""

def cb_rst(c):
    try:
        p=c.data.split("_"); uid=int(p[1]); fn="_".join(p[2:])
        if c.from_user.id!=uid and c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        if is_running(uid,fn):
            k=f"{uid}_{fn}"
            if k in bot_scripts: kill_proc(bot_scripts[k]); del bot_scripts[k]
            time.sleep(1)
        proj=_get_proj_for_file(uid,fn); fo=get_project_folder(uid,proj) if proj else get_folder(uid)
        fp=os.path.join(fo,fn)
        if not os.path.exists(fp): bot.answer_callback_query(c.id,B("❌ Not found"),show_alert=True); return
        ft="py"
        for entry in user_files.get(uid,[]):
            if entry[0]==fn: ft=entry[1]; break
        bot.answer_callback_query(c.id,B("🔄 Restarting..."))
        if ft=="py": threading.Thread(target=run_py,args=(fp,uid,fo,fn,c.message)).start()
        else: threading.Thread(target=run_js,args=(fp,uid,fo,fn,c.message)).start()
    except Exception as e: logger.error(f"Restart err: {e}")

def cb_del(c):
    try:
        p=c.data.split("_"); uid=int(p[1]); fn="_".join(p[2:])
        if c.from_user.id!=uid and c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        if is_running(uid,fn):
            k=f"{uid}_{fn}"
            if k in bot_scripts: kill_proc(bot_scripts[k]); del bot_scripts[k]
        proj=_get_proj_for_file(uid,fn); fo=get_project_folder(uid,proj) if proj else get_folder(uid)
        fp=os.path.join(fo,fn); lp=os.path.join(fo,f"{os.path.splitext(fn)[0]}.log")
        if os.path.exists(fp): os.remove(fp)
        if os.path.exists(lp): os.remove(lp)
        del_file(uid,fn)
        bot.answer_callback_query(c.id,B("🗑️ Deleted"))
        cb_files(c)
    except Exception as e: logger.error(f"Del err: {e}")

def cb_log(c):
    try:
        p=c.data.split("_"); uid=int(p[1]); fn="_".join(p[2:])
        if c.from_user.id!=uid and c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        proj=_get_proj_for_file(uid,fn); fo=get_project_folder(uid,proj) if proj else get_folder(uid)
        lp=os.path.join(fo,f"{os.path.splitext(fn)[0]}.log")
        if not os.path.exists(lp): bot.answer_callback_query(c.id,B("📭 No logs"),show_alert=True); return
        with open(lp,encoding="utf-8",errors="ignore") as f: lc=f.read()
        if len(lc)>3000: lc="...\n"+lc[-3000:]
        bot.answer_callback_query(c.id)
        bot.send_message(c.message.chat.id, B(f"📜 `{fn}`\n```\n{lc}\n```"), parse_mode="Markdown")
    except Exception as e: logger.error(f"Log err: {e}")

def cb_sp(c):
    s=time.time(); bot.answer_callback_query(c.id)
    l=round((time.time()-s)*1000,2)
    bot.edit_message_text(B(f"⚡ {l}ms"), c.message.chat.id, c.message.message_id)

def cb_stats(c):
    uid=c.from_user.id; tu=len(active_users); tf=sum(len(f) for f in user_files.values())
    rs=sum(1 for k,v in bot_scripts.items() if is_running(v["uid"],v["fn"])); ruc=rec.count()
    ru=sum(1 for u in active_users if refsys.count(u)>0); are=sum(1 for u in active_users if refsys.is_auto(u))
    bot.answer_callback_query(c.id)
    bot.edit_message_text(B(f"""
📊 STATS

👥 {tu} | 📁 {tf} | 🟢 {rs} | 💾 {ruc} | {'🔴' if bot_locked else '🟢'}

🎫 FREE:{sum(1 for u in active_users if get_tier(u)=='free')} | PREM:{sum(1 for u in active_users if get_tier(u)=='premium')} | OWN:{sum(1 for u in active_users if get_tier(u)=='owner')}

🤝 Ref: {ru} | Auto: {are}
"""), c.message.chat.id, c.message.message_id)

def cb_profile(c):
    uid=c.from_user.id; tier=get_tier(uid); ti=TIERS[tier]
    rc=refsys.count(uid); ar=refsys.is_auto(uid) if tier=="free" else True; rk=refsys.rank(uid)
    bot.answer_callback_query(c.id)
    bot.edit_message_text(B(f"""
👤 PROFILE

`{uid}` | {ti["icon"]}
📁 {file_count(uid)}/{file_limit(uid)}
🟢 {sum(1 for f in user_files.get(uid,[]) if is_running(uid,f[0]))}

🤝 {rc}/{TIERS["free"]["rn"]} | #{rk if rk else "-"}
🔄 {'✅' if ar else '❌'}
"""), c.message.chat.id, c.message.message_id)

def cb_refer(c):
    uid=c.from_user.id; tier=get_tier(uid); rc=refsys.count(uid); ar=refsys.is_auto(uid) if tier=="free" else True
    bu=bot.get_me().username; cd=refsys.get_code(uid); link=f"https://t.me/{bu}?start={cd}"
    bot.answer_callback_query(c.id)
    bot.edit_message_text(B(f"""
🤝 REFERRAL

`{uid}` | {rc}/{TIERS["free"]["rn"]} | {'✅' if ar else '❌'}

🔗 `{link}`
"""), c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=ref_mk(uid))

def cb_myrk(c):
    uid=c.from_user.id; rk=refsys.rank(uid); rc=refsys.count(uid); ar=refsys.is_auto(uid)
    bot.answer_callback_query(c.id)
    bot.send_message(c.message.chat.id, B(f"🏆 Rank: #{rk if rk else '-'} | {rc}/{TIERS['free']['rn']} | {'✅' if ar else '❌'}"), parse_mode="Markdown")

def cb_cpy(c):
    try:
        uid=int(c.data.split("_")[1])
        if c.from_user.id!=uid: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        bu=bot.get_me().username; cd=refsys.get_code(uid); link=f"https://t.me/{bu}?start={cd}"
        bot.answer_callback_query(c.id,B("🔗 Copied!"),show_alert=True)
        bot.send_message(c.message.chat.id, f"🔗 *Your Link:*\n\n{link}\n\n*Share with friends!*", parse_mode="Markdown")
    except Exception as e: logger.error(f"Copy err: {e}")

def cb_qr(c):
    try:
        uid=int(c.data.split("_")[1])
        if c.from_user.id!=uid: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        bu=bot.get_me().username; cd=refsys.get_code(uid); link=f"https://t.me/{bu}?start={cd}"
        qr=qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
        qr.add_data(link); qr.make(fit=True); img=qr.make_image(fill_color="black",back_color="white")
        bio=BytesIO(); img.save(bio,'PNG'); bio.seek(0)
        bot.answer_callback_query(c.id,B("📱 Generating..."))
        bot.send_photo(c.message.chat.id,bio,caption=f"📱 *QR for your link*\n\n{link}", parse_mode="Markdown")
    except Exception as e: logger.error(f"QR err: {e}")

def cb_myr(c):
    try:
        uid=int(c.data.split("_")[1])
        if c.from_user.id!=uid: bot.answer_callback_query(c.id,B("⚠️ Denied"),show_alert=True); return
        info=refsys.info(uid)
        if not info:
            bot.answer_callback_query(c.id); bot.send_message(c.message.chat.id, B(f"📊 0/{TIERS['free']['rn']} | ❌"), parse_mode="Markdown"); return
        rc=info.get("cnt",0); ar=info.get("ar",False); rk=info.get("rank","-"); refs=info.get("r",[])
        t=B(f"📊 {rc}/{TIERS['free']['rn']} | #{rk if rk else '-'} | {'✅' if ar else '❌'}")
        if refs:
            t+=B("\n\nReferred:")
            for i,r in enumerate(refs[:5],1): t+=B(f"\n{i}. {r.get('un','User')}")
            if len(refs)>5: t+=B(f"\n...+{len(refs)-5} more")
        bot.answer_callback_query(c.id); bot.send_message(c.message.chat.id, t, parse_mode="Markdown")
    except Exception as e: logger.error(f"Myr err: {e}")

def cb_ra(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    m=bot.send_message(c.message.chat.id, ANIM_EXEC[0]); r=0
    for uid,files in user_files.items():
        for fn,ft in files:
            if is_running(uid,fn):
                k=f"{uid}_{fn}"
                if k in bot_scripts: kill_proc(bot_scripts[k]); del bot_scripts[k]
            fo=get_folder(uid); fp=os.path.join(fo,fn)
            if os.path.exists(fp):
                if ft=="py": threading.Thread(target=run_py,args=(fp,uid,fo,fn,c.message)).start()
                else: threading.Thread(target=run_js,args=(fp,uid,fo,fn,c.message)).start()
                r+=1; time.sleep(0.5)
    bot.edit_message_text(B(f"✅ {r} restarted."), c.message.chat.id, m.message_id)
    bot.answer_callback_query(c.id)

def cb_admin(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    bot.answer_callback_query(c.id)
    bot.edit_message_text(B("👑 ADMIN"), c.message.chat.id, c.message.message_id, reply_markup=admin_mk())

def cb_sub(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    bot.answer_callback_query(c.id)
    bot.edit_message_text(B("💳 SUBS"), c.message.chat.id, c.message.message_id, reply_markup=sub_mk())

def cb_bc(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    bot.answer_callback_query(c.id)
    bot.send_message(c.message.chat.id, B("📢 Send message."))
    bot.register_next_step_handler(c.message, process_bc)

def cb_lock(c, lock):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    global bot_locked; bot_locked=lock
    bot.answer_callback_query(c.id,B("🔒 Locked" if lock else "🔓 Unlocked"))
    bot.edit_message_reply_markup(c.message.chat.id,c.message.message_id,reply_markup=main_markup(c.from_user.id))

def cb_rec(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    m=bot.send_message(c.message.chat.id,ANIM_RECV[0])
    for f in ANIM_RECV:
        try: bot.edit_message_text(f,c.message.chat.id,m.message_id); time.sleep(0.3)
        except: pass
    rv=rec.recover_all()
    bot.edit_message_text(B(f"✅ {len(rv)} recovered.") if rv else B("📭 Nothing."), c.message.chat.id, m.message_id)
    bot.answer_callback_query(c.id)

def cb_an(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    tu=len(active_users); tf=sum(len(f) for f in user_files.values())
    rs=sum(1 for k,v in bot_scripts.items() if is_running(v["uid"],v["fn"]))
    ru=sum(1 for u in active_users if refsys.count(u)>0); are=sum(1 for u in active_users if refsys.is_auto(u)); tr=sum(refsys.count(u) for u in active_users)
    ts=0
    for u2 in user_files:
        fo=get_folder(u2)
        if os.path.exists(fo):
            for r,dd,ff in os.walk(fo):
                for f in ff: ts+=os.path.getsize(os.path.join(r,f))
    t5=refsys.top(5); lb=""
    for i,r in enumerate(t5,1): lb+=B(f"{i}. {r['un'] or r['uid']}: {r['cnt']}\n")
    bot.answer_callback_query(c.id)
    bot.edit_message_text(B(f"""
📈 ANALYTICS

👥 {tu} | 📁 {tf} | 🟢 {rs}

📊 Ref: {tr} | Users: {ru} | Auto: {are}
🔄 Conv: {round(ru/max(tu,1)*100,1)}%

🏆
{lb}
💾 {round(ts/1024/1024,2)}MB
"""), c.message.chat.id, c.message.message_id)

def cb_addrm_adm(c):
    if c.from_user.id!=OWNER_ID: bot.answer_callback_query(c.id,B("⚠️ Owner only"),show_alert=True); return
    is_add = c.data=="add_adm"
    bot.answer_callback_query(c.id)
    bot.send_message(c.message.chat.id, B(f"👑 Enter user ID to {'add' if is_add else 'remove'}:"))
    bot.register_next_step_handler(c.message, lambda m: process_adm(m, is_add))

def process_adm(msg, is_add):
    if msg.from_user.id!=OWNER_ID: return
    try:
        uid=int(msg.text.strip())
        if not is_add and uid==OWNER_ID: bot.reply_to(msg,B("❌ Cannot remove owner.")); return
        with DBL:
            conn=sqlite3.connect(DB_PATH,check_same_thread=False); c=conn.cursor()
            if is_add: c.execute("INSERT OR IGNORE INTO adm VALUES(?,?,?)",(uid,OWNER_ID,datetime.now().isoformat()))
            else: c.execute("DELETE FROM adm WHERE uid=?",(uid,))
            conn.commit(); conn.close()
        if is_add: admin_ids.add(uid)
        else: admin_ids.discard(uid)
        bot.reply_to(msg,B(f"✅ {'Added' if is_add else 'Removed'} `{uid}`."))
    except: bot.reply_to(msg,B("❌ Invalid ID."))

def cb_list_adm(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    al="\n".join(f"• `{u}` {'👑' if u==OWNER_ID else ''}" for u in sorted(admin_ids))
    bot.answer_callback_query(c.id); bot.edit_message_text(B(f"👑 Admins:\n\n{al}"), c.message.chat.id, c.message.message_id, parse_mode="Markdown")

def cb_sys(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    cpu=psutil.cpu_percent(interval=1); mem=psutil.virtual_memory(); disk=psutil.disk_usage("/")
    bot.answer_callback_query(c.id)
    bot.edit_message_text(B(f"""
🖥️ SYSTEM

CPU: {cpu}%
RAM: {mem.percent}% ({round(mem.used/1024**3,1)}/{round(mem.total/1024**3,1)}GB)
Disk: {disk.percent}% ({round(disk.used/1024**3,1)}/{round(disk.total/1024**3,1)}GB)

🤖 Bot: {len(active_users)} users | {sum(len(f) for f in user_files.values())} files | {len(bot_scripts)} running | {'🔴' if bot_locked else '🟢'} | {threading.active_count()} threads
"""), c.message.chat.id, c.message.message_id)

def cb_sub_ops(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    d=c.data; bot.answer_callback_query(c.id)
    if d=="add_sub": bot.send_message(c.message.chat.id,B("💳 Enter: user_id days")); bot.register_next_step_handler(c.message,lambda m: proc_sub_add(m))
    elif d=="rm_sub": bot.send_message(c.message.chat.id,B("💳 Enter user ID:")); bot.register_next_step_handler(c.message,lambda m: proc_sub_rm(m))
    elif d=="chk_sub": bot.send_message(c.message.chat.id,B("💳 Enter user ID:")); bot.register_next_step_handler(c.message,lambda m: proc_sub_chk(m))

def proc_sub_add(msg):
    if msg.from_user.id not in admin_ids: return
    try:
        p=msg.text.strip().split()
        if len(p)!=2: bot.reply_to(msg,B("❌ Use: user_id days")); return
        uid=int(p[0]); days=int(p[1])
        exp=datetime.now()+timedelta(days=days); save_sub(uid,exp,"premium")
        bot.reply_to(msg,B(f"✅ Sub for `{uid}` until {exp.strftime('%Y-%m-%d')}"))
    except: bot.reply_to(msg,B("❌ Invalid."))

def proc_sub_rm(msg):
    if msg.from_user.id not in admin_ids: return
    try: uid=int(msg.text.strip()); rem_sub(uid); bot.reply_to(msg,B(f"✅ Removed sub for `{uid}`"))
    except: bot.reply_to(msg,B("❌ Invalid."))

def proc_sub_chk(msg):
    if msg.from_user.id not in admin_ids: return
    try:
        uid=int(msg.text.strip())
        if uid in user_subscriptions:
            s=user_subscriptions[uid]; exp=s.get("expiry"); tier=s.get("tier","premium")
            if exp and exp>datetime.now(): bot.reply_to(msg,B(f"✅ Active | {tier} | {exp.strftime('%Y-%m-%d')} | {(exp-datetime.now()).days}d left"))
            else: bot.reply_to(msg,B("⚠️ Expired")); rem_sub(uid)
        else: bot.reply_to(msg,B("📭 No sub."))
    except: bot.reply_to(msg,B("❌ Invalid."))

def cb_bcc(c):
    if c.from_user.id not in admin_ids: bot.answer_callback_query(c.id,B("⚠️ Admin only"),show_alert=True); return
    try:
        bot.answer_callback_query(c.id,B("🚀 Sending..."))
        s=f=0; orig=c.message.reply_to_message
        if not orig: bot.edit_message_text(B("❌ Not found."),c.message.chat.id,c.message.message_id); return
        for u in list(active_users):
            try:
                if orig.text: bot.send_message(u,orig.text)
                elif orig.caption:
                    if orig.photo: bot.send_photo(u,orig.photo[-1].file_id,caption=orig.caption)
                    elif orig.video: bot.send_video(u,orig.video.file_id,caption=orig.caption)
                    elif orig.document: bot.send_document(u,orig.document.file_id,caption=orig.caption)
                s+=1
            except: f+=1
            time.sleep(0.1)
        bot.edit_message_text(B(f"✅ Done! Sent:{s} Failed:{f} Total:{len(active_users)}"),c.message.chat.id,c.message.message_id)
    except Exception as e: logger.error(f"BCC err: {e}")

def cb_back(c):
    uid=c.from_user.id; tier=get_tier(uid); ti=TIERS[tier]; rc=refsys.count(uid)
    ar=refsys.is_auto(uid) if tier=="free" else True; rk=refsys.rank(uid)
    wt=B(f"""
╔══ 𝐁𝐋𝐀𝐂𝐊 𝐓𝐈𝐓𝐀𝐍 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 ══╗
║         𝐕𝟒.𝟎                  ║
╚═══════════════════════════════╝

👋 {c.from_user.first_name}
🆔 `{uid}` | {ti["icon"]} {ti["name"]}
📁 {file_count(uid)}/{file_limit(uid)}
🤝 {rc}/{TIERS["free"]["rn"]} | #{rk if rk else "-"} | {'✅' if ar else '❌'}
""")
    bot.answer_callback_query(c.id)
    bot.edit_message_text(wt, c.message.chat.id, c.message.message_id, reply_markup=main_markup(uid), parse_mode="Markdown")

# ====== CREDITS ======
atexit.register(lambda: (logger.info("Shutdown..."), [kill_proc(v) for k,v in list(bot_scripts.items())], refsys.save()))

if __name__=="__main__":
    print("="*50)
    print("🤖 BLACK TITAN HOSTING BOT V4.0")
    print(f"👑 Owner: {OWNER_ID}")
    print(f"🛡️ Admins: {len(admin_ids)}")
    print(f"👥 Users: {len(active_users)}")
    print("="*50)
    threading.Thread(target=lambda: bot.send_message(OWNER_ID, B("🚀 BLACK TITAN HOSTING BOT STARTED! ✅"))).start()
    while True:
        try: bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout: time.sleep(5)
        except requests.exceptions.ConnectionError: time.sleep(15)
        except Exception as e: logger.critical(f"Fatal: {e}", exc_info=True); time.sleep(30)

"""
██████╗ ██╗      █████╗  ██████╗██╗  ██╗    ████████╗██╗████████╗ █████╗ ███╗   ██╗
██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝    ╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║
██████╔╝██║     ███████║██║     █████╔╝        ██║   ██║   ██║   ███████║██╔██╗ ██║
██╔══██╗██║     ██╔══██║██║     ██╔═██╗        ██║   ██║   ██║   ██╔══██║██║╚██╗██║
██████╔╝███████╗██║  ██║╚██████╗██║  ██╗       ██║   ██║   ██║   ██║  ██║██║ ╚████║
╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝       ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝

██████╗  ██████╗ ████████╗    ██╗   ██╗███████╗██████╗ ███████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗╚══██╔══╝    ██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗████╗  ██║
██████╔╝██║   ██║   ██║       ██║   ██║█████╗  ██████╔╝█████╗  ██║██║   ██║██╔██╗ ██║
██╔══██╗██║   ██║   ██║       ╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║   ██║██║╚██╗██║
██████╔╝╚██████╔╝   ██║        ╚████╔╝ ███████╗██║  ██║██║     ██║╚██████╔╝██║ ╚████║
╚═════╝  ╚═════╝    ╚═╝         ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

██╗  ██╗ ██████╗ ███████╗████████╗██╗███╗   ██╗ ██████╗
██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝
███████║██║   ██║███████╗   ██║   ██║██╔██╗ ██║██║  ███╗
██╔══██║██║   ██║╚════██║   ██║   ██║██║╚██╗██║██║   ██║
██║  ██║╚██████╔╝███████║   ██║   ██║██║ ╚████║╚██████╔╝
╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝

██████╗ ██╗   ██╗███████╗████████╗███████╗███╗   ███╗
██╔══██╗██║   ██║██╔════╝╚══██╔══╝██╔════╝████╗ ████║
██████╔╝██║   ██║███████╗   ██║   █████╗  ██╔████╔██║
██╔══██╗██║   ██║╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
██████╔╝╚██████╔╝███████║   ██║   ███████╗██║ ╚═╝ ██║
╚═════╝  ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝

𝐕𝐈𝐏 𝐃𝐀𝐑𝐊 𝐆𝐎𝐃 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 - 𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐈𝐎𝐍𝐀𝐋 𝐁𝐎𝐓 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐏𝐋𝐀𝐓𝐅𝐎𝐑𝐌
𝐕𝐄𝐑𝐒𝐈𝐎𝐍 𝟒.𝟎 - 𝐄𝐍𝐓𝐄𝐑𝐏𝐑𝐈𝐒𝐄 𝐆𝐑𝐀𝐃𝐄
𝐂𝐑𝐄𝐃𝐈𝐓𝐒: 𝐕𝐈𝐏 𝐃𝐀𝐑𝐊 𝐆𝐎𝐃
"""

import subprocess, sys, os, time, hashlib, json, sqlite3, shutil, tempfile, zipfile, re, atexit, threading, random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from collections import defaultdict, deque
from functools import wraps

_pip_base = [sys.executable,"-m","pip","install","--quiet"]
try: subprocess.run([sys.executable,"-m","pip","install","--dry-run","setuptools"], capture_output=True)
except: _pip_base.append("--break-system-packages")

_MOD_MAP = {"PIL":"Pillow","telebot":"pyTelegramBotAPI","flask":"Flask"}
for mod in ["telebot","psutil","requests","flask","qrcode","PIL","cryptography"]:
    try:
        __import__(mod)
    except ModuleNotFoundError:
        pkg = _MOD_MAP.get(mod, mod)
        print(f"Installing {pkg}...")
        subprocess.run(_pip_base + [pkg], capture_output=True)

import telebot
from telebot import types
import psutil
import requests
from flask import Flask, render_template_string
from threading import Thread
import qrcode

TOKEN = os.environ.get("BOT_TOKEN", "8792154488:AAHEi2aH2UrHRq_3QfX_J2gxWpmFY7Ptdkw")
OWNER_ID = int(os.environ.get("OWNER_ID", "7892915425"))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7702588711"))
ADMIN_IDS = {OWNER_ID, ADMIN_ID}
BOT_USERNAME = os.environ.get("BOT_USERNAME", "@VIP_DARK_GOD")
UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/vip_dark_god_primel")
UPDATE_GROUP = os.environ.get("UPDATE_GROUP", "https://t.me/vip_dark_god_chat")
SUPPORT_LINK = os.environ.get("SUPPORT_LINK", "https://t.me/vip_dark_god_support")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'bt_uploads')
BT_DATA_DIR = os.path.join(BASE_DIR, 'bt_data')
DATABASE_PATH = os.path.join(BT_DATA_DIR, 'vip_bot.db')
RUNNING_SCRIPTS_DB = os.path.join(BT_DATA_DIR, 'running_scripts.json')
LOGS_DIR = os.path.join(BT_DATA_DIR, 'logs')
BACKUP_DIR = os.path.join(BT_DATA_DIR, 'backups')

for dir_path in [UPLOAD_BOTS_DIR, BT_DATA_DIR, LOGS_DIR, BACKUP_DIR]:
    os.makedirs(dir_path, exist_ok=True)

startup_time = datetime.now()
PORT = int(os.environ.get("PORT", 8080))

class FontStyler:
    @staticmethod
    def bold(text: str) -> str:
        return f"<b>{text}</b>"
    @staticmethod
    def code(text: str) -> str:
        return f"<code>{text}</code>"
    @staticmethod
    def math_bold(text: str) -> str:
        m = {'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈','J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑','S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙','a':'𝐚','b':'𝐛','c':'𝐜','d':'𝐝','e':'𝐞','f':'𝐟','g':'𝐠','h':'𝐡','i':'𝐢','j':'𝐣','k':'𝐤','l':'𝐥','m':'𝐦','n':'𝐧','o':'𝐨','p':'𝐩','q':'𝐪','r':'𝐫','s':'𝐬','t':'𝐭','u':'𝐮','v':'𝐯','w':'𝐰','x':'𝐱','y':'𝐲','z':'𝐳',
         '0':'𝟎','1':'𝟏','2':'𝟐','3':'𝟑','4':'𝟒','5':'𝟓','6':'𝟔','7':'𝟕','8':'𝟖','9':'𝟗'}
        return ''.join(m.get(c, c) for c in text)

F = FontStyler()

ANIM_UPLOAD = ["📤 [▒▒▒▒▒▒▒▒▒▒] 0%","📤 [█▒▒▒▒▒▒▒▒▒] 10%","📤 [██▒▒▒▒▒▒▒▒] 20%","📤 [███▒▒▒▒▒▒▒] 30%","📤 [████▒▒▒▒▒▒] 40%","📤 [█████▒▒▒▒▒] 50%","📤 [██████▒▒▒▒] 60%","📤 [███████▒▒▒] 70%","📤 [████████▒▒] 80%","📤 [█████████▒] 90%","✅ [██████████] 100%"]
ANIM_DEPLOY = ["🚀 [░░░░░░░░░░]","🚀 [▓░░░░░░░░░]","🚀 [▓▓░░░░░░░░]","🚀 [▓▓▓░░░░░░░]","🚀 [▓▓▓▓░░░░░░]","🚀 [▓▓▓▓▓░░░░░]","🚀 [▓▓▓▓▓▓░░░░]","🚀 [▓▓▓▓▓▓▓░░░]","🚀 [▓▓▓▓▓▓▓▓░░]","🚀 [▓▓▓▓▓▓▓▓▓░]","✅ [▓▓▓▓▓▓▓▓▓▓]"]
ANIM_EXEC = ["⚡ Initializing...","⚡ Executing...","⚡ Running...","✅ Done!"]
ANIM_RECV = ["🔄","🔃","🔄","🔃"]
B = FontStyler.bold

logging = __import__('logging')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    def _init_db(self):
        conn = self._get_connection(); c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,username TEXT,first_name TEXT,last_name TEXT,tier TEXT DEFAULT 'free',joined_at TIMESTAMP,last_active TIMESTAMP,total_uploads INTEGER DEFAULT 0,total_bot_runs INTEGER DEFAULT 0,total_storage_used INTEGER DEFAULT 0,referral_code TEXT UNIQUE,referred_by INTEGER,is_banned BOOLEAN DEFAULT 0,notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (user_id INTEGER PRIMARY KEY,tier TEXT,expires_at TIMESTAMP,payment_method TEXT,transaction_id TEXT,amount REAL,activated_by INTEGER,activated_at TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,filename TEXT,file_type TEXT,file_size INTEGER,file_path TEXT,uploaded_at TIMESTAMP,last_started TIMESTAMP,is_running BOOLEAN DEFAULT 0,pid INTEGER,UNIQUE(user_id,filename))''')
        c.execute('''CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT,referrer_id INTEGER,referred_id INTEGER UNIQUE,referred_at TIMESTAMP,status TEXT DEFAULT 'pending')''')
        c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,action TEXT,details TEXT,timestamp TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT,message TEXT,created_by INTEGER,created_at TIMESTAMP,sent_to_all BOOLEAN DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY,value TEXT,updated_at TIMESTAMP)''')
        c.execute("INSERT OR IGNORE INTO settings VALUES (?,?,?)",('bot_locked','false',datetime.now().isoformat()))
        conn.commit(); conn.close()
    def execute(self, q, p=()):
        conn=self._get_connection(); c=conn.cursor(); c.execute(q,p); conn.commit(); conn.close(); return c
    def fetch_one(self, q, p=()):
        conn=self._get_connection(); conn.row_factory=sqlite3.Row; c=conn.cursor(); c.execute(q,p); r=c.fetchone(); conn.close(); return dict(r) if r else None
    def fetch_all(self, q, p=()):
        conn=self._get_connection(); conn.row_factory=sqlite3.Row; c=conn.cursor(); c.execute(q,p); r=c.fetchall(); conn.close(); return [dict(x) for x in r]

db = DatabaseManager(DATABASE_PATH)

class ReferralManager:
    @staticmethod
    def generate_code(uid):
        return hashlib.md5(f"{uid}{time.time()}".encode()).hexdigest()[:8].upper()
    @staticmethod
    def stats(uid):
        t=db.fetch_one("SELECT COUNT(*) as c FROM referrals WHERE referrer_id=? AND status='completed'",(uid,))
        p=db.fetch_one("SELECT COUNT(*) as c FROM referrals WHERE referrer_id=? AND status='pending'",(uid,))
        return {'total':t['c']if t else 0,'pending':p['c']if p else 0,'completed':t['c']if t else 0}
    @staticmethod
    def add(ref, rid):
        if ref==rid: return False
        if db.fetch_one("SELECT id FROM referrals WHERE referred_id=?",(rid,)): return False
        db.execute("INSERT INTO referrals(referrer_id,referred_id,referred_at,status) VALUES(?,?,?,?)",(ref,rid,datetime.now().isoformat(),'completed'))
        db.execute("UPDATE users SET referral_code=? WHERE user_id=?",(ReferralManager.generate_code(rid),rid))
        return True
    @staticmethod
    def leaderboard(limit=10):
        return db.fetch_all("SELECT u.user_id,u.username,COUNT(r.id) as referral_count FROM users u LEFT JOIN referrals r ON u.user_id=r.referrer_id AND r.status='completed' GROUP BY u.user_id ORDER BY referral_count DESC LIMIT ?",(limit,))

bot_scripts: Dict[str, Dict] = {}
active_users: set = set()
user_files: Dict[int, List[Dict]] = {}
bot_locked = False
user_projects: Dict[int, str] = {}

class UserTier(Enum):
    FREE="free"; PREMIUM="premium"; PRO="pro"; ULTIMATE="ultimate"; ENTERPRISE="enterprise"; ADMIN="admin"; OWNER="owner"

@dataclass
class TierBenefits:
    name:str; icon:str; color:str; upload_limit:int; max_file_size:int; auto_restart:bool; concurrent_bots:int; priority_support:bool; referral_needed:int; backup_retention_days:int; custom_domain:bool; api_access:bool; dedicated_resources:bool

TIER_SYSTEM = {
    UserTier.FREE: TierBenefits("FREE","🆓","#2ecc71",3,50*1024*1024,False,1,False,3,1,False,False,False),
    UserTier.PREMIUM: TierBenefits("PREMIUM","⭐","#f39c12",15,200*1024*1024,True,3,False,0,7,False,False,False),
    UserTier.PRO: TierBenefits("PRO","💎","#9b59b6",50,500*1024*1024,True,10,True,0,14,False,True,False),
    UserTier.ULTIMATE: TierBenefits("ULTIMATE","👑","#e74c3c",150,1024*1024*1024,True,30,True,0,30,True,True,True),
    UserTier.ENTERPRISE: TierBenefits("ENTERPRISE","🏢","#34495e",500,5*1024*1024*1024,True,100,True,0,90,True,True,True),
    UserTier.ADMIN: TierBenefits("ADMIN","🛡️","#1abc9c",10**9,10**12,True,10**9,True,0,365,True,True,True),
    UserTier.OWNER: TierBenefits("OWNER","🔥","#8b00ff",10**9,10**12,True,10**9,True,0,365,True,True,True),
}

def get_user_tier(uid):
    if uid==OWNER_ID: return UserTier.OWNER
    if uid in ADMIN_IDS: return UserTier.ADMIN
    u=db.fetch_one("SELECT tier FROM users WHERE user_id=?",(uid,))
    if not u: return UserTier.FREE
    sub=db.fetch_one("SELECT tier,expires_at FROM subscriptions WHERE user_id=? AND expires_at>?",(uid,datetime.now().isoformat()))
    if sub:
        try: return UserTier(sub['tier'])
        except: pass
    try: return UserTier(u['tier'])
    except: return UserTier.FREE

def get_tier_benefits(uid):
    return TIER_SYSTEM[get_user_tier(uid)]

def get_or_create_user(uid, uname=None, fn=None, ln=None):
    u=db.fetch_one("SELECT * FROM users WHERE user_id=?",(uid,))
    if not u:
        rc=ReferralManager.generate_code(uid)
        db.execute("INSERT INTO users(user_id,username,first_name,last_name,tier,joined_at,last_active,referral_code) VALUES(?,?,?,?,?,?,?,?)",
                   (uid,uname,fn,ln,'free',datetime.now().isoformat(),datetime.now().isoformat(),rc))
        u=db.fetch_one("SELECT * FROM users WHERE user_id=?",(uid,))
        logger.info(f"New user: {uid}")
    else:
        db.execute("UPDATE users SET last_active=?,username=COALESCE(?,username),first_name=COALESCE(?,first_name) WHERE user_id=?",
                   (datetime.now().isoformat(),uname,fn,uid))
    return dict(u) if u else {}

def get_user_files(uid):
    return db.fetch_all("SELECT * FROM files WHERE user_id=? ORDER BY uploaded_at DESC",(uid,))

def get_file_count(uid):
    r=db.fetch_one("SELECT COUNT(*) as c FROM files WHERE user_id=?",(uid,)); return r['c'] if r else 0

def can_upload(uid, size):
    tb=get_tier_benefits(uid); c=get_file_count(uid)
    if c>=tb.upload_limit: return False, f"File limit ({c}/{tb.upload_limit})"
    if size>tb.max_file_size: return False, f"File too large ({size/1024/1024:.1f}MB / {tb.max_file_size/1024/1024:.0f}MB)"
    return True, "OK"

def add_file(uid, fn, ft, size, path):
    try:
        db.execute("INSERT OR REPLACE INTO files(user_id,filename,file_type,file_size,file_path,uploaded_at) VALUES(?,?,?,?,?,?)",
                   (uid,fn,ft,size,path,datetime.now().isoformat()))
        db.execute("UPDATE users SET total_uploads=total_uploads+1,total_storage_used=total_storage_used+? WHERE user_id=?",(size,uid))
        return True
    except: return False

def delete_file(uid, fn):
    fi=db.fetch_one("SELECT file_path,file_size FROM files WHERE user_id=? AND filename=?",(uid,fn))
    if not fi: return False
    kill_script(uid, fn)
    try:
        if os.path.exists(fi['file_path']): os.remove(fi['file_path'])
        lp=os.path.join(os.path.dirname(fi['file_path']), f"{os.path.splitext(fn)[0]}.log")
        if os.path.exists(lp): os.remove(lp)
    except: pass
    db.execute("DELETE FROM files WHERE user_id=? AND filename=?",(uid,fn))
    db.execute("UPDATE users SET total_storage_used=total_storage_used-? WHERE user_id=?",(fi['file_size'],uid))
    return True

def is_running(uid, fn):
    k=f"{uid}_{fn}"
    if k not in bot_scripts: return False
    try: return psutil.Process(bot_scripts[k]['process'].pid).is_running()
    except: return False

def kill_proc(pi):
    try:
        p=pi.get("process")
        if not p or not hasattr(p,"pid"): return
        try:
            parent=psutil.Process(p.pid)
            for c in parent.children(recursive=True):
                try: c.terminate()
                except: pass
            parent.terminate(); parent.wait(timeout=3)
        except:
            try: parent.kill()
            except: pass
    except: pass

def kill_script(uid, fn):
    k=f"{uid}_{fn}"
    if k in bot_scripts: kill_proc(bot_scripts[k]); del bot_scripts[k]

def start_script(uid, fn, path, tp, msg):
    k=f"{uid}_{fn}"
    if k in bot_scripts:
        if is_running(uid,fn):
            bot.reply_to(msg, B("⚠️ Already running."))
            return
        del bot_scripts[k]
    folder=os.path.dirname(path)
    lf=open(os.path.join(folder,f"{os.path.splitext(fn)[0]}.log"),"w",encoding="utf-8",errors="ignore")
    sinfo=None
    if os.name=="nt":
        sinfo=subprocess.STARTUPINFO(); sinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow=subprocess.SW_HIDE
    cmd=[sys.executable,path] if tp=="py" else ["node",path]
    proc=subprocess.Popen(cmd,cwd=folder,stdout=lf,stderr=lf,stdin=subprocess.PIPE,startupinfo=sinfo)
    bot_scripts[k]={"process":proc,"lf":lf,"fn":fn,"uid":uid,"st":datetime.now(),"tp":tp,"sk":k}
    db.execute("UPDATE files SET is_running=1,pid=?,last_started=? WHERE user_id=? AND filename=?",(proc.pid,datetime.now().isoformat(),uid,fn))
    bot.send_message(msg.chat.id, B(f"✅ `{fn}` started! PID: {proc.pid}"))

MODS = {"telebot":"pyTelegramBotAPI","psutil":"psutil","requests":"requests","flask":"Flask","qrcode":"qrcode","PIL":"Pillow","cryptography":"cryptography",
        "aiogram":"aiogram","aiogram.contrib":"aiogram"}

def _pip_install(*args):
    return subprocess.run(_pip_base + list(args), capture_output=True, text=True)

def install_mod(name, msg):
    root=name.split(".")[0]; pkg=MODS.get(root.lower(),root)
    try:
        bot.reply_to(msg, B(f"🐍 Installing `{root}`..."))
        env_override = {**os.environ, "AIOHTTP_NO_EXTENSIONS": "1"} if root == "aiogram" else None
        r = subprocess.run(_pip_base + [pkg], capture_output=True, text=True, env=env_override)
        if r.returncode==0:
            bot.reply_to(msg, B(f"✅ `{pkg}` installed.")); return True
        else:
            err=r.stderr[:200] if r.stderr else r.stdout[:200]
            if "aiogram" in name.lower() and ("aiohttp" in err or "build" in err):
                bot.reply_to(msg, B("❌ Python 3.14 broke aiohttp C extensions. Try manual: `AIOHTTP_NO_EXTENSIONS=1 pip3 install --break-system-packages aiogram`"))
            else:
                bot.reply_to(msg, B(f"❌ Failed `{pkg}`.\n{err}"))
            return False
    except Exception as e:
        bot.reply_to(msg, B(f"❌ {e}")); return False

def animate(msg, frames):
    m=bot.reply_to(msg, frames[0])
    for f in frames:
        try: bot.edit_message_text(f, msg.chat.id, m.message_id); time.sleep(0.3)
        except: pass
    return m

DBL = threading.Lock()

class RecoveryManager:
    def __init__(self, db):
        self.db=db; self._recover()
    def _recover(self):
        for f in self.db.fetch_all("SELECT * FROM files WHERE is_running=1"):
            uid,fn,path=f['user_id'],f['filename'],f['file_path']
            if os.path.exists(path):
                k=f"{uid}_{fn}"; folder=os.path.dirname(path)
                lf=open(os.path.join(folder,f"{os.path.splitext(fn)[0]}.log"),"a",encoding="utf-8",errors="ignore")
                sinfo=None
                if os.name=="nt":
                    sinfo=subprocess.STARTUPINFO(); sinfo.dwFlags|=subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow=subprocess.SW_HIDE
                tp='py' if path.endswith('.py') else 'js'
                cmd=[sys.executable,path] if tp=='py' else ["node",path]
                try:
                    proc=subprocess.Popen(cmd,cwd=folder,stdout=lf,stderr=lf,stdin=subprocess.PIPE,startupinfo=sinfo)
                    bot_scripts[k]={"process":proc,"lf":lf,"fn":fn,"uid":uid,"st":datetime.now(),"tp":tp,"sk":k}
                    logger.info(f"Recovered: {k} (PID {proc.pid})")
                except: pass
    def save(self):
        try:
            import json
            with open(RUNNING_SCRIPTS_DB,'w') as f:
                json.dump({k:{'uid':v['uid'],'fn':v['fn'],'tp':v['tp'],'st':v['st'].isoformat() if isinstance(v['st'],datetime) else v['st']} for k,v in bot_scripts.items()},f)
        except: pass
    def recover_all(self):
        restored=[]
        for k,v in list(bot_scripts.items()):
            if not is_running(v['uid'],v['fn']): continue
            kill_proc(v)
            uid,fn,path=v['uid'],v['fn'],None
            f=db.fetch_one("SELECT file_path FROM files WHERE user_id=? AND filename=?",(uid,fn))
            if f: path=f['file_path']
            if path and os.path.exists(path):
                start_script(uid,fn,path,v['tp'],None); restored.append(k)
        return restored

rec=RecoveryManager(db)

atexit.register(lambda: (logger.info("Shutdown..."), [kill_proc(v) for k,v in list(bot_scripts.items())], rec.save()))

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><title>VIP DARK GOD HOSTING</title>
    <style>
    body{background:linear-gradient(135deg,#0a0a0a 0%,#1a1a2e 100%);color:#fff;font-family:'Courier New',monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
    .container{text-align:center;padding:2rem;border:2px solid #8b00ff;border-radius:20px;background:rgba(0,0,0,0.7);box-shadow:0 0 50px rgba(139,0,255,0.3)}
    h1{font-size:3rem;margin:0;background:linear-gradient(45deg,#8b00ff,#ff00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .status{color:#00ff88;margin-top:20px}
    .glow{animation:glow 2s ease-in-out infinite alternate}
    @keyframes glow{from{text-shadow:0 0 5px #8b00ff}to{text-shadow:0 0 20px #8b00ff}}
    </style></head><body>
    <div class="container">
    <h1>⚡ VIP DARK GOD HOSTING ⚡</h1>
    <p class="glow">Enterprise Grade Bot Hosting Platform</p>
    <p class="status">🟢 SYSTEM ONLINE 🟢</p>
    <p>Version 4.0 | Status: Operational</p>
    </div></body></html>""")

@flask_app.route('/health')
def health():
    return {"status":"running","users":db.fetch_one("SELECT COUNT(*) as c FROM users")['c'],"scripts":len(bot_scripts),"uptime":str(datetime.now()-startup_time)}

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

Thread(target=run_flask, daemon=True).start()
print("✅ Management Dashboard started.")

def main_markup(uid):
    mk=types.InlineKeyboardMarkup(row_width=2)
    btns=[
        types.InlineKeyboardButton("📤 Upload Bot",callback_data="upload"),
        types.InlineKeyboardButton("📂 My Bots",callback_data="my_bots"),
        types.InlineKeyboardButton("📊 Dashboard",callback_data="dashboard"),
        types.InlineKeyboardButton("👤 Profile",callback_data="profile"),
        types.InlineKeyboardButton("🤝 Referral",callback_data="referral"),
        types.InlineKeyboardButton("🏆 Leaderboard",callback_data="leaderboard"),
        types.InlineKeyboardButton("⚡ Speed Test",callback_data="speed"),
        types.InlineKeyboardButton("📢 Updates",url=UPDATE_CHANNEL),
        types.InlineKeyboardButton("💬 Support",url=SUPPORT_LINK),
        types.InlineKeyboardButton("📞 Contact",url=f"https://t.me/{BOT_USERNAME.replace('@','')}")
    ]
    if uid in ADMIN_IDS or uid==OWNER_ID:
        mk.add(btns[0],btns[1]); mk.add(btns[2],btns[3]); mk.add(btns[4],btns[5])
        mk.add(btns[6]); mk.add(types.InlineKeyboardButton("👑 Admin Panel",callback_data="admin_panel"))
        mk.add(types.InlineKeyboardButton("📢 Broadcast",callback_data="broadcast"))
        mk.add(btns[7],btns[8]); mk.add(btns[9])
    else:
        for i in range(0,len(btns),2):
            mk.add(*btns[i:i+2])
    return mk

def ctrl_btns(uid, fn, running=True):
    mk=types.InlineKeyboardMarkup(row_width=2)
    if running:
        mk.row(types.InlineKeyboardButton("🔴 Stop",callback_data=f"stp_{uid}_{fn}"),
               types.InlineKeyboardButton("🔄 Restart",callback_data=f"rst_{uid}_{fn}"))
        mk.row(types.InlineKeyboardButton("🗑️ Delete",callback_data=f"del_{uid}_{fn}"),
               types.InlineKeyboardButton("📜 Logs",callback_data=f"log_{uid}_{fn}"))
    else:
        mk.row(types.InlineKeyboardButton("🟢 Start",callback_data=f"sta_{uid}_{fn}"),
               types.InlineKeyboardButton("🗑️ Delete",callback_data=f"del_{uid}_{fn}"))
        mk.row(types.InlineKeyboardButton("📜 Logs",callback_data=f"log_{uid}_{fn}"))
    mk.add(types.InlineKeyboardButton("🔙 Back",callback_data="check_files"))
    return mk

def admin_mk():
    mk=types.InlineKeyboardMarkup(row_width=2)
    mk.row(types.InlineKeyboardButton("➕ Add Admin",callback_data="add_adm"),
           types.InlineKeyboardButton("➖ Remove Admin",callback_data="rm_adm"))
    mk.row(types.InlineKeyboardButton("📋 List Admins",callback_data="list_adm"),
           types.InlineKeyboardButton("📊 System Stats",callback_data="sys_stats"))
    mk.row(types.InlineKeyboardButton("🔙 Back",callback_data="back"))
    return mk

USER_PAGE = """<html><head><style>body{{font-family:Arial;background:#111;color:#fff;padding:20px}}
.card{{background:#222;border-radius:10px;padding:20px;margin-bottom:10px;border-left:4px solid {color}}}
.glow{{color:{color}}}</style></head><body>
<h2 class="glow">{icon} {name} TIER</h2>
<div class="card"><b>👤 User:</b> {first_name} (@{username})<br><b>🆔 ID:</b> <code>{user_id}</code></div>
<div class="card"><b>📊 Stats</b><br>📁 Files: {files}/{upload_limit}<br>💾 Used: {storage_used:.1f}MB / {storage_max:.0f}MB<br>🤖 Running: {running}<br>🤝 Referrals: {referrals}</div>
<div class="card"><b>🎫 Features</b><br>🔄 Auto-Restart: {auto_restart}<br>🔄 Concurrent: {concurrent}<br>🎯 Priority: {priority}<br>🌐 Custom Domain: {domain}</div></body></html>"""

FILES_PAGE = """<html><head><style>body{{font-family:Arial;background:#111;color:#fff;padding:20px}}
.card{{background:#222;border-radius:10px;padding:15px;margin-bottom:8px;border-left:4px solid #8b00ff}}
.glow{{color:#8b00ff}}</style></head><body>
<h2 class="glow">📁 {name}'s Files</h2>
{rows}</body></html>"""

SCRIPTS_PAGE = """<html><head><style>body{{font-family:Arial;background:#111;color:#fff;padding:20px}}
.card{{background:#222;border-radius:10px;padding:15px;margin-bottom:8px;border-left:4px solid #8b00ff}}
.status{{color:{color}}}</style></head><body>
<h2>📊 Running Scripts</h2>
{rows}</body></html>"""

REFS_PAGE = """<html><head><style>body{{font-family:Arial;background:#111;color:#fff;padding:20px}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:10px;text-align:left;border-bottom:1px solid #333}}
th{{color:#8b00ff;font-size:1.2em}}
.glow{{color:#ffd700}}</style></head><body>
<h2 class="glow">🏆 Referral Leaderboard</h2>
<table><tr><th>#</th><th>User</th><th>Referrals</th></tr>
{rows}</table></body></html>"""

@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid=message.from_user.id; uname=message.from_user.username; fn=message.from_user.first_name; ln=message.from_user.last_name
    user=get_or_create_user(uid,uname,fn,ln)
    if len(message.text.split())>1:
        rc=message.text.split()[1]
        ref=db.fetch_one("SELECT user_id FROM users WHERE referral_code=?",(rc,))
        if ref and ref['user_id']!=uid: ReferralManager.add(ref['user_id'],uid)
    tb=get_tier_benefits(uid); fc=get_file_count(uid)
    active_users.add(uid)
    txt=f"""
{F.math_bold('🔥 VIP DARK GOD HOSTING 🔥')}
{F.math_bold('═══════════════════════════')}

{B('Welcome, '+fn+'!')}

📊 {B('Your Status')}
└ 🆔 ID: <code>{uid}</code>
└ 🎫 Tier: {tb.icon} {tb.name}
└ 📁 Files: {fc}/{tb.upload_limit}
└ 🔄 Auto-Restart: {'✅' if tb.auto_restart else '❌'}

📈 {B('System Stats')}
└ 👥 Users: {db.fetch_one('SELECT COUNT(*) as c FROM users')['c']}
└ 🤖 Online Bots: {len(bot_scripts)}

{B('Need Help?')}
📢 Updates: {UPDATE_CHANNEL}
💬 Support: {SUPPORT_LINK}
    """
    bot.send_message(message.chat.id, txt, reply_markup=main_markup(uid))

@bot.message_handler(commands=['help'])
def cmd_help(message):
    txt=f"""
{F.math_bold('📚 VIP DARK GOD HOSTING - HELP')}
{F.math_bold('═══════════════════════════')}

{B('📤 Uploading Bots')}
• Send a .py, .js, or .zip file
• Bot auto-detects main file
• Dependencies auto-installed

{B('🎫 Tier System')}
• FREE: 3 bots, 50MB max
• PREMIUM: 15 bots, 200MB max
• PRO: 50 bots, 500MB max
• ULTIMATE: 150 bots, 1GB max
• ENTERPRISE: 500 bots, 5GB max

{B('🤝 Referral Program')}
• Invite friends using your referral link
• Get rewards for each referral
• Unlock auto-restart for FREE tier

{B('📞 Support')}
• Channel: {UPDATE_CHANNEL}
• Group: {UPDATE_GROUP}
• Contact: {BOT_USERNAME}
    """
    bot.reply_to(message, txt)

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, B("❌ Admin only.")); return
    msg=message.text.replace('/broadcast','',1).strip()
    if not msg: bot.reply_to(message, B("Usage: /broadcast <message>")); return
    users=db.fetch_all("SELECT user_id FROM users")
    sent=0
    for u in users:
        try: bot.send_message(u['user_id'],B(f"📢 Broadcast\n\n{msg}")); sent+=1; time.sleep(0.05)
        except: pass
    bot.reply_to(message, B(f"✅ Sent to {sent} users."))

@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    if message.from_user.id not in ADMIN_IDS: return
    bot.send_message(message.chat.id, B("👑 Admin Panel"), reply_markup=admin_mk())

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    tu=len(active_users); tf=sum(len(f) for f in user_files.values())
    rs=sum(1 for k,v in bot_scripts.items() if is_running(v['uid'],v['fn']))
    txt=f"""
📊 {B('System Stats')}
👥 Active Users: {tu}
📁 Total Files: {tf}
🤖 Running Scripts: {rs}
💾 RAM: {psutil.virtual_memory().percent}%
⚡ CPU: {psutil.cpu_percent()}%
📅 Uptime: {datetime.now()-startup_time}
    """
    bot.reply_to(message, txt)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    uid=message.from_user.id
    tb=get_tier_benefits(uid)
    fc=get_file_count(uid)
    if bot_locked and uid not in ADMIN_IDS:
        bot.reply_to(message, B("🔒 Bot locked for maintenance.")); return
    doc=message.document; fn=doc.file_name; fs=doc.file_size
    ok,err=can_upload(uid,fs)
    if not ok: bot.reply_to(message, B(f"❌ {err}")); return
    ext=os.path.splitext(fn)[1].lower()
    if ext not in ['.py','.js','.zip']:
        bot.reply_to(message, B("❌ Only .py, .js, .zip files allowed.")); return
    proj=user_projects.get(uid)
    if not proj:
        bot.reply_to(message, B("📁 Send a project name first, or use /setproject <name>"))
        return
    folder=os.path.join(UPLOAD_BOTS_DIR,str(uid),proj); os.makedirs(folder,exist_ok=True)
    fi=os.path.join(folder,fn)
    animate(message, ANIM_UPLOAD)
    try:
        file_info=bot.get_file(doc.file_id); downloaded=bot.download_file(file_info.file_path)
        with open(fi,'wb') as f: f.write(downloaded)
    except Exception as e:
        bot.reply_to(message, B(f"❌ Download failed.")); return
    if ext=='.zip':
        try:
            with zipfile.ZipFile(fi,'r') as zf:
                zf.extractall(folder)
            os.remove(fi)
            pyfiles=[f for f in os.listdir(folder) if f.endswith('.py')]
            if pyfiles: fn=pyfiles[0]; fi=os.path.join(folder,fn)
            else: bot.reply_to(message, B("❌ No .py found in zip.")); return
            # install deps from requirements.txt
            req_path=os.path.join(folder,'requirements.txt')
            if os.path.exists(req_path):
                install_mod_msg = bot.reply_to(message, B("📦 Installing deps..."))
                with open(req_path) as f:
                    for line in f:
                        line=line.strip()
                        if line and not line.startswith('#'):
                            _pip_install(line.split('>=')[0].split('==')[0].strip())
        except Exception as e:
            bot.reply_to(message, B(f"❌ Zip error: {e}")); return
    add_file(uid,fn,ext,fs,fi)
    bot.send_message(message.chat.id, B(f"✅ `{fn}` uploaded!"), reply_markup=ctrl_btns(uid,fn,False))

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/setproject'))
def set_project(message):
    uid=message.from_user.id
    parts=message.text.split(maxsplit=1)
    if len(parts)<2: bot.reply_to(message,B("Usage: /setproject <name>")); return
    user_projects[uid]=parts[1].strip()
    bot.reply_to(message,B(f"📁 Project set: `{parts[1]}`"))

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/'))
def handle_cmd(message):
    pass

@bot.message_handler(func=lambda m: True)
def handle_project_name(message):
    uid=message.from_user.id
    txt=message.text.strip()
    if not txt.startswith('/'):
        user_projects[uid]=txt
        bot.reply_to(message,B(f"📁 Project set: `{txt}`"))

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(c):
    uid=c.from_user.id; d=c.data
    if d=="upload":
        bot.send_message(c.message.chat.id, B("📁 Send your project name or use /setproject <name>\nThen upload .py, .js, or .zip"))
        bot.answer_callback_query(c.id)
    elif d=="my_bots" or d=="check_files":
        files=get_user_files(uid)
        if not files:
            bot.edit_message_text(B("📭 No files uploaded yet."),c.message.chat.id,c.message.message_id,reply_markup=main_markup(uid))
        else:
            txt=B("📂 Your Bots\n"); mk=types.InlineKeyboardMarkup(row_width=1)
            for f in files:
                fn=f['filename']; ru=is_running(uid,fn)
                status="🟢" if ru else "🔴"
                mk.add(types.InlineKeyboardButton(f"{status} {fn}",callback_data=f"file_{uid}_{fn}"))
            mk.add(types.InlineKeyboardButton("🔙 Main Menu",callback_data="back"))
            bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=mk)
        bot.answer_callback_query(c.id)
    elif d.startswith("file_"):
        parts=d.split('_',2); fuid=int(parts[1]); fn=parts[2]; ru=is_running(fuid,fn)
        txt=B(f"{'🟢' if ru else '🔴'} `{fn}`\n{'Running' if ru else 'Stopped'}")
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=ctrl_btns(fuid,fn,ru))
        bot.answer_callback_query(c.id)
    elif d.startswith("sta_"):
        parts=d.split('_',2); fuid=int(parts[1]); fn=parts[2]
        f=db.fetch_one("SELECT file_path,file_type FROM files WHERE user_id=? AND filename=?",(fuid,fn))
        if f and os.path.exists(f['file_path']):
            start_script(fuid,fn,f['file_path'],'py' if fn.endswith('.py') else 'js',c.message)
            ru=is_running(fuid,fn)
            bot.edit_message_reply_markup(c.message.chat.id,c.message.message_id,reply_markup=ctrl_btns(fuid,fn,ru))
        else: bot.answer_callback_query(c.id,B("❌ File not found."),show_alert=True)
        bot.answer_callback_query(c.id)
    elif d.startswith("stp_"):
        parts=d.split('_',2); fuid=int(parts[1]); fn=parts[2]; kill_script(fuid,fn)
        db.execute("UPDATE files SET is_running=0,pid=NULL WHERE user_id=? AND filename=?",(fuid,fn))
        bot.edit_message_reply_markup(c.message.chat.id,c.message.message_id,reply_markup=ctrl_btns(fuid,fn,False))
        bot.answer_callback_query(c.id)
    elif d.startswith("rst_"):
        parts=d.split('_',2); fuid=int(parts[1]); fn=parts[2]
        f=db.fetch_one("SELECT file_path,file_type FROM files WHERE user_id=? AND filename=?",(fuid,fn))
        if f and os.path.exists(f['file_path']):
            kill_script(fuid,fn); time.sleep(1)
            start_script(fuid,fn,f['file_path'],'py' if fn.endswith('.py') else 'js',c.message)
        bot.answer_callback_query(c.id)
    elif d.startswith("del_"):
        parts=d.split('_',2); fuid=int(parts[1]); fn=parts[2]
        delete_file(fuid,fn)
        bot.edit_message_text(B(f"🗑️ `{fn}` deleted."),c.message.chat.id,c.message.message_id,reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d.startswith("log_"):
        parts=d.split('_',2); fuid=int(parts[1]); fn=parts[2]
        folder=os.path.join(UPLOAD_BOTS_DIR,str(fuid),user_projects.get(fuid,""))
        lp=os.path.join(folder,f"{os.path.splitext(fn)[0]}.log")
        if os.path.exists(lp):
            try:
                with open(lp,'r',encoding='utf-8',errors='ignore') as f: content=f.read()
                if len(content)>3000: content=content[-3000:]
                bot.send_message(c.message.chat.id,B(f"📜 Logs for `{fn}`:\n<pre>{content}</pre>"))
            except: bot.send_message(c.message.chat.id,B("❌ Error reading log."))
        else: bot.send_message(c.message.chat.id,B("📭 No logs."))
        bot.answer_callback_query(c.id)
    elif d=="back":
        bot.edit_message_text(B("🏠 Main Menu"),c.message.chat.id,c.message.message_id,reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d=="dashboard":
        tu=len(active_users)
        rs=sum(1 for k,v in bot_scripts.items() if is_running(v['uid'],v['fn']))
        txt=f"📊 {B('Dashboard')}\n👥 Users: {tu}\n🤖 Running: {rs}\n📁 Total Files: {sum(len(f) for f in user_files.values())}"
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d=="profile":
        tb=get_tier_benefits(uid); fc=get_file_count(uid)
        ru=sum(1 for f in get_user_files(uid) if is_running(uid,f['filename']))
        refs=ReferralManager.stats(uid)
        txt=f"""
👤 {B('Profile')}
🆔 ID: <code>{uid}</code>
🎫 Tier: {tb.icon} {tb.name}
📁 Files: {fc}/{tb.upload_limit}
🤖 Running: {ru}
🤝 Referrals: {refs['total']}
        """
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d=="referral":
        u=db.fetch_one("SELECT referral_code FROM users WHERE user_id=?",(uid,))
        rc=u['referral_code'] if u else ""
        refs=ReferralManager.stats(uid)
        link=f"https://t.me/{BOT_USERNAME.replace('@','')}?start={rc}"
        txt=f"""
🤝 {B('Referral Program')}
🔗 Your Link: {link}
📊 Total Referrals: {refs['total']}
⏳ Pending: {refs['pending']}

Invite friends to unlock rewards!
        """
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d=="leaderboard":
        lb=ReferralManager.leaderboard()
        txt=f"🏆 {B('Referral Leaderboard')}\n"
        for i,u in enumerate(lb[:10],1):
            txt+=f"{i}. {u.get('username','Unknown')} - {u['referral_count']} referrals\n"
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d=="speed":
        import time
        s=time.time()
        bot.answer_callback_query(c.id)
        bot.send_message(c.message.chat.id,B(f"⚡ Response time: {(time.time()-s)*1000:.0f}ms"))
    elif d=="admin_panel":
        if uid not in ADMIN_IDS: return
        bot.edit_message_text(B("👑 Admin Panel"),c.message.chat.id,c.message.message_id,reply_markup=admin_mk())
        bot.answer_callback_query(c.id)
    elif d=="broadcast":
        if uid not in ADMIN_IDS: return
        bot.send_message(c.message.chat.id,B("📢 Send the broadcast message as /broadcast <message>"))
        bot.answer_callback_query(c.id)
    elif d=="add_adm":
        if uid!=OWNER_ID: return
        bot.send_message(c.message.chat.id,B("Send user ID to add as admin."))
        bot.register_next_step_handler(c.message, lambda m: (ADMIN_IDS.add(int(m.text)), bot.reply_to(m,B("✅ Admin added."))))
        bot.answer_callback_query(c.id)
    elif d=="rm_adm":
        if uid!=OWNER_ID: return
        bot.send_message(c.message.chat.id,B("Send user ID to remove from admin."))
        bot.register_next_step_handler(c.message, lambda m: (ADMIN_IDS.discard(int(m.text)), bot.reply_to(m,B("✅ Admin removed."))))
        bot.answer_callback_query(c.id)
    elif d=="list_adm":
        txt="👑 Admins:\n"+'\n'.join(str(x) for x in ADMIN_IDS)
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=admin_mk())
        bot.answer_callback_query(c.id)
    elif d=="sys_stats":
        tu=len(active_users); tf=sum(len(f) for f in user_files.values())
        rs=sum(1 for k,v in bot_scripts.items() if is_running(v['uid'],v['fn']))
        mem=psutil.virtual_memory(); cpu=psutil.cpu_percent()
        txt=f"""📊 {B('System Stats')}
👥 Users: {db.fetch_one('SELECT COUNT(*) as c FROM users')['c']}
🤖 Running: {rs}
💾 RAM: {mem.percent}% ({mem.used//1024//1024}MB/{mem.total//1024//1024}MB)
⚡ CPU: {cpu}%
📅 Uptime: {datetime.now()-startup_time}"""
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=admin_mk())
        bot.answer_callback_query(c.id)
    else:
        bot.answer_callback_query(c.id)

print("="*60)
print("🔥 VIP DARK GOD HOSTING BOT v4.0 🔥")
print("="*60)
print(f"Owner: {OWNER_ID}")
print(f"Admins: {len(ADMIN_IDS)}")
print(f"Users: {db.fetch_one('SELECT COUNT(*) as c FROM users')['c']}")
print("="*60)

try: bot.send_message(OWNER_ID, B("🚀 VIP DARK GOD HOSTING BOT STARTED! ✅"))
except: pass

try: os.waitpid(-1, os.WNOHANG)
except ChildProcessError: pass

while True:
    try: bot.polling(timeout=30, long_polling_timeout=15, non_stop=False)
    except Exception as e:
        em=str(e)
        if "409" in em:
            logger.warning("409 Conflict - releasing...")
            try: requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=5)
            except: pass
            try: requests.get(f"https://api.telegram.org/bot{TOKEN}/close", timeout=5)
            except: pass
            time.sleep(3)
        elif "ReadTimeout" in type(e).__name__: time.sleep(1)
        elif "ConnectionError" in type(e).__name__: time.sleep(3)
        else: time.sleep(2)
    try: os.waitpid(-1, os.WNOHANG)
    except ChildProcessError: pass

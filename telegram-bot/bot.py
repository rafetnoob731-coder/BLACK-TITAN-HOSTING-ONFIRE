"""
███████╗██╗  ██╗██╗   ██╗    ██╗  ██╗ ██████╗ ███████╗████████╗██╗███╗   ██╗ ██████╗
██╔════╝██║  ██║██║   ██║    ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝
█████╗  ███████║██║   ██║    ███████║██║   ██║███████╗   ██║   ██║██╔██╗ ██║██║  ███╗
██╔══╝  ██╔══██║██║   ██║    ██╔══██║██║   ██║╚════██║   ██║   ██║██║╚██╗██║██║   ██║
██║     ██║  ██║╚██████╔╝    ██║  ██║╚██████╔╝███████║   ██║   ██║██║ ╚████║╚██████╔╝
╚═╝     ╚═╝  ╚═╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝

𝐄𝐗𝐔 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐁𝐎𝐓 𝐕𝟑.𝟏
𝐀𝐔𝐓𝐎-𝐑𝐄𝐂𝐎𝐕𝐄𝐑𝐘 & 𝐓𝐈𝐄𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓
𝐂𝐑𝐄𝐃𝐈𝐓𝐒: 𝐄𝐗𝐔 𝐂𝐎𝐃𝐄𝐑 | 𝐕𝐈𝐏 𝐃𝐀𝐑𝐊 𝐆𝐎𝐃 | 𝐁𝐋𝐀𝐂𝐊 𝐓𝐈𝐓𝐀𝐍
𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘: 𝐎𝐏𝐄𝐍𝐂𝐎𝐃𝐄 𝐀𝐈
"""

import subprocess, sys, os, hashlib, json, sqlite3, shutil, tempfile, zipfile, re, atexit, threading, random, time, signal, base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from collections import defaultdict, deque
from functools import wraps

_pip_base = [sys.executable, "-m", "pip", "install", "--quiet"]
try: subprocess.run([sys.executable, "-m", "pip", "install", "--dry-run", "setuptools"], capture_output=True)
except: _pip_base.append("--break-system-packages")

_MOD_MAP = {"PIL": "Pillow", "telebot": "pyTelegramBotAPI", "flask": "Flask", "dotenv": "python-dotenv"}
for mod in ["telebot", "psutil", "requests", "flask", "qrcode", "PIL", "cryptography"]:
    try: __import__(mod)
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

TOKEN = os.environ.get("BOT_TOKEN", "8456808453:AAFjORqN7K9g2uXMAkx-e5FJCwFJa5YFtDY")
OWNER_ID = int(os.environ.get("OWNER_ID", "8469461108"))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8469461108"))
ADMIN_IDS = {OWNER_ID, ADMIN_ID}
BOT_USERNAME = os.environ.get("BOT_USERNAME", "@EXUCODER")
UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/exucoder1")
UPDATE_GROUP = os.environ.get("UPDATE_GROUP", "https://t.me/exulive")
SUPPORT_LINK = os.environ.get("SUPPORT_LINK", "https://t.me/exucoder1")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'exu_uploads')
EXU_DATA_DIR = os.path.join(BASE_DIR, 'exu_data')
DATABASE_PATH = os.path.join(EXU_DATA_DIR, 'exu_bot.db')
RUNNING_SCRIPTS_DB = os.path.join(EXU_DATA_DIR, 'running_scripts.json')
LOGS_DIR = os.path.join(EXU_DATA_DIR, 'logs')
BACKUP_DIR = os.path.join(EXU_DATA_DIR, 'backups')

for dir_path in [UPLOAD_BOTS_DIR, EXU_DATA_DIR, LOGS_DIR, BACKUP_DIR]:
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
        m = {'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
             'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
             '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'}
        return ''.join(m.get(c, c) for c in text)

F = FontStyler()
B = FontStyler.bold

ANIM_UPLOAD = ["📤 [▒▒▒▒▒▒▒▒▒▒] 0%","📤 [█▒▒▒▒▒▒▒▒▒] 10%","📤 [██▒▒▒▒▒▒▒▒] 20%","📤 [███▒▒▒▒▒▒▒] 30%","📤 [████▒▒▒▒▒▒] 40%","📤 [█████▒▒▒▒▒] 50%","📤 [██████▒▒▒▒] 60%","📤 [███████▒▒▒] 70%","📤 [████████▒▒] 80%","📤 [█████████▒] 90%","✅ [██████████] 100%"]
ANIM_DEPLOY = ["🚀 [░░░░░░░░░░]","🚀 [▓░░░░░░░░░]","🚀 [▓▓░░░░░░░░]","🚀 [▓▓▓░░░░░░░]","🚀 [▓▓▓▓░░░░░░]","🚀 [▓▓▓▓▓░░░░░]","🚀 [▓▓▓▓▓▓░░░░]","🚀 [▓▓▓▓▓▓▓░░░]","🚀 [▓▓▓▓▓▓▓▓░░]","🚀 [▓▓▓▓▓▓▓▓▓░]","✅ [▓▓▓▓▓▓▓▓▓▓]"]
ANIM_EXEC = ["⚡ Initializing...","⚡ Executing...","⚡ Running...","✅ Done!"]
ANIM_RECV = ["🔄","🔃","🔄","🔃"]

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
        c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, tier TEXT DEFAULT 'free', joined_at TIMESTAMP, last_active TIMESTAMP, total_uploads INTEGER DEFAULT 0, total_bot_runs INTEGER DEFAULT 0, total_storage_used INTEGER DEFAULT 0, referral_code TEXT UNIQUE, referred_by INTEGER, is_banned BOOLEAN DEFAULT 0, credits INTEGER DEFAULT 0, notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (user_id INTEGER PRIMARY KEY, tier TEXT, expires_at TIMESTAMP, payment_method TEXT, transaction_id TEXT, amount REAL, activated_by INTEGER, activated_at TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, filename TEXT, file_type TEXT, file_size INTEGER, file_path TEXT, uploaded_at TIMESTAMP, last_started TIMESTAMP, is_running BOOLEAN DEFAULT 0, pid INTEGER, UNIQUE(user_id, filename))''')
        c.execute('''CREATE TABLE IF NOT EXISTS referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, referred_id INTEGER UNIQUE, referred_at TIMESTAMP, status TEXT DEFAULT 'completed')''')
        c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, details TEXT, timestamp TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, created_by INTEGER, created_at TIMESTAMP, sent_to_all BOOLEAN DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS shop_items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price_credits INTEGER, item_type TEXT, duration_days INTEGER, created_at TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_inventory (user_id INTEGER, item_id INTEGER, purchased_at TIMESTAMP, expires_at TIMESTAMP, active BOOLEAN DEFAULT 1)''')
        c.execute("INSERT OR IGNORE INTO settings VALUES (?,?,?)", ('bot_locked', 'false', datetime.now().isoformat()))
        c.execute("INSERT OR IGNORE INTO settings VALUES (?,?,?)", ('maintenance_mode', 'false', datetime.now().isoformat()))
        c.execute("INSERT OR IGNORE INTO settings VALUES (?,?,?)", ('daily_credits', '5', datetime.now().isoformat()))
        conn.commit(); conn.close()
    def execute(self, q, p=()):
        conn = self._get_connection(); c = conn.cursor(); c.execute(q, p); conn.commit(); conn.close(); return c
    def fetch_one(self, q, p=()):
        conn = self._get_connection(); conn.row_factory = sqlite3.Row; c = conn.cursor(); c.execute(q, p); r = c.fetchone(); conn.close(); return dict(r) if r else None
    def fetch_all(self, q, p=()):
        conn = self._get_connection(); conn.row_factory = sqlite3.Row; c = conn.cursor(); c.execute(q, p); r = c.fetchall(); conn.close(); return [dict(x) for x in r]

db = DatabaseManager(DATABASE_PATH)

class ReferralManager:
    @staticmethod
    def generate_code(uid):
        return hashlib.md5(f"{uid}{time.time()}".encode()).hexdigest()[:8].upper()
    @staticmethod
    def stats(uid):
        t = db.fetch_one("SELECT COUNT(*) as c FROM referrals WHERE referrer_id=? AND status='completed'", (uid,))
        p = db.fetch_one("SELECT COUNT(*) as c FROM referrals WHERE referrer_id=? AND status='pending'", (uid,))
        return {'total': t['c'] if t else 0, 'pending': p['c'] if p else 0, 'completed': t['c'] if t else 0}
    @staticmethod
    def add(ref, rid):
        if ref == rid: return False
        if db.fetch_one("SELECT id FROM referrals WHERE referred_id=?", (rid,)): return False
        db.execute("INSERT INTO referrals(referrer_id,referred_id,referred_at,status) VALUES(?,?,?,?)", (ref, rid, datetime.now().isoformat(), 'completed'))
        db.execute("UPDATE users SET referral_code=? WHERE user_id=?", (ReferralManager.generate_code(rid), rid))
        # Give credits to referrer
        db.execute("UPDATE users SET credits=COALESCE(credits,0)+10 WHERE user_id=?", (ref,))
        return True
    @staticmethod
    def leaderboard(limit=10):
        return db.fetch_all("SELECT u.user_id, u.username, COUNT(r.id) as referral_count FROM users u LEFT JOIN referrals r ON u.user_id=r.referrer_id AND r.status='completed' GROUP BY u.user_id ORDER BY referral_count DESC LIMIT ?", (limit,))

class CreditShop:
    @staticmethod
    def get_balance(uid):
        u = db.fetch_one("SELECT credits FROM users WHERE user_id=?", (uid,))
        return u['credits'] if u else 0
    @staticmethod
    def add_credits(uid, amount):
        db.execute("UPDATE users SET credits=COALESCE(credits,0)+? WHERE user_id=?", (amount, uid))
    @staticmethod
    def spend(uid, amount):
        bal = CreditShop.get_balance(uid)
        if bal < amount: return False
        db.execute("UPDATE users SET credits=COALESCE(credits,0)-? WHERE user_id=?", (amount, uid))
        return True
    @staticmethod
    def claim_daily(uid):
        today = datetime.now().strftime("%Y-%m-%d")
        claimed = db.fetch_one("SELECT value FROM settings WHERE key=?", (f"daily_{uid}",))
        if claimed and claimed['value'] == today: return False
        db.execute("INSERT OR REPLACE INTO settings(key,value,updated_at) VALUES(?,?,?)", (f"daily_{uid}", today, datetime.now().isoformat()))
        amount = int(db.fetch_one("SELECT value FROM settings WHERE key='daily_credits'")['value'])
        CreditShop.add_credits(uid, amount)
        return amount
    @staticmethod
    def get_items():
        return db.fetch_all("SELECT * FROM shop_items ORDER BY price_credits ASC")
    @staticmethod
    def buy_item(uid, item_id):
        item = db.fetch_one("SELECT * FROM shop_items WHERE id=?", (item_id,))
        if not item: return False, "Item not found"
        if CreditShop.get_balance(uid) < item['price_credits']: return False, "Insufficient credits"
        CreditShop.spend(uid, item['price_credits'])
        expires = (datetime.now() + timedelta(days=item['duration_days'])).isoformat() if item['duration_days'] else None
        db.execute("INSERT INTO user_inventory(user_id,item_id,purchased_at,expires_at) VALUES(?,?,?,?)", (uid, item_id, datetime.now().isoformat(), expires))
        if item['item_type'] == 'premium':
            db.execute("INSERT OR REPLACE INTO subscriptions(user_id,tier,expires_at,activated_at) VALUES(?,?,?,?)", (uid, 'premium', expires, datetime.now().isoformat()))
        return True, f"Purchased {item['name']}!"

bot_scripts: Dict[str, Dict] = {}
active_users: set = set()
user_files: Dict[int, List[Tuple[str, str]]] = {}
bot_locked = False
user_projects: Dict[int, str] = {}

TIER_SYSTEM = {
    "free": {"name": "FREE", "upload_limit": 3, "max_file_size": 50 * 1024 * 1024, "icon": "🎫", "color": "#2ecc71", "auto_restart": False, "referral_needed": 3, "concurrent_bots": 1},
    "premium": {"name": "PREMIUM", "upload_limit": 15, "max_file_size": 200 * 1024 * 1024, "icon": "⭐", "color": "#f39c12", "auto_restart": True, "referral_needed": 0, "concurrent_bots": 5},
    "pro": {"name": "PRO", "upload_limit": 50, "max_file_size": 500 * 1024 * 1024, "icon": "💎", "color": "#9b59b6", "auto_restart": True, "referral_needed": 0, "concurrent_bots": 15},
    "ultimate": {"name": "ULTIMATE", "upload_limit": 150, "max_file_size": 1024 * 1024 * 1024, "icon": "👑", "color": "#e74c3c", "auto_restart": True, "referral_needed": 0, "concurrent_bots": 50},
    "owner": {"name": "OWNER", "upload_limit": 10**9, "max_file_size": 10**12, "icon": "🔥", "color": "#8b00ff", "auto_restart": True, "referral_needed": 0, "concurrent_bots": 10**9},
}

def get_user_tier(uid):
    if uid == OWNER_ID: return "owner"
    if uid in ADMIN_IDS: return "owner"
    u = db.fetch_one("SELECT tier FROM users WHERE user_id=?", (uid,))
    if not u: return "free"
    sub = db.fetch_one("SELECT tier,expires_at FROM subscriptions WHERE user_id=? AND expires_at>?", (uid, datetime.now().isoformat()))
    if sub:
        try: return sub['tier']
        except: pass
    try: return u['tier']
    except: return "free"

def get_tier_benefits(uid):
    return TIER_SYSTEM.get(get_user_tier(uid), TIER_SYSTEM["free"])

def get_or_create_user(uid, uname=None, fn=None, ln=None):
    u = db.fetch_one("SELECT * FROM users WHERE user_id=?", (uid,))
    if not u:
        rc = ReferralManager.generate_code(uid)
        db.execute("INSERT INTO users(user_id,username,first_name,last_name,tier,joined_at,last_active,referral_code) VALUES(?,?,?,?,?,?,?,?)", (uid, uname, fn, ln, 'free', datetime.now().isoformat(), datetime.now().isoformat(), rc))
        u = db.fetch_one("SELECT * FROM users WHERE user_id=?", (uid,))
    else:
        db.execute("UPDATE users SET last_active=?,username=COALESCE(?,username),first_name=COALESCE(?,first_name) WHERE user_id=?", (datetime.now().isoformat(), uname, fn, uid))
    return dict(u) if u else {}

def get_user_files(uid):
    return db.fetch_all("SELECT * FROM files WHERE user_id=? ORDER BY uploaded_at DESC", (uid,))

def get_file_count(uid):
    r = db.fetch_one("SELECT COUNT(*) as c FROM files WHERE user_id=?", (uid,)); return r['c'] if r else 0

def can_upload(uid, size):
    tb = get_tier_benefits(uid); c = get_file_count(uid)
    if c >= tb['upload_limit']: return False, f"File limit ({c}/{tb['upload_limit']})"
    if size > tb['max_file_size']: return False, f"File too large ({size/1024/1024:.1f}MB / {tb['max_file_size']/1024/1024:.0f}MB)"
    return True, "OK"

def add_file(uid, fn, ft, size, path):
    try:
        db.execute("INSERT OR REPLACE INTO files(user_id,filename,file_type,file_size,file_path,uploaded_at) VALUES(?,?,?,?,?,?)", (uid, fn, ft, size, path, datetime.now().isoformat()))
        db.execute("UPDATE users SET total_uploads=total_uploads+1,total_storage_used=total_storage_used+? WHERE user_id=?", (size, uid))
        return True
    except: return False

def delete_file(uid, fn):
    fi = db.fetch_one("SELECT file_path,file_size FROM files WHERE user_id=? AND filename=?", (uid, fn))
    if not fi: return False
    kill_script(uid, fn)
    try:
        if os.path.exists(fi['file_path']): os.remove(fi['file_path'])
        lp = os.path.join(os.path.dirname(fi['file_path']), f"{os.path.splitext(fn)[0]}.log")
        if os.path.exists(lp): os.remove(lp)
    except: pass
    db.execute("DELETE FROM files WHERE user_id=? AND filename=?", (uid, fn))
    db.execute("UPDATE users SET total_storage_used=total_storage_used-? WHERE user_id=?", (fi['file_size'], uid))
    return True

def is_running(uid, fn):
    k = f"{uid}_{fn}"
    if k not in bot_scripts: return False
    try: return psutil.Process(bot_scripts[k]['process'].pid).is_running()
    except: return False

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

def kill_script(uid, fn):
    k = f"{uid}_{fn}"
    if k in bot_scripts: kill_proc(bot_scripts[k]); del bot_scripts[k]

def start_script(uid, fn, path, tp, msg):
    k = f"{uid}_{fn}"
    if k in bot_scripts:
        if is_running(uid, fn):
            if msg: bot.reply_to(msg, B("⚠️ Already running."))
            return
        del bot_scripts[k]
    folder = os.path.dirname(path)
    lf = open(os.path.join(folder, f"{os.path.splitext(fn)[0]}.log"), "w", encoding="utf-8", errors="ignore")
    sinfo = None
    if os.name == "nt":
        sinfo = subprocess.STARTUPINFO(); sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow = subprocess.SW_HIDE
    cmd = [sys.executable, path] if tp == "py" else ["node", path]
    proc = subprocess.Popen(cmd, cwd=folder, stdout=lf, stderr=lf, stdin=subprocess.PIPE, startupinfo=sinfo)
    bot_scripts[k] = {"process": proc, "lf": lf, "fn": fn, "uid": uid, "st": datetime.now(), "tp": tp, "sk": k}
    db.execute("UPDATE files SET is_running=1,pid=?,last_started=? WHERE user_id=? AND filename=?", (proc.pid, datetime.now().isoformat(), uid, fn))
    if msg: bot.send_message(msg.chat.id, B(f"✅ `{fn}` started! PID: {proc.pid}"))

MODS = {"telebot": "pyTelegramBotAPI", "psutil": "psutil", "requests": "requests", "flask": "Flask", "qrcode": "qrcode", "PIL": "Pillow", "cryptography": "cryptography", "aiogram": "aiogram", "aiogram.contrib": "aiogram"}

def _pip_install(*args):
    return subprocess.run(_pip_base + list(args), capture_output=True, text=True)

def install_mod(name, msg):
    root = name.split(".")[0]; pkg = MODS.get(root.lower(), root)
    try:
        bot.reply_to(msg, B(f"🐍 Installing `{root}`..."))
        env_override = {**os.environ, "AIOHTTP_NO_EXTENSIONS": "1"} if root == "aiogram" else None
        r = subprocess.run(_pip_base + [pkg], capture_output=True, text=True, env=env_override)
        if r.returncode == 0:
            bot.reply_to(msg, B(f"✅ `{pkg}` installed.")); return True
        else:
            err = r.stderr[:200] if r.stderr else r.stdout[:200]
            if "aiogram" in name.lower() and ("aiohttp" in err or "build" in err):
                bot.reply_to(msg, B("❌ Python 3.14 broke aiohttp C extensions. Try manual: `AIOHTTP_NO_EXTENSIONS=1 pip3 install --break-system-packages aiogram`"))
            else:
                bot.reply_to(msg, B(f"❌ Failed `{pkg}`.\n{err}"))
            return False
    except Exception as e:
        bot.reply_to(msg, B(f"❌ {e}")); return False

def animate(msg, frames):
    m = bot.reply_to(msg, frames[0])
    for f in frames:
        try: bot.edit_message_text(f, msg.chat.id, m.message_id); time.sleep(0.3)
        except: pass
    return m

DBL = threading.Lock()

class RecoveryManager:
    def __init__(self, db):
        self.db = db; self._recover()

    def _recover(self):
        for f in self.db.fetch_all("SELECT * FROM files WHERE is_running=1"):
            uid, fn, path = f['user_id'], f['filename'], f['file_path']
            if os.path.exists(path):
                k = f"{uid}_{fn}"; folder = os.path.dirname(path)
                lf = open(os.path.join(folder, f"{os.path.splitext(fn)[0]}.log"), "a", encoding="utf-8", errors="ignore")
                sinfo = None
                if os.name == "nt":
                    sinfo = subprocess.STARTUPINFO(); sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW; sinfo.wShowWindow = subprocess.SW_HIDE
                tp = 'py' if path.endswith('.py') else 'js'
                cmd = [sys.executable, path] if tp == 'py' else ["node", path]
                try:
                    proc = subprocess.Popen(cmd, cwd=folder, stdout=lf, stderr=lf, stdin=subprocess.PIPE, startupinfo=sinfo)
                    bot_scripts[k] = {"process": proc, "lf": lf, "fn": fn, "uid": uid, "st": datetime.now(), "tp": tp, "sk": k}
                except: pass

    def save(self):
        try:
            with open(RUNNING_SCRIPTS_DB, 'w') as f:
                json.dump({k: {'uid': v['uid'], 'fn': v['fn'], 'tp': v['tp'], 'st': v['st'].isoformat() if isinstance(v['st'], datetime) else v['st']} for k, v in bot_scripts.items()}, f)
        except: pass

    def recover_all(self):
        restored = []
        for k, v in list(bot_scripts.items()):
            if not is_running(v['uid'], v['fn']): continue
            kill_proc(v)
            uid, fn, path = v['uid'], v['fn'], None
            f = db.fetch_one("SELECT file_path FROM files WHERE user_id=? AND filename=?", (uid, fn))
            if f: path = f['file_path']
            if path and os.path.exists(path):
                start_script(uid, fn, path, v['tp'], None); restored.append(k)
        return restored

rec = RecoveryManager(db)

atexit.register(lambda: (logger.info("Shutdown..."), [kill_proc(v) for k, v in list(bot_scripts.items())], rec.save()))

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><title>EXU HOSTING</title>
    <style>
    body{background:linear-gradient(135deg,#0a0a0a 0%,#1a1a2e 100%);color:#fff;font-family:'Courier New',monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
    .container{text-align:center;padding:2rem;border:2px solid #00ccff;border-radius:20px;background:rgba(0,0,0,0.7);box-shadow:0 0 50px rgba(0,204,255,0.3)}
    h1{font-size:3rem;margin:0;background:linear-gradient(45deg,#00ccff,#ff00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .status{color:#00ff88;margin-top:20px}
    .glow{animation:glow 2s ease-in-out infinite alternate}
    @keyframes glow{from{text-shadow:0 0 5px #00ccff}to{text-shadow:0 0 20px #00ccff}}
    </style></head><body>
    <div class="container">
    <h1>⚡ EXU HOSTING ⚡</h1>
    <p class="glow">Advanced Bot Hosting Platform</p>
    <p class="status">🟢 SYSTEM ONLINE 🟢</p>
    <p>Version 3.1 | Credits: EXU CODER</p>
    </div></body></html>""")

@flask_app.route('/health')
def health():
    return {"status": "running", "users": db.fetch_one("SELECT COUNT(*) as c FROM users")['c'], "scripts": len(bot_scripts), "uptime": str(datetime.now() - startup_time)}

@flask_app.route('/stats')
def web_stats():
    tu = db.fetch_one("SELECT COUNT(*) as c FROM users")['c']
    rs = sum(1 for k, v in bot_scripts.items() if is_running(v['uid'], v['fn']))
    return f"EXU HOSTING - Users: {tu} | Running: {rs} | Uptime: {datetime.now() - startup_time}"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

Thread(target=run_flask, daemon=True).start()
print("✅ Management Dashboard started.")

def reply_kb(uid):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = ["📤 Upload", "📂 My Files", "📊 Stats", "👤 Profile", "🤝 Refer", "🏆 Leadrboard", "🛒 Shop", "🎁 Daily", "📢 Updates", "📞 Contact"]
    if uid in ADMIN_IDS or uid == OWNER_ID:
        btns += ["👑 Admin", "📢 Broadcast"]
    for i in range(0, len(btns), 2):
        mk.add(*[types.KeyboardButton(t) for t in btns[i:i + 2]])
    return mk

def main_markup(uid):
    mk = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("📤 Upload", callback_data="upload"),
        types.InlineKeyboardButton("📂 My Files", callback_data="my_bots"),
        types.InlineKeyboardButton("📊 Dashboard", callback_data="dashboard"),
        types.InlineKeyboardButton("👤 Profile", callback_data="profile"),
        types.InlineKeyboardButton("🤝 Refer", callback_data="referral"),
        types.InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
        types.InlineKeyboardButton("🛒 Shop", callback_data="shop"),
        types.InlineKeyboardButton("🎁 Daily", callback_data="daily"),
        types.InlineKeyboardButton("⚡ Speed", callback_data="speed"),
        types.InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL),
        types.InlineKeyboardButton("💬 Support", url=SUPPORT_LINK),
        types.InlineKeyboardButton("📞 Contact", url=f"https://t.me/{BOT_USERNAME.replace('@', '')}")
    ]
    if uid in ADMIN_IDS or uid == OWNER_ID:
        mk.add(btns[0], btns[1]); mk.add(btns[2], btns[3]); mk.add(btns[4], btns[5])
        mk.add(btns[6], btns[7]); mk.add(btns[8])
        mk.add(types.InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel"))
        mk.add(types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"))
        mk.add(btns[9], btns[10]); mk.add(btns[11])
    else:
        for i in range(0, len(btns), 2):
            mk.add(*btns[i:i + 2])
    return mk

def ctrl_btns(uid, fn, running=True):
    mk = types.InlineKeyboardMarkup(row_width=2)
    if running:
        mk.row(types.InlineKeyboardButton("🔴 Stop", callback_data=f"stp_{uid}_{fn}"), types.InlineKeyboardButton("🔄 Restart", callback_data=f"rst_{uid}_{fn}"))
        mk.row(types.InlineKeyboardButton("🗑️ Delete", callback_data=f"del_{uid}_{fn}"), types.InlineKeyboardButton("📜 Logs", callback_data=f"log_{uid}_{fn}"))
    else:
        mk.row(types.InlineKeyboardButton("🟢 Start", callback_data=f"sta_{uid}_{fn}"), types.InlineKeyboardButton("🗑️ Delete", callback_data=f"del_{uid}_{fn}"))
        mk.row(types.InlineKeyboardButton("📜 Logs", callback_data=f"log_{uid}_{fn}"))
    mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="check_files"))
    return mk

def admin_mk():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.row(types.InlineKeyboardButton("➕ Add Admin", callback_data="add_adm"), types.InlineKeyboardButton("➖ Remove Admin", callback_data="rm_adm"))
    mk.row(types.InlineKeyboardButton("📋 List Admins", callback_data="list_adm"), types.InlineKeyboardButton("📊 System Stats", callback_data="sys_stats"))
    mk.row(types.InlineKeyboardButton("🔒 Lock Bot", callback_data="lock_bot"), types.InlineKeyboardButton("🔄 Recover", callback_data="recover_all"))
    mk.row(types.InlineKeyboardButton("💳 Subs", callback_data="subscription"), types.InlineKeyboardButton("📈 Analytics", callback_data="analytics"))
    mk.row(types.InlineKeyboardButton("🛒 Shop Mgmt", callback_data="shop_mgmt"), types.InlineKeyboardButton("🚀 Restart Bot", callback_data="restart_bot"))
    mk.row(types.InlineKeyboardButton("🔙 Back", callback_data="back"))
    return mk

CREDIT_ITEMS = """
📦 𝐂𝐑𝐄𝐃𝐈𝐓 𝐒𝐇𝐎𝐏

🪙 𝐖𝐡𝐚𝐭 𝐚𝐫𝐞 𝐂𝐫𝐞𝐝𝐢𝐭𝐬?
Credits are the premium currency of EXU HOSTING.
Earn them by referring friends or claiming daily rewards.

📊 𝐇𝐨𝐰 𝐭𝐨 𝐄𝐚𝐫𝐧:
• 🎁 /daily - Claim 5 credits every day
• 🤝 /refer - Earn 10 credits per referral
• 🏆 Leaderboard bonuses for top referrers

🛒 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐈𝐭𝐞𝐦𝐬:
• Premium (30d) - 100 credits
• Extra Upload Slot - 50 credits
• Priority Support - 30 credits
• Custom Domain - 200 credits

💎 𝐔𝐬𝐞 /shop to browse and buy!
"""

SHOP_ITEMS = [
    {"name": "⭐ Premium (7d)", "desc": "7 days premium access", "price": 50, "type": "premium", "days": 7},
    {"name": "👑 Premium (30d)", "desc": "30 days premium access", "price": 150, "type": "premium", "days": 30},
    {"name": "💎 Premium (90d)", "desc": "90 days premium access", "price": 400, "type": "premium", "days": 90},
    {"name": "📁 Extra Slot", "desc": "+5 file upload slots", "price": 100, "type": "slot", "days": 0},
    {"name": "🚀 Priority Support", "desc": "Priority support for 30d", "price": 75, "type": "support", "days": 30},
]

@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid = message.from_user.id; uname = message.from_user.username; fn = message.from_user.first_name; ln = message.from_user.last_name
    user = get_or_create_user(uid, uname, fn, ln)
    if len(message.text.split()) > 1:
        rc = message.text.split()[1]
        ref = db.fetch_one("SELECT user_id FROM users WHERE referral_code=?", (rc,))
        if ref and ref['user_id'] != uid: ReferralManager.add(ref['user_id'], uid)
    tb = get_tier_benefits(uid); fc = get_file_count(uid)
    credits = CreditShop.get_balance(uid)
    active_users.add(uid)
    txt = f"""
{F.math_bold('⚡ EXU HOSTING v3.1 ⚡')}
{F.math_bold('═══════════════════════════')}

{B('Welcome, ' + fn + '!')}

📊 {B('Your Status')}
└ 🆔 ID: <code>{uid}</code>
└ 🎫 Tier: {tb['icon']} {tb['name']}
└ 📁 Files: {fc}/{tb['upload_limit']}
└ 🪙 Credits: {credits}
└ 🔄 Auto-Restart: {'✅' if tb['auto_restart'] else '❌'}

📈 {B('System Stats')}
└ 👥 Users: {db.fetch_one('SELECT COUNT(*) as c FROM users')['c']}
└ 🤖 Online: {len(bot_scripts)}

{B('📢 Updates:')} {UPDATE_CHANNEL}
{B('💬 Support:')} {SUPPORT_LINK}
"""
    bot.send_message(message.chat.id, txt, reply_markup=main_markup(uid))
    bot.send_message(message.chat.id, B("📌 Use buttons below:"), reply_markup=reply_kb(uid))

@bot.message_handler(commands=['help'])
def cmd_help(message):
    txt = f"""
{F.math_bold('📚 EXU HOSTING - HELP')}
{F.math_bold('═══════════════════════════')}

{B('📤 Uploading Bots')}
• Send .py, .js, or .zip file
• Dependencies auto-installed
• Use /setproject name first

{B('🎟️ Tier System')}
• FREE: 3 bots, 50MB max
• PREMIUM: 15 bots, 200MB max
• PRO: 50 bots, 500MB max
• ULTIMATE: 150 bots, 1GB max

{B('🪙 Credits')}
• /daily - Claim 5 credits
• /refer - Earn 10 per referral
• /shop - Browse items

{B('🤝 Referral Program')}
• Invite friends using your link
• Earn credits + auto-restart
• /refer to see your link

{B('📞 Contact')}
• Channel: {UPDATE_CHANNEL}
• Group: {UPDATE_GROUP}
• Owner: {BOT_USERNAME}
"""
    bot.reply_to(message, txt)

@bot.message_handler(commands=['shop'])
def cmd_shop(message):
    uid = message.from_user.id
    bal = CreditShop.get_balance(uid)
    mk = types.InlineKeyboardMarkup(row_width=1)
    for i, item in enumerate(SHOP_ITEMS):
        mk.add(types.InlineKeyboardButton(f"{item['name']} - {item['price']}🪙", callback_data=f"buy_{i}"))
    mk.add(types.InlineKeyboardButton("🔙 Back", callback_data="back"))
    bot.reply_to(message, B(f"🛒 {B('EXU SHOP')}\n\n{B('Your Balance:')} {bal}🪙\n\nChoose an item:"), reply_markup=mk)

@bot.message_handler(commands=['daily'])
def cmd_daily(message):
    uid = message.from_user.id
    result = CreditShop.claim_daily(uid)
    if result:
        bot.reply_to(message, B(f"🎁 You claimed {result} credits! Balance: {CreditShop.get_balance(uid)}🪙"))
    else:
        bot.reply_to(message, B("⏳ Already claimed today. Come back tomorrow!"))

@bot.message_handler(commands=['credits'])
def cmd_credits(message):
    uid = message.from_user.id
    bal = CreditShop.get_balance(uid)
    bot.reply_to(message, B(f"🪙 Your balance: {bal} credits\n\nEarn more:\n• /daily - 5 credits/day\n• /refer - 10 credits/referral"))

@bot.message_handler(commands=['refer'])
def cmd_refer(message):
    uid = message.from_user.id
    u = db.fetch_one("SELECT referral_code FROM users WHERE user_id=?", (uid,))
    rc = u['referral_code'] if u else ""
    refs = ReferralManager.stats(uid)
    bal = CreditShop.get_balance(uid)
    link = f"https://t.me/{BOT_USERNAME.replace('@', '')}?start={rc}"
    txt = f"""
🤝 {B('Referral Program')}
🔗 Your Link: <code>{link}</code>
📊 Referrals: {refs['total']}
🪙 Credits Earned: {refs['total'] * 10}
🏆 Rank: #{ReferralManager.stats(uid)['total']}

Invite friends and earn 10🪙 each!
    """
    bot.reply_to(message, txt)

@bot.message_handler(commands=['leaderboard'])
def cmd_leaderboard(message):
    lb = ReferralManager.leaderboard()
    txt = f"🏆 {B('Referral Leaderboard')}\n"
    for i, u in enumerate(lb[:10], 1):
        txt += f"{i}. {u.get('username', 'Unknown')} - {u['referral_count']} referrals\n"
    bot.reply_to(message, txt)

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, B("❌ Admin only.")); return
    msg = message.text.replace('/broadcast', '', 1).strip()
    if not msg: bot.reply_to(message, B("Usage: /broadcast <message>")); return
    users = db.fetch_all("SELECT user_id FROM users")
    sent = 0
    for u in users:
        try: bot.send_message(u['user_id'], B(f"📢 Broadcast\n\n{msg}")); sent += 1; time.sleep(0.05)
        except: pass
    bot.reply_to(message, B(f"✅ Sent to {sent} users."))

@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    if message.from_user.id not in ADMIN_IDS: return
    bot.send_message(message.chat.id, B("👑 Admin Panel"), reply_markup=admin_mk())

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    tu = len(active_users); tf = sum(len(f) for f in user_files.values())
    rs = sum(1 for k, v in bot_scripts.items() if is_running(v['uid'], v['fn']))
    mem = psutil.virtual_memory(); cpu = psutil.cpu_percent()
    txt = f"""
📊 {B('System Stats')}
👥 Active Users: {tu}
📁 Total Files: {tf}
🤖 Running Scripts: {rs}
💾 RAM: {mem.percent}%
⚡ CPU: {cpu}%
🪙 Total Credits: {sum(CreditShop.get_balance(u) for u in active_users)}
📅 Uptime: {datetime.now() - startup_time}
    """
    bot.reply_to(message, txt)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    uid = message.from_user.id
    tb = get_tier_benefits(uid)
    fc = get_file_count(uid)
    if bot_locked and uid not in ADMIN_IDS:
        bot.reply_to(message, B("🔒 Bot locked for maintenance.")); return
    doc = message.document; fn = doc.file_name; fs = doc.file_size
    ok, err = can_upload(uid, fs)
    if not ok: bot.reply_to(message, B(f"❌ {err}")); return
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, B("❌ Only .py, .js, .zip files allowed.")); return
    proj = user_projects.get(uid)
    if not proj:
        bot.reply_to(message, B("📁 Send a project name first, or use /setproject <name>"))
        return
    folder = os.path.join(UPLOAD_BOTS_DIR, str(uid), proj); os.makedirs(folder, exist_ok=True)
    fi = os.path.join(folder, fn)
    animate(message, ANIM_UPLOAD)
    try:
        file_info = bot.get_file(doc.file_id); downloaded = bot.download_file(file_info.file_path)
        with open(fi, 'wb') as f: f.write(downloaded)
    except:
        bot.reply_to(message, B(f"❌ Download failed.")); return
    if ext == '.zip':
        try:
            with zipfile.ZipFile(fi, 'r') as zf: zf.extractall(folder)
            os.remove(fi)
            pyfiles = [f for f in os.listdir(folder) if f.endswith('.py')]
            if pyfiles: fn = pyfiles[0]; fi = os.path.join(folder, fn)
            else: bot.reply_to(message, B("❌ No .py found in zip.")); return
            req_path = os.path.join(folder, 'requirements.txt')
            if os.path.exists(req_path):
                with open(req_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            _pip_install(line.split('>=')[0].split('==')[0].strip())
        except Exception as e:
            bot.reply_to(message, B(f"❌ Zip error: {e}")); return
    add_file(uid, fn, ext, fs, fi)
    bot.send_message(message.chat.id, B(f"✅ `{fn}` uploaded!"), reply_markup=ctrl_btns(uid, fn, False))

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/setproject'))
def set_project(message):
    uid = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: bot.reply_to(message, B("Usage: /setproject <name>")); return
    user_projects[uid] = parts[1].strip()
    bot.reply_to(message, B(f"📁 Project set: `{parts[1]}`"))

@bot.message_handler(func=lambda m: m.text in ["📤 Upload", "📂 My Files", "📊 Stats", "👤 Profile", "🤝 Refer", "🏆 Leadrboard", "🛒 Shop", "🎁 Daily", "📢 Updates", "📞 Contact", "👑 Admin", "📢 Broadcast"])
def handle_kb_btn(message):
    uid = message.from_user.id; txt = message.text
    if txt == "📂 My Files":
        files = get_user_files(uid)
        if not files: bot.reply_to(message, B("📭 No files."), reply_markup=reply_kb(uid)); return
        msg = B("📂 Your Files\n")
        for f in files:
            ru = is_running(uid, f['filename'])
            msg += f"{'🟢' if ru else '🔴'} `{f['filename']}`\n"
        bot.reply_to(message, msg)
    elif txt == "📊 Stats":
        bot.reply_to(message, f"👥 Users: {db.fetch_one('SELECT COUNT(*) as c FROM users')['c']}\n🤖 Running: {sum(1 for k,v in bot_scripts.items() if is_running(v['uid'],v['fn']))}")
    elif txt == "👤 Profile":
        tb = get_tier_benefits(uid); fc = get_file_count(uid); bal = CreditShop.get_balance(uid)
        bot.reply_to(message, B(f"🎫 {tb['icon']} {tb['name']}\n📁 Files: {fc}/{tb['upload_limit']}\n🪙 Credits: {bal}\n🔄 Auto-Restart: {'✅' if tb['auto_restart'] else '❌'}"))
    elif txt == "🤝 Refer":
        u = db.fetch_one("SELECT referral_code FROM users WHERE user_id=?", (uid,))
        rc = u['referral_code'] if u else ""
        bot.reply_to(message, B(f"🔗 https://t.me/{BOT_USERNAME.replace('@','')}?start={rc}"))
    elif txt == "🏆 Leadrboard":
        cmd_leaderboard(message)
    elif txt == "🛒 Shop":
        cmd_shop(message)
    elif txt == "🎁 Daily":
        cmd_daily(message)
    elif txt == "📢 Updates":
        bot.reply_to(message, B(f"📢 {UPDATE_CHANNEL}"))
    elif txt == "📞 Contact":
        bot.reply_to(message, B(f"📞 {BOT_USERNAME}"))
    elif txt == "👑 Admin" and uid in ADMIN_IDS:
        bot.reply_to(message, B("👑 Admin Panel"), reply_markup=admin_mk())
    elif txt == "📢 Broadcast" and uid in ADMIN_IDS:
        bot.reply_to(message, B("Usage: /broadcast <message>"))

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/'))
def handle_cmd(message):
    pass

@bot.message_handler(func=lambda m: True)
def handle_project_name(message):
    uid = message.from_user.id
    txt = message.text.strip()
    if not txt.startswith('/'):
        user_projects[uid] = txt
        bot.reply_to(message, B(f"📁 Project set: `{txt}`"))

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(c):
    uid = c.from_user.id; d = c.data
    if d == "upload":
        bot.send_message(c.message.chat.id, B("📁 Send project name or /setproject <name>\nThen upload .py, .js, or .zip"))
        bot.answer_callback_query(c.id)
    elif d == "my_bots" or d == "check_files":
        files = get_user_files(uid)
        if not files:
            bot.edit_message_text(B("📭 No files uploaded yet."), c.message.chat.id, c.message.message_id, reply_markup=main_markup(uid))
        else:
            txt = B("📂 Your Files\n"); mk = types.InlineKeyboardMarkup(row_width=1)
            for f in files:
                fn = f['filename']; ru = is_running(uid, fn)
                mk.add(types.InlineKeyboardButton(f"{'🟢' if ru else '🔴'} {fn}", callback_data=f"file_{uid}_{fn}"))
            mk.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="back"))
            bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=mk)
        bot.answer_callback_query(c.id)
    elif d.startswith("file_"):
        parts = d.split('_', 2); fuid = int(parts[1]); fn = parts[2]; ru = is_running(fuid, fn)
        txt = B(f"{'🟢' if ru else '🔴'} `{fn}`\n{'Running' if ru else 'Stopped'}")
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=ctrl_btns(fuid, fn, ru))
        bot.answer_callback_query(c.id)
    elif d.startswith("sta_"):
        parts = d.split('_', 2); fuid = int(parts[1]); fn = parts[2]
        f = db.fetch_one("SELECT file_path,file_type FROM files WHERE user_id=? AND filename=?", (fuid, fn))
        if f and os.path.exists(f['file_path']):
            start_script(fuid, fn, f['file_path'], 'py' if fn.endswith('.py') else 'js', c.message)
            ru = is_running(fuid, fn)
            bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=ctrl_btns(fuid, fn, ru))
        else: bot.answer_callback_query(c.id, B("❌ File not found."), show_alert=True)
        bot.answer_callback_query(c.id)
    elif d.startswith("stp_"):
        parts = d.split('_', 2); fuid = int(parts[1]); fn = parts[2]; kill_script(fuid, fn)
        db.execute("UPDATE files SET is_running=0,pid=NULL WHERE user_id=? AND filename=?", (fuid, fn))
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=ctrl_btns(fuid, fn, False))
        bot.answer_callback_query(c.id)
    elif d.startswith("rst_"):
        parts = d.split('_', 2); fuid = int(parts[1]); fn = parts[2]
        f = db.fetch_one("SELECT file_path,file_type FROM files WHERE user_id=? AND filename=?", (fuid, fn))
        if f and os.path.exists(f['file_path']):
            kill_script(fuid, fn); time.sleep(1)
            start_script(fuid, fn, f['file_path'], 'py' if fn.endswith('.py') else 'js', c.message)
        bot.answer_callback_query(c.id)
    elif d.startswith("del_"):
        parts = d.split('_', 2); fuid = int(parts[1]); fn = parts[2]
        delete_file(fuid, fn)
        bot.edit_message_text(B(f"🗑️ `{fn}` deleted."), c.message.chat.id, c.message.message_id, reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d.startswith("log_"):
        parts = d.split('_', 2); fuid = int(parts[1]); fn = parts[2]
        folder = os.path.join(UPLOAD_BOTS_DIR, str(fuid), user_projects.get(fuid, ""))
        lp = os.path.join(folder, f"{os.path.splitext(fn)[0]}.log")
        if os.path.exists(lp):
            try:
                with open(lp, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
                if len(content) > 3000: content = content[-3000:]
                bot.send_message(c.message.chat.id, B(f"📜 Logs for `{fn}`:\n<pre>{content}</pre>"))
            except: bot.send_message(c.message.chat.id, B("❌ Error reading log."))
        else: bot.send_message(c.message.chat.id, B("📭 No logs."))
        bot.answer_callback_query(c.id)
    elif d == "back":
        bot.edit_message_text(B("🏠 Main Menu"), c.message.chat.id, c.message.message_id, reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d == "dashboard":
        tu = len(active_users)
        rs = sum(1 for k, v in bot_scripts.items() if is_running(v['uid'], v['fn']))
        txt = f"📊 {B('Dashboard')}\n👥 Users: {tu}\n🤖 Running: {rs}\n📁 Files: {sum(len(f) for f in user_files.values())}"
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d == "profile":
        tb = get_tier_benefits(uid); fc = get_file_count(uid); bal = CreditShop.get_balance(uid)
        ru = sum(1 for f in get_user_files(uid) if is_running(uid, f['filename']))
        refs = ReferralManager.stats(uid)
        txt = f"""
👤 {B('Profile')}
🆔 ID: <code>{uid}</code>
🎫 Tier: {tb['icon']} {tb['name']}
📁 Files: {fc}/{tb['upload_limit']}
🤖 Running: {ru}
🪙 Credits: {bal}
🤝 Referrals: {refs['total']}
        """
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=main_markup(uid))
        bot.answer_callback_query(c.id)
    elif d == "referral":
        cmd_refer(c.message)
        bot.answer_callback_query(c.id)
    elif d == "leaderboard":
        cmd_leaderboard(c.message)
        bot.answer_callback_query(c.id)
    elif d == "speed":
        s = time.time()
        bot.answer_callback_query(c.id)
        bot.send_message(c.message.chat.id, B(f"⚡ Response: {(time.time() - s) * 1000:.0f}ms"))
    elif d == "admin_panel":
        if uid not in ADMIN_IDS: return
        bot.edit_message_text(B("👑 Admin Panel"), c.message.chat.id, c.message.message_id, reply_markup=admin_mk())
        bot.answer_callback_query(c.id)
    elif d == "broadcast":
        if uid not in ADMIN_IDS: return
        bot.send_message(c.message.chat.id, B("📢 Send message as /broadcast <message>"))
        bot.answer_callback_query(c.id)
    elif d == "add_adm":
        if uid != OWNER_ID: return
        bot.send_message(c.message.chat.id, B("Send user ID to add as admin."))
        bot.register_next_step_handler(c.message, lambda m: (ADMIN_IDS.add(int(m.text)), bot.reply_to(m, B("✅ Admin added."))))
        bot.answer_callback_query(c.id)
    elif d == "rm_adm":
        if uid != OWNER_ID: return
        bot.send_message(c.message.chat.id, B("Send user ID to remove from admin."))
        bot.register_next_step_handler(c.message, lambda m: (ADMIN_IDS.discard(int(m.text)), bot.reply_to(m, B("✅ Admin removed."))))
        bot.answer_callback_query(c.id)
    elif d == "list_adm":
        txt = "👑 Admins:\n" + '\n'.join(str(x) for x in ADMIN_IDS)
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=admin_mk())
        bot.answer_callback_query(c.id)
    elif d == "sys_stats":
        tu = len(active_users); tf = sum(len(f) for f in user_files.values())
        rs = sum(1 for k, v in bot_scripts.items() if is_running(v['uid'], v['fn']))
        mem = psutil.virtual_memory(); cpu = psutil.cpu_percent()
        txt = f"""📊 {B('System Stats')}
👥 Users: {db.fetch_one('SELECT COUNT(*) as c FROM users')['c']}
🤖 Running: {rs}
💾 RAM: {mem.percent}% ({mem.used // 1024 // 1024}MB/{mem.total // 1024 // 1024}MB)
⚡ CPU: {cpu}%
📅 Uptime: {datetime.now() - startup_time}"""
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=admin_mk())
        bot.answer_callback_query(c.id)
    elif d == "shop":
        cmd_shop(c.message)
        bot.answer_callback_query(c.id)
    elif d == "daily":
        cmd_daily(c.message)
        bot.answer_callback_query(c.id)
    elif d.startswith("buy_"):
        idx = int(d.split("_")[1])
        if idx < len(SHOP_ITEMS):
            item = SHOP_ITEMS[idx]
            bal = CreditShop.get_balance(uid)
            if bal < item['price']:
                bot.answer_callback_query(c.id, B(f"❌ Need {item['price']}🪙, you have {bal}🪙"), show_alert=True)
            else:
                CreditShop.spend(uid, item['price'])
                if item['type'] == 'premium':
                    expires = (datetime.now() + timedelta(days=item['days'])).isoformat()
                    db.execute("INSERT OR REPLACE INTO subscriptions(user_id,tier,expires_at,activated_at) VALUES(?,?,?,?)", (uid, 'premium', expires, datetime.now().isoformat()))
                bot.answer_callback_query(c.id, B(f"✅ Purchased {item['name']}!"), show_alert=True)
        bot.answer_callback_query(c.id)
    elif d == "lock_bot":
        if uid not in ADMIN_IDS: return
        global bot_locked; bot_locked = True
        bot.answer_callback_query(c.id, B("🔒 Locked"))
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=admin_mk())
    elif d == "unlock_bot":
        if uid not in ADMIN_IDS: return
        bot_locked = False
        bot.answer_callback_query(c.id, B("🔓 Unlocked"))
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=admin_mk())
    elif d == "recover_all":
        if uid not in ADMIN_IDS: return
        recovered = rec.recover_all()
        bot.answer_callback_query(c.id, B(f"✅ Recovered {len(recovered)} scripts."))
    elif d == "subscription":
        bot.answer_callback_query(c.id, B("💳 Use /admin to manage subs"))
    elif d == "analytics":
        if uid not in ADMIN_IDS: return
        tu = len(active_users); rs = sum(1 for k, v in bot_scripts.items() if is_running(v['uid'], v['fn']))
        tf = sum(len(f) for f in user_files.values())
        tc = sum(CreditShop.get_balance(u) for u in active_users)
        mem = psutil.virtual_memory()
        txt = f"""📈 {B('Analytics')}
👥 Users: {tu}
📁 Files: {tf}
🤖 Running: {rs}
🪙 Total Credits: {tc}
💾 RAM: {mem.percent}%
📅 Uptime: {datetime.now() - startup_time}"""
        bot.edit_message_text(txt, c.message.chat.id, c.message.message_id, reply_markup=admin_mk())
        bot.answer_callback_query(c.id)
    elif d == "shop_mgmt":
        if uid not in ADMIN_IDS: return
        bot.send_message(c.message.chat.id, B(f"🛒 Shop Management\n\n{CREDIT_ITEMS}"))
        bot.answer_callback_query(c.id)
    elif d == "restart_bot":
        if uid not in ADMIN_IDS: return
        bot.answer_callback_query(c.id, B("🚀 Restarting..."))
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        bot.answer_callback_query(c.id)

print("=" * 60)
print("⚡ EXU HOSTING BOT v3.1 ⚡")
print("=" * 60)
print(f"Owner: {OWNER_ID}")
print(f"Admins: {len(ADMIN_IDS)}")
print(f"Users: {db.fetch_one('SELECT COUNT(*) as c FROM users')['c']}")
print("=" * 60)
print("CREDITS: EXU CODER | VIP DARK GOD | BLACK TITAN")
print("POWERED BY: OPENCODE AI")
print("=" * 60)

try: bot.send_message(OWNER_ID, B("🚀 EXU HOSTING BOT STARTED! ✅"))
except: pass

try: os.waitpid(-1, os.WNOHANG)
except ChildProcessError: pass

while True:
    try: bot.polling(timeout=30, long_polling_timeout=15, non_stop=False)
    except Exception as e:
        em = str(e)
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

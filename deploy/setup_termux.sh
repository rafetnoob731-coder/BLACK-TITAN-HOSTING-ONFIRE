#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BOT_DIR="/storage/emulated/0/opencode/AI_Projects/NEXUS_HOST"
cd "$BOT_DIR"

echo "============================================"
echo "  BLACK TITAN HOSTING - TERMUX SETUP"
echo "============================================"

# 1. Install Python deps
echo "[1/5] Installing Python dependencies..."
pip3 install --break-system-packages pyTelegramBotAPI psutil requests Flask qrcode[pil] Pillow cryptography

# 3. Create data dirs
echo "[3/5] Creating data directories..."
mkdir -p telegram-bot/bt_data telegram-bot/bt_uploads

# 4. Create start/stop scripts
echo "[4/5] Creating management scripts..."

# Start script using screen
cat > start_bot.sh << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
BOT_DIR="/storage/emulated/0/opencode/AI_Projects/NEXUS_HOST"
cd "$BOT_DIR"
source venv/bin/activate

# Kill old session if exists
screen -S blacktitan -X quit 2>/dev/null || true
sleep 1

# Release any stale Telegram polling session
TOKEN="8792154488:AAHEi2aH2UrHRq_3QfX_J2gxWpmFY7Ptdkw"
curl -s "https://api.telegram.org/bot$TOKEN/deleteWebhook?drop_pending_updates=true" > /dev/null
curl -s "https://api.telegram.org/bot$TOKEN/close" > /dev/null

# Start bot in screen session
screen -dmS blacktitan -L -Logfile /storage/emulated/0/opencode/AI_Projects/NEXUS_HOST/bot.log \
  bash -c 'source venv/bin/activate && python3 telegram-bot/bot.py'

echo "✅ Bot started in screen session 'blacktitan'"
echo "   Attach: screen -r blacktitan"
echo "   Detach: Ctrl+A, D"
echo "   Logs: tail -f bot.log"
SCRIPT

# Stop script
cat > stop_bot.sh << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
echo "Stopping bot..."
screen -S blacktitan -X quit 2>/dev/null || true
sleep 1
TOKEN="8792154488:AAHEi2aH2UrHRq_3QfX_J2gxWpmFY7Ptdkw"
curl -s "https://api.telegram.org/bot$TOKEN/close" > /dev/null
echo "✅ Bot stopped"
SCRIPT

chmod +x start_bot.sh stop_bot.sh

# 5. Create auto-start (Termux:Boot)
echo "[5/5] Setting up auto-start..."
BOOT_DIR="$HOME/.termux/boot"
mkdir -p "$BOOT_DIR"
cat > "$BOOT_DIR/blacktitan.sh" << 'BOOTSCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
sleep 30  # wait for network
/storage/emulated/0/opencode/AI_Projects/NEXUS_HOST/start_bot.sh
BOOTSCRIPT
chmod +x "$BOOT_DIR/blacktitan.sh"

echo ""
echo "============================================"
echo "  ✅ SETUP COMPLETE"
echo "============================================"
echo "  Start bot:  cd $BOT_DIR && bash start_bot.sh"
echo "  Stop bot:   cd $BOT_DIR && bash stop_bot.sh"
echo "  View logs:  screen -r blacktitan"
echo "  Tail logs:  tail -f $BOT_DIR/bot.log"
echo ""
echo "  Auto-start: Enabled via Termux:Boot"
echo "  Wake lock:  Enabled (prevents sleep)"
echo "============================================"

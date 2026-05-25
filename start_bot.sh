#!/data/data/com.termux/files/usr/bin/bash
BOT_DIR="/storage/emulated/0/opencode/AI_Projects/NEXUS_HOST"
cd "$BOT_DIR"
screen -S blacktitan -X quit 2>/dev/null || true
sleep 1
TOKEN="8792154488:AAHEi2aH2UrHRq_3QfX_J2gxWpmFY7Ptdkw"
curl -s "https://api.telegram.org/bot$TOKEN/close" > /dev/null
screen -dmS blacktitan -L -Logfile "$BOT_DIR/bot.log" python3 telegram-bot/bot.py
echo "✅ Bot started (screen: blacktitan)"
echo "   Attach: screen -r blacktitan"

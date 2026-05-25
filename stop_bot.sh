#!/data/data/com.termux/files/usr/bin/bash
BOT_DIR="/storage/emulated/0/opencode/AI_Projects/NEXUS_HOST"
TOKEN="8792154488:AAHEi2aH2UrHRq_3QfX_J2gxWpmFY7Ptdkw"
screen -S blacktitan -X quit 2>/dev/null || true
curl -s "https://api.telegram.org/bot$TOKEN/close" > /dev/null
echo "✅ Bot stopped"

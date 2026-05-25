#!/bin/bash
# Kill any stale Python processes using the same token (prevents 409 conflict)
TOKEN="8792154488:AAHEi2aH2UrHRq_3QfX_J2gxWpmFY7Ptdkw"
PID=$(ps aux | grep "python3.*bot.py" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
    echo "[prestart] Killing existing bot process: $PID"
    kill -9 $PID 2>/dev/null || true
    sleep 2
fi
# Also try to release Telegram polling via API
curl -s "https://api.telegram.org/bot$TOKEN/deleteWebhook?drop_pending_updates=true" > /dev/null
curl -s "https://api.telegram.org/bot$TOKEN/close" > /dev/null
echo "[prestart] Ready to start"
exit 0

#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# BLACK TITAN HOSTING BOT V4.0 - Server Setup Script
# ============================================================
# Run on your Linux server as root or with sudo
#
#   chmod +x setup.sh && sudo ./setup.sh
# ============================================================

INSTALL_DIR="/opt/blacktitan"
REPO_URL="https://github.com/rafetnoob731-coder/BLACK-TITAN-HOSTING-ONFIRE.git"

echo "========================================"
echo "  BLACK TITAN HOSTING BOT - INSTALL"
echo "========================================"

# --- Install system dependencies ---
echo "[1/5] Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv python3-dev git curl build-essential libssl-dev libffi-dev nginx

# --- Clone repo ---
echo "[2/5] Cloning repository..."
if [ -d "$INSTALL_DIR" ]; then
    echo "  Directory $INSTALL_DIR exists, pulling updates..."
    cd "$INSTALL_DIR" && git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# --- Python virtualenv ---
echo "[3/5] Creating Python virtualenv..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# --- Setup data directories ---
echo "[4/5] Creating data directories..."
mkdir -p telegram-bot/bt_data telegram-bot/bt_uploads
chmod -R 755 telegram-bot

# --- Install systemd service ---
echo "[5/5] Installing systemd service..."
cp deploy/blacktitan.service /etc/systemd/system/blacktitan.service
systemctl daemon-reload
systemctl enable blacktitan
systemctl start blacktitan

echo ""
echo "========================================"
echo "  ✅ INSTALL COMPLETE"
echo "========================================"
echo "  Service: blacktitan"
echo "  Status: $(systemctl is-active blacktitan)"
echo "  Logs: journalctl -u blacktitan -f"
echo "  Restart: systemctl restart blacktitan"
echo "  Stop: systemctl stop blacktitan"
echo "========================================"

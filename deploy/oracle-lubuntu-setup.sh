#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/cestacontrol"
REPO_URL="https://github.com/ArthurBrit/CestaControl.git"

sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git curl

if [ ! -d "$APP_DIR/.git" ]; then
  sudo mkdir -p "$APP_DIR"
  sudo chown -R "$USER:$USER" "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Arquivo .env criado em $APP_DIR/.env. Edite usuario, senha e SECRET_KEY antes de expor o sistema."
fi

sudo cp deploy/cestacontrol.service /etc/systemd/system/cestacontrol.service
sudo cp deploy/nginx-cestacontrol.conf /etc/nginx/sites-available/cestacontrol

if [ ! -e /etc/nginx/sites-enabled/cestacontrol ]; then
  sudo ln -s /etc/nginx/sites-available/cestacontrol /etc/nginx/sites-enabled/cestacontrol
fi

sudo rm -f /etc/nginx/sites-enabled/default
sudo chown -R www-data:www-data "$APP_DIR"
sudo systemctl daemon-reload
sudo systemctl enable cestacontrol
sudo systemctl restart cestacontrol
sudo nginx -t
sudo systemctl reload nginx

echo "Deploy base concluido. Acesse pelo IP publico da instancia apos liberar as portas 80/443 na Oracle."

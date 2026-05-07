# Deploy com Nginx na Oracle Cloud

Este guia considera uma instancia gratuita da Oracle Cloud rodando Lubuntu/Ubuntu com acesso SSH.

Fontes oficiais uteis:

- Oracle Free Tier / Always Free: https://docs.oracle.com/iaas/Content/FreeTier/resourceref.htm
- Regras de seguranca da rede Oracle: https://www.oracle.com/cloud/networking/virtual-cloud-network/faq/

## Visao geral

```text
Internet ou rede interna
  -> Oracle VCN / Security List
  -> Nginx na VM
  -> FastAPI/Uvicorn em 127.0.0.1:8000
  -> SQLite em data/cestacontrol.db
```

Para o seu volume de uso, SQLite continua adequado. O ponto mais importante e backup do arquivo do banco.

## 0. Criar a VM na Oracle

Na Oracle Cloud:

1. Crie uma instancia Compute marcada como Always Free.
2. Use uma imagem Ubuntu ou Lubuntu.
3. Escolha uma subnet publica.
4. Salve a chave SSH privada no seu computador.
5. Anote o IP publico da instancia.

Se aparecer erro de capacidade ao criar Ampere A1, tente outra regiao/shape Always Free ou uma VM pequena x86 Always Free quando disponivel.

## 1. Liberar portas na Oracle

No painel da Oracle, va em:

`Virtual Cloud Networks -> sua VCN -> Security Lists ou Network Security Groups -> Add Ingress Rules`

Crie regras de entrada:

```text
Source CIDR: 0.0.0.0/0
IP Protocol: TCP
Destination Port Range: 80
Description: HTTP CestaControl
```

Se for usar HTTPS:

```text
Source CIDR: 0.0.0.0/0
IP Protocol: TCP
Destination Port Range: 443
Description: HTTPS CestaControl
```

Mantenha SSH:

```text
Source CIDR: seu-ip/32, se possivel
IP Protocol: TCP
Destination Port Range: 22
Description: SSH
```

Para uso interno, o ideal e restringir as portas 80/443 ao IP da empresa, VPN ou rede confiavel. `0.0.0.0/0` deixa publico.

## 2. Acessar via SSH

No seu computador:

```bash
ssh -i caminho/da/sua-chave.key ubuntu@IP_PUBLICO
```

Dependendo da imagem, o usuario pode ser `ubuntu`. Se a Oracle mostrar outro usuario na tela da instancia, use o usuario indicado.

## 3. Preparar o servidor

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git
```

Se o Lubuntu estiver com `ufw` ativo, libere HTTP/HTTPS:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw status
```

## 4. Baixar o projeto

```bash
sudo mkdir -p /var/www/cestacontrol
sudo chown -R $USER:$USER /var/www/cestacontrol
git clone https://github.com/ArthurBrit/CestaControl.git /var/www/cestacontrol
cd /var/www/cestacontrol
```

## 5. Criar ambiente Python

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite o `.env`:

```bash
nano .env
```

Troque principalmente:

```env
SECRET_KEY=uma-chave-grande-e-aleatoria
ADMIN_USERNAME=usuario-interno
ADMIN_PASSWORD=senha-forte
DATABASE_URL=sqlite:///./data/cestacontrol.db
```

Gere uma `SECRET_KEY` forte:

```bash
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

## 6. Testar a aplicacao

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Em outro terminal:

```bash
curl http://127.0.0.1:8000/login
```

## 7. Configurar systemd

Copie o arquivo de servico:

```bash
sudo cp deploy/cestacontrol.service /etc/systemd/system/cestacontrol.service
sudo chown -R www-data:www-data /var/www/cestacontrol
sudo systemctl daemon-reload
sudo systemctl enable cestacontrol
sudo systemctl start cestacontrol
sudo systemctl status cestacontrol
```

Se a VM nao usar o usuario `www-data`, mantenha `www-data` mesmo assim para o processo web. O comando `chown` acima da permissao ao app.

## 8. Configurar Nginx

Copie o exemplo:

```bash
sudo cp deploy/nginx-cestacontrol.conf /etc/nginx/sites-available/cestacontrol
sudo ln -s /etc/nginx/sites-available/cestacontrol /etc/nginx/sites-enabled/cestacontrol
sudo nginx -t
sudo systemctl reload nginx
```

Antes de recarregar, edite:

```bash
sudo nano /etc/nginx/sites-available/cestacontrol
```

Altere:

```nginx
server_name seu-dominio.com.br;
```

Para seu dominio ou IP publico:

```nginx
server_name IP_PUBLICO;
```

Teste no navegador:

```text
http://IP_PUBLICO
```

## 9. HTTPS

Se tiver dominio apontando para o servidor, use Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com.br
```

Sem dominio, da para usar HTTP pelo IP, mas para acesso externo real eu recomendo dominio + HTTPS.

## 10. Backup

O banco SQLite fica em:

```text
/var/www/cestacontrol/data/cestacontrol.db
```

Faca backup periodico desse arquivo. Uma rotina simples pode copiar o banco para outra pasta ou armazenamento externo diariamente.

Exemplo de backup local:

```bash
sudo mkdir -p /var/backups/cestacontrol
sudo cp /var/www/cestacontrol/data/cestacontrol.db /var/backups/cestacontrol/cestacontrol-$(date +%F).db
```

## 11. Atualizar o sistema depois de mudancas

```bash
cd /var/www/cestacontrol
sudo -u www-data git pull
sudo -u www-data .venv/bin/pip install -r requirements.txt
sudo systemctl restart cestacontrol
```

## Instalacao automatizada opcional

Depois de clonar o repositorio, voce pode rodar:

```bash
chmod +x deploy/oracle-lubuntu-setup.sh
./deploy/oracle-lubuntu-setup.sh
```

Mesmo usando o script, revise o `.env` e o `server_name` do Nginx.

## Comandos uteis

```bash
sudo systemctl restart cestacontrol
sudo journalctl -u cestacontrol -f
sudo nginx -t
sudo systemctl reload nginx
```

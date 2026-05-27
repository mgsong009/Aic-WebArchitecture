# AWS EC2 Demo Deployment

This runbook deploys the full AIC Web stack on one low-cost EC2 instance with Docker Compose:

- `frontend`: nginx serving Vue and proxying `/api/` to the backend
- `backend`: FastAPI on the internal Docker network
- `pipeline`: FastAPI analysis service on the internal Docker network
- `db`: MySQL 8 in Docker with a named volume

The demo target is HTTPS at `https://aic-webproject.kro.kr`. Caddy terminates TLS and redirects plain HTTP requests to HTTPS.

## 1. Create EC2

Use the AWS console to create an instance:

- AMI: Ubuntu Server 22.04 LTS or 24.04 LTS
- Instance type: `t3.medium` minimum for the analysis pipeline demo
- Storage: 30 GB minimum, 50 GB recommended
- Security group inbound rules:
  - SSH `22` from your IP only
  - HTTP `80` from `0.0.0.0/0`
  - HTTPS `443` from `0.0.0.0/0`

Avoid opening MySQL, backend, or pipeline ports to the internet. Only Caddy publishes ports `80` and `443`.

## 2. Connect to EC2

```bash
ssh -i /path/to/key.pem ubuntu@EC2_PUBLIC_IP
```

## 3. Install Docker

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu
```

Log out and reconnect so the `docker` group takes effect.

Verify:

```bash
docker --version
docker compose version
```

## 4. Upload Or Clone The Project

Clone the repository if it is available remotely:

```bash
git clone REPOSITORY_URL
cd Aic-WebArchitecture
```

If the repository is only local, copy it from your machine:

```bash
scp -i /path/to/key.pem -r C:/Users/김우현/.git_repository/AIC-WebProject/Aic-WebArchitecture ubuntu@EC2_PUBLIC_IP:~/Aic-WebArchitecture
ssh -i /path/to/key.pem ubuntu@EC2_PUBLIC_IP
cd ~/Aic-WebArchitecture
```

## 5. Create `.env`

```bash
cp .env.example .env
nano .env
```

Set real secret values:

```dotenv
MYSQL_ROOT_PASSWORD=...
MYSQL_PASSWORD=...
JWT_SECRET=...
ACME_EMAIL=...
DISCORD_WEBHOOK_URL=...
```

Rules:

- Use different MySQL root and app passwords.
- Keep `JWT_SECRET` at least 32 characters.
- Do not use words like `placeholder`, `default`, `example`, `your_`, or `change_` in `JWT_SECRET`.
- Set `ACME_EMAIL` to an email address used for TLS certificate issuance notices.
- Set `DISCORD_WEBHOOK_URL` only if you want Discord notifications when the ELT health check fails.
- Never commit `.env`.

Generate a JWT secret on EC2:

```bash
openssl rand -hex 32
```

## 6. Start The Stack

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

The pipeline image downloads a sentence-transformer model during build, so the first build can take several minutes.
Caddy automatically obtains and renews the TLS certificate for `aic-webproject.kro.kr` through ZeroSSL. Confirm the domain's `A` record points to the EC2 public IP before starting the stack.

Check status:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f caddy
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f pipeline
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f db
```

## 7. Verify

From your local browser:

```text
https://aic-webproject.kro.kr
```

From EC2:

```bash
curl http://localhost
curl -I https://aic-webproject.kro.kr
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec pipeline python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:9000/health').read().decode())"
```

The expected health response is:

```json
{"status":"ok"}
```

## 8. Common Operations

Restart after code changes:

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Apply `init.sql` changes to an existing EC2 demo database:

```bash
git pull
docker compose up --build -d db
bash scripts/recreate_demo_db_from_init.sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

MySQL only runs files mounted into `/docker-entrypoint-initdb.d/` when `/var/lib/mysql` is empty. Because this project keeps MySQL data in the named Docker volume `mysql_data`, changes to `init.sql` are not applied by `docker compose up --build -d` after the first initialization.

The script above asks you to type `RESET` before changing the database. For non-interactive demo maintenance, run `bash scripts/recreate_demo_db_from_init.sh --yes`.

The script drops and recreates only the `aic_db` database from the current `init.sql`, then restarts the backend. Use it for the disposable EC2 demo database when you want the server to match the repository seed data. Do not use it on production data without replacing it with a proper migration plan.

Run the ELT once and record warehouse run history:

```bash
AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/run_elt_once.sh
```

Schedule the ELT with host cron:

```bash
crontab -e
```

```cron
0 3 * * * cd /home/ubuntu/Aic-WebArchitecture && AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/run_elt_once.sh
30 3 * * * cd /home/ubuntu/Aic-WebArchitecture && AIC_ELT_USE_PROD_COMPOSE=1 bash scripts/check_elt_health_and_notify.sh >> logs/elt/health.log 2>&1
```

Confirm the last run in warehouse:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T warehouse psql -U warehouse_user -d aic_warehouse -c "SELECT run_id, status, started_at, finished_at, duration_ms, error_message FROM elt_run_history ORDER BY started_at DESC LIMIT 5;"
```

Detailed warehouse validation and cron troubleshooting live in [WAREHOUSE_VALIDATION.md](WAREHOUSE_VALIDATION.md).

Stop:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

Stop and delete local MySQL/model volumes:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down -v
```

Use `down -v` only when you intentionally want to erase the demo database and model cache.

## 9. GitHub Actions Auto Deploy

The workflow at `.github/workflows/deploy-ec2.yml` deploys automatically when `dev` receives a push.

It uses this flow:

1. Check out the repository in GitHub Actions.
2. Build a deployment archive while excluding `.git`, `.env`, `node_modules`, and `dist`.
3. Upload the archive to EC2 over SSH.
4. Preserve the existing EC2 `.env`.
5. Run `sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d` on EC2.

Configure these GitHub repository secrets:

| Secret | Value |
| --- | --- |
| `EC2_HOST` | EC2 public IP or public DNS, for example `13.125.245.16` |
| `EC2_USER` | SSH user, usually `ubuntu` |
| `EC2_SSH_KEY` | Private key contents for the EC2 key pair |

The EC2 security group must allow the GitHub Actions runner to reach SSH port `22`.
For a quick demo, the simplest option is:

- SSH `22` from `0.0.0.0/0`
- HTTP `80` from `0.0.0.0/0`
- HTTPS `443` from `0.0.0.0/0`

This keeps password login disabled and still requires the private key in `EC2_SSH_KEY`.
For a longer-lived deployment, replace broad SSH access with a narrower option such as a self-hosted runner, AWS SSM, or a workflow step that temporarily opens the current runner IP.

The EC2 deployment directory is fixed to:

```text
~/Aic-WebArchitecture
```

Before the first automated deploy, confirm this file exists on EC2:

```bash
~/Aic-WebArchitecture/.env
```

The workflow intentionally does not upload or replace `.env`.

## 10. Troubleshooting

If `http://EC2_PUBLIC_IP` does not open:

- Confirm the EC2 security group allows inbound TCP `80`.
- Confirm `docker compose -f docker-compose.yml -f docker-compose.prod.yml ps` shows `caddy` and `frontend` running.
- Check `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f caddy`.

If `https://aic-webproject.kro.kr` does not open:

- Confirm the domain `A` record points to the EC2 public IP.
- Confirm the EC2 security group allows inbound TCP `443`.
- Check `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f caddy`.

If login or API requests fail:

- Confirm frontend nginx still proxies `/api/` to `http://backend:8000`.
- Check `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend`.
- Check `JWT_SECRET` passes the backend validator.

If analysis is slow on first run:

- Check `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f pipeline`.
- Use at least `t3.medium`; smaller instances may struggle with the model.

If MySQL does not become healthy:

- Check `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f db`.
- Confirm `.env` exists and has `MYSQL_ROOT_PASSWORD` and `MYSQL_PASSWORD`.
- If this is a disposable demo and the DB initialized with bad credentials, recreate volumes with `docker compose -f docker-compose.yml -f docker-compose.prod.yml down -v` and start again.

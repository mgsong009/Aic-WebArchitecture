# AWS EC2 Demo Deployment

This runbook deploys the full AIC Web stack on one low-cost EC2 instance with Docker Compose:

- `frontend`: nginx serving Vue and proxying `/api/` to the backend
- `backend`: FastAPI on the internal Docker network
- `pipeline`: FastAPI analysis service on the internal Docker network
- `db`: MySQL 8 in Docker with a named volume

The first demo target is plain HTTP at `http://EC2_PUBLIC_IP`. Domain, HTTPS, and redirects are tracked as a follow-up in `TODO.md`.

## 1. Create EC2

Use the AWS console to create an instance:

- AMI: Ubuntu Server 22.04 LTS or 24.04 LTS
- Instance type: `t3.medium` minimum for the analysis pipeline demo
- Storage: 30 GB minimum, 50 GB recommended
- Security group inbound rules:
  - SSH `22` from your IP only
  - HTTP `80` from `0.0.0.0/0`

Avoid opening MySQL, backend, or pipeline ports to the internet. Only the frontend publishes port `80`.

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
```

Rules:

- Use different MySQL root and app passwords.
- Keep `JWT_SECRET` at least 32 characters.
- Do not use words like `placeholder`, `default`, `example`, `your_`, or `change_` in `JWT_SECRET`.
- Never commit `.env`.

Generate a JWT secret on EC2:

```bash
openssl rand -hex 32
```

## 6. Start The Stack

```bash
docker compose up --build -d
```

The pipeline image downloads a sentence-transformer model during build, so the first build can take several minutes.

Check status:

```bash
docker compose ps
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f pipeline
docker compose logs -f db
```

## 7. Verify

From your local browser:

```text
http://EC2_PUBLIC_IP
```

From EC2:

```bash
curl http://localhost
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
docker compose exec pipeline python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:9000/health').read().decode())"
```

The expected health response is:

```json
{"status":"ok"}
```

## 8. Common Operations

Restart after code changes:

```bash
git pull
docker compose up --build -d
```

Stop:

```bash
docker compose down
```

Stop and delete local MySQL/model volumes:

```bash
docker compose down -v
```

Use `down -v` only when you intentionally want to erase the demo database and model cache.

## 9. Troubleshooting

If `http://EC2_PUBLIC_IP` does not open:

- Confirm the EC2 security group allows inbound TCP `80`.
- Confirm `docker compose ps` shows `frontend` running.
- Check `docker compose logs -f frontend`.

If login or API requests fail:

- Confirm frontend nginx still proxies `/api/` to `http://backend:8000`.
- Check `docker compose logs -f backend`.
- Check `JWT_SECRET` passes the backend validator.

If analysis is slow on first run:

- Check `docker compose logs -f pipeline`.
- Use at least `t3.medium`; smaller instances may struggle with the model.

If MySQL does not become healthy:

- Check `docker compose logs -f db`.
- Confirm `.env` exists and has `MYSQL_ROOT_PASSWORD` and `MYSQL_PASSWORD`.
- If this is a disposable demo and the DB initialized with bad credentials, recreate volumes with `docker compose down -v` and start again.

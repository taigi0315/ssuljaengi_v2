#!/usr/bin/env bash
# ── Gossiptoon V2 – EC2 First-Time Setup ──────────────────────────────────────
# Run this ONCE on a fresh Amazon Linux 2023 / Ubuntu EC2 instance.
#
# Usage:
#   bash ec2-first-setup.sh \
#     <REDDIT_CLIENT_ID> \
#     <REDDIT_CLIENT_SECRET> \
#     <GOOGLE_API_KEY>
#
# After this script completes, GitHub Actions will handle future deploys.
# ------------------------------------------------------------------------------

set -euo pipefail

REDDIT_CLIENT_ID="${1:?ERROR: pass REDDIT_CLIENT_ID as arg 1}"
REDDIT_CLIENT_SECRET="${2:?ERROR: pass REDDIT_CLIENT_SECRET as arg 2}"
GOOGLE_API_KEY="${3:?ERROR: pass GOOGLE_API_KEY as arg 3}"

REPO_URL="https://github.com/taigi0315/ssuljaengi_v2.git"
APP_DIR="$HOME/ssuljaengi_v2"

echo "==> Detecting OS..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="unknown"
fi

# ── Install Docker ──────────────────────────────────────────────────────────
echo "==> Installing Docker..."
if command -v docker &>/dev/null; then
    echo "    Docker already installed: $(docker --version)"
else
    if [[ "$OS" == "amzn" ]]; then
        sudo dnf update -y
        sudo dnf install -y docker git
        sudo systemctl enable --now docker
        sudo usermod -aG docker ec2-user
    elif [[ "$OS" == "ubuntu" ]]; then
        sudo apt-get update -y
        sudo apt-get install -y ca-certificates curl gnupg git
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
            sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
            sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update -y
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        sudo systemctl enable --now docker
        sudo usermod -aG docker ubuntu
    else
        echo "Unsupported OS: $OS — install Docker manually."
        exit 1
    fi
fi

# ── Install Docker Compose plugin (if not already bundled) ──────────────────
if ! docker compose version &>/dev/null; then
    echo "==> Installing Docker Compose plugin..."
    COMPOSE_VERSION="v2.27.1"
    sudo mkdir -p /usr/local/lib/docker/cli-plugins
    sudo curl -SL \
        "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-$(uname -m)" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose
    sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

echo "    Docker Compose: $(docker compose version)"

# ── Create persistent data directories ─────────────────────────────────────
echo "==> Creating data directories..."
sudo mkdir -p /data/gossiptoon/cache /data/gossiptoon/data
sudo chown -R "$(whoami)":"$(whoami)" /data/gossiptoon

# ── Clone the repository ────────────────────────────────────────────────────
if [ -d "$APP_DIR/.git" ]; then
    echo "==> Repository already cloned — pulling latest..."
    git -C "$APP_DIR" pull origin main
else
    echo "==> Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
fi

# ── Write the initial .env file ─────────────────────────────────────────────
EC2_HOST=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_EC2_IP")

echo "==> Writing deploy/.env..."
cat > "$APP_DIR/deploy/.env" <<EOF
REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
GOOGLE_API_KEY=${GOOGLE_API_KEY}
FRONTEND_URL=http://${EC2_HOST}:3000
NEXT_PUBLIC_API_URL=http://${EC2_HOST}:8000
EOF

echo "    EC2 public IP detected: ${EC2_HOST}"

# ── Initial container build & start ─────────────────────────────────────────
echo "==> Building and starting containers (this may take a few minutes)..."
cd "$APP_DIR"
docker compose -f deploy/docker-compose.ec2.yml up --build -d

echo ""
echo "✓ Setup complete!"
echo ""
echo "  Frontend:  http://${EC2_HOST}:3000"
echo "  Backend:   http://${EC2_HOST}:8000"
echo "  API docs:  http://${EC2_HOST}:8000/docs"
echo ""
echo "  Make sure EC2 Security Group allows inbound TCP on ports 3000 and 8000."
echo ""
echo "  Next: Add these GitHub Secrets to your repo:"
echo "    EC2_HOST             = ${EC2_HOST}"
echo "    EC2_SSH_KEY          = (paste your private key)"
echo "    REDDIT_CLIENT_ID     = (already set)"
echo "    REDDIT_CLIENT_SECRET = (already set)"
echo "    GOOGLE_API_KEY       = (already set)"

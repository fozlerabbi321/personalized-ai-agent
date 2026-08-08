#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# setup.sh — Copy .env.example → .env for backend and frontend
# Usage: bash setup.sh  (called automatically by `make dev` and `make setup`)
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

echo ""
echo -e "${BLUE}🔧  personalized_ai_agent — Environment Setup${RESET}"
echo "────────────────────────────────────────────────"

# ── Backend ──────────────────────────────────────────────────────────────────
if [ ! -f backend/.env ]; then
    if [ -f backend/.env.example ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✅  Created backend/.env from .env.example${RESET}"
    else
        echo -e "${YELLOW}⚠️   backend/.env.example not found — skipping${RESET}"
    fi
else
    echo -e "${YELLOW}ℹ️   backend/.env already exists — skipping${RESET}"
fi

# ── Frontend ─────────────────────────────────────────────────────────────────
if [ ! -f frontend/.env.local ]; then
    if [ -f frontend/.env.example ]; then
        cp frontend/.env.example frontend/.env.local
        echo -e "${GREEN}✅  Created frontend/.env.local from .env.example${RESET}"
    else
        echo -e "${YELLOW}ℹ️   frontend/.env.example not found${RESET}"
    fi
else
    echo -e "${YELLOW}ℹ️   frontend/.env.local already exists — skipping${RESET}"
fi

echo "────────────────────────────────────────────────"
echo -e "${GREEN}✅  Setup complete!${RESET}"
echo ""
echo -e "📝  ${BLUE}Next steps:${RESET}"
echo "   1. Edit backend/.env — add your GOOGLE_API_KEY and SECRET_KEY"
echo "   2. Run: make dev"
echo ""

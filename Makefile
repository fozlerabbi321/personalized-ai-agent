.PHONY: dev backend frontend setup seed stop logs clean help

SHELL := /bin/bash

# ──────────────────────────────────────────────────────────────────────────────
# HELP
# ──────────────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  personalized-ai-agent"
	@echo "  ─────────────────────────────────────────────────────"
	@echo "  make dev       Start ALL services (Docker + Next.js)"
	@echo "  make backend   Start only backend (Docker: FastAPI + PostgreSQL)"
	@echo "  make frontend  Start only Next.js dev server"
	@echo "  make setup     Copy .env.example → .env for backend & web"
	@echo "  make seed      Populate DB with dummy users, sessions & messages"
	@echo "  make stop      Stop all Docker services"
	@echo "  make logs      Tail all Docker service logs"
	@echo "  make clean     Remove Docker containers + volumes (full reset)"
	@echo ""
	@echo "  📖 API Docs  → http://localhost:8000/docs"
	@echo "  🌐 Frontend  → http://localhost:3000"
	@echo ""

# ──────────────────────────────────────────────────────────────────────────────
# SETUP — copy .env files
# ──────────────────────────────────────────────────────────────────────────────
setup:
	@chmod +x setup.sh && bash setup.sh

# ──────────────────────────────────────────────────────────────────────────────
# DEV — full stack (Docker backend + Next.js frontend)
# ──────────────────────────────────────────────────────────────────────────────
dev: setup
	@echo ""
	@echo "🚀  Starting backend (Docker)..."
	docker-compose up -d --build
	@echo "⏳  Waiting 15s for services to be healthy..."
	@sleep 15
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  ✅  Backend API  → http://localhost:8000"
	@echo "  ✅  API Docs     → http://localhost:8000/docs"
	@echo "  🌐  Starting Frontend..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	cd web && npm run dev

# ──────────────────────────────────────────────────────────────────────────────
# BACKEND ONLY
# ──────────────────────────────────────────────────────────────────────────────
backend: setup
	@echo "🚀  Starting backend services..."
	docker-compose up -d --build
	@echo ""
	@echo "  ✅  FastAPI  → http://localhost:8000"
	@echo "  ✅  Docs     → http://localhost:8000/docs"
	@echo "  ✅  Postgres → localhost:5432"
	@echo ""
	@echo "Tip: Run 'make seed' to populate with test data"

# ──────────────────────────────────────────────────────────────────────────────
# FRONTEND ONLY
# ──────────────────────────────────────────────────────────────────────────────
frontend:
	@echo "🌐  Starting Next.js dev server..."
	cd web && npm run dev

# ──────────────────────────────────────────────────────────────────────────────
# SEED — populate DB with test data
# ──────────────────────────────────────────────────────────────────────────────
seed:
	@echo "🌱  Running database seeder inside backend container..."
	docker-compose exec backend python seeder.py

# ──────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────────────────────────────────────
stop:
	docker-compose down
	@echo "✅  All Docker services stopped"

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
	@echo "✅  Containers and volumes removed"

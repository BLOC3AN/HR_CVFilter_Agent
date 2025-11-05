.PHONY: help install install-backend install-frontend run-backend run-frontend dev logs down build clean docker-build docker-up docker-down docker-logs

help:
	@echo "Available commands:"
	@echo "  make install         - Install all dependencies"
	@echo "  make install-backend - Install backend dependencies"
	@echo "  make install-frontend- Install frontend dependencies"
	@echo ""
	@echo "Local development (localhost):"
	@echo "  make dev             - Start all services locally"
	@echo "  make logs            - View logs of running services"
	@echo "  make down            - Stop all local services"
	@echo ""
	@echo "  make run-backend     - Run backend API only"
	@echo "  make run-frontend    - Run frontend UI only"
	@echo "  make build           - Build frontend for production"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build    - Build Docker images"
	@echo "  make docker-up       - Start Docker containers"
	@echo "  make docker-down     - Stop Docker containers"
	@echo "  make docker-logs     - View Docker logs"
	@echo ""
	@echo "  make clean           - Clean up temporary files"

install: install-backend install-frontend

install-backend:
	pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

run-backend:
	cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

# Local development commands
dev:
	@echo "🚀 Starting all services locally..."
	@echo "   - Backend API: http://localhost:8000"
	@echo "   - Frontend UI: http://localhost:8501"
	@echo "   - API Docs: http://localhost:8000/docs"
	@echo ""
	@mkdir -p logs
	@echo "Starting backend in background..."
	@cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 & echo $$! > ../.backend.pid
	@sleep 2
	@echo "✅ Backend started (PID: $$(cat .backend.pid))"
	@echo ""
	@echo "Starting frontend in background..."
	@cd frontend && npm run dev > ../logs/frontend.log 2>&1 & echo $$! > ../.frontend.pid
	@sleep 2
	@echo "✅ Frontend started (PID: $$(cat .frontend.pid))"
	@echo ""
	@echo "✅ All services started!"
	@echo "   Use 'make logs' to view logs"
	@echo "   Use 'make down' to stop services"

logs:
	@echo "📋 Viewing logs (Ctrl+C to exit)..."
	@echo "Backend logs (logs/backend.log) | Frontend logs (logs/frontend.log)"
	@echo "================================================================"
	@tail -f logs/backend.log logs/frontend.log 2>/dev/null || echo "No logs found. Services may not be running."

down:
	@echo "🛑 Stopping all services..."
	@if [ -f .backend.pid ]; then \
		kill $$(cat .backend.pid) 2>/dev/null && echo "✅ Backend stopped (PID: $$(cat .backend.pid))" || echo "⚠️  Backend process not found"; \
		rm -f .backend.pid; \
	else \
		echo "⚠️  Backend PID file not found"; \
	fi
	@if [ -f .frontend.pid ]; then \
		kill $$(cat .frontend.pid) 2>/dev/null && echo "✅ Frontend stopped (PID: $$(cat .frontend.pid))" || echo "⚠️  Frontend process not found"; \
		rm -f .frontend.pid; \
	else \
		echo "⚠️  Frontend PID file not found"; \
	fi
	@pkill -f "uvicorn main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@echo "✅ All services stopped!"

build:
	@echo "🔨 Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Build completed!"

# Docker commands
docker-build:
	@echo "🔨 Building Docker images..."
	docker compose build
	@echo "✅ Build completed!"

docker-up:
	@echo "🚀 Starting Docker containers..."
	docker compose up -d
	@echo "✅ Containers started!"
	@echo "   - Frontend: http://localhost:8501"
	@echo "   - Backend API: http://localhost:8000"
	@echo "   - API Docs: http://localhost:8000/docs"

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker compose down
	@echo "✅ Containers stopped!"

docker-logs:
	@echo "📋 Viewing Docker logs (Ctrl+C to exit)..."
	docker compose logs -f

docker-restart:
	docker compose restart

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage


.PHONY: help install install-backend install-frontend run-backend run-frontend run docker-build docker-up docker-down docker-logs clean

help:
	@echo "Available commands:"
	@echo "  make install         - Install all dependencies"
	@echo "  make install-backend - Install backend dependencies"
	@echo "  make install-frontend- Install frontend dependencies"
	@echo "  make run-backend     - Run backend API locally"
	@echo "  make run-frontend    - Run frontend UI locally"
	@echo "  make run             - Run both services locally (in background)"
	@echo "  make build-frontend  - Build frontend for production"
	@echo "  make docker-build    - Build Docker images"
	@echo "  make docker-up       - Start Docker containers"
	@echo "  make docker-down     - Stop Docker containers"
	@echo "  make docker-logs     - View Docker logs"
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

build-frontend:
	cd frontend && npm run build

run:
	@echo "Starting backend API..."
	cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
	@echo "Starting frontend UI..."
	cd frontend && npm run dev

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage


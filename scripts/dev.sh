#!/bin/bash
set -e

echo "🚀 Starting Cinefilm development environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker/OrbStack first."
  exit 1
fi

# Check for required env files
if [ ! -f "backend/.env" ]; then
  echo "⚠️  backend/.env not found. Copying from env.example..."
  cp backend/env.example backend/.env
  echo "⚠️  Please update backend/.env with your Firebase credentials"
fi

if [ ! -f "web-app/.env.local" ]; then
  echo "⚠️  web-app/.env.local not found. Copying from env.example..."
  cp web-app/env.example web-app/.env.local
  echo "⚠️  Please update web-app/.env.local with your Firebase config"
fi

# Start services
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service health
echo ""
echo "🔍 Service status:"
docker-compose ps

echo ""
echo "✅ Development environment ready!"
echo ""

# Wait a bit more for services to fully start
sleep 3

# Check if services are healthy
echo "🔍 Checking service health..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
  echo "  ✅ Backend is healthy"
else
  echo "  ⚠️  Backend not ready yet (check logs: docker-compose logs backend-api)"
fi

echo ""
echo "🌐 Access points:"
echo "  • Frontend:    http://localhost:3000"
echo "  • Backend API: http://localhost:8000"
echo "  • API Docs:    http://localhost:8000/docs"
echo "  • PostgreSQL:  localhost:5432"
echo "  • Redis:       localhost:6379"
echo "  • n8n:         http://localhost:5678 (admin/changeme)"
echo ""

# Open browser tabs (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "🌐 Opening browser tabs..."
  sleep 2
  open http://localhost:3000 2>/dev/null || true
  open http://localhost:8000/docs 2>/dev/null || true
fi

echo "📝 Useful commands:"
echo "  View logs:        docker-compose logs -f [service-name]"
echo "  View all logs:    docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart service: docker-compose restart [service-name]"
echo "  Rebuild:         docker-compose build --no-cache [service-name]"
echo ""


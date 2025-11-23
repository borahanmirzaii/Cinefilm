#!/bin/bash
set -e

echo "🚀 Starting Cinefilm development environment with OrbStack..."

# Start OrbStack if not running
if ! orb status &>/dev/null; then
  echo "⚠️ OrbStack not running. Starting..."
  open -a OrbStack
  sleep 5
fi

# Start Docker Compose
cd infra/docker
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Show access URLs
echo ""
echo "✅ Development environment ready!"
echo ""
echo "🌐 Access points:"
echo " • Backend API: http://localhost:8000"
echo " • API Docs: http://localhost:8000/docs"
echo " • PostgreSQL: localhost:5432"
echo " • Redis: localhost:6379"
echo " • n8n: http://localhost:5678 (admin/changeme)"
echo ""
echo "📝 Next steps:"
echo " 1. cd ../../web-app && pnpm dev"
echo " 2. Open http://localhost:3000"
echo ""


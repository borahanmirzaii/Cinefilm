#!/bin/bash
set -e

echo "🚀 Cinefilm Platform Preflight Setup"
echo "======================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check uv
if command -v uv &> /dev/null; then
    echo "✅ uv installed: $(uv --version)"
else
    echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check pnpm
if command -v pnpm &> /dev/null; then
    echo "✅ pnpm installed: $(pnpm --version)"
else
    echo "❌ pnpm not found. Install with: brew install pnpm"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installed: $NODE_VERSION"
    if [[ ! "$NODE_VERSION" =~ v22 ]]; then
        echo "⚠️ Warning: Node.js 22 recommended. Current: $NODE_VERSION"
    fi
else
    echo "❌ Node.js not found"
    exit 1
fi

# Check gcloud
if command -v gcloud &> /dev/null; then
    echo "✅ gcloud installed: $(gcloud --version | head -n1)"
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "not set")
    echo "   Current project: $CURRENT_PROJECT"
else
    echo "❌ gcloud not found"
    exit 1
fi

# Check firebase
if command -v firebase &> /dev/null; then
    echo "✅ Firebase CLI installed: $(firebase --version)"
else
    echo "❌ Firebase CLI not found. Install with: npm install -g firebase-tools"
    exit 1
fi

echo ""
echo "✅ All prerequisites met!"
echo ""
echo "📝 Next steps:"
echo "  1. Review and update .env files in backend/ and frontend/"
echo "  2. Run: ./scripts/setup/orbstack-start.sh"
echo "  3. Install backend dependencies: cd backend && uv sync"
echo "  4. Install frontend dependencies: cd frontend && pnpm install"
echo ""


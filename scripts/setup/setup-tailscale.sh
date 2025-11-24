#!/bin/bash
# Setup Tailscale with UAE Mac as exit node
# This allows downloading Firebase emulators without IP blocking

set -e

echo "🔧 Tailscale Setup Script"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Tailscale is installed
if ! command -v tailscale &> /dev/null; then
    echo -e "${YELLOW}⚠️  Tailscale not installed${NC}"
    echo "Installing Tailscale..."
    brew install tailscale
fi

# Check if Tailscale is running
if ! tailscale status > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Tailscale not running${NC}"
    echo "Starting Tailscale..."
    sudo tailscale up
fi

# Show current status
echo ""
echo "📊 Current Tailscale Status:"
echo "=============================="
tailscale status
echo ""

# Show current IP
CURRENT_IP=$(curl -s ifconfig.me)
echo "Current Public IP: $CURRENT_IP"
echo ""

# Check for exit nodes
echo "🔍 Looking for available exit nodes..."
EXIT_NODES=$(tailscale status | grep -E "exit node|offers exit node" || echo "")

if [ -z "$EXIT_NODES" ]; then
    echo -e "${YELLOW}⚠️  No exit nodes found${NC}"
    echo ""
    echo "To set up UAE Mac as exit node:"
    echo ""
    echo "1. On UAE Mac, run:"
    echo "   sudo tailscale up --advertise-exit-node"
    echo ""
    echo "2. Get the node name from:"
    echo "   tailscale status"
    echo ""
    echo "3. On this Mac, run:"
    echo "   sudo tailscale set --exit-node=<UAE-MAC-NODE-NAME>"
    echo ""
    read -p "Press enter when UAE Mac is configured as exit node..."
else
    echo -e "${GREEN}Available exit nodes:${NC}"
    echo "$EXIT_NODES"
    echo ""
    
    # Try to find UAE Mac (look for common patterns)
    UAE_NODE=$(echo "$EXIT_NODES" | grep -i "uae\|dubai\|mac" | head -1 | awk '{print $1}' || echo "")
    
    if [ -n "$UAE_NODE" ]; then
        echo -e "${BLUE}Found potential UAE Mac node: $UAE_NODE${NC}"
        read -p "Use this as exit node? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Setting exit node..."
            sudo tailscale set --exit-node="$UAE_NODE"
        fi
    else
        echo "Please select an exit node:"
        echo "$EXIT_NODES" | awk '{print $1}' | nl
        read -p "Enter node number: " NODE_NUM
        SELECTED_NODE=$(echo "$EXIT_NODES" | awk '{print $1}' | sed -n "${NODE_NUM}p")
        if [ -n "$SELECTED_NODE" ]; then
            echo "Setting exit node to: $SELECTED_NODE"
            sudo tailscale set --exit-node="$SELECTED_NODE"
        fi
    fi
fi

# Verify exit node
echo ""
echo "🔍 Verifying exit node..."
sleep 2
NEW_IP=$(curl -s ifconfig.me)
echo "New Public IP: $NEW_IP"

if [ "$CURRENT_IP" != "$NEW_IP" ]; then
    echo -e "${GREEN}✅ Exit node active! IP changed from $CURRENT_IP to $NEW_IP${NC}"
else
    echo -e "${YELLOW}⚠️  IP unchanged. Exit node may not be active${NC}"
    echo "Check: tailscale status"
fi

# Test Google Cloud Storage access
echo ""
echo "🧪 Testing Google Cloud Storage access..."
if curl -s -I "https://storage.googleapis.com" | grep -q "200\|403"; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://storage.googleapis.com")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "403" ]; then
        echo -e "${GREEN}✅ Can reach Google Cloud Storage (HTTP $HTTP_CODE)${NC}"
    else
        echo -e "${YELLOW}⚠️  Unexpected response: HTTP $HTTP_CODE${NC}"
    fi
else
    echo -e "${RED}❌ Cannot reach Google Cloud Storage${NC}"
fi

echo ""
echo "✅ Tailscale setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/setup/download-emulators.sh"
echo "2. Start Docker: docker-compose up -d"


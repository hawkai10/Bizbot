#!/bin/bash

echo "🚀 Restarting Docker services to load MCP servers..."
echo ""

# Navigate to the docker compose directory
cd deployment/docker_compose

# Restart the services
echo "📦 Restarting Docker Compose services..."
docker compose -f docker-compose.dev.yml restart

echo ""
echo "⏳ Waiting for services to start up..."
sleep 10

echo ""
echo "✅ Services restarted! Your MCP servers should now be loaded automatically."
echo ""
echo "🌐 View your MCP servers at:"
echo "   • Admin Actions: http://localhost/admin/actions"
echo "   • Assistant Editor: http://localhost/admin/assistants"
echo "   • Chat Interface: http://localhost/chat"
echo ""
echo "📋 To check if MCP servers loaded successfully, you can:"
echo "   1. Visit http://localhost/admin/actions"
echo "   2. Look for your MCP servers in the table"
echo "   3. Check the Docker logs: docker compose -f docker-compose.dev.yml logs api_server"
echo ""
echo "🔧 To add more MCP servers:"
echo "   1. Edit Bizbot/backend/mcp_servers_config.json"
echo "   2. Run this script again: ./restart_and_view_mcp_servers.sh"

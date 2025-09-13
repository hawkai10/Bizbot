# MCP Servers Configuration

This system allows you to easily add MCP servers by simply editing a configuration file, similar to how Claude Desktop works.

## Quick Start

### 1. Add MCP Servers to Configuration

Edit `Bizbot/backend/mcp_servers_config.json` to add your MCP servers:

```json
{
  "mcpServers": {
    "Tally Prime": {
      "display_name": "Tally Prime MCP Server",
      "description": "MCP Server for Tally Prime ERP data integration",
      "server_url": "http://localhost:9001",
      "auth_type": "NONE",
      "auth_performer": "ADMIN",
      "default_headers": {},
      "category": "ERP",
      "icon_url": "https://raw.githubusercontent.com/dhananjay1405/tally-mcp-server/main/docs/tally-icon.png",
      "documentation_url": "https://github.com/dhananjay1405/tally-mcp-server",
      "is_active": true,
      "ssh_tunnel": {
        "enabled": false,
        "host": "",
        "port": 22,
        "username": "",
        "local_port": 9001,
        "remote_port": 9001
      }
    }
  }
}
```

### 2. Load Servers into Database

Run the configuration loader:

```bash
# From the backend directory
python load_mcp_servers_from_config.py
```

Or through Docker:

```bash
docker compose -f deployment/docker_compose/docker-compose.dev.yml run --rm api_server python load_mcp_servers_from_config.py
```

### 3. SSH Tunnels (Optional)

If your MCP server is running on a remote machine, you can set up SSH tunnels:

```json
"ssh_tunnel": {
  "enabled": true,
  "host": "your-remote-server.com",
  "port": 22,
  "username": "your-username",
  "local_port": 9001,
  "remote_port": 9001
}
```

Then start the tunnel:

```bash
# Start all tunnels
python ssh_tunnel_helper.py start

# Start specific tunnel
python ssh_tunnel_helper.py start "Tally Prime"

# List active tunnels
python ssh_tunnel_helper.py list

# Stop all tunnels
python ssh_tunnel_helper.py stop
```

## Configuration Options

### Server Configuration

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `display_name` | string | Human-readable name | Yes |
| `description` | string | Server description | Yes |
| `server_url` | string | MCP server URL | Yes |
| `auth_type` | string | `NONE`, `API_TOKEN`, `OAUTH` | Yes |
| `auth_performer` | string | `ADMIN`, `PER_USER` | Yes |
| `default_headers` | object | Default HTTP headers | No |
| `category` | string | Server category | Yes |
| `icon_url` | string | Icon URL | No |
| `documentation_url` | string | Documentation URL | No |
| `is_active` | boolean | Whether server is active | Yes |
| `ssh_tunnel` | object | SSH tunnel configuration | No |

### SSH Tunnel Configuration

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `enabled` | boolean | Enable SSH tunnel | Yes |
| `host` | string | Remote server hostname/IP | Yes |
| `port` | number | SSH port (default: 22) | No |
| `username` | string | SSH username | Yes |
| `local_port` | number | Local port to bind to | Yes |
| `remote_port` | number | Remote port to forward to | Yes |

## Examples

### Tally Prime (Local)
```json
"Tally Prime": {
  "display_name": "Tally Prime MCP Server",
  "description": "MCP Server for Tally Prime ERP data integration",
  "server_url": "http://localhost:9001",
  "auth_type": "NONE",
  "auth_performer": "ADMIN",
  "category": "ERP",
  "is_active": true
}
```

### GitHub (Remote with SSH)
```json
"GitHub": {
  "display_name": "GitHub MCP Server",
  "description": "MCP Server for GitHub integration",
  "server_url": "http://localhost:3001",
  "auth_type": "API_TOKEN",
  "auth_performer": "PER_USER",
  "category": "Development",
  "is_active": true,
  "ssh_tunnel": {
    "enabled": true,
    "host": "dev-server.company.com",
    "username": "developer",
    "local_port": 3001,
    "remote_port": 3001
  }
}
```

### Slack (OAuth)
```json
"Slack": {
  "display_name": "Slack MCP Server",
  "description": "MCP Server for Slack integration",
  "server_url": "http://localhost:3002",
  "auth_type": "OAUTH",
  "auth_performer": "PER_USER",
  "category": "Communication",
  "is_active": true
}
```

## Management Commands

### Load Configuration
```bash
python load_mcp_servers_from_config.py
```

### SSH Tunnel Management
```bash
# Start all tunnels
python ssh_tunnel_helper.py start

# Start specific tunnel
python ssh_tunnel_helper.py start "Tally Prime"

# List active tunnels
python ssh_tunnel_helper.py list

# Stop specific tunnel
python ssh_tunnel_helper.py stop "Tally Prime"

# Stop all tunnels
python ssh_tunnel_helper.py stop
```

## Troubleshooting

### Port Conflicts
If you get port conflicts, check your Docker Compose configuration and change the port in the MCP server configuration.

### SSH Tunnel Issues
- Ensure SSH key authentication is set up
- Check that the remote server allows port forwarding
- Verify the remote MCP server is running on the specified port

### Database Issues
- Make sure the database is running
- Check that the MCP server tables exist (run migrations if needed)
- Verify database connection settings

## Adding New MCP Servers

1. **Add the server configuration** to `mcp_servers_config.json`
2. **Restart your Docker services** - MCP servers are now loaded automatically on startup!
3. If using SSH tunnels, configure and start them
4. **View your servers** in the Onyx admin interface

## Where to View Your MCP Servers

### 1. **Admin Actions Page** (`/admin/actions`)
- **URL**: `http://localhost/admin/actions` (or your domain)
- **What you'll see**: A table showing all MCP servers with their names, descriptions, and server URLs
- **Actions**: Edit, delete, and manage your MCP servers

### 2. **Assistant Editor** (`/admin/assistants`)
- **URL**: `http://localhost/admin/assistants` (or your domain)
- **What you'll see**: MCP servers listed in the tools section when creating/editing assistants
- **Actions**: Add MCP server tools to your assistants

### 3. **Chat Interface** (when using assistants)
- **URL**: `http://localhost/chat` (or your domain)
- **What you'll see**: MCP server tools available in the action toggle panel
- **Actions**: Use MCP server tools during conversations

## Automatic Loading

**No more manual scripts!** MCP servers are now loaded automatically when the backend starts up. Just:

1. Edit `mcp_servers_config.json`
2. Restart Docker services: `docker compose restart`
3. Your MCP servers will be available immediately!

This system makes it as easy as editing a JSON file to add new MCP servers, just like Claude Desktop!

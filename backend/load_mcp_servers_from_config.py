#!/usr/bin/env python3
"""
Script to load MCP servers from configuration file into the database
Run this from the backend directory: python load_mcp_servers_from_config.py
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from onyx.db.session import get_db
from onyx.db.mcp import create_mcp_server__no_commit, get_mcp_server_by_name
from onyx.db.models import MCPAuthenticationType, MCPAuthenticationPerformer

def load_mcp_servers_from_config():
    """Load MCP servers from configuration file into the database"""
    config_file = "mcp_servers_config.json"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found!")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    db = next(get_db())
    
    try:
        servers_added = 0
        servers_updated = 0
        servers_skipped = 0
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            try:
                # Check if server already exists
                existing_server = get_mcp_server_by_name(db, server_name)
                
                if existing_server:
                    print(f"⚠️  Server '{server_name}' already exists. Skipping...")
                    servers_skipped += 1
                    continue
                
                # Map auth_type string to enum
                auth_type_map = {
                    "NONE": MCPAuthenticationType.NONE,
                    "API_TOKEN": MCPAuthenticationType.API_TOKEN,
                    "OAUTH": MCPAuthenticationType.OAUTH
                }
                
                # Map auth_performer string to enum
                auth_performer_map = {
                    "ADMIN": MCPAuthenticationPerformer.ADMIN,
                    "PER_USER": MCPAuthenticationPerformer.PER_USER
                }
                
                # Create the server using the correct function signature
                server = create_mcp_server__no_commit(
                    owner_email="",  # Empty for auto-loaded servers
                    name=server_name,
                    description=server_config.get("description", ""),
                    server_url=server_config.get("server_url", ""),
                    auth_type=auth_type_map.get(server_config.get("auth_type", "NONE"), MCPAuthenticationType.NONE),
                    db_session=db,
                    admin_connection_config_id=None
                )
                servers_added += 1
                
                print(f"✅ Added server: {server.name}")
                print(f"   URL: {server.server_url}")
                print(f"   Auth: {server.auth_type.value}")
                
                # Handle SSH tunnel configuration if present
                ssh_config = server_config.get("ssh_tunnel", {})
                if ssh_config.get("enabled", False):
                    print(f"   SSH Tunnel: {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}")
                    print(f"   Port mapping: {ssh_config['local_port']} -> {ssh_config['remote_port']}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error processing server '{server_name}': {str(e)}")
                continue
        
        db.commit()
        
        print("=" * 50)
        print(f"📊 Summary:")
        print(f"   Servers added: {servers_added}")
        print(f"   Servers updated: {servers_updated}")
        print(f"   Servers skipped: {servers_skipped}")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error loading MCP servers: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Loading MCP servers from configuration file...")
    load_mcp_servers_from_config()
    print("Done!")

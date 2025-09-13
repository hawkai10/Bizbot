"""
MCP Servers seeding functionality
Automatically loads MCP servers from configuration file on startup
"""

import json
import os
from typing import Dict, Any

from sqlalchemy.orm import Session

from onyx.db.mcp import create_mcp_server__no_commit, get_mcp_server_by_name
from onyx.db.models import MCPAuthenticationType, MCPAuthenticationPerformer
from onyx.utils.logger import setup_logger

logger = setup_logger()

def load_mcp_servers_from_config(db_session: Session) -> None:
    """
    Load MCP servers from configuration file into the database
    This function is called automatically during application startup
    """
    # Get the backend directory (where the config file is located)
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_file = os.path.join(backend_dir, "mcp_servers_config.json")
    
    if not os.path.exists(config_file):
        logger.debug(f"MCP servers configuration file not found at {config_file}")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        servers_added = 0
        servers_skipped = 0
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            try:
                # Check if server already exists
                existing_server = get_mcp_server_by_name(db_session, server_name)
                
                if existing_server:
                    logger.debug(f"MCP server '{server_name}' already exists. Skipping...")
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
                    db_session=db_session,
                    admin_connection_config_id=None
                )
                servers_added += 1
                
                logger.info(f"✅ Auto-loaded MCP server: {server.name}")
                logger.debug(f"   URL: {server.server_url}")
                logger.debug(f"   Auth: {server.auth_type.value}")
                
            except Exception as e:
                logger.error(f"❌ Error loading MCP server '{server_name}': {str(e)}")
                continue
        
        if servers_added > 0 or servers_skipped > 0:
            db_session.commit()
            logger.notice(f"📊 MCP Servers auto-loading complete: {servers_added} added, {servers_skipped} skipped")
        
    except Exception as e:
        logger.error(f"❌ Error loading MCP servers from configuration: {str(e)}")
        db_session.rollback()

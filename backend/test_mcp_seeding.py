#!/usr/bin/env python3
"""
Test script to validate MCP server seeding functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from onyx.db.session import get_db
from onyx.seeding.mcp_servers import load_mcp_servers_from_config

def test_mcp_seeding():
    """Test the MCP server seeding functionality"""
    print("🧪 Testing MCP server seeding...")
    
    try:
        # Get database session
        db = next(get_db())
        
        # Test the seeding function
        load_mcp_servers_from_config(db)
        
        print("✅ MCP server seeding test completed successfully!")
        
    except Exception as e:
        print(f"❌ MCP server seeding test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'db' in locals():
            db.close()
    
    return True

if __name__ == "__main__":
    success = test_mcp_seeding()
    sys.exit(0 if success else 1)

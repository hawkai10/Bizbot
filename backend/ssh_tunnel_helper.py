#!/usr/bin/env python3
"""
SSH Tunnel helper for MCP servers
This script helps establish SSH tunnels for MCP servers that need remote access
"""

import subprocess
import json
import os
import signal
import sys
import time
from typing import Dict, List

class SSHTunnelManager:
    def __init__(self, config_file: str = "mcp_servers_config.json"):
        self.config_file = config_file
        self.active_tunnels: Dict[str, subprocess.Popen] = {}
        
    def load_config(self) -> Dict:
        """Load MCP servers configuration"""
        if not os.path.exists(self.config_file):
            print(f"❌ Configuration file {self.config_file} not found!")
            return {}
            
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def start_tunnel(self, server_name: str, ssh_config: Dict) -> bool:
        """Start SSH tunnel for a specific server"""
        try:
            # Build SSH command
            ssh_cmd = [
                "ssh",
                "-N",  # Don't execute remote command
                "-L", f"{ssh_config['local_port']}:localhost:{ssh_config['remote_port']}",  # Port forwarding
                "-o", "StrictHostKeyChecking=no",  # Skip host key verification
                "-o", "UserKnownHostsFile=/dev/null",  # Don't save host keys
                f"{ssh_config['username']}@{ssh_config['host']}",
                "-p", str(ssh_config['port'])
            ]
            
            print(f"🔗 Starting SSH tunnel for {server_name}...")
            print(f"   Command: {' '.join(ssh_cmd)}")
            
            # Start the tunnel process
            process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.active_tunnels[server_name] = process
            
            # Give it a moment to establish
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ SSH tunnel for {server_name} started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Failed to start SSH tunnel for {server_name}")
                print(f"   Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting SSH tunnel for {server_name}: {str(e)}")
            return False
    
    def stop_tunnel(self, server_name: str) -> bool:
        """Stop SSH tunnel for a specific server"""
        if server_name in self.active_tunnels:
            try:
                process = self.active_tunnels[server_name]
                process.terminate()
                process.wait(timeout=5)
                del self.active_tunnels[server_name]
                print(f"🛑 Stopped SSH tunnel for {server_name}")
                return True
            except Exception as e:
                print(f"❌ Error stopping SSH tunnel for {server_name}: {str(e)}")
                return False
        else:
            print(f"⚠️  No active tunnel found for {server_name}")
            return False
    
    def start_all_tunnels(self) -> int:
        """Start SSH tunnels for all servers that have them enabled"""
        config = self.load_config()
        started_count = 0
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            ssh_config = server_config.get("ssh_tunnel", {})
            if ssh_config.get("enabled", False):
                if self.start_tunnel(server_name, ssh_config):
                    started_count += 1
        
        return started_count
    
    def stop_all_tunnels(self) -> int:
        """Stop all active SSH tunnels"""
        stopped_count = 0
        for server_name in list(self.active_tunnels.keys()):
            if self.stop_tunnel(server_name):
                stopped_count += 1
        return stopped_count
    
    def list_active_tunnels(self):
        """List all active SSH tunnels"""
        if not self.active_tunnels:
            print("📋 No active SSH tunnels")
            return
            
        print("📋 Active SSH tunnels:")
        for server_name, process in self.active_tunnels.items():
            status = "Running" if process.poll() is None else "Stopped"
            print(f"   {server_name}: {status} (PID: {process.pid})")
    
    def cleanup(self):
        """Cleanup all tunnels on exit"""
        print("\n🧹 Cleaning up SSH tunnels...")
        self.stop_all_tunnels()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal. Cleaning up...")
    tunnel_manager.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    tunnel_manager = SSHTunnelManager()
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ssh_tunnel_helper.py start [server_name]  - Start tunnel(s)")
        print("  python ssh_tunnel_helper.py stop [server_name]   - Stop tunnel(s)")
        print("  python ssh_tunnel_helper.py list                 - List active tunnels")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "start":
            if len(sys.argv) > 2:
                # Start specific server tunnel
                server_name = sys.argv[2]
                config = tunnel_manager.load_config()
                server_config = config.get("mcpServers", {}).get(server_name)
                if server_config and server_config.get("ssh_tunnel", {}).get("enabled", False):
                    tunnel_manager.start_tunnel(server_name, server_config["ssh_tunnel"])
                else:
                    print(f"❌ Server '{server_name}' not found or SSH tunnel not enabled")
            else:
                # Start all tunnels
                started = tunnel_manager.start_all_tunnels()
                print(f"🚀 Started {started} SSH tunnels")
                
        elif command == "stop":
            if len(sys.argv) > 2:
                # Stop specific server tunnel
                server_name = sys.argv[2]
                tunnel_manager.stop_tunnel(server_name)
            else:
                # Stop all tunnels
                stopped = tunnel_manager.stop_all_tunnels()
                print(f"🛑 Stopped {stopped} SSH tunnels")
                
        elif command == "list":
            tunnel_manager.list_active_tunnels()
            
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        tunnel_manager.cleanup()

#!/usr/bin/env python3
"""
Warp MCP Server Management Script
This script helps start and manage MCP servers for the AI Vehicle Comparison System
"""

import json
import subprocess
import sys
import time
import structlog
from pathlib import Path
from typing import Dict, List

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class WarpMCPManager:
    """
    Manager for Warp MCP servers
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "mcp-config.json"
        self.running_servers = {}
        self.logger = logger
        
    def load_config(self) -> Dict:
        """Load MCP server configuration"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                self.logger.error(f"Config file not found: {self.config_path}")
                return {}
                
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            self.logger.info("MCP configuration loaded", 
                           servers=list(config.get('mcpServers', {}).keys()))
            return config
            
        except Exception as e:
            self.logger.error("Failed to load MCP configuration", error=str(e))
            return {}
    
    def start_server(self, server_name: str, server_config: Dict) -> bool:
        """Start a single MCP server"""
        try:
            self.logger.info("Starting MCP server", server=server_name)
            
            cmd = [server_config['command']] + server_config.get('args', [])
            env = server_config.get('env', {})
            
            # Merge with current environment
            import os
            full_env = os.environ.copy()
            full_env.update(env)
            
            # Start the server process
            process = subprocess.Popen(
                cmd,
                env=full_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if process.poll() is None:
                self.running_servers[server_name] = process
                self.logger.info("MCP server started successfully", 
                               server=server_name, 
                               pid=process.pid)
                return True
            else:
                stdout, stderr = process.communicate()
                self.logger.error("MCP server failed to start", 
                                server=server_name,
                                stdout=stdout,
                                stderr=stderr)
                return False
                
        except Exception as e:
            self.logger.error("Failed to start MCP server", 
                            server=server_name, 
                            error=str(e))
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """Stop a single MCP server"""
        if server_name not in self.running_servers:
            self.logger.warning("Server not running", server=server_name)
            return False
            
        try:
            process = self.running_servers[server_name]
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.logger.warning("Server didn't stop gracefully, killing", 
                                  server=server_name)
                process.kill()
                process.wait()
            
            del self.running_servers[server_name]
            self.logger.info("MCP server stopped", server=server_name)
            return True
            
        except Exception as e:
            self.logger.error("Failed to stop MCP server", 
                            server=server_name, 
                            error=str(e))
            return False
    
    def start_all_servers(self) -> bool:
        """Start all configured MCP servers"""
        config = self.load_config()
        servers = config.get('mcpServers', {})
        
        if not servers:
            self.logger.warning("No servers configured")
            return False
        
        success_count = 0
        for server_name, server_config in servers.items():
            if self.start_server(server_name, server_config):
                success_count += 1
        
        self.logger.info("MCP servers startup complete", 
                        total_servers=len(servers),
                        successful_starts=success_count)
        
        return success_count > 0
    
    def stop_all_servers(self) -> bool:
        """Stop all running MCP servers"""
        if not self.running_servers:
            self.logger.info("No servers running")
            return True
        
        servers_to_stop = list(self.running_servers.keys())
        success_count = 0
        
        for server_name in servers_to_stop:
            if self.stop_server(server_name):
                success_count += 1
        
        self.logger.info("MCP servers shutdown complete", 
                        total_servers=len(servers_to_stop),
                        successful_stops=success_count)
        
        return success_count == len(servers_to_stop)
    
    def get_server_status(self) -> Dict:
        """Get status of all configured servers"""
        config = self.load_config()
        servers = config.get('mcpServers', {})
        
        status = {}
        for server_name in servers.keys():
            if server_name in self.running_servers:
                process = self.running_servers[server_name]
                if process.poll() is None:
                    status[server_name] = {
                        "running": True,
                        "pid": process.pid
                    }
                else:
                    status[server_name] = {
                        "running": False,
                        "status": "crashed"
                    }
                    # Clean up dead process
                    del self.running_servers[server_name]
            else:
                status[server_name] = {
                    "running": False,
                    "status": "stopped"
                }
        
        return status
    
    def print_status(self):
        """Print server status to console"""
        status = self.get_server_status()
        
        print("\n=== MCP Server Status ===")
        for server_name, server_status in status.items():
            running = server_status["running"]
            status_text = "RUNNING" if running else "STOPPED"
            pid_text = f" (PID: {server_status.get('pid', 'N/A')})" if running else ""
            
            print(f"  {server_name}: {status_text}{pid_text}")
        print()

def main():
    """Main entry point for the script"""
    if len(sys.argv) < 2:
        print("Usage: python start_mcp_servers.py [start|stop|status|restart]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = WarpMCPManager()
    
    if command == "start":
        logger.info("Starting all MCP servers...")
        success = manager.start_all_servers()
        if success:
            manager.print_status()
        else:
            logger.error("Failed to start MCP servers")
            sys.exit(1)
    
    elif command == "stop":
        logger.info("Stopping all MCP servers...")
        manager.stop_all_servers()
        
    elif command == "status":
        manager.print_status()
        
    elif command == "restart":
        logger.info("Restarting all MCP servers...")
        manager.stop_all_servers()
        time.sleep(2)
        success = manager.start_all_servers()
        if success:
            manager.print_status()
        else:
            logger.error("Failed to restart MCP servers")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, status, restart")
        sys.exit(1)

if __name__ == "__main__":
    main()

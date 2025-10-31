#!/bin/bash
set -euo pipefail

echo "Starting Kali MCP services..."

# Start PostgreSQL for Metasploit
service postgresql start || true

# Initialize Metasploit database
if command -v msfdb >/dev/null 2>&1; then
  echo "Initializing Metasploit database..."
  msfdb init || true
fi

echo "Services started successfully"
cd /app

# Keep container running - run MCP server if interactive
if [ -t 0 ]; then
  echo "Running in interactive mode - starting MCP server"
  python3 mcp_server.py --stdio
else
  echo "Kali MCP container ready. Use 'docker exec' to interact."
  tail -f /dev/null
fi

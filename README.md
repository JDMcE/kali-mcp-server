# Kali Linux MCP Server

A lightweight Docker container providing Kali Linux security tools via MCP (Model Context Protocol).

## Project Structure

```
kali_mcp/
├── dockerfile            # Original large version 
├── mcp_server.py        # Main MCP server script
├── start_services.sh    # Container startup script
└── README.md            # This file
```

## Quick Start

### 1. Build the image

```bash
# Using the Dockerfile
docker build -f dockerfile -t kali-mcp .
```

### 2. Run the container

**IMPORTANT**: Security tools like nmap, masscan, hping3, etc. require elevated privileges to function properly. You must run the container with network capabilities:

```bash
# Run in background (stays alive) - RECOMMENDED
docker run -d --name kali-mcp --cap-add=NET_ADMIN --cap-add=NET_RAW -p 4444:4444 kali-mcp

# OR run interactively (for MCP stdio mode)
docker run -it --name kali-mcp --cap-add=NET_ADMIN --cap-add=NET_RAW -p 4444:4444 kali-mcp

# Alternative: Use privileged mode (gives full access - less secure but ensures all tools work)
docker run -d --name kali-mcp --privileged -p 4444:4444 kali-mcp
```

**Capabilities explained:**
- `--cap-add=NET_ADMIN`: Allows network configuration (required for some scanning tools)
- `--cap-add=NET_RAW`: Allows raw socket access (required for nmap, ping, etc.)
- `--privileged`: Grants all capabilities (use if specific capabilities don't work)

### 3. Interact with the container

```bash
# Execute commands
docker exec -it kali-mcp bash

# Check available tools
docker exec kali-mcp nmap --version
```

## Connecting to Claude Desktop

To use this MCP server with Claude Desktop, you need to configure Claude to connect to the Docker container via stdio.

### 1. Locate your Claude Desktop config file

The configuration file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. Add the MCP server configuration

Edit the config file and add the `kali-mcp` server to the `mcpServers` section:

**Option A: Using a running container (Recommended)**

This approach assumes you have a container already running in daemon mode:

**For macOS/Linux:**
```json
{
  "mcpServers": {
    "kali-mcp": {
      "command": "docker",
      "args": ["exec", "-i", "kali-mcp", "python3", "/app/mcp_server.py", "--stdio"]
    }
  }
}
```

**For Windows:**
```json
{
  "mcpServers": {
    "kali-mcp": {
      "command": "docker",
      "args": ["exec", "-i", "kali-mcp", "sh", "-c", "python3 /app/mcp_server.py --stdio"]
    }
  }
}
```

> **Windows Note**: The `sh -c` wrapper is required to prevent Windows path conversion issues that would otherwise cause connection failures.

First, ensure the container is running with proper capabilities:
```bash
docker run -d --name kali-mcp --cap-add=NET_ADMIN --cap-add=NET_RAW -p 4444:4444 kali-mcp
```

**Option B: Start container on-demand**

This starts a new container each time Claude Desktop connects: 

**For macOS/Linux:**
```json
{
  "mcpServers": {
    "kali-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "kali-mcp", "python3", "/app/mcp_server.py", "--stdio"]
    }
  }
}
```

**For Windows:**
```json
{
  "mcpServers": {
    "kali-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "kali-mcp", "sh", "-c", "python3 /app/mcp_server.py --stdio"]
    }
  }
}
```

Note: This approach takes longer to start (container initialization time) but doesn't require a persistent container.

### 3. Restart Claude Desktop

After updating the configuration:
1. Completely quit Claude Desktop (not just close the window)
2. Restart the application
3. The MCP server should automatically connect

### 4. Verify the connection

In Claude Desktop, you should see the Kali MCP server listed in the available tools. You can test it by asking Claude to use a security tool, for example:

```
Can you scan localhost with nmap?
```

### Troubleshooting Connection Issues

**Windows: "Server disconnected" error:**
- **SOLUTION**: Make sure you're using the Windows-specific configuration with `sh -c` wrapper (see Option A above)
- This error occurs because Windows converts Unix paths like `/app/...` incorrectly
- Test manually with: `echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | docker exec -i kali-mcp sh -c "python3 /app/mcp_server.py --stdio"`
- If you see a valid JSON response, the server is working - just update your config to use `sh -c`

**Claude Desktop shows connection error:**
- Verify the container is running: `docker ps` (look for kali-mcp)
- Check container logs: `docker logs kali-mcp`
- Test the MCP server manually:
  ```bash
  # On Windows (use this):
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | docker exec -i kali-mcp sh -c "python3 /app/mcp_server.py --stdio"

  # On macOS/Linux:
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | docker exec -i kali-mcp python3 /app/mcp_server.py --stdio
  ```

**Tools not appearing:**
- Make sure you're using the `--stdio` flag in the command
- Verify the MCP server can discover tools:
  ```bash
  docker exec kali-mcp python3 /app/mcp_server.py
  ```

**"Operation not permitted" errors when running tools (nmap, masscan, etc.):**
- **SOLUTION**: Your container is missing required network capabilities
- Stop and remove the existing container: `docker stop kali-mcp && docker rm kali-mcp`
- Restart with capabilities: `docker run -d --name kali-mcp --cap-add=NET_ADMIN --cap-add=NET_RAW -p 4444:4444 kali-mcp`
- Test nmap: `docker exec kali-mcp nmap -sn 127.0.0.1`
- If still failing, try privileged mode: `docker run -d --name kali-mcp --privileged -p 4444:4444 kali-mcp`

**Container keeps exiting:**
- Use Option A (pre-running container) instead of Option B
- Ensure you're using `-i` flag for interactive stdin

**Permission issues (Linux):**
- You may need to add your user to the docker group: `sudo usermod -aG docker $USER`
- Or run Claude Desktop with appropriate permissions

## Development Workflow

### Editing the MCP Server

1. Edit `mcp_server.py` locally with your favorite IDE
2. Test locally (if you have Python): `python3 mcp_server.py`
3. Rebuild only when ready:
   ```bash
   docker build -f dockerfile -t kali-mcp .
   ```

### Adding New Tools

Edit `mcp_server.py` and add to the `tool_categories` dict (around line 24):

```python
'my_new_tool': {'cmd': 'tool-binary', 'params': ['target', 'options']},
```

### Modifying Startup Behavior

Edit `start_services.sh` to change what happens when the container starts.

## File Descriptions

### `mcp_server.py`
- Main MCP server implementation
- Discovers available Kali tools
- Handles tool execution via MCP protocol
- Can be tested standalone

### `start_services.sh`
- Starts PostgreSQL (for Metasploit)
- Initializes Metasploit database
- Runs MCP server in stdio mode (if interactive)
- Keeps container alive (if non-interactive)

### `Dockerfile`
- Optimized build 
- Single large RUN command = fewer layers
- Headless tools only (no GUI)
- Uses COPY for scripts (better than heredocs)

## Available Tools

The MCP server automatically discovers installed tools including:

- **Network:** nmap, masscan, hping3, netdiscover
- **Web:** nikto, sqlmap, gobuster, wfuzz, ffuf, wpscan
- **Password:** john, hashcat, hydra, medusa
- **Info Gathering:** theharvester, sublist3r, dnsenum
- **Forensics:** binwalk, foremost, volatility, strings
- **Reverse Engineering:** radare2, gdb, objdump
- **Exploitation:** metasploit-framework, msfvenom


## Troubleshooting

**Container exits immediately?**
- Use `-it` flag for interactive mode
- Check logs: `docker logs kali-mcp`

**Need to rebuild after script changes?**
```bash
docker build --no-cache -f dockerfile -t kali-mcp .
```

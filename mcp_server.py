#!/usr/bin/env python3
import asyncio
import json
import subprocess
import logging
import sys
import os
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveKaliServer:
    def __init__(self):
        self.tools = self.discover_tools()

    def discover_tools(self):
        """Automatically discover all available tools"""
        tools = {}

        tool_categories = {
            # Network Discovery
            'nmap': {'cmd': 'nmap', 'params': ['target', 'options']},
            'masscan': {'cmd': 'masscan', 'params': ['target', 'ports']},
            'hping3': {'cmd': 'hping3', 'params': ['target', 'options']},
            'netdiscover': {'cmd': 'netdiscover', 'params': ['interface']},
            'arp_scan': {'cmd': 'arp-scan', 'params': ['target']},

            # Web Application Testing
            'nikto': {'cmd': 'nikto', 'params': ['target']},
            'dirb': {'cmd': 'dirb', 'params': ['url', 'wordlist']},
            'gobuster': {'cmd': 'gobuster', 'params': ['mode', 'url', 'wordlist']},
            'wpscan': {'cmd': 'wpscan', 'params': ['url']},
            'whatweb': {'cmd': 'whatweb', 'params': ['target']},
            'wafw00f': {'cmd': 'wafw00f', 'params': ['url']},
            'sqlmap': {'cmd': 'sqlmap', 'params': ['url', 'options']},
            'wfuzz': {'cmd': 'wfuzz', 'params': ['url', 'wordlist']},
            'ffuf': {'cmd': 'ffuf', 'params': ['url', 'wordlist']},

            # Password Attacks
            'john': {'cmd': 'john', 'params': ['hash_file', 'options']},
            'hashcat': {'cmd': 'hashcat', 'params': ['hash', 'wordlist', 'mode']},
            'hydra': {'cmd': 'hydra', 'params': ['target', 'service', 'username', 'password_list']},
            'medusa': {'cmd': 'medusa', 'params': ['target', 'service', 'username', 'password_list']},
            'ncrack': {'cmd': 'ncrack', 'params': ['target', 'service']},
            'cewl': {'cmd': 'cewl', 'params': ['url']},
            'crunch': {'cmd': 'crunch', 'params': ['min', 'max', 'charset']},

            # Information Gathering
            'theharvester': {'cmd': 'theharvester', 'params': ['domain', 'source']},
            'recon_ng': {'cmd': 'recon-ng', 'params': ['domain']},
            'dmitry': {'cmd': 'dmitry', 'params': ['target']},
            'enum4linux': {'cmd': 'enum4linux', 'params': ['target']},
            'smbclient': {'cmd': 'smbclient', 'params': ['target']},
            'dnsrecon': {'cmd': 'dnsrecon', 'params': ['domain']},
            'dnsenum': {'cmd': 'dnsenum', 'params': ['domain']},
            'fierce': {'cmd': 'fierce', 'params': ['domain']},
            'sublist3r': {'cmd': 'sublist3r', 'params': ['domain']},

            # Forensics
            'binwalk': {'cmd': 'binwalk', 'params': ['file']},
            'foremost': {'cmd': 'foremost', 'params': ['file']},
            'volatility': {'cmd': 'volatility', 'params': ['memory_dump', 'profile']},
            'strings': {'cmd': 'strings', 'params': ['file']},

            # Steganography
            'steghide': {'cmd': 'steghide', 'params': ['file', 'passphrase']},
            'exiftool': {'cmd': 'exiftool', 'params': ['file']},

            # Reverse Engineering
            'radare2': {'cmd': 'radare2', 'params': ['file']},
            'gdb': {'cmd': 'gdb', 'params': ['binary']},
            'objdump': {'cmd': 'objdump', 'params': ['file', 'options']},
            'ltrace': {'cmd': 'ltrace', 'params': ['binary']},
            'strace': {'cmd': 'strace', 'params': ['binary']},

            # Metasploit
            'msfconsole': {'cmd': 'msfconsole', 'params': ['resource_file']},
            'msfvenom': {'cmd': 'msfvenom', 'params': ['payload', 'lhost', 'lport', 'format']},

            # Network Analysis
            'tcpdump': {'cmd': 'tcpdump', 'params': ['interface', 'filter']},
            'tshark': {'cmd': 'tshark', 'params': ['interface', 'filter']},
            'ettercap': {'cmd': 'ettercap', 'params': ['interface', 'targets']},

            # Custom execution
            'execute_command': {'cmd': 'custom', 'params': ['command']},
        }

        # Check which tools are actually installed
        for tool_name, tool_info in tool_categories.items():
            if tool_info['cmd'] != 'custom':
                if subprocess.run(['which', tool_info['cmd']], capture_output=True).returncode == 0:
                    tools[tool_name] = {
                        'func': self.execute_tool,
                        'cmd': tool_info['cmd'],
                        'params': tool_info['params']
                    }
            else:
                tools[tool_name] = {
                    'func': self.execute_custom_command,
                    'cmd': tool_info['cmd'],
                    'params': tool_info['params']
                }

        return tools

    async def execute_tool(self, **kwargs):
        """Execute any Kali tool with parameters"""
        tool_name = kwargs.get('tool_name', '')
        if tool_name not in self.tools:
            return {'success': False, 'error': 'Tool not found'}

        tool_info = self.tools[tool_name]
        cmd = tool_info['cmd']

        command_parts = [cmd]
        for param in tool_info['params']:
            if param in kwargs and kwargs[param]:
                command_parts.append(str(kwargs[param]))

        command = ' '.join(command_parts)
        return await self.execute_command(command)

    async def execute_custom_command(self, command: str) -> Dict[str, Any]:
        """Execute custom shell command"""
        return await self.execute_command(command)

    async def execute_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute shell command with timeout"""
        try:
            logger.info(f"Executing: {command}")
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return {
                'success': True,
                'stdout': stdout.decode('utf-8', errors='ignore'),
                'stderr': stderr.decode('utf-8', errors='ignore'),
                'return_code': process.returncode
            }
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return {'success': False, 'error': str(e), 'stdout': '', 'stderr': ''}

    def run_stdio(self):
        """Main MCP stdio loop"""
        logger.info(f"Starting Kali MCP server with {len(self.tools)} tools")

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)

                if request.get('method') == 'initialize':
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {
                            'protocolVersion': '2025-06-18',
                            'capabilities': {'tools': {'listChanged': True}},
                            'serverInfo': {'name': 'kali-mcp', 'version': '1.0.0'}
                        }
                    }

                elif request.get('method') == 'notifications/initialized':
                    continue

                elif request.get('method') == 'tools/list':
                    tools_list = []
                    for tool_name, tool_info in self.tools.items():
                        properties = {}
                        required = []

                        for param in tool_info['params']:
                            properties[param] = {
                                'type': 'string',
                                'description': f'{param} parameter for {tool_name}'
                            }
                            if param in ['target', 'url', 'domain', 'file', 'command']:
                                required.append(param)

                        tools_list.append({
                            'name': tool_name,
                            'description': f'Kali Linux tool: {tool_name} ({tool_info["cmd"]})',
                            'inputSchema': {
                                'type': 'object',
                                'properties': properties,
                                'required': required
                            }
                        })

                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {'tools': tools_list}
                    }

                elif request.get('method') == 'tools/call':
                    tool_name = request['params']['name']
                    arguments = request['params'].get('arguments', {})
                    arguments['tool_name'] = tool_name

                    if tool_name in self.tools:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(self.tools[tool_name]['func'](**arguments))
                        finally:
                            loop.close()

                        response = {
                            'jsonrpc': '2.0',
                            'id': request.get('id'),
                            'result': {
                                'content': [{
                                    'type': 'text',
                                    'text': f"Tool: {tool_name}\nCommand: {self.tools[tool_name]['cmd']}\nSuccess: {result.get('success')}\n\nOutput:\n{result.get('stdout', '')[:10000]}\n\nErrors:\n{result.get('stderr', '')[:5000]}"
                                }]
                            }
                        }
                    else:
                        response = {
                            'jsonrpc': '2.0',
                            'id': request.get('id'),
                            'error': {'code': -32601, 'message': f'Tool not found: {tool_name}'}
                        }

                else:
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {'content': [{'type': 'text', 'text': f'Kali MCP Server with {len(self.tools)} tools ready'}]}
                    }

                print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(json.dumps({
                    'jsonrpc': '2.0',
                    'id': 1,
                    'error': {'code': -32603, 'message': str(e)}
                }), flush=True)

if __name__ == "__main__":
    server = ComprehensiveKaliServer()
    if len(sys.argv) > 1 and sys.argv[1] == '--stdio':
        server.run_stdio()
    else:
        print(f"Kali MCP Server with {len(server.tools)} tools available")
        print("Use --stdio flag for MCP mode")

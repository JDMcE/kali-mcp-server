# Optimized Dockerfile - Focus on essential headless tools for MCP
FROM kalilinux/kali-rolling:latest

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Fix Kali repositories
RUN echo "deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb-src http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware" >> /etc/apt/sources.list

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Single large RUN to minimize layers and enable cleanup in same layer
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Core utilities
        apt-transport-https ca-certificates gnupg2 wget curl sudo \
        python3 python3-pip git bash-completion procps \
        dnsutils whois traceroute mtr netcat-openbsd socat ncat \
        tree htop tmux screen vim nano pv \
        # Essential tool categories (headless only)
        kali-tools-top10 \
        kali-tools-information-gathering \
        kali-tools-web \
        kali-tools-passwords \
        kali-tools-exploitation \
        # Network scanning
        nmap masscan hping3 netdiscover arp-scan \
        # Web testing
        nikto dirb gobuster wfuzz ffuf whatweb wafw00f wpscan sqlmap \
        # Password attacks
        john hashcat hydra medusa ncrack cewl crunch \
        # Information gathering
        theharvester recon-ng dmitry enum4linux smbclient \
        dnsrecon dnsenum fierce sublist3r \
        # Network analysis (headless)
        tcpdump tshark ettercap-text-only wireshark-common \
        ssldump sslscan \
        # Metasploit
        metasploit-framework postgresql postgresql-contrib \
        # Reverse engineering (CLI tools)
        radare2 gdb binutils ltrace strace binwalk \
        # Forensics
        foremost yara exiftool \
        # Steganography
        steghide exiftool \
        # Password tools
        responder impacket-scripts crackmapexec \
        # Utilities
        proxychains4 tor macchanger \
        # Programming languages
        python3-dev ruby golang nodejs npm && \
    # Clean up in same layer to reduce size
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Wordlists (only essential ones)
RUN mkdir -p /usr/share/wordlists && \
    cd /usr/share/wordlists && \
    apt-get update && \
    apt-get install -y --no-install-recommends seclists wordlists && \
    wget -q -O rockyou.txt.gz https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt 2>/dev/null || true && \
    gunzip -f rockyou.txt.gz 2>/dev/null || true && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files 
COPY mcp_server.py /app/
COPY start_services.sh /app/

# Make scripts executable
RUN chmod +x /app/mcp_server.py /app/start_services.sh

# Expose ports
EXPOSE 4444

# Set default command
CMD ["/app/start_services.sh"]

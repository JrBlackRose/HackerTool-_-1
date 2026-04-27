#!/usr/bin/env python3
# Kali Penetration Testing Toolkit (KPT)
# Author: ALLENDRAA A/L ANBALAGAN (JrBlackRose)
# Version: 2.0 (Masterpiece Edition)
# License: MIT

import os
import sys
import time
import shutil
import argparse
import subprocess
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    import nmap
    from colorama import Fore, Style, init
except ImportError as e:
    print(f"[-] Missing Python dependency: {e}")
    print("[*] Install required packages: pip install python-nmap requests beautifulsoup4 colorama")
    sys.exit(1)

# Initialize colorama for Windows/Linux compatibility
init(autoreset=True)

def display_banner():
    banner = f"""{Fore.RED}
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠈⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⢀⣠⣤⣤⣤⣤⣄⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠾⣿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⣤⣶⣤⣉⣿⣿⡯⣀⣴⣿⡗⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⡈⠀⠀⠉⣿⣿⣶⡉⠀⠀⣀⡀⠀⠀⠀⢻⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⢸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠉⢉⣽⣿⠿⣿⡿⢻⣯⡍⢁⠄⠀⠀⠀⣸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠐⡀⢉⠉⠀⠠⠀⢉⣉⠀⡜⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠿⠁⠀⠀⠀⠘⣤⣭⣟⠛⠛⣉⣁⡜⠀⠀⠀⠀⠀⠛⠿⣿⣿⣿
⡿⠟⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⡀⠀⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{Style.RESET_ALL}"""
    print(banner)
    print(Fore.GREEN + "\t\tKPT: Kali Penetration Testing Toolkit")
    print(Fore.YELLOW + "\t\tAuthor: ALLENDRAA A/L ANBALAGAN")
    print(Fore.BLUE + "\t\tVersion: 2.0 (Magnum Opus)")
    print("=" * 80)

def check_dependencies(deps: list):
    """Ensure required system binaries are installed."""
    missing = [dep for dep in deps if shutil.which(dep) is None]
    if missing:
        print(Fore.RED + f"[-] Missing system dependencies: {', '.join(missing)}")
        print(Fore.YELLOW + "[*] Please install them using apt/pacman before continuing.")
        sys.exit(1)

def camera_scanner(target_ip: str, output_file: str = None):
    print(Fore.CYAN + f"\n[+] Scanning for cameras on {target_ip}...")
    common_ports = [80, 8080, 554, 37777]
    camera_urls = []
    
    try:
        nm = nmap.PortScanner()
        nm.scan(target_ip, ','.join(str(p) for p in common_ports))
    except nmap.PortScannerError as e:
        print(Fore.RED + f"[-] Nmap Error: {e}")
        return

    for host in nm.all_hosts():
        print(f"\nHost: {host} ({nm[host].hostname()}) - State: {nm[host].state()}")
        for proto in nm[host].all_protocols():
            ports = nm[host][proto].keys()
            for port in sorted(ports):
                state = nm[host][proto][port]['state']
                print(f"Port: {port}\tState: {state}")
                
                if state == 'open':
                    url = f"http://{host}:{port}"
                    try:
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            print(Fore.GREEN + f"[+] Potential interface found: {url}")
                            camera_urls.append(url)
                            if any(kw in response.text.lower() for kw in ["dvr", "camera"]):
                                print(Fore.YELLOW + "[!] Possible DVR/Camera system detected.")
                    except requests.RequestException:
                        pass
                        
    if output_file and camera_urls:
        with open(output_file, 'w') as f:
            f.write('\n'.join(camera_urls) + '\n')
        print(Fore.GREEN + f"\n[+] Results saved to {output_file}")

def wifi_penetrator(interface: str, wordlist: str, target_ssid: str = None):
    check_dependencies(['airmon-ng', 'airodump-ng', 'aireplay-ng', 'aircrack-ng'])
    print(Fore.CYAN + "\n[+] Starting WiFi penetration module...")
    
    if not os.path.isfile(wordlist):
        print(Fore.RED + "[-] Wordlist file not found!")
        return
        
    try:
        print(Fore.YELLOW + "[*] Engaging monitor mode...")
        subprocess.run(['airmon-ng', 'check', 'kill'], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check=True)
        subprocess.run(['iwconfig', interface, 'mode', 'monitor'], check=True)
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True)
        
        if not target_ssid:
            print(Fore.YELLOW + "[*] Scanning for nearby networks (60s)...")
            subprocess.run(['airodump-ng', interface], timeout=60)
            print(Fore.YELLOW + "\n[*] Scan complete. Run again with -t <SSID> to target.")
        else:
            print(Fore.CYAN + f"\n[+] Targeting SSID: {target_ssid}")
            cap_file = f"capture_{target_ssid.replace(' ', '_')}"
            
            print(Fore.YELLOW + "[*] Capturing handshake (Ctrl+C to stop)...")
            dump_proc = subprocess.Popen(['airodump-ng', '--bssid', target_ssid, '-w', cap_file, interface])
            time.sleep(5)
            
            print(Fore.YELLOW + "[*] Sending deauth packets...")
            subprocess.run(['aireplay-ng', '--deauth', '5', '-a', target_ssid, interface])
            
            dump_proc.wait() # Wait for user to stop capture
            
            print(Fore.YELLOW + "[*] Attempting to crack handshake...")
            crack_result = subprocess.run(
                ['aircrack-ng', '-w', wordlist, f'{cap_file}-01.cap'], 
                capture_output=True, text=True
            )
            if "KEY FOUND" in crack_result.stdout:
                print(Fore.GREEN + "[+] Password found! Check aircrack output above.")
            else:
                print(Fore.RED + "[-] Password not found in wordlist.")

    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[-] Subprocess Error: {e}")
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[*] User interrupted. Cleaning up...")
    finally:
        print(Fore.YELLOW + "[*] Restoring network manager...")
        subprocess.run(['airmon-ng', 'stop', interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['systemctl', 'start', 'NetworkManager'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def website_cloner(target_url: str, output_dir: str = "cloned_site"):
    print(Fore.CYAN + f"\n[+] Cloning website: {target_url}")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        response = requests.get(target_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        downloaded = set()
        for tag, attr in {'img': 'src', 'link': 'href', 'script': 'src'}.items():
            for element in soup.find_all(tag):
                resource_url = element.get(attr)
                if not resource_url:
                    continue
                    
                absolute_url = urljoin(target_url, resource_url)
                parsed_url = urlparse(absolute_url)
                
                # Only download assets from the same domain to avoid infinite recursion/errors
                if parsed_url.netloc == urlparse(target_url).netloc and absolute_url not in downloaded:
                    downloaded.add(absolute_url)
                    try:
                        res_data = requests.get(absolute_url, timeout=5)
                        filename = os.path.basename(parsed_url.path) or "index.html"
                        local_path = os.path.join(output_dir, filename)
                        
                        with open(local_path, 'wb') as f:
                            f.write(res_data.content)
                        element[attr] = filename # Point local HTML to local file
                    except requests.RequestException:
                        continue

        with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        print(Fore.GREEN + f"[+] Website cloned successfully to {output_dir}/")
    except Exception as e:
        print(Fore.RED + f"[-] Error cloning website: {e}")

def port_scanner(target_ip: str, ports: str = "1-1000", output_file: str = None):
    print(Fore.CYAN + f"\n[+] Scanning ports {ports} on {target_ip}...")
    try:
        nm = nmap.PortScanner()
        nm.scan(target_ip, ports)
    except nmap.PortScannerError as e:
        print(Fore.RED + f"[-] Nmap Error: {e}")
        return

    open_ports = []
    for host in nm.all_hosts():
        print(f"\nHost: {host} ({nm[host].hostname()}) - State: {nm[host].state()}")
        for proto in nm[host].all_protocols():
            for port in sorted(nm[host][proto].keys()):
                state = nm[host][proto][port]['state']
                service = nm[host][proto][port]['name']
                print(f"Port: {port}\tState: {state}\tService: {service}")
                if state == 'open':
                    open_ports.append((port, proto, service))
                    
    if output_file and open_ports:
        with open(output_file, 'w') as f:
            f.write(f"Port scan results for {target_ip}\n{'='*50}\n")
            for port, proto, service in open_ports:
                f.write(f"Port: {port}/{proto}\tService: {service}\n")
        print(Fore.GREEN + f"\n[+] Results saved to {output_file}")

def main():
    if os.geteuid() != 0:
        print(Fore.RED + "[-] Error: This masterpiece requires root privileges. Run with sudo.")
        sys.exit(1)

    display_banner()
    parser = argparse.ArgumentParser(description="KPT: Kali Penetration Testing Toolkit")
    subparsers = parser.add_subparsers(dest='command', help='Available modules')
    
    cp = subparsers.add_parser('camscan', help='Scan for vulnerable cameras')
    cp.add_argument('target', help='Target IP or IP range')
    cp.add_argument('-o', '--output', help='Output file')
    
    wp = subparsers.add_parser('wifipen', help='WiFi penetration tools')
    wp.add_argument('interface', help='Wireless interface (e.g., wlan0)')
    wp.add_argument('wordlist', help='Path to password wordlist')
    wp.add_argument('-t', '--target', help='Specific SSID to target')
    
    cl = subparsers.add_parser('clone', help='Clone a website')
    cl.add_argument('url', help='URL of website')
    cl.add_argument('-o', '--output', default="cloned_site", help='Output directory')
    
    ps = subparsers.add_parser('portscan', help='Scan open ports')
    ps.add_argument('target', help='Target IP')
    ps.add_argument('-p', '--ports', default="1-1000", help='Port range')
    ps.add_argument('-o', '--output', help='Output file')
    
    args = parser.parse_args()
    
    if args.command == 'camscan': camera_scanner(args.target, args.output)
    elif args.command == 'wifipen': wifi_penetrator(args.interface, args.wordlist, args.target)
    elif args.command == 'clone': website_cloner(args.url, args.output)
    elif args.command == 'portscan': port_scanner(args.target, args.ports, args.output)
    else: parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Operation aborted by user. Exiting cleanly.")
        sys.exit(0)

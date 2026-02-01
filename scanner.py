import nmap
import requests
import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Any

class VulnerabilityScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def scan_website(self, url: str) -> Dict[str, Any]:
        results = {
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'host': '',
            'ip': '',
            'ports': [],
            'http_headers': {},
            'security_headers': {},
            'ssl_info': {},
            'vulnerabilities': [],
            'risk_score': 0
        }

        try:
            parsed = urlparse(url if url.startswith('http') else f'http://{url}')
            host = parsed.netloc or parsed.path
            results['host'] = host

            try:
                results['ip'] = socket.gethostbyname(host)
            except socket.gaierror:
                results['vulnerabilities'].append({
                    'type': 'DNS Resolution',
                    'severity': 'HIGH',
                    'description': 'Unable to resolve hostname',
                    'recommendation': 'Verify the domain name is correct'
                })
                return results

            results['ports'] = self._scan_ports(results['ip'])
            results['http_headers'] = self._check_http_headers(url)
            results['security_headers'] = self._analyze_security_headers(results['http_headers'])

            if '443' in [str(p['port']) for p in results['ports']]:
                results['ssl_info'] = self._check_ssl(host)

            results['vulnerabilities'] = self._identify_vulnerabilities(results)
            results['risk_score'] = self._calculate_risk_score(results['vulnerabilities'])

        except Exception as e:
            results['error'] = str(e)

        return results

    def _scan_ports(self, ip: str) -> List[Dict[str, Any]]:
        ports = []
        common_ports = '21,22,23,25,53,80,110,143,443,465,587,993,995,3306,3389,5432,8080,8443'

        try:
            self.nm.scan(ip, common_ports, arguments='-sV --version-light -T4')

            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    lport = self.nm[host][proto].keys()
                    for port in lport:
                        port_info = self.nm[host][proto][port]
                        ports.append({
                            'port': port,
                            'state': port_info['state'],
                            'service': port_info.get('name', 'unknown'),
                            'version': port_info.get('version', ''),
                            'product': port_info.get('product', '')
                        })
        except Exception as e:
            print(f"Port scan error: {e}")

        return ports

    def _check_http_headers(self, url: str) -> Dict[str, str]:
        headers = {}
        try:
            if not url.startswith('http'):
                url = f'http://{url}'

            response = requests.get(url, timeout=10, allow_redirects=True, verify=False)
            headers = dict(response.headers)
        except Exception as e:
            print(f"HTTP header check error: {e}")

        return headers

    def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        security_headers = {
            'Strict-Transport-Security': headers.get('Strict-Transport-Security', 'Missing'),
            'X-Frame-Options': headers.get('X-Frame-Options', 'Missing'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'Missing'),
            'Content-Security-Policy': headers.get('Content-Security-Policy', 'Missing'),
            'X-XSS-Protection': headers.get('X-XSS-Protection', 'Missing'),
            'Referrer-Policy': headers.get('Referrer-Policy', 'Missing'),
            'Permissions-Policy': headers.get('Permissions-Policy', 'Missing')
        }

        return security_headers

    def _check_ssl(self, host: str) -> Dict[str, Any]:
        ssl_info = {}
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as secure_sock:
                    cert = secure_sock.getpeercert()
                    ssl_info['version'] = secure_sock.version()
                    ssl_info['cipher'] = secure_sock.cipher()
                    ssl_info['valid_from'] = cert.get('notBefore', 'Unknown')
                    ssl_info['valid_until'] = cert.get('notAfter', 'Unknown')
        except Exception as e:
            ssl_info['error'] = str(e)

        return ssl_info

    def _identify_vulnerabilities(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        vulnerabilities = []

        open_ports = [p for p in results['ports'] if p['state'] == 'open']
        risky_ports = [21, 23, 25, 3389]
        for port_info in open_ports:
            if port_info['port'] in risky_ports:
                vulnerabilities.append({
                    'type': 'Open Risky Port',
                    'severity': 'MEDIUM',
                    'description': f"Port {port_info['port']} ({port_info['service']}) is open",
                    'recommendation': f"Consider closing port {port_info['port']} if not required"
                })

        sec_headers = results['security_headers']
        critical_headers = ['Strict-Transport-Security', 'X-Frame-Options', 'X-Content-Type-Options', 'Content-Security-Policy']
        for header in critical_headers:
            if sec_headers.get(header) == 'Missing':
                vulnerabilities.append({
                    'type': 'Missing Security Header',
                    'severity': 'MEDIUM',
                    'description': f"{header} header is not set",
                    'recommendation': f"Implement {header} to enhance security"
                })

        if 'error' in results.get('ssl_info', {}):
            vulnerabilities.append({
                'type': 'SSL/TLS Issue',
                'severity': 'HIGH',
                'description': 'SSL/TLS certificate validation failed',
                'recommendation': 'Verify SSL certificate is valid and properly configured'
            })

        http_80_open = any(p['port'] == 80 and p['state'] == 'open' for p in results['ports'])
        https_443_open = any(p['port'] == 443 and p['state'] == 'open' for p in results['ports'])

        if http_80_open and not https_443_open:
            vulnerabilities.append({
                'type': 'No HTTPS',
                'severity': 'HIGH',
                'description': 'Website does not support HTTPS',
                'recommendation': 'Implement SSL/TLS certificate for secure communication'
            })

        server_header = results['http_headers'].get('Server', '')
        if server_header and any(version in server_header.lower() for version in ['apache', 'nginx', 'iis']):
            vulnerabilities.append({
                'type': 'Server Banner Disclosure',
                'severity': 'LOW',
                'description': f"Server banner reveals: {server_header}",
                'recommendation': 'Hide server version information in HTTP headers'
            })

        return vulnerabilities

    def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]]) -> int:
        score = 0
        severity_weights = {'LOW': 1, 'MEDIUM': 3, 'HIGH': 5, 'CRITICAL': 10}

        for vuln in vulnerabilities:
            score += severity_weights.get(vuln['severity'], 0)

        return min(score, 100)

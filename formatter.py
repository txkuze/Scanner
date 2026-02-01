from typing import Dict, Any

class TelegramFormatter:
    @staticmethod
    def format_scan_results(results: Dict[str, Any]) -> str:
        if 'error' in results:
            return f"❌ <b>Scan Error</b>\n\n{results['error']}"

        risk_level = TelegramFormatter._get_risk_level(results['risk_score'])
        risk_emoji = TelegramFormatter._get_risk_emoji(results['risk_score'])

        message = f"{risk_emoji} <b>SECURITY ASSESSMENT REPORT</b>\n\n"

        message += "<blockquote expandable>\n"
        message += f"<b>TARGET INFORMATION</b>\n"
        message += f"━━━━━━━━━━━━━━━━\n"
        message += f"🌐 <b>URL:</b> {results['url']}\n"
        message += f"🖥️ <b>Host:</b> {results['host']}\n"
        message += f"📍 <b>IP:</b> {results['ip']}\n"
        message += f"📅 <b>Scan Date:</b> {results['timestamp']}\n"
        message += f"⚠️ <b>Risk Score:</b> {results['risk_score']}/100 ({risk_level})\n\n"

        if results['ports']:
            message += f"<b>OPEN PORTS ({len(results['ports'])})</b>\n"
            message += f"━━━━━━━━━━━━━━━━\n"
            for port in results['ports'][:10]:
                version = f"{port.get('product', '')} {port.get('version', '')}".strip()
                message += f"▫️ Port <code>{port['port']}</code> - {port['service']}"
                if version:
                    message += f" ({version})"
                message += f"\n"

            if len(results['ports']) > 10:
                message += f"\n<i>... and {len(results['ports']) - 10} more ports</i>\n"
            message += "\n"

        if results['security_headers']:
            missing_headers = [h for h, v in results['security_headers'].items() if v == 'Missing']
            present_headers = [h for h, v in results['security_headers'].items() if v != 'Missing']

            message += f"<b>SECURITY HEADERS</b>\n"
            message += f"━━━━━━━━━━━━━━━━\n"

            if present_headers:
                message += f"✅ <b>Present ({len(present_headers)}):</b>\n"
                for header in present_headers[:5]:
                    message += f"  • {header}\n"
                if len(present_headers) > 5:
                    message += f"  <i>... and {len(present_headers) - 5} more</i>\n"

            if missing_headers:
                message += f"\n❌ <b>Missing ({len(missing_headers)}):</b>\n"
                for header in missing_headers[:5]:
                    message += f"  • {header}\n"
                if len(missing_headers) > 5:
                    message += f"  <i>... and {len(missing_headers) - 5} more</i>\n"
            message += "\n"

        if results['ssl_info']:
            message += f"<b>SSL/TLS INFORMATION</b>\n"
            message += f"━━━━━━━━━━━━━━━━\n"
            if 'error' in results['ssl_info']:
                message += f"❌ SSL Error: {results['ssl_info']['error']}\n"
            else:
                if 'version' in results['ssl_info']:
                    message += f"🔒 Version: {results['ssl_info']['version']}\n"
                if 'valid_until' in results['ssl_info']:
                    message += f"📅 Valid Until: {results['ssl_info']['valid_until']}\n"
            message += "\n"

        if results['vulnerabilities']:
            message += f"<b>VULNERABILITIES FOUND ({len(results['vulnerabilities'])})</b>\n"
            message += f"━━━━━━━━━━━━━━━━\n"

            high_vulns = [v for v in results['vulnerabilities'] if v['severity'] == 'HIGH']
            medium_vulns = [v for v in results['vulnerabilities'] if v['severity'] == 'MEDIUM']
            low_vulns = [v for v in results['vulnerabilities'] if v['severity'] == 'LOW']

            if high_vulns:
                message += f"\n🔴 <b>HIGH SEVERITY ({len(high_vulns)})</b>\n"
                for vuln in high_vulns[:3]:
                    message += f"  • {vuln['type']}: {vuln['description']}\n"

            if medium_vulns:
                message += f"\n🟡 <b>MEDIUM SEVERITY ({len(medium_vulns)})</b>\n"
                for vuln in medium_vulns[:3]:
                    message += f"  • {vuln['type']}: {vuln['description']}\n"

            if low_vulns:
                message += f"\n🟢 <b>LOW SEVERITY ({len(low_vulns)})</b>\n"
                for vuln in low_vulns[:3]:
                    message += f"  • {vuln['type']}: {vuln['description']}\n"

            message += "\n"
        else:
            message += f"✅ <b>NO MAJOR VULNERABILITIES DETECTED</b>\n\n"

        message += f"<b>SUMMARY</b>\n"
        message += f"━━━━━━━━━━━━━━━━\n"
        message += f"📊 Total Ports Scanned: {len(results['ports'])}\n"
        message += f"⚠️ Vulnerabilities: {len(results['vulnerabilities'])}\n"
        message += f"🛡️ Risk Level: {risk_level}\n"

        message += "</blockquote>\n\n"
        message += "📄 <i>Detailed PDF report attached</i>\n\n"
        message += "⚠️ <b>LEGAL NOTICE:</b> Only scan systems you own or have authorization to test."

        return message

    @staticmethod
    def _get_risk_level(score: int) -> str:
        if score >= 20:
            return "CRITICAL"
        elif score >= 10:
            return "HIGH"
        elif score >= 5:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def _get_risk_emoji(score: int) -> str:
        if score >= 20:
            return "🔴"
        elif score >= 10:
            return "🟠"
        elif score >= 5:
            return "🟡"
        else:
            return "🟢"

    @staticmethod
    def format_help() -> str:
        return """
🤖 <b>VULNERABILITY SCANNER BOT</b>

<b>Available Commands:</b>

/start - Start the bot and see welcome message
/help - Show this help message
/vulnerscan &lt;website&gt; - Scan a website for vulnerabilities

<b>Example Usage:</b>
<code>/vulnerscan example.com</code>
<code>/vulnerscan https://example.com</code>

<b>Features:</b>
✅ Port scanning and service detection
✅ HTTP security header analysis
✅ SSL/TLS configuration check
✅ Vulnerability identification
✅ Risk scoring and severity assessment
✅ Detailed PDF report generation

⚠️ <b>IMPORTANT LEGAL NOTICE:</b>
This bot is for educational and defensive security purposes only. Only scan websites you own or have explicit written authorization to test. Unauthorized scanning may be illegal in your jurisdiction.

🛡️ <b>Security Best Practices:</b>
• Always obtain written permission before scanning
• Use for defensive security and awareness
• Never use findings for malicious purposes
• Report vulnerabilities responsibly

📧 Questions? Contact your security administrator.
        """

    @staticmethod
    def format_start() -> str:
        return """
👋 <b>Welcome to Vulnerability Scanner Bot!</b>

I'm a defensive security tool designed to help you assess website security posture through authorized vulnerability scanning.

<b>What I Can Do:</b>
🔍 Comprehensive port and service scanning
🛡️ Security header analysis
🔒 SSL/TLS configuration assessment
📊 Risk scoring and vulnerability reporting
📄 Professional PDF report generation

<b>Quick Start:</b>
Use /vulnerscan &lt;website&gt; to scan a website
Example: <code>/vulnerscan example.com</code>

<b>Need Help?</b>
Type /help for detailed information

⚠️ <b>CRITICAL REMINDER:</b>
Only scan systems you own or have explicit authorization to test. This tool is for educational and defensive security purposes only.

Let's enhance your security awareness! 🚀
        """

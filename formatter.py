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

        if results.get('tech_stack'):
            message += f"<b>DETECTED TECHNOLOGY</b>\n"
            message += f"━━━━━━━━━━━━━━━━\n"
            for tech in results['tech_stack'][:5]:
                message += f"🔧 {tech}\n"
            if len(results['tech_stack']) > 5:
                message += f"<i>... and {len(results['tech_stack']) - 5} more</i>\n"
            message += "\n"

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

        if results.get('cookies'):
            message += f"<b>COOKIES FOUND ({len(results['cookies'])})</b>\n"
            message += f"━━━━━━━━━━━━━━━━\n"
            for cookie in results['cookies'][:5]:
                flags = []
                if cookie.get('secure'):
                    flags.append("🔒 Secure")
                if cookie.get('httponly'):
                    flags.append("🔐 HttpOnly")
                if cookie.get('samesite'):
                    flags.append("🛡️ SameSite")

                flag_str = " | ".join(flags) if flags else "⚠️ No security flags"
                message += f"🍪 {cookie['name']}: {flag_str}\n"

            if len(results['cookies']) > 5:
                message += f"<i>... and {len(results['cookies']) - 5} more cookies</i>\n"
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
        return """<blockquote expandable>🤖 <b>ADVANCED AI BOT - HELP MENU</b>

━━━━━━━━━━━━━━━━━━━━━━

📋 <b>AVAILABLE COMMANDS:</b>

🚀 <b>General Commands:</b>
  /start - 🏁 Start the bot and see welcome message
  /help - 📖 Show this comprehensive help menu
  /chat - 💬 Chat with Gemini AI assistant
  /history - 📊 View your username/name history (Sangmata)
  /clear - 🗑️ Clear your chat history with AI

🔐 <b>Sudo Commands (Authorized Users Only):</b>
  /vulnerscan &lt;website&gt; - 🔍 Scan a website for vulnerabilities

👑 <b>Owner Commands:</b>
  /addsudo &lt;user&gt; - ➕ Add a user to sudo list
  /delsudo &lt;user&gt; - ➖ Remove a user from sudo list
  /sudolist - 👥 View all sudo users

━━━━━━━━━━━━━━━━━━━━━━

🎯 <b>FEATURES:</b>

🤖 <b>AI Chatbot:</b>
  ✨ Powered by Google Gemini AI
  💭 Natural conversation capabilities
  🧠 Context-aware responses
  📚 Knowledge about cybersecurity & tech

🔍 <b>Vulnerability Scanning:</b>
  ✅ Port scanning and service detection
  ✅ HTTP security header analysis
  ✅ SSL/TLS configuration check
  ✅ Cookie security assessment
  ✅ Vulnerability identification
  ✅ Risk scoring and severity assessment
  ✅ Professional PDF report generation

📊 <b>Sangmata Feature:</b>
  ✅ Track username changes
  ✅ Monitor name changes
  ✅ Complete user history log
  ✅ Automatic change detection

━━━━━━━━━━━━━━━━━━━━━━

📝 <b>EXAMPLE USAGE:</b>

💬 Chat with AI:
  <code>/chat Hello! How are you?</code>
  <code>/chat Explain SQL injection</code>

🔍 Scan a website (Sudo only):
  <code>/vulnerscan example.com</code>
  <code>/vulnerscan https://example.com</code>

👑 Manage sudo users (Owner only):
  <code>/addsudo @username</code>
  <code>/addsudo 123456789</code>
  <code>/delsudo @username</code>

━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>IMPORTANT NOTICE:</b>
This bot is for educational and security awareness purposes. Vulnerability scanning requires sudo access and should only be performed on systems you own or have authorization to test.

🛡️ <b>Security Best Practices:</b>
  • Always obtain written permission before scanning
  • Use for defensive security and awareness
  • Never use findings for malicious purposes
  • Report vulnerabilities responsibly

━━━━━━━━━━━━━━━━━━━━━━

💡 <b>Need Support?</b>
Contact the bot administrator for assistance!

🌟 Enjoy using the bot!</blockquote>"""

    @staticmethod
    def format_start() -> str:
        return """<blockquote expandable>👋 <b>WELCOME TO ADVANCED AI BOT!</b>

━━━━━━━━━━━━━━━━━━━━━━

🤖 <b>I'm your advanced AI assistant with multiple powerful capabilities!</b>

━━━━━━━━━━━━━━━━━━━━━━

✨ <b>WHAT I CAN DO:</b>

💬 <b>AI Chatbot (Gemini Powered):</b>
  🧠 Intelligent conversations
  📚 Knowledge assistance
  💡 Problem solving
  🎯 Context-aware responses

🔍 <b>Vulnerability Scanning:</b>
  🌐 Comprehensive port scanning
  🛡️ Security header analysis
  🔒 SSL/TLS assessment
  🍪 Cookie security check
  📊 Risk scoring & reporting
  📄 Professional PDF reports

📊 <b>Sangmata Feature:</b>
  👤 Track username changes
  📝 Monitor name updates
  🕐 Complete history log
  🔍 Automatic detection

━━━━━━━━━━━━━━━━━━━━━━

🚀 <b>QUICK START GUIDE:</b>

💬 <b>Chat with me:</b>
  Just type /chat followed by your message!
  Example: <code>/chat Hello, how can you help me?</code>

📊 <b>Check your history:</b>
  Use <code>/history</code> to see your Sangmata data!

🔍 <b>Scan websites (Sudo users):</b>
  Use <code>/vulnerscan example.com</code>

📖 <b>Need more help?</b>
  Type <code>/help</code> for detailed command list!

━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>IMPORTANT REMINDER:</b>

🔐 Vulnerability scanning requires sudo access
📝 Only scan systems you own or have authorization
🛡️ This tool is for educational purposes only
✅ Always follow ethical hacking guidelines

━━━━━━━━━━━━━━━━━━━━━━

🌟 <b>Let's get started!</b>

💬 Try chatting with me or explore the features!
📖 Use /help anytime for guidance!

🚀 <i>Powered by Google Gemini AI & Advanced Security Tools</i></blockquote>"""

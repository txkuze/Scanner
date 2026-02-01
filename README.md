# Vulnerability Scanner Telegram Bot

A comprehensive Python-based Telegram bot designed for defensive website security analysis and awareness. This bot performs authorized vulnerability assessments and generates detailed security reports.

## Features

- **Port Scanning**: Comprehensive network port discovery and service detection
- **Security Headers Analysis**: Evaluation of HTTP security headers
- **SSL/TLS Assessment**: Certificate validation and configuration checks
- **Risk Scoring**: Automated vulnerability severity assessment
- **PDF Reports**: Professional tabular reports with findings and recommendations
- **Real-time Updates**: Progress updates during scans
- **Concurrent Scanning**: Support for multiple users with rate limiting

## Commands

- `/start` - Welcome message and bot introduction
- `/help` - Detailed usage instructions
- `/vulnerscan <website>` - Perform security scan on specified website

## Requirements

- Python 3.8 or higher
- Nmap installed on system
- Telegram Bot Token
- VPS or server for deployment

## Installation

### 1. System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip nmap
```

#### CentOS/RHEL
```bash
sudo yum install -y python3 python3-pip nmap
```

#### macOS
```bash
brew install python3 nmap
```

### 2. Python Dependencies

Clone the repository and install Python packages:

```bash
git clone <repository-url>
cd <project-directory>
pip3 install -r requirements.txt
```

### 3. Telegram Bot Setup

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Save the **Bot Token** provided by BotFather

### 4. Get API Credentials

1. Visit https://my.telegram.org/auth
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Save your **API ID** and **API Hash**

### 5. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here

MAX_CONCURRENT_SCANS=3
SCAN_TIMEOUT=300
REPORT_DIR=reports
```

## Running the Bot

### Local Development

```bash
python3 main.py
```

### Production Deployment (VPS)

#### Using systemd service

1. Create a service file:

```bash
sudo nano /etc/systemd/system/vulnscanner-bot.service
```

2. Add the following configuration:

```ini
[Unit]
Description=Vulnerability Scanner Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vulnscanner-bot
sudo systemctl start vulnscanner-bot
```

4. Check status:

```bash
sudo systemctl status vulnscanner-bot
```

#### Using Screen (Alternative)

```bash
screen -S vulnscanner
python3 main.py
```

Detach with `Ctrl+A` then `D`. Reattach with `screen -r vulnscanner`.

#### Using tmux (Alternative)

```bash
tmux new -s vulnscanner
python3 main.py
```

Detach with `Ctrl+B` then `D`. Reattach with `tmux attach -t vulnscanner`.

## Usage Examples

### Basic Scan
```
/vulnerscan example.com
```

### Scan with Protocol
```
/vulnerscan https://example.com
```

### Get Help
```
/help
```

## Output Format

The bot provides two types of output:

1. **Telegram Message**: Formatted summary with expandable details
   - Target information
   - Open ports
   - Security headers status
   - SSL/TLS information
   - Vulnerability summary
   - Risk score

2. **PDF Report**: Comprehensive document including
   - Executive summary
   - Detailed port scan results
   - Security header analysis
   - SSL/TLS configuration
   - Vulnerability details with severity levels
   - Remediation recommendations
   - Security best practices

## Security Considerations

### Legal and Ethical Use

- Only scan websites you own or have explicit written authorization to test
- Unauthorized vulnerability scanning may be illegal in your jurisdiction
- This tool is for educational and defensive security purposes only
- Never use findings for malicious purposes

### Bot Security

- Keep your `.env` file secure and never commit it to version control
- Use strong, unique tokens
- Run the bot with minimal system privileges
- Regularly update dependencies
- Monitor bot logs for suspicious activity

### Scan Limitations

- The bot performs non-intrusive scans only
- No exploit code or active attacks are performed
- Results are informational and should be verified
- False positives may occur

## Troubleshooting

### Nmap Permission Issues

If you encounter permission errors with nmap:

```bash
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

### Python Module Not Found

Ensure all dependencies are installed:

```bash
pip3 install -r requirements.txt --upgrade
```

### Bot Not Responding

1. Check bot is running: `sudo systemctl status vulnscanner-bot`
2. Verify credentials in `.env` file
3. Check logs: `sudo journalctl -u vulnscanner-bot -f`
4. Ensure network connectivity

### Scan Timeout Issues

Increase timeout in `.env`:

```env
SCAN_TIMEOUT=600
```

## Project Structure

```
.
├── main.py                 # Bot entry point and command handlers
├── scanner.py              # Vulnerability scanning logic
├── report_generator.py     # PDF report generation
├── formatter.py            # Telegram message formatting
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template
├── .env                    # Your credentials (not in git)
└── reports/                # Generated PDF reports (auto-created)
```

## Technologies Used

- **python-telegram-bot**: Telegram Bot API wrapper
- **python-nmap**: Nmap integration for port scanning
- **requests**: HTTP header analysis
- **reportlab**: PDF generation
- **python-dotenv**: Environment configuration

## Limitations

- Scans are limited to common ports by default
- Deep vulnerability testing requires additional tools
- Results should be verified by security professionals
- Network firewalls may block some scan attempts

## Contributing

Contributions are welcome for:
- Additional security checks
- Enhanced reporting features
- Performance improvements
- Bug fixes

## Disclaimer

This tool is provided for educational and defensive security purposes only. Users are solely responsible for ensuring they have proper authorization before scanning any systems. The authors and contributors are not responsible for any misuse or damage caused by this tool.

Unauthorized vulnerability scanning may violate computer fraud and abuse laws in many jurisdictions. Always obtain explicit written permission before scanning systems you do not own.

## License

This project is intended for educational purposes. Use responsibly and ethically.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the maintainer.

---

**Remember**: With great power comes great responsibility. Use this tool ethically and legally.

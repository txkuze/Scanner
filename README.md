# Advanced AI Telegram Bot

A comprehensive, market-level Telegram bot powered by Google Gemini AI with advanced vulnerability scanning, user tracking, and sudo management features. This bot combines AI chatbot capabilities with professional security assessment tools.

## Features

### AI Chatbot (Gemini Powered)
- **Natural Conversations**: Powered by Google Gemini AI for intelligent, context-aware responses
- **Chat History**: Maintains conversation context across multiple messages
- **Multi-topic Knowledge**: Help with cybersecurity, programming, general questions, and more
- **Conversation Management**: Clear chat history anytime with `/clear` command

### Vulnerability Scanner
- **Deep Port Scanning**: Comprehensive network port discovery and service detection with version identification
- **Security Headers Analysis**: Evaluation of HTTP security headers and misconfigurations
- **SSL/TLS Assessment**: Certificate validation, cipher suite analysis, and configuration checks
- **Cookie Security Analysis**: Detection and evaluation of session cookie security flags
- **Technology Stack Detection**: Identification of web servers, frameworks, and technologies
- **DNS Information**: IPv4 and IPv6 address resolution
- **Risk Scoring**: Automated vulnerability severity assessment with weighted calculations
- **Professional PDF Reports**: Detailed tabular reports with findings, recommendations, and best practices
- **Sudo-Only Access**: Scanning restricted to authorized sudo users only

### Sangmata Feature
- **Username Tracking**: Automatically tracks and records username changes
- **Name History**: Monitors first name and last name changes
- **Complete History Log**: View all historical changes for any user
- **Automatic Detection**: Changes detected and recorded in real-time

### Sudo User Management
- **Owner-Only Controls**: Only the bot owner can manage sudo users
- **Multiple Methods**: Add users by ID, username, or by replying to their message
- **Sudo List**: View all sudo users with detailed information
- **Owner Protection**: Bot owner cannot be removed from sudo list

### Logging System
- **Telegram Group Logging**: All events logged to specified Telegram group
- **Comprehensive Event Tracking**: Scans, commands, sudo changes, errors, and AI chats
- **Detailed Logs**: Includes user info, timestamps, and event details
- **Real-time Monitoring**: Instant notifications for all bot activities

### User Interface
- **Rich Formatting**: All messages use emoji-rich expandable blockquotes
- **Interactive Buttons**: Inline keyboards for easy navigation
- **Progress Updates**: Real-time status updates during scans
- **Professional Design**: Market-level UI/UX experience

## Commands

### General Commands
- `/start` - Start the bot with interactive menu
- `/help` - Display comprehensive help menu
- `/chat <message>` - Chat with Gemini AI
- `/clear` - Clear your AI chat history
- `/history` - View your username/name change history

### Sudo Commands (Authorized Users Only)
- `/vulnerscan <website>` - Perform deep security scan on any website

### Owner Commands (Bot Owner Only)
- `/addsudo <user_id or @username>` - Add a user to sudo list
- `/delsudo <user_id or @username>` - Remove a user from sudo list
- `/sudolist` - View all sudo users

## Requirements

- Python 3.8 or higher
- Nmap installed on system
- Telegram Bot Token
- Google Gemini API Key
- Supabase Database
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

### 3. Get Required API Keys

#### Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Save the **Bot Token** provided by BotFather

#### Telegram API Credentials
1. Visit https://my.telegram.org/auth
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Save your **API ID** and **API Hash**

#### Google Gemini API Key
1. Visit https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Save your **Gemini API Key**

#### Supabase Database
1. Visit https://supabase.com
2. Create a new project
3. Get your **Supabase URL** and **Supabase Anon Key** from project settings

### 4. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Bot Settings
OWNER_ID=your_telegram_user_id_here
LOG_GROUP_ID=-1003228624224
MAX_CONCURRENT_SCANS=3
SCAN_TIMEOUT=300
REPORT_DIR=reports
```

**Important**: Replace all placeholder values with your actual credentials!

### 5. Get Your Telegram User ID

To find your Telegram user ID:
1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy your user ID and add it to `OWNER_ID` in `.env`

## Running the Bot

### Local Development

```bash
python3 main.py
```

### Production Deployment (VPS)

#### Using systemd service

1. Create a service file:

```bash
sudo nano /etc/systemd/system/aibot.service
```

2. Add the following configuration:

```ini
[Unit]
Description=Advanced AI Telegram Bot
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
sudo systemctl enable aibot
sudo systemctl start aibot
```

4. Check status:

```bash
sudo systemctl status aibot
```

#### Using Screen (Alternative)

```bash
screen -S aibot
python3 main.py
```

Detach with `Ctrl+A` then `D`. Reattach with `screen -r aibot`.

## Usage Examples

### AI Chat
```
/chat Hello! How are you?
/chat Explain SQL injection vulnerabilities
/chat What is the OWASP Top 10?
```

### View History
```
/history
```

### Scan Website (Sudo only)
```
/vulnerscan example.com
/vulnerscan https://example.com
```

### Manage Sudo Users (Owner only)
```
/addsudo @username
/addsudo 123456789
/delsudo @username
/sudolist
```

## Database Schema

The bot uses Supabase with the following tables:

- **sudo_users**: Stores authorized sudo users
- **user_history**: Tracks username and name changes (Sangmata)
- **chat_sessions**: Stores AI chat conversation history
- **scan_logs**: Logs all vulnerability scans performed

## Security Features

- **Sudo System**: Vulnerability scanning restricted to authorized users only
- **Owner Protection**: Only bot owner can manage sudo access
- **Comprehensive Logging**: All actions logged to Telegram group
- **User Tracking**: Automatic tracking of user changes
- **Data Persistence**: Supabase database for reliable storage

## Output Formats

### Telegram Messages
- Rich emoji-enhanced formatting
- Expandable blockquotes for detailed information
- Inline keyboards for navigation
- Real-time progress updates

### PDF Reports
- Professional tabular format
- Executive summary with risk assessment
- Detailed findings and recommendations
- Technology stack analysis
- Vulnerability severity breakdown
- Security best practices

## Project Structure

```
.
├── main.py                 # Main bot entry point
├── config.py               # Configuration management
├── database.py             # Database operations (Supabase)
├── gemini_ai.py            # Gemini AI integration
├── sangmata.py             # User history tracking
├── sudo_manager.py         # Sudo user management
├── logger.py               # Telegram group logging
├── scanner.py              # Vulnerability scanning logic
├── report_generator.py     # PDF report generation
├── formatter.py            # Message formatting
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template
├── .env                    # Your credentials (not in git)
└── reports/                # Generated PDF reports
```

## Technologies Used

- **python-telegram-bot**: Telegram Bot API wrapper
- **google-generativeai**: Google Gemini AI integration
- **supabase**: Database and real-time features
- **python-nmap**: Nmap integration for port scanning
- **requests**: HTTP header analysis
- **reportlab**: PDF generation
- **python-dotenv**: Environment configuration

## Troubleshooting

### Nmap Permission Issues

```bash
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

### Python Module Not Found

```bash
pip3 install -r requirements.txt --upgrade
```

### Bot Not Responding

1. Check bot is running: `sudo systemctl status aibot`
2. Verify credentials in `.env` file
3. Check logs: `sudo journalctl -u aibot -f`
4. Ensure network connectivity

### Database Connection Issues

1. Verify Supabase URL and Key in `.env`
2. Check Supabase project is active
3. Verify Row Level Security policies

## Important Notes

### Legal Notice
- Only scan websites you own or have explicit authorization to test
- Unauthorized vulnerability scanning may be illegal in your jurisdiction
- This tool is for educational and defensive security purposes only

### Gemini AI
- Requires active Google Gemini API key
- Free tier has rate limits
- Conversations are stored in database

### Logging
- All bot activities are logged to specified Telegram group
- Ensure log group ID is correct in `.env`
- Bot must be added to the log group as admin

## Contributing

Contributions are welcome for:
- Additional security checks
- Enhanced AI capabilities
- New features and improvements
- Bug fixes

## License

This project is intended for educational and professional security purposes. Use responsibly and ethically.

## Support

For issues, questions, or contributions:
- Channel: https://t.me/dark_musictm
- Developer: https://t.me/cyber_github

---

**Built with passion for advanced AI and security automation!**

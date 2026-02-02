# Advanced AI & Group Management Telegram Bot

A comprehensive, production-ready Telegram bot powered by Google Gemini AI with advanced group management capabilities, vulnerability scanning, and intelligent chat features.

## Features Overview

### AI Chatbot (Gemini Powered)
- Natural conversation without commands
- Trigger words: hi, hello, hey, sup, yo, greetings, good morning, etc.
- Context-aware responses with chat history
- Multi-topic knowledge (cybersecurity, programming, general topics)
- Automatic response in private chats

### Advanced Group Management
- **User Moderation**: Ban, kick, mute, unmute, warn users
- **Welcome System**: Customizable welcome messages for new members
- **Rules Management**: Set and display group rules
- **Notes System**: Save and retrieve group notes
- **Filters**: Auto-reply to trigger words
- **Warnings System**: 3-strike system with auto-ban
- **Pin Management**: Pin/unpin important messages
- **Antiflood Protection**: Prevent message flooding

### Vulnerability Scanner
- Comprehensive port scanning with nmap
- Security headers analysis
- SSL/TLS configuration checking
- Cookie security assessment
- Technology stack detection
- Risk scoring and severity assessment
- Professional PDF report generation
- Sudo-only access control

### User Tracking (Sangmata)
- Automatic username change tracking
- Name history monitoring
- Complete historical log
- Real-time change detection

### Security & Access Control
- Sudo user management system
- Owner-only administrative commands
- Database-backed permissions
- Comprehensive activity logging

## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or remote)
- Nmap installed on system
- Telegram Bot Token
- Google Gemini API Key

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip nmap mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### CentOS/RHEL
```bash
sudo yum install -y python3 python3-pip nmap mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS
```bash
brew install python3 nmap mongodb-community
brew services start mongodb-community
```

### Python Dependencies

```bash
pip3 install -r requirements.txt
```

### Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_from_botfather
API_ID=your_api_id_from_my_telegram_org
API_HASH=your_api_hash_from_my_telegram_org

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_NAME=telegram_bot

# Bot Settings
OWNER_ID=your_telegram_user_id
LOG_GROUP_ID=-1003228624224
MAX_CONCURRENT_SCANS=3
SCAN_TIMEOUT=300
REPORT_DIR=reports
```

### Getting API Credentials

#### Telegram Bot Token
1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow prompts to create your bot
4. Copy the Bot Token provided

#### Telegram API Credentials
1. Visit https://my.telegram.org/auth
2. Login with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy API ID and API Hash

#### Google Gemini API Key
1. Visit https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

#### Your Telegram User ID
1. Start a chat with @userinfobot on Telegram
2. Send any message
3. Copy your user ID

## Running the Bot

### Development

```bash
python3 main.py
```

### Production (Systemd Service)

1. Create service file:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

2. Add configuration:
```ini
[Unit]
Description=Advanced Telegram Bot
After=network.target mongodb.service

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

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## Commands Reference

### General Commands
| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Start bot and show menu | Everyone |
| `/help` | Display help menu | Everyone |
| `/chat <message>` | Chat with AI (optional) | Everyone |
| `/clear` | Clear AI chat history | Everyone |
| `/history` | View user history | Everyone |

### Admin Commands (Group Only)
| Command | Description | Usage |
|---------|-------------|-------|
| `/ban` | Ban user from group | Reply to message or `/ban <user_id> [reason]` |
| `/kick` | Kick user (can rejoin) | Reply to message or `/kick <user_id> [reason]` |
| `/mute` | Mute user | Reply to message or `/mute <user_id> [minutes]` |
| `/unmute` | Unmute user | Reply to message or `/unmute <user_id>` |
| `/unban` | Unban user | `/unban <user_id>` |
| `/warn` | Warn user (3 = auto-ban) | Reply to message or `/warn <user_id> [reason]` |
| `/warnings` | Check user warnings | Reply to message |
| `/resetwarns` | Reset user warnings | Reply to message |
| `/pin` | Pin message | Reply to message |
| `/unpin` | Unpin message | Reply to message or unpin all |

### Group Settings (Admin Only)
| Command | Description | Usage |
|---------|-------------|-------|
| `/setrules` | Set group rules | `/setrules Your rules here` |
| `/rules` | View group rules | `/rules` |
| `/setwelcome` | Set welcome message | `/setwelcome Welcome {mention} to {chat}!` |
| `/welcome` | Toggle welcome on/off | `/welcome` |

### Notes System (Admin)
| Command | Description | Usage |
|---------|-------------|-------|
| `/save` | Save a note | `/save <name> <content>` |
| `/get` | Get a note | `/get <name>` |
| `/notes` | List all notes | `/notes` |
| `/clear` | Delete a note | `/clear <name>` |

### Filters System (Admin)
| Command | Description | Usage |
|---------|-------------|-------|
| `/filter` | Add auto-reply filter | `/filter <keyword> <reply>` |
| `/filters` | List all filters | `/filters` |
| `/stop` | Remove filter | `/stop <keyword>` |

### Security Commands
| Command | Description | Access |
|---------|-------------|--------|
| `/vulnerscan <url>` | Scan website security | Sudo users only |

### Owner Commands
| Command | Description | Access |
|---------|-------------|--------|
| `/addsudo <user>` | Add sudo user | Owner only |
| `/delsudo <user>` | Remove sudo user | Owner only |
| `/sudolist` | View sudo users | Everyone |

## AI Chat Triggers

The bot automatically responds to these trigger words without needing commands:
- hi, hello, hey
- sup, yo
- greetings
- good morning, good afternoon, good evening

In private chats, the bot responds to ALL messages automatically.

## Welcome Message Variables

When setting welcome messages with `/setwelcome`, you can use:
- `{mention}` - Mentions the new user
- `{name}` - User's first name
- `{chat}` - Group name

Example:
```
/setwelcome Welcome {mention} to {chat}! Please read the /rules
```

## MongoDB Collections

The bot creates these collections automatically:

- **sudo_users** - Authorized users for scanning
- **user_history** - Username/name change tracking
- **chat_sessions** - AI conversation history
- **scan_logs** - Vulnerability scan records
- **groups** - Group settings and configuration
- **warnings** - User warnings tracking
- **notes** - Saved group notes
- **filters** - Auto-reply filters
- **user_flood** - Antiflood tracking

## Security Features

- Sudo system for vulnerability scanning
- Owner-only management commands
- Admin verification for group commands
- Database-backed permissions
- Comprehensive activity logging
- Automatic owner initialization
- Antiflood protection
- Warnings system with auto-moderation

## Usage Examples

### AI Chat
```
User: Hi!
Bot: Hello! How can I help you today?

User: What is SQL injection?
Bot: SQL injection is a web security vulnerability...
```

### Group Moderation
```
Admin: (replies to spammer) /warn Stop spamming
Bot: User has been warned (1/3)
Reason: Stop spamming

Admin: (replies to spammer) /mute 60
Bot: User has been muted for 60 minutes
```

### Notes and Filters
```
Admin: /save rules Be respectful to all members
Bot: Note 'rules' saved!

User: #rules
Admin: /get rules
Bot: Be respectful to all members

Admin: /filter hello Welcome to our group!
Bot: Filter for 'hello' added!

User: hello
Bot: Welcome to our group!
```

### Vulnerability Scanning
```
Sudo User: /vulnerscan example.com
Bot: Scanning: example.com
     This may take 1-3 minutes...

     (After scan completes)
     Sends PDF report with detailed findings
```

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check MongoDB is running
sudo systemctl status mongodb

# Start MongoDB
sudo systemctl start mongodb

# Check connection
mongosh --eval "db.adminCommand('ping')"
```

### Nmap Permission Issues
```bash
# Grant capabilities to nmap
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

### Python Module Errors
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --upgrade --force-reinstall
```

### Bot Not Responding
1. Check bot is running: `sudo systemctl status telegram-bot`
2. Verify credentials in `.env` file
3. Check logs: `sudo journalctl -u telegram-bot -f`
4. Ensure network connectivity

## Important Notes

### Legal Notice
Only scan websites you own or have explicit authorization to test. Unauthorized vulnerability scanning may be illegal in your jurisdiction.

### MongoDB Setup
For production use, consider:
- Setting up authentication
- Configuring replica sets
- Regular backups
- Remote database hosting (MongoDB Atlas)

### Group Administration
- Bot needs admin rights in groups for moderation commands
- Users need admin rights to use admin commands
- Bot automatically detects admin status

## Architecture

```
project/
├── main.py                 # Main bot entry point
├── config.py               # Configuration management
├── mongodb_database.py     # MongoDB operations
├── gemini_ai.py            # Gemini AI integration
├── group_manager.py        # Group management features
├── sangmata.py             # User tracking
├── sudo_manager.py         # Sudo system
├── logger.py               # Telegram logging
├── scanner.py              # Vulnerability scanning
├── report_generator.py     # PDF reports
├── formatter.py            # Message formatting
├── requirements.txt        # Python dependencies
└── .env                    # Configuration (not in git)
```

## Technologies Used

- **python-telegram-bot** - Telegram Bot API wrapper
- **google-generativeai** - Google Gemini AI
- **pymongo** - MongoDB driver
- **python-nmap** - Network scanning
- **requests** - HTTP requests
- **reportlab** - PDF generation
- **python-dotenv** - Environment configuration

## Support

For issues, questions, or contributions:
- Channel: https://t.me/dark_musictm
- Developer: https://t.me/cyber_github

## License

This project is for educational and professional use. Use responsibly and ethically.

Built with passion for AI and automation!

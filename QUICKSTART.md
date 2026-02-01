# Quick Start Guide

Get your Vulnerability Scanner Bot running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.8+ installed
- [ ] Nmap installed
- [ ] Telegram account
- [ ] VPS or local machine for hosting

## Step 1: Install System Dependencies

### Ubuntu/Debian
```bash
sudo apt update && sudo apt install -y python3 python3-pip nmap
```

### CentOS/RHEL
```bash
sudo yum install -y python3 python3-pip nmap
```

### macOS
```bash
brew install python3 nmap
```

## Step 2: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

## Step 3: Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send: `/newbot`
3. Choose a name: `My Vuln Scanner`
4. Choose a username: `myname_vulnscanner_bot`
5. Copy the **Bot Token** you receive

## Step 4: Get API Credentials

1. Visit: https://my.telegram.org/auth
2. Login with your phone number
3. Click "API development tools"
4. Fill the form (any values work for personal use)
5. Copy your **API ID** and **API Hash**

## Step 5: Configure Environment

```bash
cp .env.example .env
nano .env
```

Add your credentials:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
```

Save with `Ctrl+X`, `Y`, `Enter`

## Step 6: Run the Bot

### Option A: Direct Run
```bash
python3 main.py
```

### Option B: Using Start Script
```bash
./start.sh
```

### Option C: Background Service
```bash
nohup python3 main.py > bot.log 2>&1 &
```

## Step 7: Test Your Bot

1. Open Telegram
2. Search for your bot username
3. Send: `/start`
4. Try a scan: `/vulnerscan example.com`

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip3 install -r requirements.txt --upgrade
```

### "nmap: command not found"
```bash
sudo apt install nmap  # Ubuntu/Debian
```

### "Bot doesn't respond"
- Check bot token is correct
- Verify bot is running: `ps aux | grep main.py`
- Check logs for errors

### "Permission denied" for nmap
```bash
sudo setcap cap_net_raw,cap_net_admin+eip $(which nmap)
```

## Production Deployment

For 24/7 operation on VPS:

```bash
sudo nano /etc/systemd/system/vulnscanner.service
```

Add:
```ini
[Unit]
Description=Vulnerability Scanner Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vulnscanner
sudo systemctl start vulnscanner
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot |
| `/help` | Show help message |
| `/vulnerscan <url>` | Scan a website |

## Example Usage

```
/vulnerscan example.com
/vulnerscan https://example.com
/vulnerscan 192.168.1.1
```

## Legal Notice

Only scan systems you own or have permission to test!

---

Need more details? Check `README.md` and `SECURITY.md`

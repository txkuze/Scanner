# MongoDB Setup Guide

This guide will help you set up MongoDB for the bot.

## Option 1: Local MongoDB

### Install MongoDB on Ubuntu/Debian

```bash
# Import MongoDB public key
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list
sudo apt update

# Install MongoDB
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
mongosh --eval "db.adminCommand('ping')"
```

### Install MongoDB on macOS

```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Verify installation
mongosh --eval "db.adminCommand('ping')"
```

### Configure Local MongoDB

1. Edit your `.env` file:
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_NAME=telegram_bot
```

2. That's it! The bot will automatically create the database and collections.

## Option 2: MongoDB Atlas (Cloud)

MongoDB Atlas is a free cloud database service - perfect for production!

### Setup Steps

1. Visit https://www.mongodb.com/cloud/atlas/register

2. Create a free account

3. Create a free cluster (M0 Sandbox - FREE)

4. Wait for cluster to be created (2-3 minutes)

5. Click "Connect" button

6. Whitelist your IP address or add `0.0.0.0/0` for all IPs

7. Create a database user with username and password

8. Choose "Connect your application"

9. Copy the connection string

10. Replace `<password>` with your database user password

Example connection string:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

11. Update your `.env` file:
```env
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_NAME=telegram_bot
```

### MongoDB Atlas Advantages

- Free 512MB storage
- No server maintenance
- Automatic backups
- High availability
- Better performance
- Accessible from anywhere

## Option 3: Docker MongoDB

### Using Docker

```bash
# Pull MongoDB image
docker pull mongo:latest

# Run MongoDB container
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest

# Verify running
docker ps

# Check logs
docker logs mongodb
```

### Configure Docker MongoDB

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_NAME=telegram_bot
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

volumes:
  mongodb_data:
```

Run with:
```bash
docker-compose up -d
```

## Verifying Connection

Test your MongoDB connection:

```python
from pymongo import MongoClient

# Replace with your connection string
client = MongoClient("mongodb://localhost:27017/")

# Test connection
try:
    client.admin.command('ping')
    print("✓ MongoDB connection successful!")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")

# List databases
print("Databases:", client.list_database_names())
```

Save as `test_mongodb.py` and run:
```bash
python3 test_mongodb.py
```

## Common Issues

### Connection Refused

```bash
# Check if MongoDB is running
sudo systemctl status mongod

# If not running, start it
sudo systemctl start mongod

# Check port
sudo netstat -tlnp | grep 27017
```

### Authentication Failed

If you enabled authentication:

```env
MONGODB_URI=mongodb://username:password@localhost:27017/
```

### Firewall Issues

```bash
# Allow MongoDB port
sudo ufw allow 27017
```

### Permission Issues

```bash
# Fix MongoDB directory permissions
sudo chown -R mongodb:mongodb /var/lib/mongodb
sudo chown mongodb:mongodb /tmp/mongodb-27017.sock
```

## Database Management Tools

### MongoDB Compass (GUI)

Free official GUI for MongoDB:
- Download: https://www.mongodb.com/try/download/compass
- Connect using your MongoDB URI
- Visual interface for browsing collections

### mongosh (Command Line)

```bash
# Connect to local MongoDB
mongosh

# Connect to remote MongoDB
mongosh "mongodb+srv://cluster.xxxxx.mongodb.net/" --username myuser

# Show databases
show dbs

# Use database
use telegram_bot

# Show collections
show collections

# Query collection
db.sudo_users.find()

# Count documents
db.chat_sessions.countDocuments()
```

## Backup and Restore

### Backup

```bash
# Backup entire database
mongodump --db telegram_bot --out /backup/

# Backup specific collection
mongodump --db telegram_bot --collection sudo_users --out /backup/
```

### Restore

```bash
# Restore database
mongorestore --db telegram_bot /backup/telegram_bot/

# Restore specific collection
mongorestore --db telegram_bot --collection sudo_users /backup/telegram_bot/sudo_users.bson
```

## Security Best Practices

1. **Enable Authentication** (Production):
```bash
# Edit MongoDB config
sudo nano /etc/mongod.conf

# Add:
security:
  authorization: enabled

# Restart MongoDB
sudo systemctl restart mongod
```

2. **Create Admin User**:
```javascript
use admin
db.createUser({
  user: "admin",
  pwd: "strong_password",
  roles: ["root"]
})
```

3. **Create Bot User**:
```javascript
use telegram_bot
db.createUser({
  user: "bot_user",
  pwd: "strong_password",
  roles: [{ role: "readWrite", db: "telegram_bot" }]
})
```

4. **Update Connection String**:
```env
MONGODB_URI=mongodb://bot_user:strong_password@localhost:27017/telegram_bot
```

## Monitoring

### Check Database Size

```javascript
use telegram_bot
db.stats()
```

### Monitor Collections

```javascript
// Check collection sizes
db.chat_sessions.stats()
db.user_history.stats()
```

### Index Performance

```javascript
// Check indexes
db.sudo_users.getIndexes()

// Analyze query performance
db.chat_sessions.find({user_id: 123}).explain("executionStats")
```

## Maintenance

### Clean Old Data

```javascript
// Delete old chat sessions (older than 30 days)
db.chat_sessions.deleteMany({
  created_at: {
    $lt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  }
})

// Delete old flood records
db.user_flood.deleteMany({})
```

### Optimize Database

```bash
# Compact database
mongosh telegram_bot --eval "db.runCommand({compact: 'chat_sessions'})"
```

## Troubleshooting

If the bot fails to connect to MongoDB:

1. Check MongoDB is running
2. Verify connection string in `.env`
3. Test connection with `mongosh`
4. Check firewall settings
5. Verify database permissions

For more help, see MongoDB documentation: https://www.mongodb.com/docs/

Recommended: Use MongoDB Atlas (cloud) for production - it's free and reliable!

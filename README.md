# Telegram Time Zone Bot Deployment Guide

## Overview
This Telegram bot provides current local times for major cities in the US and Canada through an interactive inline keyboard interface.

## 🔧 Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (you have: `8494227712:AAGI5na8W94Sv620GB5HF7zH759xMOydzgo`)
- Basic knowledge of Python and command line

## 📋 Step-by-Step Deployment Instructions

### Step 1: Environment Setup

#### Local Development Setup

1. **Clone or download the project files**
   ```bash
   # If using git
   git clone <your-repo-url>
   cd telegram-timezone-bot
   
   # Or create a new directory and add the files
   mkdir telegram-timezone-bot
   cd telegram-timezone-bot
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Environment Variables Setup

#### Option A: Using .env file (Recommended for development)

1. **Create a .env file**
   ```bash
   touch .env  # On Windows: type nul > .env
   ```

2. **Add your bot token to .env**
   ```
   BOT_TOKEN=8494227712:AAGI5na8W94Sv620GB5HF7zH759xMOydzgo
   ```

#### Option B: System Environment Variables

**Windows:**
```cmd
set BOT_TOKEN=8494227712:AAGI5na8W94Sv620GB5HF7zH759xMOydzgo
```

**macOS/Linux:**
```bash
export BOT_TOKEN=8494227712:AAGI5na8W94Sv620GB5HF7zH759xMOydzgo
```

### Step 3: Local Testing

1. **Run the bot locally**
   ```bash
   python bot.py
   ```

2. **Test the bot**
   - Open Telegram
   - Search for your bot using its username
   - Send `/start` command
   - Try selecting different cities

### Step 4: Production Deployment Options

#### Option A: VPS/Cloud Server Deployment

1. **Upload files to your server**
   ```bash
   scp -r . user@your-server:/path/to/bot/
   ```

2. **Install dependencies on server**
   ```bash
   ssh user@your-server
   cd /path/to/bot/
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set environment variable**
   ```bash
   export BOT_TOKEN=8494227712:AAGI5na8W94Sv620GB5HF7zH759xMOydzgo
   ```

4. **Run with process manager (PM2 or systemd)**

#### Option B: Heroku Deployment

1. **Install Heroku CLI**
2. **Create Heroku app**
   ```bash
   heroku create your-bot-name
   ```

3. **Set environment variable**
   ```bash
   heroku config:set BOT_TOKEN=8494227712:AAGI5na8W94Sv620GB5HF7zH759xMOydzgo
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy bot"
   git push heroku main
   ```

#### Option C: Docker Deployment

See `Dockerfile` and `docker-compose.yml` for containerized deployment.

## 🔒 Security Best Practices

1. **Never commit tokens to version control**
2. **Use environment variables for sensitive data**
3. **Regularly rotate bot tokens**
4. **Monitor bot usage and logs**
5. **Implement rate limiting for production**

## 🧪 Testing Instructions

### Manual Testing Checklist

- [ ] Bot responds to `/start` command
- [ ] Inline keyboard displays correctly
- [ ] City selection works
- [ ] Time display is accurate
- [ ] Pagination works (if more than 6 cities per page)
- [ ] Error handling works for invalid selections

### Automated Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## 🐛 Troubleshooting

### Common Issues

1. **"BOT_TOKEN is not set" error**
   - Verify environment variable is set correctly
   - Check .env file format

2. **"Unauthorized" error**
   - Verify bot token is correct
   - Check if bot was deleted or token revoked

3. **Bot not responding**
   - Check internet connection
   - Verify bot is running
   - Check Telegram API status

4. **Timezone errors**
   - Ensure pytz is installed correctly
   - Check timezone names in CITY_TIMEZONES dict

### Debug Mode

Enable debug logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring and Maintenance

1. **Log Analysis**: Monitor bot.log for errors
2. **Performance**: Track response times
3. **Usage**: Monitor user interactions
4. **Updates**: Keep dependencies updated

## 🔄 Webhook Setup (Optional)

For production environments, webhooks are more efficient than polling:

1. **Set webhook URL**
   ```python
   application.run_webhook(
       listen="0.0.0.0",
       port=int(os.environ.get('PORT', 5000)),
       url_path=BOT_TOKEN,
       webhook_url=f"https://your-domain.com/{BOT_TOKEN}"
   )
   ```

2. **Configure reverse proxy (nginx)**
   ```nginx
   location /webhook {
       proxy_pass http://localhost:5000;
   }
   ```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review logs for error messages
3. Verify all dependencies are installed
4. Test with a fresh bot token if needed

---

**Security Reminder**: Keep your bot token secure and never share it publicly!
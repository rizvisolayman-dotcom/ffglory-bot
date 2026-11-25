# FFGlory Telegram Bot

Control your ffglory.pro clan groups via Telegram buttons.

## Features

- 🚀 **Launch Groups** - Start new auto-clan groups with region selection
- 📋 **List Groups** - View all your groups with status
- 🎮 **Group Actions** - Stop, Restart, Delete, Get Glory, Get Clan Info
- 💰 **Check Balance** - View basic/premium credits
- 🎫 **Create Coupons** - Bulk create coupons with custom credits

## Local Development

```bash
cd ffglory-bot
pip install -r requirements.txt
export BOT_TOKEN="your_bot_token_from_botfather"
python bot.py
```

## Deploy to Render (Free)

### Option 1: Using render.yaml (Recommended)

1. Push this folder to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New** → **Blueprint**
4. Connect your GitHub repo
5. Add environment variable `BOT_TOKEN` with your bot token
6. Click **Apply**

### Option 2: Manual Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Environment**: Docker
   - **Build Command**: (leave empty)
   - **Start Command**: (leave empty - uses Dockerfile CMD)
5. Add environment variable:
   - `BOT_TOKEN` = your bot token
6. Click **Create Web Service**

## Get Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow instructions
4. Copy the token

## API Credentials (Already Configured)

- **Base URL**: https://ffglory.pro
- **API Key**: `ak_0f5db189209bbfb274f5b605508f019303ba2f92fcd70abe867d9e17f41122f6`
- **Master Key**: `22e15fc938aef0cf08bff1a4dd7a4aaa`

## Bot Commands

- `/start` - Show main menu
- `/cancel` - Cancel current operation

## Button Flow

```
Main Menu
├── 🚀 Launch Group → Select Region → Enter Clan ID
├── 📋 My Groups → Select Group → Actions (Stop/Restart/Delete/Glory/Clan Info)
├── 💰 Check Balance
└── 🎫 Create Coupons → Count → Basic Credits → Premium Credits
```

## Error Handling

All API errors are caught and displayed in the bot. Common errors:
- `401` - Invalid API key
- `402` - Insufficient credits
- `404` - Group not found
- `429` - Rate limited

## Security Notes

- Never commit `BOT_TOKEN` to GitHub
- Use Render environment variables for secrets
- The API keys are hardcoded in bot.py - consider moving to env vars for production
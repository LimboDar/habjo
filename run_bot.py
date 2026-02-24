#!/usr/bin/env python
# Main script to run the Telegram fantasy game bot

import asyncio
from telegram_bot import FantasyGameBot

# Replace YOUR_TELEGRAM_BOT_TOKEN with your actual bot token from @BotFather
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

async def main():
    print("Initializing Fantasy Game Bot...")
    bot = FantasyGameBot(TOKEN)
    print("Starting bot...")
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
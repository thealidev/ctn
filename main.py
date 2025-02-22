import telegram
import requests
import asyncio
import time
import os

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") # store this in env variables.
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") # store this in env variables.
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/tokens/solana"
MIN_LIQUIDITY = 1000000
DEX_ID = "meteora" #filter for meteora

async def send_telegram_message(message):
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

async def check_new_coins():
    seen_pairs = set()  # Keep track of already notified pairs
    while True:
        try:
            response = requests.get(DEXSCREENER_API_URL)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            pairs = data.get("pairs", [])

            for pair in pairs:
                if pair.get("dexId") == DEX_ID and pair.get("liquidity", {}).get("usd", 0) >= MIN_LIQUIDITY:
                    pair_id = pair.get("pairAddress") #use pairaddress as unique identifier.

                    if pair_id not in seen_pairs:
                        seen_pairs.add(pair_id) #add to seen pairs.

                        message = f"New coin launched on Meteora:\n"
                        message += f"Pair: {pair.get('baseToken', {}).get('name', 'Unknown')} / {pair.get('quoteToken', {}).get('name', 'Unknown')}\n"
                        message += f"Address: {pair.get('pairAddress')}\n"
                        message += f"Liquidity: ${pair.get('liquidity', {}).get('usd', 0):,}\n"
                        message += f"Dexscreener: {pair.get('url')}"

                        await send_telegram_message(message)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Dexscreener: {e}")
        except Exception as e:
             print(f"An unexpected error occurred: {e}")

        await asyncio.sleep(60) # Check every 60 seconds

async def main():
    print("Telegram bot started. Monitoring for new coins...")
    await check_new_coins()

if __name__ == "__main__":
    asyncio.run(main())

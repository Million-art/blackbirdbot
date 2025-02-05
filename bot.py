import os
import json
import requests
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)

# Function to fetch market price from CoinPaprika API
def get_market_price(symbol):
    url = f"https://api.coinpaprika.com/v1/tickers/{symbol.lower()}"
    try:
        response = requests.get(url)
        data = response.json()

        # Check if data contains the necessary price information
        if "quotes" in data:
            price = data["quotes"]["USD"]["price"]
            return f"Current price of {symbol.upper()} is: ${price:.2f}"
        else:
            return "Invalid token pair! Please try again (e.g., bitcoin, ethereum)."
    except Exception as e:
        return f"Error fetching market price: {str(e)}"

# Function to generate main keyboard
def generate_main_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📈 Market Price", callback_data="market_price"),
        types.InlineKeyboardButton("🚀 Launch App", web_app=types.WebAppInfo(url="https://blackbird-2lbs.vercel.app"))
    )
    return keyboard

# Handle /start command
@bot.message_handler(commands=['start'])
async def start(message):
    welcome_message = "Welcome! How can I assist you today?"
    await bot.send_message(message.chat.id, welcome_message, reply_markup=generate_main_keyboard())

# Handle button clicks
@bot.callback_query_handler(func=lambda call: call.data == "market_price")
async def ask_for_token_pair(call):
    await bot.send_message(call.message.chat.id, "Please enter the token pair (e.g., BTC, ETH):")

# Handle user input for market price
@bot.message_handler(func=lambda message: True)
async def fetch_market_price(message):
    token_pair = message.text.strip().lower()
    price_info = get_market_price(token_pair)
    await bot.send_message(message.chat.id, price_info)

# HTTP Server to handle updates from Telegram Webhook
class Handler(BaseHTTPRequestHandler):
    async def process_update(self, update_dict):
        update = types.Update.de_json(update_dict)
        await bot.process_new_updates([update])

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  
        post_data = self.rfile.read(content_length)
        update_dict = json.loads(post_data.decode('utf-8'))

        asyncio.run(self.process_update(update_dict))

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello, the bot is running!")

# Start HTTP Server
def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, Handler)
    print("Starting HTTP server on port 8000...")
    httpd.serve_forever()

# Start the bot
if __name__ == "__main__":
    run_server()

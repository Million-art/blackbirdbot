import os
import json
import requests
import asyncio
import websockets
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)

# Binance WebSocket URL
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/"

# Store active WebSocket connections
active_websockets = {}

# Function to start a WebSocket connection
async def get_live_market_price(symbol, chat_id):
    symbol = symbol.lower()  # Binance expects lowercase pairs
    ws_url = f"{BINANCE_WS_URL}{symbol}@trade"

    try:
        async with websockets.connect(ws_url) as websocket:
            active_websockets[chat_id] = websocket
            while True:
                response = await websocket.recv()
                data = json.loads(response)

                if "p" in data:
                    price = data["p"]
                    await bot.send_message(chat_id, f"🔴 Live Price Update for {symbol.upper()}: ${price}")

    except Exception as e:
        await bot.send_message(chat_id, "⚠️ Error connecting to live market data.")
        print(f"WebSocket Error: {e}")

# Handle /start command
@bot.message_handler(commands=['start'])
async def start(message):
    welcome_message = "Welcome! Send a token pair (e.g., **BTCUSDT**) to get live prices."
    await bot.send_message(message.chat.id, welcome_message)

# Handle user input for real-time market price
@bot.message_handler(func=lambda message: True)
async def fetch_market_price(message):
    token_pair = message.text.strip().upper()
    
    if message.chat.id in active_websockets:
        await bot.send_message(message.chat.id, "⚠️ You already have a live stream running. Send /stop to disconnect first.")
        return

    await bot.send_message(message.chat.id, f"✅ Starting live price updates for {token_pair}...")
    asyncio.create_task(get_live_market_price(token_pair, message.chat.id))

# Handle /stop command to close WebSocket
@bot.message_handler(commands=['stop'])
async def stop_stream(message):
    if message.chat.id in active_websockets:
        websocket = active_websockets.pop(message.chat.id)
        await websocket.close()
        await bot.send_message(message.chat.id, "✅ Live price stream stopped.")
    else:
        await bot.send_message(message.chat.id, "⚠️ No active price stream found.")

# HTTP Server to handle Webhook updates
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


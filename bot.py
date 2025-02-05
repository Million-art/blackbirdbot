import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the Telegram bot token from the environment variable
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Telegram bot token is missing. Set TELEGRAM_BOT_TOKEN in the environment.")

# Command to start the bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to BlackbirdAI! How can I assist you today?')

# Handle any other messages
def handle_message(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('I dont know what you are saying. Use /start to begin.')

# Main function to start the bot
def main() -> None:
    # Initialize the Updater with your bot token
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the /start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Register a message handler for any other text messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

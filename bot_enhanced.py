import logging
import os
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ---------------------- CONFIG ----------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
PORT = int(os.getenv("PORT", 5000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # For production webhook mode
CITIES_PER_PAGE = 6

# ---------------------- CITY TIMEZONES ----------------------
CITY_TIMEZONES = {
    # ---------------- US TOP 50 ----------------
    "New York": "America/New_York",
    "Los Angeles": "America/Los_Angeles",
    "Chicago": "America/Chicago",
    "Houston": "America/Chicago",
    "Phoenix": "America/Phoenix",
    "Philadelphia": "America/New_York",
    "San Antonio": "America/Chicago",
    "San Diego": "America/Los_Angeles",
    "Dallas": "America/Chicago",
    "San Jose": "America/Los_Angeles",
    "Austin": "America/Chicago",
    "Jacksonville": "America/New_York",
    "Fort Worth": "America/Chicago",
    "Columbus": "America/New_York",
    "Charlotte": "America/New_York",
    "San Francisco": "America/Los_Angeles",
    "Indianapolis": "America/Indiana/Indianapolis",
    "Seattle": "America/Los_Angeles",
    "Denver": "America/Denver",
    "Washington DC": "America/New_York",
    "Boston": "America/New_York",
    "El Paso": "America/Denver",
    "Nashville": "America/Chicago",
    "Detroit": "America/Detroit",
    "Oklahoma City": "America/Chicago",
    "Portland": "America/Los_Angeles",
    "Las Vegas": "America/Los_Angeles",
    "Memphis": "America/Chicago",
    "Louisville": "America/Kentucky/Louisville",
    "Baltimore": "America/New_York",
    "Milwaukee": "America/Chicago",
    "Albuquerque": "America/Denver",
    "Tucson": "America/Phoenix",
    "Fresno": "America/Los_Angeles",
    "Sacramento": "America/Los_Angeles",
    "Mesa": "America/Phoenix",
    "Kansas City": "America/Chicago",
    "Atlanta": "America/New_York",
    "Omaha": "America/Chicago",
    "Colorado Springs": "America/Denver",
    "Raleigh": "America/New_York",
    "Miami": "America/New_York",
    "Long Beach": "America/Los_Angeles",
    "Virginia Beach": "America/New_York",
    "Oakland": "America/Los_Angeles",
    "Minneapolis": "America/Chicago",
    "Tulsa": "America/Chicago",
    "Arlington": "America/Chicago",
    "Tampa": "America/New_York",

    # ---------------- CANADA TOP 50 ----------------
    "Toronto": "America/Toronto",
    "Montreal": "America/Toronto",
    "Calgary": "America/Edmonton",
    "Ottawa": "America/Toronto",
    "Edmonton": "America/Edmonton",
    "Mississauga": "America/Toronto",
    "Winnipeg": "America/Winnipeg",
    "Vancouver": "America/Vancouver",
    "Brampton": "America/Toronto",
    "Hamilton": "America/Toronto",
    "Quebec City": "America/Toronto",
    "Surrey": "America/Vancouver",
    "Laval": "America/Toronto",
    "Halifax": "America/Halifax",
    "London": "America/Toronto",
    "Markham": "America/Toronto",
    "Vaughan": "America/Toronto",
    "Gatineau": "America/Toronto",
    "Saskatoon": "America/Regina",
    "Longueuil": "America/Toronto",
    "Kitchener": "America/Toronto",
    "Burnaby": "America/Vancouver",
    "Windsor": "America/Toronto",
    "Regina": "America/Regina",
    "Richmond": "America/Vancouver",
    "Richmond Hill": "America/Toronto",
    "Oakville": "America/Toronto",
    "Burlington": "America/Toronto",
    "Greater Sudbury": "America/Toronto",
    "Sherbrooke": "America/Toronto",
    "Oshawa": "America/Toronto",
    "Saguenay": "America/Toronto",
    "Lévis": "America/Toronto",
    "Barrie": "America/Toronto",
    "Abbotsford": "America/Vancouver",
    "Coquitlam": "America/Vancouver",
    "Trois-Rivières": "America/Toronto",
    "St. Catharines": "America/Toronto",
    "Cambridge": "America/Toronto",
    "Whitby": "America/Toronto",
    "Kelowna": "America/Vancouver",
    "Kingston": "America/Toronto",
    "Ajax": "America/Toronto",
    "Langley": "America/Vancouver",
    "Saanich": "America/Vancouver",
    "Terrebonne": "America/Toronto",
    "Milton": "America/Toronto",
    "St. John's": "America/St_Johns",
    "Thunder Bay": "America/Toronto",
    "Waterloo": "America/Toronto",
}

# ---------------------- LOGGING ----------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ---------------------- HELPERS ----------------------
def build_keyboard(page: int = 0):
    """Builds a paginated inline keyboard of cities."""
    cities = list(CITY_TIMEZONES.keys())
    start = page * CITIES_PER_PAGE
    end = start + CITIES_PER_PAGE
    page_cities = cities[start:end]

    keyboard = []
    for city in page_cities:
        keyboard.append([InlineKeyboardButton(city, callback_data=f"city:{city}")])

    # Pagination controls
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page:{page-1}"))
    if end < len(cities):
        navigation.append(InlineKeyboardButton("Next ➡️", callback_data=f"page:{page+1}"))
    if navigation:
        keyboard.append(navigation)

    # Add refresh button
    keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data=f"page:{page}")])

    return InlineKeyboardMarkup(keyboard)


def get_local_time(city: str) -> str:
    """Return formatted local time for a given city."""
    try:
        tz_name = CITY_TIMEZONES[city]
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        day_str = now.strftime("%A")
        return f"{time_str}\n📅 {day_str}, {date_str}"
    except Exception as e:
        logger.error(f"Error fetching time for {city}: {e}")
        return "❌ Timezone not found."


# ---------------------- HANDLERS ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    welcome_message = (
        f"👋 Hello {user.first_name}!\n\n"
        "🌍 Welcome to the **Time Zone Bot**!\n\n"
        "Select any city below to get the current local time. "
        "I support major cities across the US and Canada.\n\n"
        "🔄 Use the navigation buttons to browse all available cities."
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=build_keyboard(page=0),
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "🤖 **Time Zone Bot Help**\n\n"
        "**Available Commands:**\n"
        "• `/start` - Show city selection menu\n"
        "• `/help` - Show this help message\n"
        "• `/about` - About this bot\n\n"
        "**How to use:**\n"
        "1. Use `/start` to see the city list\n"
        "2. Click on any city to get current time\n"
        "3. Use ⬅️ Next ➡️ buttons to navigate\n"
        "4. Use 🔄 Refresh to update the menu\n\n"
        "**Supported Regions:**\n"
        "• 🇺🇸 Top 50 US cities\n"
        "• 🇨🇦 Top 50 Canadian cities"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    about_text = (
        "ℹ️ **About Time Zone Bot**\n\n"
        "This bot provides real-time local times for major cities "
        "across the United States and Canada.\n\n"
        "**Features:**\n"
        "• 🕐 Real-time clock data\n"
        "• 🌍 100+ supported cities\n"
        "• 📱 Easy-to-use interface\n"
        "• 🔄 Always up-to-date\n\n"
        "**Developer:** Your Name\n"
        "**Version:** 2.0\n"
        "**Last Updated:** 2025"
    )
    
    await update.message.reply_text(about_text, parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses from inline keyboard."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    logger.info(f"User {user.id} ({user.username}) pressed button: {query.data}")

    try:
        if query.data.startswith("city:"):
            city = query.data.split(":", 1)[1]
            time_info = get_local_time(city)
            
            response_text = f"🕐 **{city}**\n\n{time_info}"
            
            # Create a "Back to Menu" button
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="page:0")]
            ])
            
            await query.message.reply_text(
                response_text,
                parse_mode='Markdown',
                reply_markup=back_keyboard
            )

        elif query.data.startswith("page:"):
            page = int(query.data.split(":", 1)[1])
            await query.edit_message_reply_markup(reply_markup=build_keyboard(page))

    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        await query.message.reply_text("❌ An error occurred. Please try again.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by Updates."""
    logger.error("Exception while handling an update:", exc_info=context.error)


# ---------------------- HEALTH CHECK ----------------------
async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Health check endpoint for monitoring."""
    await update.message.reply_text("✅ Bot is running normally!")


# ---------------------- MAIN ----------------------
def main():
    """Run the bot."""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is not set. Please set the environment variable.")
        print("❌ Error: BOT_TOKEN environment variable is required!")
        print("💡 Set it with: export BOT_TOKEN=your_token_here")
        return

    logger.info("🚀 Starting Telegram Time Zone Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("health", health_check))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    # Run bot
    # Always use polling mode for simplicity
    logger.info("🔄 Starting polling mode...")
    print("✅ Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
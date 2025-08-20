import logging
import os  # Added to access environment variables
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
BOT_TOKEN = os.getenv("BOT_TOKEN")  # <<< Reads token from environment variable
CITIES_PER_PAGE = 6  # number of city buttons per page

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
    "St. John’s": "America/St_Johns",
    "Thunder Bay": "America/Toronto",
    "Waterloo": "America/Toronto",
}

# ---------------------- LOGGING ----------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
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

    return InlineKeyboardMarkup(keyboard)


def get_local_time(city: str) -> str:
    """Return formatted local time for a given city."""
    try:
        tz_name = CITY_TIMEZONES[city]
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        return now.strftime("%I:%M:%S %p")
    except Exception as e:
        logger.error(f"Error fetching time for {city}: {e}")
        return "Timezone not found."


# ---------------------- HANDLERS ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Please choose a city to get the current local time:",
        reply_markup=build_keyboard(page=0),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses from inline keyboard."""
    query = update.callback_query
    await query.answer()  # remove "loading..."

    if query.data.startswith("city:"):
        city = query.data.split(":", 1)[1]
        time_str = get_local_time(city)
        await query.message.reply_text(f"🕑 {city}\nCurrent time: {time_str}")

    elif query.data.startswith("page:"):
        page = int(query.data.split(":", 1)[1])
        await query.edit_message_reply_markup(reply_markup=build_keyboard(page))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


# ---------------------- MAIN ----------------------
def main():
    """Run the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Please set the environment variable.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling()


if __name__ == "__main__":
    main()


from amazon_bot import AmazonBot
from constants import ITEMS

# Create bot
bot = AmazonBot(ITEMS)
# Search for the items
bot.search_items()
# Create excel from data extracted
bot.generate_excel()

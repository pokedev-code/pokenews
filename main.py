import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks, commands
import os

intents = discord.Intents.default()
intents.message_content = True  # Required for message content access
bot = commands.Bot(command_prefix='!', intents=intents)
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL'))
LAST_CHECKED_FILE = 'last_checked.txt'


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_news.start()


@tasks.loop(minutes=30)  # Check every 30 minutes
async def check_news():
    channel = bot.get_channel(CHANNEL_ID)
    new_links = get_new_pokebeach_news()

    for link in new_links:
        await channel.send(f"New Pokébeach article: {link}")


def get_new_pokebeach_news():
    url = 'https://www.pokebeach.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.select('.post-title a')
    new_links = []

    try:
        with open(LAST_CHECKED_FILE, 'r') as f:
            last_checked = f.read().splitlines()
    except FileNotFoundError:
        last_checked = []

    for article in articles:
        link = article['href']
        if link not in last_checked:
            new_links.append(link)

    # Update last checked
    with open(LAST_CHECKED_FILE, 'w') as f:
        f.write('\n'.join([article['href'] for article in articles]))

    return new_links


# Command to manually check news
@bot.command()
async def updatenews(ctx):
    new_links = get_new_pokebeach_news()
    if new_links:
        await ctx.send(f"New updates found: {len(new_links)}")
    else:
        await ctx.send("No new articles found")


if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
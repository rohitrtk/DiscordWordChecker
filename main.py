import discord
import replit
import os

from discord.ext import commands
from dotenv import load_dotenv

# Constants
CMD_IDENTIFIER = '$'

CMD_ADD_WORD = 'aw'
CMD_REM_WORD = 'rw'

CMD_ADD_USER = 'au'
CMD_REM_USER = 'ru'

CMD_GET_WORDS = 'gw'
CMD_GET_USERS = 'gu'

CMD_PURGE_WORDS = 'pw'
CMD_PURGE_USERS = 'pu'

DB_WORDS = 'WORDS'
DB_USERS = 'USERS'

load_dotenv(os.path.join('venv/', '.env'))
client = commands.Bot(command_prefix=CMD_IDENTIFIER)
db = replit.Database(os.getenv('DB_URL'))

### Word commands

"""
Adds a word to the database.
"""
@client.command(name='AddWord', aliases=[CMD_ADD_WORD])
async def add_word(ctx, *args):
    if len(args) == 0:
        return
    
    word = args[0]

    if DB_WORDS not in db.keys():
        db[DB_WORDS] = [word]
    
    word = args[0].lower()
    words = db[DB_WORDS]
    
    if word in words:
        await ctx.send('{0} is already in the database.'.format(word))
        return
    
    words.append(word)

    db[DB_WORDS] = words
    await ctx.send('{0} successfuly added to the database.'.format(word))

"""
Removes a word from the database.
"""
@client.command(aliases=[CMD_REM_WORD])
async def remove_word(ctx, *args):
    await ctx.send('Deleting word!')

"""
Gets a list of all words in the database and sends
it as a discord message.
"""
@client.command(aliases=[CMD_GET_WORDS])
async def get_words(ctx):
    await ctx.send('Getting words!')

"""
Removes all words from the database.
"""
@client.command(aliases=[CMD_PURGE_WORDS])
async def purge_words(ctx):
    await ctx.send('Purging words!')

### User commands

"""
Adds a user to the database.
"""
@client.command(aliases=[CMD_ADD_USER])
async def add_user(ctx, *args):
    await ctx.send('Adding user!')

"""
Removes a user from the database.
"""
@client.command(aliases=[CMD_REM_USER])
async def remove_user(ctx, *args):
    await ctx.send('Deleting user!')

"""
Gets a user from the database.
"""
@client.command(aliases=[CMD_GET_USERS])
async def get_users(ctx):
    await ctx.send('Getting users!')

"""
Removes all users from the database.
"""
@client.command(aliases=[CMD_PURGE_USERS])
async def purge_users(ctx):
    await ctx.send('Purging users!')

### ### ###

"""
Called when bot has finished starting up.
"""
@client.event
async def on_ready():
    print('Bot running')

"""
Called when their is a message is sent in discord
"""
@client.event
async def on_message(ctx):
    # Stop the bot responding to itself
    if ctx.author == client.user:
        return

    await client.process_commands(ctx)

client.run(os.getenv('BOT_TOKEN'))
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

### Helpers

"""
Checks if the database exists. If it doesn't, create it.
"""
async def check_db_exists(ctx, name, init, msg=None):
    if name not in db.keys():
        db[name] = init
        
        if msg == None:
            return
        
        await ctx.send(msg)
        
        return False
    return True
    

### Word commands

"""
Adds a word to the database.
"""
@client.command(name='AddWord', aliases=[CMD_ADD_WORD])
async def add_word(ctx, *args):
    if len(args) == 0:
        return
    
    word = args[0]

    await check_db_exists(ctx, DB_WORDS, [word])
    
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
    if len(args) == 0:
        return

    word = args[0]

    if not await check_db_exists(ctx, DB_WORDS, [], '{0} does not exist in the database'.format(word)):
        return

    words = db[DB_WORDS]

    try:
        words.remove(word)
        await ctx.send('Successfully removed {0} from the database.'.format(word))
    except ValueError:
        await ctx.send('{0} does not exist in the database.'.format(word))

"""
Gets a list of all words in the database and sends
it as a discord message.
"""
@client.command(aliases=[CMD_GET_WORDS])
async def get_words(ctx):
    await check_db_exists(ctx, DB_WORDS, [])

    words = db[DB_WORDS]
    length = len(words)

    if length == 0:
        await ctx.send('There are currently no words in the database.')
        return
    elif length == 1:
        await ctx.send('The only word in the database is: {0}'.format(words[0]))
        return

    s = ''
    for i in range(0, length):
        s += words[i]
        
        if i == length - 2:
            s += ', and '
        elif i != length - 1:
            s += ', '
    
    await ctx.send('The words currently in the database are: {0}.'.format(s))


"""
Removes all words from the database.
"""
@client.command(aliases=[CMD_PURGE_WORDS])
async def purge_words(ctx):
    db[DB_WORDS] = []
    
    await ctx.send('Purged all words from the database.')

### User commands

"""
Adds a user to the database.
"""
@client.command(aliases=[CMD_ADD_USER])
async def add_user(ctx, *args):
    if len(args) == 0:
        return
    
    await check_db_exists(ctx, DB_USERS, {})

    users = db[DB_USERS]
    user = args[0]

    if user in users:
        await ctx.send('User {0} is already in the database.'.format(user))
        return

    users[user] = {}
    db[DB_USERS] = users
    
    await ctx.send('Now tracking user {0}.'.format(user))


"""
Removes a user from the database.
"""
@client.command(aliases=[CMD_REM_USER])
async def remove_user(ctx, *args):
    user = args[0]
    
    if not await check_db_exists(ctx, DB_USERS, {}, 'User {0} does not exist in the database.'.format(user)):
        return

    users = db[DB_USERS]

    if user in users.keys():
        users.pop(user, None)
        await ctx.send('Successully removed user {0} from the database.'.format(user))
    else:
        await ctx.send('User {0} does not exist in the database.'.format(user))        

"""
Gets a user from the database.
"""
@client.command(aliases=[CMD_GET_USERS])
async def get_users(ctx):
    await check_db_exists(ctx, DB_USERS, {})

    users = list(db[DB_USERS].keys())
    length = len(users)

    if length == 0:
        await ctx.send('There are currently no users in the database.')
    elif length == 1:
        await ctx.send('The only user in the database is: {0}.'.format(users[0]))
    else:
        s = ''
        for i in range(0, len(users)):
            s += users[i]
            
            if i == length - 2:
                s += ', and '
            elif i != length - 1:
                s += ', '

        await ctx.send('The users currently in the database are: {0}.'.format(s))

"""
Removes all users from the database.
"""
@client.command(aliases=[CMD_PURGE_USERS])
async def purge_users(ctx):
    db[DB_USERS] = {}

    await ctx.send('Purged all users from the database.')

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
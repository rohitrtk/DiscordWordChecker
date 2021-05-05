import discord
import replit
import os
import re

from discord.ext import commands
from dotenv import load_dotenv

from ping import keep_running

# Constants
CMD_IDENTIFIER = '$'

CMD_ADD_WORD = ['addword', 'aw']
CMD_REM_WORD = ['removeword' 'rw']

CMD_ADD_USER = ['adduser', 'au']
CMD_REM_USER = ['removeuser', 'ru']

CMD_GET_WORDS = ['getwords', 'gw']
CMD_GET_USERS = ['getusers', 'gu']

CMD_PURGE_WORDS = ['purgewords', 'pw']
CMD_PURGE_USERS = ['purgeusers', 'pu']

DB_WORDS = 'WORDS'
DB_USERS = 'USERS'

# Load .env
load_dotenv(os.path.join('venv/', '.env'))

# Create client
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=CMD_IDENTIFIER, intents=intents)

# Get database
db = replit.Database(os.getenv('DB_URL'))

# Purge stuff
try_purge_words, try_purge_users = False, False

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
@client.command(name='AddWord', aliases=CMD_ADD_WORD)
async def add_word(ctx, *args):
    if len(args) == 0:
        return

    word = ''.join(args).lower().replace(' ', '')

    await check_db_exists(ctx, DB_WORDS, [word])
    
    words = db[DB_WORDS]
    
    # Construct regex
    word_as_chars = [char for char in word]
    regex = '.'.join(word_as_chars) + '|' + '*'.join(word_as_chars)

    for word in words:
        if re.match(regex, word):
            await ctx.send('{0} is already in the database.'.format(word))
            return
    
    words.append(word)

    db[DB_WORDS] = words
    await ctx.send('{0} successfuly added to the database.'.format(word))


"""
Removes a word from the database.
"""
@client.command(name='RemoveWord', aliases=CMD_REM_WORD)
async def remove_word(ctx, *args):
    if len(args) == 0:
        return

    word = args[0].lower().replace(' ', '')

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
@client.command(name='GetWords', aliases=CMD_GET_WORDS)
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
@client.command(name='PurgeWords', aliases=CMD_PURGE_WORDS)
async def purge_words(ctx):
    global try_purge_words

    if not try_purge_words:
        try_purge_words = True
        await ctx.send('Do you really want to purge all words from the database? Use the command again if you really want to.')
        
        return

    db[DB_WORDS] = []
    
    try_purge_words = False

    await ctx.send('Purged all words from the database.')

### User commands

"""
Adds a user to the database.
"""
@client.command(name='AddUser', aliases=CMD_ADD_USER)
async def add_user(ctx, *args):
    if len(args) == 0:
        return
    
    await check_db_exists(ctx, DB_USERS, {})

    users = db[DB_USERS]
    user = args[0]

    members = [member.name + '#' + member.discriminator for member in client.get_all_members()]

    if user not in members:
        await ctx.send('Could not find member with that username.')
        return

    if user in users:
        await ctx.send('User {0} is already in the database.'.format(user))
        return

    users[user] = {}
    db[DB_USERS] = users
    
    await ctx.send('Now tracking user {0}.'.format(user))


"""
Removes a user from the database.
"""
@client.command(name='RemoveUser', aliases=CMD_REM_USER)
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
@client.command(name='GetUsers', aliases=CMD_GET_USERS)
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
@client.command(name='PurgeUsers', aliases=CMD_PURGE_USERS)
async def purge_users(ctx):
    global try_purge_users

    if not try_purge_users:
        try_purge_users = True
        await ctx.send('Do you really want to purge all users from the database? Type the command again if you really want to.')
        
        return

    db[DB_USERS] = {}

    try_purge_users = False

    await ctx.send('Purged all users from the database.')

### ### ###

"""
Called when a user sends a discord message. Check if the message author
is being tracked. If they are, check if the message contains any words
that are being tracked. If there is a word, update the number of times
the user has said that word.
"""
async def check_message(ctx):
    words_msg = ctx.content.split()
    author = str(ctx.author)
    users = db[DB_USERS]

    if author not in users:
        return

    words = db[DB_WORDS]

    for word in words_msg:
        # Remove whitespace and convert string to lower case
        word = word.replace(' ', '').lower()
        
        # Construct regex
        word_as_chars = [char for char in word]
        regex = '.'.join(word_as_chars) + '|' + '*'.join(word_as_chars)

        for word in words:
            if re.match(regex, word):
                user = users[author]

                if word in user.keys():
                    user[word] += 1
                else:
                    user[word] = 1

                output_msg = '{0} has said {1} {2} times.'.format(ctx.author.mention, word, user[word])
                await ctx.channel.send(output_msg)


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

    if ctx.content[0] == CMD_IDENTIFIER:
        await client.process_commands(ctx)
    else:
        await check_message(ctx)

keep_running()
client.run(os.getenv('BOT_TOKEN'))
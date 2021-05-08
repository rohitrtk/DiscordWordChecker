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
CMD_REM_WORD = ['removeword', 'rw']

CMD_ADD_USER = ['adduser', 'au']
CMD_REM_USER = ['removeuser', 'ru']

CMD_GET_WORDS = ['getwords', 'gw']
CMD_GET_USERS = ['getusers', 'gu']

CMD_PURGE_WORDS = ['purgewords', 'pw']
CMD_PURGE_USERS = ['purgeusers', 'pu']

DB_NAME = 'USERS'

# If i'm debugging the bot
debug = True

# Load .env
load_dotenv(os.path.join('venv/', '.env'))

# Create client
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=CMD_IDENTIFIER, intents=intents)

# Database setup
db = replit.Database(os.getenv('DB_URL'))
if DB_NAME not in db.keys():
    db[DB_NAME] = {}

database = db[DB_NAME]

# Purge stuff
try_purge_words, try_purge_users = False, False

### Helpers

def print_debug(s):
    """
    Debug print function.
    """
    global debug

    if debug:
        print('DEBUG: ' + s)


async def user_exists_in_server(ctx, username):
    """
    Return True if the given username exists in the server. Otherwise, return False.
    """
    members = [member.name + '#' + member.discriminator for member in client.get_all_members()]

    if username in members:
        return True
    return False


### Word commands

@client.command(name='AddWord', aliases=CMD_ADD_WORD)
async def add_word(ctx, username, word):
    """
    Adds a word to a specific users dictionary.
    """
    global database

    if username not in database.keys():
        await ctx.send('Unable to add word. {0} is not currently being tracked.'.format(username))

    word = ''.join(word).lower().replace(' ', '')    
    
    words = database[username]

    # Construct regex
    word_as_chars = [char for char in word]
    regex = '.'.join(word_as_chars) + '|' + '*'.join(word_as_chars)
    
    for w in words.keys():
        if re.match(regex, w):
            await ctx.send('{0} is already in the database.'.format(w))
            return
    
    words[word] = 0

    await ctx.send('{0} successfuly added to the database.'.format(word))


@client.command(name='RemoveWord', aliases=CMD_REM_WORD)
async def remove_word(ctx, username, word):
    """
    Removes a word from the database.
    """
    global database

    word = word.lower().replace(' ', '')

    if username not in database.keys():
        await ctx.send('{0} is not in the database.'.format(username))
        return

    if word not in database[username].keys():
        await ctx.send('Not tracking the word {0} for user {1}.'.format(word, username))
        return

    del database[username][word]
    await ctx.send('Removed {0} from {1}\'s database.'.format(word, username))


@client.command(name='GetWords', aliases=CMD_GET_WORDS)
async def get_words(ctx, username):
    """
    Gets a list of all words in the database and sends
    it as a discord message.
    """
    global database
    
    if username not in database.keys():
        await ctx.send('That user does not exist.')
        return

    words = list(database[username].keys())
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


@client.command(name='PurgeWords', aliases=CMD_PURGE_WORDS)
async def purge_words(ctx, username):
    """
    Removes all words from the database.
    """
    global try_purge_words

    if username not in database.keys():
        await ctx.send('User {0} does not exist in the database.'.format(username))
        return

    if not try_purge_words:
        try_purge_words = True
        await ctx.send('Do you really want to purge all words from the database? Use the command again if you really want to.')
        
        return

    database[username] = {}
    
    try_purge_words = False

    await ctx.send('Purged all words for user: {0}.'.format(username))

### User commands

@client.command(name='AddUser', aliases=CMD_ADD_USER)
async def add_user(ctx, *args):
    """
    Adds a user to the database.
    """
    global database

    if len(args) == 0:
        await ctx.send('Invalid command arguments.')
        return

    users = database.keys()
    user = args[0]

    members = [member.name + '#' + member.discriminator for member in client.get_all_members()]

    if user not in members:
        await ctx.send('Could not find member with that username.')
        return

    if user in users:
        await ctx.send('User {0} is already in the database.'.format(user))
        return

    database[user] = {}
    ddatabase = users
    
    await ctx.send('Now tracking user {0}.'.format(user))


@client.command(name='RemoveUser', aliases=CMD_REM_USER)
async def remove_user(ctx, username):
    """
    Removes a user from the database.
    """
    global database

    users = database.keys()

    if username not in database.keys():
        await ctx.send('User {0} does not exist in the database.'.format(user))
        return

    database.pop(user)
    await ctx.send('Successully removed user {0} from the database.'.format(user))


@client.command(name='GetUsers', aliases=CMD_GET_USERS)
async def get_users(ctx):
    """
    Gets a user from the database.
    """
    global database

    users = list(database.keys())
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


@client.command(name='PurgeUsers', aliases=CMD_PURGE_USERS)
async def purge_users(ctx):
    """
    Removes all users from the database.
    """
    global try_purge_users, database

    if not try_purge_users:
        try_purge_users = True
        await ctx.send('Do you really want to purge all users from the database? Type the command again if you really want to.')
        
        return

    database = {}
    try_purge_users = False

    await ctx.send('Purged all users from the database.')

### ### ###

async def check_message(ctx):
    """
    Called when a user sends a discord message. Check if the message author
    is being tracked. If they are, check if the message contains any words
    that are being tracked. If there is a word, update the number of times
    the user has said that word.
    """
    author = str(ctx.author)
    users = database.keys()
    words_msg = ctx.content.split()

    if author not in users:
        return

    words = database[author]

    for w in words_msg:
        # Remove whitespace and convert string to lower case
        word = w.replace(' ', '').lower()
        
        # Construct regex
        word_as_chars = [char for char in word]
        regex = '.'.join(word_as_chars) + '|' + '*'.join(word_as_chars)

        for word in words:
            if re.match(regex, word):
                user = database[author]

                if word in user.keys():
                    user[word] += 1

                output_msg = '{0} has said {1} {2} times.'.format(ctx.author.mention, word, user[word])
                await ctx.channel.send(output_msg)


@client.event
async def on_ready():
    """
    Called when bot has finished starting up.
    """
    print('Bot running')


@client.event
async def on_message(ctx):
    """
    Called when their is a message is sent in discord
    """
    # Stop the bot responding to itself
    if ctx.author == client.user:
        return

    if ctx.content[0] == CMD_IDENTIFIER:
        await client.process_commands(ctx)
    else:
        await check_message(ctx)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('Unknown command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('An error occured whilst trying to run your command. Missing required arguments.')
    else:
        await ctx.send('Wtf happened Rohit?')
        print(error)

### MAIN ###

if __name__ == '__main__':
    if not debug:
        keep_running()

    client.run(os.getenv('BOT_TOKEN'))
import discord
import replit
import os
import re

from discord.ext import commands
from dotenv import load_dotenv

from errors import ErrorMessageGenerator

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

CMD_GET_USER_WORDS_COUNT = ['getuserwordscount', 'guwc']
CMD_GET_ALL_USER_WORDS_COUNT = ['alluserwordscountall', 'auwc']

CMD_ENABLE = ['enable', 'en']

DB_NAME = 'USERS'

# Dynamics
debug = True
enable = True

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
try_purge_words = False
try_purge_users = False
try_disable_bot = False

# Error message stuff
emg = ErrorMessageGenerator('venv/error_messages.txt')

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


async def user_exists_in_db(ctx, username):
    """
    Return True if the username exists in the database. Otherwise, return False.
    """
    if username not in database.keys():
        return False
    return True

### Word commands

@client.command(name='AddWord', aliases=CMD_ADD_WORD)
async def add_word(ctx, username, *word_list):
    """
    Adds words to a users database.
    """
    global database

    if len(word_list) == 0:
        raise commands.errors.MissingRequiredArgument

    if not await user_exists_in_db(ctx, username):
        await ctx.send('Unable to add word. {0} is not in the database.'.format(username))

    for word in word_list:
        word = ''.join(word).lower().replace(' ', '')
        
        words = database[username]

        # Construct regex
        word_as_chars = [char for char in word]
        regex = '+'.join(word_as_chars)
        
        for w in words.keys():
            if re.match(regex, w):
                await ctx.send('{0} is already in the database.'.format(w))
                continue
        
        words[word] = 0

        await ctx.send('{0} successfuly added to the database.'.format(word))


@client.command(name='RemoveWord', aliases=CMD_REM_WORD)
async def remove_word(ctx, username, *word_list):
    """
    Removes words from a users database.
    """
    global database

    if len(word_list) == 0:
        raise commands.errors.MissingRequiredArgument

    if not await user_exists_in_db(ctx, username):
        await ctx.send('{0} is not in the database.'.format(username))
        return

    for word in word_list:
        word = word.lower().replace(' ', '')

        if word not in database[username].keys():
            await ctx.send('Not tracking the word {0} for user {1}.'.format(word, username))
            continue

        del database[username][word]
        await ctx.send('Removed {0} from {1}\'s database.'.format(word, username))


@client.command(name='GetWords', aliases=CMD_GET_WORDS)
async def get_words(ctx, username):
    """
    Gets a list of all words in the database and sends
    it as a discord message.
    """
    global database
    
    if not await user_exists_in_db(ctx, username):
        await ctx.send('User {0} does not exist in the database.'.format(username))
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

    if not await user_exists_in_db(ctx, username):
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
async def add_user(ctx, *user_list):
    """
    Adds a user to the database.
    """
    global database

    if len(user_list) == 0:
        raise commands.errors.MissingRequiredArgument

    members = [member.name + '#' + member.discriminator for member in client.get_all_members()]
    users = database.keys()

    for user in user_list:
        if user not in members:
            await ctx.send('Could not find member with that username.')
            continue

        if user in users:
            await ctx.send('User {0} is already in the database.'.format(user))
            continue

        database[user] = {}
        
        await ctx.send('Now tracking user {0}.'.format(user))


@client.command(name='RemoveUser', aliases=CMD_REM_USER)
async def remove_user(ctx, *user_list):
    """
    Removes a user from the database.
    """
    global database

    if len(user_list) == 0:
        raise commands.errors.MissingRequiredArgument

    for user in user_list:
        if not await user_exists_in_db(ctx, user):
            await ctx.send('User {0} does not exist in the database.'.format(user))
            continue

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


@client.command(name='GetUserWordsCount', aliases=CMD_GET_USER_WORDS_COUNT)
async def get_user_words_count(ctx, username):
    """
    Lists the count for all words for a user.
    """
    global database

    if not await user_exists_in_db(ctx, username):
        await ctx.send('User {0} does not exist in the database.'.format(username))
        return

    for word in database[username].keys():
        await ctx.send('{0} has said {1}, {2} times.'.format(username, word, database[username][word]))


@client.command(name='AllUserWordsCount', aliases=CMD_GET_ALL_USER_WORDS_COUNT)
async def get_all_user_words_count(ctx):
    """
    Lists the word count for all users.
    """
    global database

    for username in database.keys():
        for word in database[username].keys():
            await ctx.send('{0} has said {1}, {2} times.'.format(username, word, database[username][word]))


@client.command(name='Enable', aliases=CMD_ENABLE)
@commands.has_role('Admin')
async def activate_bot(ctx, option):
    """
    Enables/Disables the bot.
    """
    if option == 'enable':
        if enable:
            return
        enable = True
        ctx.send('I am no enabled.')
    elif option == 'disable':
        if not enable:
            return
        enable = False
        ctx.send('I am now disabled.')
    else:
        ctx.send('Unknown parameter {0}.'.format(option))


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

    words_in_database = database[author]

    for word in words_in_database:
        w = word.replace(' ', '').lower()

        word_as_char = [char for char in w]
        regex = '+'.join(word_as_char) + '+'

        for word_input in words_msg:
            if not re.match(regex, word_input):
                continue
        
            user = database[author]

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
    if ctx.author == client.user or not enable:
        return

    if ctx.content[0] == CMD_IDENTIFIER:
        await client.process_commands(ctx)
    else:
        await check_message(ctx)


@client.event
async def on_command_error(ctx, error):
    """
    Called when an error is thrown when using a command.
    """
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('Unknown command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('An error occured whilst trying to run your command. Missing required arguments.')
    else:
        await ctx.send(emg.get_random_message())
        print(error)

### MAIN ###

if not debug:
    keep_running()

client.run(os.getenv('BOT_TOKEN'))
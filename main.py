#!/usr/bin/discord-bot/venv/bin/python3

import os
import random
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')

intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

bedtime_quotes = [
        'Good night!',
        'Halleluja',
        'Sleep tight!',
        'Good job!'
    ]

random_affirm = [
    'Bitchen!',
    'Roger Roger',
    'Yessir.',
    'It shall be so.'
]

random_negative = [
    'Sorry, that failed.',
    'Moop. Sorry!',
    'Alas, I have failed at that command.'
]

@bot.command(name='bedtime', help="Turns off the lights")
async def bedtime(ctx):
    """Triggers bedtime via server"""

    response = requests.post(f"http://{SERVER_IP}/lighting/bedtime")

    if response.status_code == 200:
        message = random.choice(bedtime_quotes)
    else:
        message = "Bedtime failed, sorry!"
    await ctx.send(message)

@bot.command(name='landscape', help="Trigger the landscape lights (on/off)")
async def landscape_on(ctx, request):
    """Triggers landscape lighting on or off via server"""
    if not request:
        await ctx.send('I need to know what to do with the lights! (on/off)')
        return
    if request.lower() not in ['on', 'off']:
        await ctx.send('Please specify ON or OFF!')
        return
    state = False
    if request.lower() == 'on':
        state = True

    response = requests.post(f"http://{SERVER_IP}/landscape/change-state", json={"state": state})

    if response.status_code == 201:
        message = random.choice(random_affirm)
    else:
        message = random.choice(random_negative)
    await ctx.send(message)

@bot.command(name='pool-temp', help="Change the set pool temp in F (i.e. !pool-temp 85)")
async def pool_change(ctx, request=None):
    """Changes pool set temp based on param provided via server"""
    if not request:
        await ctx.send('Please pass a valid temperature!')
        return
    try:
        int(request)
    except ValueError:
        await ctx.send('Please pass a valid temperature!')
        return
    response = requests.post(f"http://{SERVER_IP}/pool/temp/set-temp", json={"setting": request})

    if response.status_code == 201:
        message = random.choice(random_affirm)
    else:
        message = random.choice(random_negative)
    
    await ctx.send(message)

@bot.command(name='pool-info', help="See current pool temps")
async def pool_info(ctx):
    """Gathers current pool status from server and sends as message"""

    valve = "closed"

    response = requests.get(f"http://{SERVER_IP}/pool/status")
    data = response.json()
    
    if response.status_code == 200:
        if data['valve'] == 1:
            valve = "open"
        
        message = f"""Solar valve is currently {valve}.\nPool temp is currently {data['water_temp']}°F.\nRoof sensor is reading: {data['roof_temp']}°F.\nSet temp is {data['set_temp']}°F."""
    else:
        message = random.choice(random_negative)
    
    await ctx.send(message)

@bot.command(name='climate-info', help="See current house climate")
async def pool_info(ctx):
    """Gathers current climate data from server and sends back as message"""

    response = requests.get(f"http://{SERVER_IP}/climate/current_temps")
    data = response.json()
    
    if response.status_code == 200:
        message = f"""Temp at thermostat {int(data['thermostat'])}°F.\nTemp at server {int(data['living_room'])}°F.\nTemp outside {int(data['outside'])}°F.\nTemp in garage {data['garage']}°F.\nBarometric Pressure {data['pressure']}mb."""
    else:
        message = random.choice(random_negative)
    
    await ctx.send(message)

if __name__ == "__main__":
    bot.run(TOKEN)

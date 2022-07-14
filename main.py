# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 13:22:55 2022

@author: Ethan
"""

# tutorial link: https://www.youtube.com/watch?v=fU-kWx-OYvE

# bot invite url (paste into browser): 
# https://discord.com/api/oauth2/authorize?client_id=996826543286386858&permissions=532576467008&scope=bot

#import aiohttp
# import nest_asyncio
# nest_asyncio.apply()
# __import__('IPython').embed()


import discord
import random
import re
import time
import os

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_NAME = 'general'

client = discord.Client()



lip_words_ed = []
lip_words_er = []
lip_words_other = []

@client.event
async def on_ready():
    print('we have logged in as {0.user}'.format(client))
    
@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    m = user_message.lower()
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')
    
    # make sure bot doesn't respond to itself
    if message.author == client.user:
        return
    
    # only respond in designated channel
    if m == CHANNEL_NAME:
        if m == 'hello':
            await message.channel.send(f'Hello {username}!')
            return
        elif m == 'bye':
            await message.channel.send(f'See you later {username}!')
            return
        elif m == '!random':
            response = f'This is your random number: {random.randrange(100000)}'
            await message.channel.send(response)
            return
    
    # if you don't check channel name, bot can respond anywhere
    if m == '!anywhere':
        await message.channel.send('this command can be used anywhere!')
        return
    
    if 'lip' in m:
        lip_token = random.choice([t for t in m.split() if 'lip' in t])
        await message.channel.send(f'{lip_token} lipped lipid licker')
        return
    
    if message_is_wordle(m):
        await message.channel.send('ayyyyyyy its wordle!')
        return
    else:
        await message.channel.send('not wordle...')
        return
    
    
        
def message_is_wordle(m):
    return ('wordle' in m) and re.search('[🟨🟩⬛]{5,6}', m) 
    

if __name__ == '__main__':
    client.run(TOKEN)

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
import re
import os
import time

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_NAME = 'general'

# client = discord.Client()
intents = discord.Intents(messages=True, message_content=True, guilds=True, guild_messages=True)
client = discord.Client(intents=intents)

# client = discord.Client(intents=discord.Intents().all())

import tracery
from tracery.modifiers import base_english

# put your grammar here as the value assigned to "rules"
rules = {
    # a lip phrase is two parts: 
    # PART1: Noun + ING-Verb, or ADJ/[some_nouns]-lipped)
    # PART2: Noun + ER-verb
    "lip_phrase": ["#lip_part_1# #lip_part_2#"],
    "lip_part_1": ["#lip_noun# #lip_verb_ing#", "#lipped_prefix#-lipped"],
    "lip_part_2": ["#lip_noun# #lip_verb_er#"],
    "lip_noun": ["lip", "lip", "liver", "lint", 'lard', "ligament", "libertarian", "ligma", "librarian", 
                 "liquorice", "liquid", "lizard", "liquor", "lichen", "lipid", "leg", 
                 "limb", "litter", "lettuce", "laundry", "laser", "quiver"],
    "lip_adj": ["limp", "limp", "linear", "lithospheric", "liquidy", "limber",
                "lippy", "limy", "lit", "literal", "little", "lanky"],
    "lip_verb_ing": ["licking", "licking", "lipping", "loving"],
    "lip_verb_er": ["licker", "licker", "lipper", "lifter", "flipper", "slipper", 
                    "lover", "liquefier"],
    "lipped_prefix": ["#lip_adj#", "#lip_noun#"],
    
    "rolled": ["rolled like #roll_thing_singular##modifier#.", "rolled harder than #roll_thing_singular##modifier#."],
    "modifier": [" on #thing_on#", " in #thing_in#", " covered in #roll_thing_plural#", " #attached_to# #roll_thing_singular#", " made of #roll_thing_plural#"],
    "roll_thing_singular": ["a cinnamon roll", "a fruit roll-up", "a rolling pin", 
                            "a tyrannosrollus rex", "a bean burrito", "a Ferrari#wheel_modifier#",
                            "a pizza roll", "a sushi roll", "a spring roll", "a tootsie roll", 
                            "a pinewood derby car#wheel_modifier#", "an ankle", "a D20", "Hammond from Overwatch", 
                            "a bacci ball", "a dung beetle pushing #roll_thing_singular#",
                            "a wheel of parmagiano romano", "a pillbug",
                            "Louis XVI's head in the french revolution", "a coconut",
                            "thomas the tank engine#wheel_modifier#", "a roll of toilet paper", 
                            "a hay bale", "that one cart wheel that refuses to cooperate but you already took the cart and there's people behind you so you're stuck with it and you should have just gotten a basket for the two things you needed but now i guess i'm gonna drag this heavy-ass hunk of metal around wegmans until the fucking rubber melts into the floor tiles#wheel_modifier#",
                            "an armadillo", "a pencil dropped during a math exam", 
                            "Wario's motorbike#wheel_modifier#", "a boulder", "a can of beans",
                            "a very round loaf of bread", "a restless baby", "a tumbleweed"],
    "wheel_modifier": ["", " with wheels made of #roll_thing_plural#", " with wheels made of #roll_thing_plural#"],          
    "roll_thing_plural": ["heads during the french revolution", "tumbleweeds",
                          "cinnamon rolls", "fruit roll-ups", "rolling pins", 
                            "bean burritos", 
                            "pizza rolls", "sushi rolls", "spring rolls", "tootsie rolls", 
                            "pinewood derby cars#wheel_modifier#", "ankles", "D20s", "Hammonds from Overwatch", 
                            "bacci balls", "dung beetles pushing #roll_thing_plural#",
                            "wheels of parmagiano romano",  
                            "heads in the french revolution", "coconuts",
                            "rolls of toilet paper", "restless babies", "pillbugs",
                            "hay bales", "those cart wheels that refuse to cooperate but you already took the cart and there's people behind you so you're stuck with it and you should have just gotten a basket for the two things you needed but now i guess i'm gonna drag this heavy-ass hunk of metal around wegmans until the fucking rubber melts into the floor tiles",
                            "armadillos", "pencils dropped during a math exam", 
                            "Wario's motorbikes#wheel_modifier#", "boulders", "cans of beans",
                            "very round loaves of bread"],
    "thing_on": ["a hill", "a treadmill", "a skateboard", "rollerskates", "ecstasy", "a windmill", 
                 "a rollercoaster", "a yo-yo", "a slip 'n' slide", "#roll_thing_singular#"],
    "thing_in": ["a rock tumbler", "a washing machine", "an industrial centrifuge", "a hurricane", 
                 "a wind tunnel", "a cocktail shaker", "a gymnastics class", "a parkour video", 
                 "a salad spinner", "the back of an Amazon delivery van"],
    "attached_to": ["stapled to", "welded to", "glued to", "in orbit with", "duct taped to", 
                    "magically fused with"]
}

grammar = tracery.Grammar(rules) # create a grammar object from the rules
grammar.add_modifiers(base_english) # add pre-programmed modifiers
# print(grammar.flatten("#lip_phrase#")) # and flatten, starting with origin rule




# -----------------------
# Bot Commands
# -----------------------


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
    if message.channel.name == 'general':
        if m == '!hello':
            await message.channel.send(f'Hello {username}!')
            return
    
    # if you don't check channel name, bot can respond anywhere
    if any(x in m.split() for x in ['!lip', 'lip', 'lipped', 'lipping', 'lipper', 'licker', '!lip']):
        # lip_token = random.choice([t for t in m.split() if 'lip' in t]) # TODO: incorporate the word containing 'lip'
        await message.channel.send(grammar.flatten("#lip_phrase#"))
        return
    
    # command version of the 'rolled' message
    if '!rolled' in m:
        await message.channel.send(grammar.flatten("#rolled#"))
        return
    
    # if the message is a wordle score, reply with the 'rolled' message
    if message_is_wordle(m):
        time.sleep(2)
        await message.channel.send(grammar.flatten("#rolled#"))
        return
    
    if 'good bot' in m:
        await message.channel.send('♥')
        return

    if 'bad bot' in m:
        await message.channel.send('sorry')
        return

    
        
def message_is_wordle(m):
    # returns true if message is a pasted wordle score
    return ('dle' in m) and re.search('[🟨🟩⬛]{5,6}', m) 
    






if __name__ == '__main__':
    client.run(TOKEN)

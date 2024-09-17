
import discord
from faq_bot_brain import *

class MyClient(discord.Client):

    """
    This is the constructor. Sets the default 'intents' for the bot.
    """
    def __init__(self):
        
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    
    """
    Called when the bot is fully logged in.
    
    """
    async def on_ready(self):
        print('Logged on as', self.user)

    
    """
    Called whenever the bot receives a message. The 'message' object
    contains all the pertinent information.
    """
    async def on_message(self, message):

        # don't respond to ourselves
        if message.author == self.user:
            return

        # get the utterance and generate the response
        utterance = message.content
        intent = understand(utterance)
        response = generate(intent)

        # send the response
        await message.channel.send(response)


## Set up and log in
client = MyClient()
with open("bot_token.txt") as file:
    token = file.read()
client.run(token)
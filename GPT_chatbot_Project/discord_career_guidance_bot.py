"""
Author: Maharshi Patel, 000738366
Date: 17-11-2024
Description: This script implements a Discord chatbot that uses the career_guidance_bot_brain.py's logic.
"""

import discord
from career_guidance_bot_brain import *

class MyClient(discord.Client):
    """
    Discord client class for the bot, handling bot events such as logging in and responding to messages.
    """

    def __init__(self):
        """
        Initializes the bot with default intents and enables message content reading.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        """
        Event handler called when the bot has successfully logged in.
        """
        print('Logged on as', self.user)

    async def on_message(self, message):
        """
        Event handler called when a message is received. Processes and responds to messages.

        Args:
            message (discord.Message): The message object containing information about the received message.
        """
        # Don't respond to the bot's own messages.
        if message.author == self.user:
            return

        # Process the message to generate a response.
        response = handle_user_input(message.content)

        # Send the generated response back to the channel where the message was received.
        await message.channel.send(response)


## Set up and log in
client = MyClient()
with open("bot_token.txt") as file:
    token = file.read()
client.run(token)
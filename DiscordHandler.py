import yaml
import sys
import logging
import discord
import asyncio
from threading import Thread

class DiscordHandler:

    token = None
    loop = None
    def __init__(self,token):
        self.token = token
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self.launch_bot()
        self.client.event(self.on_ready)

    @staticmethod
    async def on_ready():
        print("Bip Beep Bip... Discord bot started")

    def generate_discord_file(self,file):
        return discord.File(file)

    async def start(self):
        await self.client.start(self.token)

    def send_async_message(self,channel, message, files=None):
        if files:
            asyncio.run_coroutine_threadsafe(self.send_message_content(channel,message,files=files), self.loop)
        else:
            asyncio.run_coroutine_threadsafe(self.send_message_content(channel, message), self.loop)

    async def get_channel(self, channel_id):
        try:
            channel = self.client.get_channel(channel_id)
            return channel
        except Exception as e:
            print("[-] Error while fetching channel: " + str(e))
            return None

    async def get_channel_message(self, channel_id, message_id, files=None):
        try:
            chan = await self.get_channel(channel_id)
            message = await chan.fetch_message(message_id)
            return message
        except Exception as e:
            print("[-] Error while fetching message: " + str(e))
            return None

    async def send_message_content(self, channel_id, message, files=None):
        channel = await self.get_channel(channel_id)
        if files:
            await channel.send(message,suppress_embeds=True,files=files)
        else:
            await (channel.send(message,suppress_embeds=True))
        return True

    async def update_message_content(self, message, message_content, files=None):
        if files:
            await message.edit(content=message_content,files=files)
        else:
            await message.edit(content=message_content)
        return True

    def launch_bot(self):
        self.loop = asyncio.new_event_loop()
        self.loop.create_task(self.start())
        Thread(target=self.loop.run_forever).start()


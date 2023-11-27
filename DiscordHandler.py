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

    async def start(self):
        await self.client.start(self.token)

    def send_async_message(self,channel, message):
        asyncio.run_coroutine_threadsafe(self.send_message_content(channel,message), self.loop)

    async def send_message_content(self, channel_id, message):
        channel = self.client.get_channel(channel_id)
        await channel.send(message)
        return True

    def launch_bot(self):
        self.loop = asyncio.new_event_loop()
        self.loop.create_task(self.start())
        Thread(target=self.loop.run_forever).start()


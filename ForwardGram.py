from telethon import TelegramClient, events, sync
from telethon.tl.types import InputChannel
import yaml
import sys
import logging
import DiscordHandler
import subprocess
from googletrans import Translator
import re
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)

class Forwardgram:
    forward_settings = {}
    input_channels_entities = []
    def __init__(self, config):
        self.config = config
        self.client = TelegramClient(config["session_name"],
                                     config["api_id"],
                                     config["api_hash"])

        loop = asyncio.get_event_loop()  # Here
        self.discord = DiscordHandler.DiscordHandler(config["discord_bot_token"])
        self.client.start()
        self.client.add_event_handler(self.new_message_handler, events.NewMessage(chats=self.input_channels_entities))
        loop.run_until_complete(self.retrieve_config())
        print("Forwardram started, waiting for messages........")
        self.client.run_until_disconnected()

    @staticmethod
    def process_message(mess, dest_lang):
        out = {"tmessage": "", "confidence": 0, "olanguage": ""}
        if mess is not None:
            mess_txt = '"' + mess + '"'
        else:
            mess_txt = "None"
        if mess_txt != "None":
            translator = Translator()
            detection = translator.detect(mess_txt)
            translation_confidence = detection.confidence
            translation = translator.translate(mess_txt,dest=dest_lang)
            original_language = translation.src
            translated_text = translation.text
            out = {"tmessage": translated_text, "confidence": translation_confidence, "olanguage": original_language, "omessage": mess_txt}
        return out

    async def retrieve_config(self):
        await self.retrieve_config_settings()

    async def retrieve_channels(self, id=0, name="", username=""):
        entity = None
        input_str = ""
        if name != "":
            input_str = f"name: {name}"
        elif username != "":
            input_str = f"username: {username}"
        elif id != 0:
            input_str = f"id: {id}"

        async for dia in self.client.iter_dialogs():
            if str(name).strip() != "" and dia.name == str(name).strip() or dia.entity.id == id:
                entity = InputChannel(dia.entity.id, dia.entity.access_hash)
                print(f"[+] Channel {dia.name} found.")
                break
        if not entity:
            try:
                entity = await self.client.get_entity(id)
                if entity:
                    print(f"[+] Channel {input_str} added.")
            except:
                pass
        if not entity:
            try:
                entity = await self.client.get_entity(username)
                if entity:
                    print(f"[+] Channel {input_str} added.")
            except:
                pass
        return entity

    @staticmethod
    def align_telegram_channel_id(id, with_minus=True):
        if with_minus:
            if id > 0:
                return int("-100" + str(id))
            else:
                return id
        else:
            return int(str(id).replace("-100",""))

    async def retrieve_config_settings(self):
        for key, value in self.config.items():
            if re.match(r"forward_[0-9]+", key):
                current_forward = {"telegram":[], "discord":[], "language_processing": ""}

                input_channel_handler = ""
                current_chl = None
                error = False
                for forwarditem in self.config[key]:
                    if "input" in forwarditem.keys():

                        if len(forwarditem["input"]) != 1:
                            print("[-] Error: Only one input channel is allowed per forward.")
                            error = True
                            continue

                        elif len(forwarditem["input"][0].keys()) != 1 or "telegram_channel" not in forwarditem["input"][0].keys():
                            print("[-] Error: Input setting wrong.")
                            error = True
                            continue

                        for attr in forwarditem["input"][0]["telegram_channel"]:
                            if "id" in attr.keys():
                                current_chl = await self.retrieve_channels(id=Forwardgram.align_telegram_channel_id(attr["id"],False))
                                input_channel_handler = "id: {}".format(attr["id"])
                            elif "name" in attr.keys():
                                current_chl = await self.retrieve_channels(name=attr["name"])
                                input_channel_handler = "name: {}".format(attr["name"])
                            elif "username" in attr.keys():
                                current_chl = await self.retrieve_channels(username=attr["username"])
                                input_channel_handler = "username: {}".format(attr["username"])
                            elif "language" in attr.keys():
                                current_forward["language_processing"] = attr["language"]
                        if current_chl:
                            self.input_channels_entities.append(current_chl)
                        else:
                            continue

                    if "output" in forwarditem.keys():
                        for cckey in forwarditem["output"]:
                            if len(cckey.keys()) != 1:
                                error = True
                                print("[-] Error: Output setting wrong.")
                                continue
                            key_name = list(cckey.keys())[0]
                            forward = {"entity":None, "language":""}

                            if "telegram_channel" in key_name:

                                for attr in cckey[key_name]:
                                    if "id" in attr.keys():
                                        forward["entity"] = await self.retrieve_channels(id=Forwardgram.align_telegram_channel_id(attr["id"],True))
                                    elif "name" in attr.keys():
                                        forward["entity"] = await self.retrieve_channels(name=attr["name"])
                                    elif "username" in attr.keys():
                                        forward["entity"] = await self.retrieve_channels(username=attr["username"])
                                    elif "language" in attr.keys():
                                        forward["language"] = attr["language"]

                                current_forward["telegram"].append(forward)

                            elif "discord_channel" in key_name:
                                for attr in cckey[key_name]:
                                    if "id" in attr.keys():
                                        forward["entity"] = attr["id"]
                                    elif "language" in attr.keys():
                                        forward["language"] = attr["language"]
                                current_forward["discord"].append(forward)

                if not error and current_chl and current_chl.channel_id not in self.forward_settings.keys():
                    self.forward_settings[current_chl.channel_id] = current_forward
                elif not current_chl:
                    print(f"[-] Error, {input_channel_handler}, Channel not found.")
                elif current_chl.channel_id in self.forward_settings.keys():
                    print(f"[-] Error: Channel {current_chl.channel_id} is already configured in another forward, check you config.yml.")


    async def new_message_handler(self,event):
        for channel in self.forward_settings[event.message.chat.id]["telegram"]:
            if "language" in channel.keys() and channel["language"] != "":
                message = Forwardgram.process_message(event.message.text, channel["language"])["tmessage"]
                message = message.replace("] (","](").replace(") ,","),")
            else:
                message = event.message.text
            await self.client.forward_messages(channel["entity"], message)

        for channel in self.forward_settings[event.message.chat.id]["discord"]:
            detected_language = ""
            if "language" in channel.keys() and channel["language"] != "":
                translated_message = Forwardgram.process_message(event.message.text, channel["language"])
                message = translated_message["tmessage"].replace("] (","](").replace(") ,","),")
                detected_language = translated_message["olanguage"]
            else:
                message = event.message.text
            if detected_language != "":
                detected_language = f"({detected_language.upper()})"

            if event.message.chat.username and event.message.chat.username != "":
                message = f"_[{event.message.chat.title} {detected_language}](https://t.me/{event.message.chat.username}/{event.message.id}), posted:_\n>>> {message}"
            else:
                message = f"_[{event.message.chat.title} {detected_language}](https://t.me/{event.message.chat.id}/{event.message.id}), posted:_\n>>> {message}"

            if message.strip() == "":
                message = ">>> [Empty message, or with no text, follow the link to see the original message]"

            self.discord.send_async_message(channel["entity"],message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} {{CONFIG_PATH}}")
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        config = yaml.safe_load(f)
    Forwardgram(config)

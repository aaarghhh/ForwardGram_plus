from telethon import TelegramClient, events, sync
from telethon.tl.types import InputChannel
import yaml
import sys
import logging
import DiscordHandler
import subprocess
from googletrans import Translator
import re
import os
import asyncio
import Util

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


class Forwardgram:

    forward_settings = {}
    input_channels_entities = []
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    group_id_messages = {}
    util = Util.Util()

    def __init__(self):
        self.config = self.util.get_config()
        self.client = TelegramClient(self.config["session_name"],
                                     self.config["api_id"],
                                     self.config["api_hash"])

        loop = asyncio.get_event_loop()  # Here
        self.discord = DiscordHandler.DiscordHandler(self.config["discord_bot_token"])
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

    #implement a static function for extracting a caption from a message via regex
    def extract_caption(self, message):
        caption = ""
        if message.entities:
            for entity in message.entities:
                if entity.__class__.__name__ == "MessageEntityTextUrl":
                    caption = message.message[entity.offset:entity.offset + entity.length]
                    break
        return caption

    async def new_message_handler(self,event):

        ### creare un unico messaggio con tutti i file
        ### introdurre OCR con messaggio
        ### introdurre vision per le immagini e la loro descrizione

        for channel in self.forward_settings[event.message.chat.id]["telegram"]:
            if "language" in channel.keys() and channel["language"] != "":
                message = self.util.process_message(event.message.text, channel["language"])["tmessage"]
                message = message.replace("] (","](").replace(") ,","),")
            else:
                message = event.message.text
            await self.client.forward_messages(channel["entity"], message)

        for channel in self.forward_settings[event.message.chat.id]["discord"]:
            detected_language = ""
            if "language" in channel.keys() and channel["language"] != "":
                match, message = Util.Util.extract_message_url(event.message.text)
                translated_message = self.util.process_message(message, channel["language"])
                message = Util.Util.recover_url(translated_message["tmessage"], match)
                message = Util.Util.clean_message(message)
                detected_language = translated_message["olanguage"]
            else:
                message = event.message.text
            if detected_language != "":
                detected_language = f"({detected_language.upper()})"

            ### to do implementare lista di file
            ### valutare se il grouped del messaggio di telegram è uguale al precedente
            ### se è uguale non modficare il messaggio aggiungendo il file

            message_pieces = Util.Util.split_message(message)
            photo_sent = True
            first_message = True
            for mmsg in message_pieces:
                photo_list_path = []
                photo_list = []
                if event.message.photo and photo_sent:
                        filename = str(event.message.photo.id) + event.message.file.ext
                        await event.message.download_media(os.path.join(self.temp_dir, filename))
                        photo_list_path.append(os.path.join(self.temp_dir, filename))

                        #picture_string = Util.Util.process_image(os.path.join(self.temp_dir, filename))
                        #print(picture_string)

                        with open(os.path.join(self.temp_dir, filename), 'rb') as filehandle:
                            picture = self.discord.generate_discord_file(filehandle)
                            photo_list.append(picture)
                        photo_sent = False

                if not first_message:
                    mmsg = ">>> ...." + mmsg
                first_message = False

                if event.message.chat.username and event.message.chat.username != "":
                    message = f"_[{event.message.chat.title} {detected_language}](https://t.me/{event.message.chat.username}/{event.message.id}), posted:_\n>>> {mmsg}"
                else:
                    message = f"_[{event.message.chat.title} {detected_language}](https://t.me/c/{event.message.chat.id}/{event.message.id}), posted:_\n>>> {mmsg}"

                if message.strip() == "":
                    message = ">>> [Empty message, or with no text, follow the link to see the original message]"

                if len(photo_list) > 0:
                    self.discord.send_async_message(channel["entity"],message,files=photo_list)
                else:
                    self.discord.send_async_message(channel["entity"],message)

                for photo in photo_list_path:
                    os.remove(photo)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} {{CONFIG_PATH}}")
        sys.exit(1)
    Forwardgram()

import re

import yaml
import sys
from googletrans import Translator
from PIL import Image
import pytesseract

class Util:

    config = None
    def __init__(self):
        pass

    def get_config(self):
        if self.config:
            return self.config
        else:
            self.load_config()
            return self.config

    def load_config(self):
        with open("config.yml", 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print("[-] Error while loading config.yml")
                sys.exit(1)

    @staticmethod
    def recover_url(msg, urls):
        msg_out = msg
        for url in urls:
            msg_out = msg.replace("{{"+str(urls.index(url))+"}}", url)
        return msg_out

    @staticmethod
    def extract_message_url(msg):
        match = re.findall(r"\[[\S\n]+\]\(https?://[\S\n]+\)", msg)
        count = 0
        for m in match:
            msg = msg.replace(m, "{{"+str(count)+"}}")
            count += 1
        return match, msg

    @staticmethod
    def clean_message(msg):
        return msg.replace("] (","](").replace(") ,","),")

    # split message in array of 2000 chars string length
    @staticmethod
    def split_message(msg):
        return [msg[i:i+1800] for i in range(0, len(msg), 1800)]

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
            translation = translator.translate(mess_txt, dest=dest_lang)
            original_language = translation.src
            translated_text = translation.text
            out = {"tmessage": translated_text, "confidence": translation_confidence, "olanguage": original_language,
                   "omessage": mess_txt}
        return out

    @staticmethod
    def process_image(image_path):
        image_string = ""
        try:
            image_string = pytesseract.image_to_string(image_path, timeout=2)  # Timeout after 2 seconds
        except RuntimeError as timeout_error:
            # Tesseract processing is terminated
            pass
        return image_string
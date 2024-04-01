import re

import yaml
import sys
from googletrans import Translator
from PIL import Image
import pytesseract
import math


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
        with open("config.yml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print("[-] Error while loading config.yml")
                sys.exit(1)

    @staticmethod
    def recover_url(msg, urls):
        msg_out = msg
        for url in urls:
            msg_out = msg_out.replace("{{" + str(urls.index(url)) + "}}", url)
        return msg_out

    @staticmethod
    def extract_message_url(msg):
        match = re.findall(
            r"((?:[*]{2})?\[(?:[*]{2})?[\w\s\n\u00a9\u00ae\u2000-\u3300\ud83c\ud000-\udfff\ud83d\ud000-\udfff\ud83e\ud000-\udfffа-я]+(?:[*]{2})?\]\((?:[*]{2})?https?://[\S\n]+(?:[*]{2})?\)(?:[*]{2})?)",
            msg,
            re.IGNORECASE | re.MULTILINE,
        )
        urls = []
        count = 0
        for m in match:
            msg = msg.replace(m, "{{" + str(count) + "}}")
            current_match = m.replace("\n","").replace("\r","").replace("\t","").replace("**","")
            if not current_match + ")" in urls:
                urls.append(current_match)
                count += 1
        return urls, msg

    @staticmethod
    def clean_message(msg):
        return msg.replace("] (", "](").replace(") ,", "),")

    # split message in array of 2000 chars string length
    @staticmethod
    def split_message(msg):
        index = 0
        res = {"len": 0, "messages": []}
        if msg is not None and len(msg) > 1800:
            res = {"len": math.ceil(len(msg) / 1800), "messages": []}
            for i in range(0, len(msg), 1800):
                index = index + 1
                res["messages"].append({"msg": msg[i : i + 1800], "piece": index})
            res["messages"].sort(key=lambda x: x["piece"])
        elif msg is not None and len(msg) > 0:
            res = {"len": 1, "messages": [{"msg": msg, "piece": 1}]}
        return res

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
            out = {
                "tmessage": translated_text,
                "confidence": translation_confidence,
                "olanguage": original_language,
                "omessage": mess_txt,
            }
        return out

    @staticmethod
    def process_ocr_image(image_path, lang=None):
        image_string = ""
        try:
            if lang:
                _lang = lang
                image_string = pytesseract.image_to_string(
                    image_path, timeout=2, lang=_lang
                )  # Timeout after 2 seconds
            else:
                image_string = pytesseract.image_to_string(image_path, timeout=2)
        except RuntimeError as timeout_error:
            # Tesseract processing is terminated
            pass
        return image_string

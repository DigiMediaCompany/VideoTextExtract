import os
from time import sleep

from selenium.webdriver import Keys
from seleniumbase import SB

import glo
from config import chrome_dir, output_dir, central_lang, to_lang

urls = [
    # TODO: add bot by-pass test and shit
    "chrome://version/",
    "https://www.browserscan.net",
    "https://deviceandbrowserinfo.com/are_you_a_bot",
    "https://bot-detector.rebrowser.net",
    "https://fingerprint.com/products/bot-detection",
]

def gpt_helper(func, *args, **kwargs):
    with SB(
        headed=True,
        browser="chrome",
        uc=True,
        chromium_arg=[
            f"--user-data-dir={chrome_dir}",
            "--disable-blink-features=AutomationControlled"
        ],
    ) as sb:
        func(sb, *args, **kwargs)

def gpt_translate(text):
    def get_translation(sb):
        sleep(5)
        chat_box_selector = "p[data-placeholder='Ask anything']"
        chat_box =  sb.find_element(chat_box_selector)
        sb.wait_for_element(chat_box_selector)
        sb.wait_for_element_visible(chat_box_selector)
        sb.wait_for_element_clickable(chat_box_selector)
        sb.click(chat_box_selector)
        sb.type(chat_box_selector, text)
        chat_box.send_keys(Keys.ENTER)
        sleep(3354353)


        # output = sb.get_text(".output-selector")
        # print("Translated text:", output)
        return 'toi la ai'

    return gpt_helper(get_translation)





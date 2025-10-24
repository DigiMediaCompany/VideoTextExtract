import os
from enum import Enum
from time import sleep
import re
import pyperclip
from bs4 import BeautifulSoup
from selenium.webdriver import Keys
from seleniumbase import SB
import random

import glo
from config import chrome_dir, output_dir, central_lang, to_lang
from youtube import get_info

urls = [
    # TODO: add bot by-pass test and shit
    "chrome://version/",
    "https://www.browserscan.net",
    "https://deviceandbrowserinfo.com/are_you_a_bot",
    "https://bot-detector.rebrowser.net",
    "https://fingerprint.com/products/bot-detection",
]

class ProjectType(Enum):
    CONTEXT = "CONTEXT"
    ARTICLE = "ARTICLE"
    TITLE = "TITLE"
    SUB = "SUB"

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

def read_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def gpt_translate(type):
    def get_translation(sb):
        if type == ProjectType.CONTEXT:
            url = "https://chatgpt.com/g/g-p-68ba062ba24c819189184d76fad578fc-context/project"
        elif type == ProjectType.ARTICLE:
            url = "https://chatgpt.com"
        elif type == ProjectType.TITLE:
            url = "https://chatgpt.com/g/g-p-68ba064304348191b64d09c1189bf17d-title/project"
        elif type == ProjectType.SUB:
            url = "https://chatgpt.com/"
        # Step 1: Ensure correct link
        sleep(random.uniform(3, 5))
        if sb.get_current_url() != url:
            sb.open(url)
        
        # Step 2: Type into <p data-placeholder="New chat in Context">\
        if type == ProjectType.ARTICLE:
            sub_file = os.path.join(output_dir, glo.video_id, f"script.{central_lang}.txt")
            title_file = os.path.join(output_dir, glo.video_id, f"title.{central_lang}.txt")
            context_file = os.path.join(output_dir, glo.video_id, f"context.{central_lang}.txt")
            info = get_info()
            sub_text = read_file(sub_file)
            title_text = read_file(title_file)
            context_text = read_file(context_file)
            message = f"""tiếp theo viết bài này 
            1. Title:
            {title_text}

            2. Tập phim:
            {info.get("title", "")} {info.get("upload_date", "")}

            3. Tóm tắt tuyến sự kiện:
            {context_text}

            4. Tone mong muốn:
            Drama căng thẳng, nhiều cảm xúc

            5. Transcribe
            {sub_text}
            """
            if glo.instruction:
                message += f"""
                        6. Instruction:
                        {glo.instruction}
                        """
        elif type == ProjectType.SUB:
            sub_file = os.path.join(output_dir, glo.video_id, f"sub.{central_lang}.srt")
            srt_text = read_file(sub_file)
            srt_text_clean = "\n".join(
                line for line in srt_text.splitlines()
                if not re.match(r"^\s*\[music\]\s*$", line, re.IGNORECASE)
            )
            message = f"""
                You are a skilled subtitle translator.
                Translate the following dialogue from {central_lang} to {to_lang},
                ensuring natural, conversational phrasing while keeping timing and tone.
                Do not explain anything — just return the translated text.


                {srt_text_clean}
                """

        else:
            message = ""
            sub = os.path.join(output_dir, glo.video_id, f"sub.{central_lang}.srt")
            if not os.path.exists(sub):
                raise FileNotFoundError(f"❌ Input file not found: {sub}")
            with open(sub, "r", encoding="utf-8") as f:
                message = f.read()

        chat_box_selector = '#prompt-textarea > p'
        sb.wait_for_element(chat_box_selector, timeout=10)
        chat_box = sb.driver.find_element("css selector", chat_box_selector)
        chat_box.click()
        pyperclip.copy(message)
        chat_box.send_keys(Keys.CONTROL, "v")

        # Step 3: Random wait then click submit

        sleep(random.uniform(3, 5))
        sb.click('#composer-submit-button')

        # Step 4: Get HTML content from target class
        sleep(random.uniform(60, 90))
        sb.wait_for_element(
            '.markdown.prose.dark\\:prose-invert.w-full.break-words.dark.markdown-new-styling',
            timeout=15,
        )
        html_content = sb.get_attribute(
            '.markdown.prose.dark\\:prose-invert.w-full.break-words.dark.markdown-new-styling',
            "outerHTML",
        )

        # Step 5: Parse and format HTML into text
        soup = BeautifulSoup(html_content, "html.parser")

        formatted_lines = []
        for element in soup.descendants:
            if element.name == "h1":
                text = element.get_text(strip=True)
                if text:
                    formatted_lines.append("# " + text + "\n")
            elif element.name == "h2":
                text = element.get_text(strip=True)
                if text:
                    formatted_lines.append("## " + text + "\n")
            elif element.name == "p":
                text = element.get_text(strip=True)
                if text:
                    formatted_lines.append(text + "\n")
            elif element.name == "br":
                formatted_lines.append("\n")
            elif element.name == "hr":
                formatted_lines.append("\n" + "-" * 40 + "\n")

        formatted_text = "".join(formatted_lines)
        print(formatted_text)
        # Step 6: Save to file
        if type == ProjectType.ARTICLE:
            outfile = os.path.join(output_dir, glo.video_id, f"article.{central_lang}.txt")
        elif type == ProjectType.CONTEXT:
            outfile = os.path.join(output_dir, glo.video_id, f"context.{central_lang}.txt")
        elif type == ProjectType.TITLE:
            outfile = os.path.join(output_dir, glo.video_id, f"title.{central_lang}.txt")
        elif type == ProjectType.SUB:
            outfile = os.path.join(output_dir, glo.video_id, f"sub.{to_lang}.srt")
        else:
            raise Exception("I'm fucked")

        with open(outfile, "w", encoding="utf-8") as f:
            f.write(formatted_text)
        return 'toi la ai'

    return gpt_helper(get_translation)


def get_context():
    def get_context2(sb):
        pass


    return gpt_helper(get_context2)


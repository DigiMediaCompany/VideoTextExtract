import os

from openai import OpenAI

import glo
from config import output_dir, to_lang


def text_to_speech():
    glo.job = "Turning text to speech"
    input_path = os.path.join(output_dir, glo.video_id, f"script.{to_lang}.txt")
    output_path = os.path.join(output_dir, glo.video_id, f"audio.{to_lang}.txt")

    if not os.path.exists(output_path):
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        response = (glo.openai_client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy", # voices: "alloy", "verse", "sage", etc.
            input=text
        ))

        with open(output_path, "wb") as f:
            f.write(response.read())


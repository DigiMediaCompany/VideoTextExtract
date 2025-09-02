import os
import re

from openai import OpenAI

import glo
from config import output_dir, to_lang, OPEN_AI_CHARACTER_LIMIT


def text_to_speech():
    glo.job = "Turning text to speech"
    input_path = os.path.join(output_dir, glo.video_id, f"script.{to_lang}.txt")
    output_path = os.path.join(output_dir, glo.video_id, f"audio.{to_lang}.mp3")

    if not os.path.exists(output_path):
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        sentences = re.split(r'(?<=[.!?]) +', text)

        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > OPEN_AI_CHARACTER_LIMIT:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence
        if current_chunk:
            chunks.append(current_chunk.strip())

        with open(output_path, "wb") as f:
            for i, chunk in enumerate(chunks):
                print(f"TTS chunk: {i+1}/{len(chunks)}")
                response = glo.openai_client.audio.speech.create(
                    model="gpt-4o-mini-tts",
                    voice="alloy", # voices: "alloy", "verse", "sage", etc.
                    input=chunk
                )
                f.write(response.read())

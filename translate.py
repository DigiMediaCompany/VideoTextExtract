import os
import re
import time
from pathlib import Path

import openai

from config import to_lang, OPEN_AI_CHARACTER_LIMIT, output_dir, central_lang
from glo import openai_client, video_id


def read_srt(file_path):
    text = Path(file_path).read_text(encoding="utf-8")

    text = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", text)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()

def chunk_text(text, max_chars=OPEN_AI_CHARACTER_LIMIT):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())

    return chunks

def translate_chunk(chunk):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are a professional translator. Translate into {to_lang}."},
            {"role": "user", "content": chunk}
        ]
    )
    return response.choices[0].message.content.strip()

def translate_srt():
    input_file = os.path.join(output_dir, video_id, f"sub.{central_lang}.srt")
    output_file = os.path.join(output_dir, video_id, f"sub.{to_lang}.srt")

    if not os.path.exists(output_file):
        text = read_srt(input_file)
        chunks = chunk_text(text)

        translations = []
        for i, chunk in enumerate(chunks, 1):
            print(f"  Translating chunk {i}/{len(chunks)}...")
            translated = translate_chunk(chunk)
            translations.append(translated)

        final_text = "\n\n".join(translations)
        Path(output_file).write_text(final_text, encoding="utf-8")

        print(f"✅ Done! Translation saved to {output_file}")
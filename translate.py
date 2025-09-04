import os
import re
import time
from pathlib import Path

from config import to_lang, OPEN_AI_CHARACTER_LIMIT, output_dir, central_lang, rest_time
import glo
from gpt import gpt_translate


def read_srt(file_path):
    glo.job = "Reading srt file"
    text = Path(file_path).read_text(encoding="utf-8")

    text = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", text)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\[.*?]", "", text)

    return text.strip()


def chunk_text(text, max_chars=OPEN_AI_CHARACTER_LIMIT):
    glo.job = "Chunking texts"
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
    glo.job = "Translating via GPT"
    response = glo.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a professional translator. Translate the following subtitles into {to_lang}. 
Rules:
- Keep only meaningful dialogue and narration.
- Remove:
  • Section/chapter/part introductions (e.g., "part one", "chapter three").  
  • Social media requests (e.g., "like, share, subscribe", "comment below").  
  • Background cues such as [Music], [Applause], [Laughter].  
- Do not add introductions, explanations, or quotes.  
- Output clean, natural {to_lang} text only, in paragraph form."""
            },
            {"role": "user", "content": chunk}
        ]
    )
    return response.choices[0].message.content.strip()


def translate_srt(use_api=False):
    if use_api:
        translate_srt_via_api()
    else:
        gpt_translate()


def translate_srt_via_api(sb=None):
    input_file = os.path.join(output_dir, glo.video_id, f"sub.{central_lang}.srt")
    output_file: str = os.path.join(output_dir, glo.video_id, f"script.{to_lang}.txt")
    if not os.path.exists(output_file) and os.path.exists(input_file):
        text = read_srt(input_file)
        chunks = chunk_text(text)

        translations = []
        for i, chunk in enumerate(chunks, 1):
            print(f"Translating chunk {i}/{len(chunks)}...")
            if sb:
                translated
            else:
                translated = translate_chunk(chunk)
            translated = translated.replace('"', '')
            translations.append(translated)
            time.sleep(rest_time)

        final_text = " ".join(translations)
        final_text = re.sub(r"\s+", " ", final_text).strip()
        Path(output_file).write_text(final_text, encoding="utf-8")


def srt_to_txt():
    input_file = os.path.join(output_dir, glo.video_id, f"sub.{central_lang}.srt")
    output_file = os.path.join(output_dir, glo.video_id, f"script.{to_lang}.txt")
    if not os.path.exists(output_file) and os.path.exists(input_file):
        text = read_srt(input_file)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

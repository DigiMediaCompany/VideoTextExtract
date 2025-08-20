import re
import time

import openai
# from openai import OpenAI

from config import to_lang

openai.api_key = ""
client = OpenAI(api_key=OPENAI_API_KEY)

def read_srt(file_path):
    """Reads the srt file and returns list of entries (num, time, text)."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"(\d+)\s+([\d:,]+ --> [\d:,]+)\s+(.+?)(?=\n\d+\n|\Z)", re.S)
    entries = []
    for match in pattern.finditer(content):
        num = int(match.group(1))
        time_range = match.group(2).strip()
        text = match.group(3).replace("\n", " ").strip()
        entries.append((num, time_range, text))
    return entries


def chunk_entries(entries, min_lines=20):
    """Groups entries into chunks of >=20 lines, ending at a '.' if possible."""
    chunks, current, current_idx = [], [], []
    for idx, (num, time_range, text) in enumerate(entries):
        current.append(text)
        current_idx.append((num, time_range))
        # if we've got enough lines and the text ends with ".", close the chunk
        if len(current) >= min_lines and text.endswith("."):
            chunks.append((" ".join(current), current_idx))
            current, current_idx = [], []
    if current:  # leftover
        chunks.append((" ".join(current), current_idx))
    return chunks


def translate_text(text, target_lang="vi"):
    """Send text to GPT for translation."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # you can change to gpt-4o or gpt-3.5-turbo
        messages=[
            {"role": "system", "content": f"Translate the following into {target_lang}. Keep meaning, natural style."},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response.choices[0].message["content"].strip()


def rebuild_srt(chunks, translations, output_file):
    """Reconstruct srt with translated text mapped to original times."""
    with open(output_file, "w", encoding="utf-8") as f:
        for chunk, trans in zip(chunks, translations):
            original_texts, idx_times = chunk
            # Split translation into roughly same number of lines
            trans_lines = trans.split(". ")
            if len(trans_lines) < len(idx_times):
                # pad if fewer sentences than entries
                trans_lines += [""] * (len(idx_times) - len(trans_lines))

            for (num, time_range), line in zip(idx_times, trans_lines):
                f.write(f"{num}\n{time_range}\n{line.strip()}\n\n")


def translate_srt(input_file, output_file):

    entries = read_srt(input_file)
    chunks = chunk_entries(entries)

    translations = []
    for text, idx_times in chunks:
        print(f"Translating chunk ({len(idx_times)} lines)...")
        trans = translate_text(text, target_lang=to_lang)  # example: Vietnamese
        translations.append(trans)
        time.sleep(20)

    rebuild_srt(chunks, translations, output_file)
    print("✅ Translation completed:", output_file)


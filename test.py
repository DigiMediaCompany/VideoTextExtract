import re

def count_words_in_srt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove timestamp lines
    content = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", content)

    # Remove subtitle numbering (lines with only digits)
    content = re.sub(r"^\d+$", "", content, flags=re.MULTILINE)

    # Collapse multiple newlines/spaces into one space
    content = re.sub(r"\s+", " ", content).strip()

    # Split into words
    words = re.findall(r"\w+", content)

    return len(words)

import openai

def get_usage():
    openai.api_key = ""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello GPT!"}]
        )
        print(response["choices"][0]["message"]["content"])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # srt_file = "result/a.srt"  # change to your .srt file path
    # word_count = count_words_in_srt(srt_file)
    # print(f"Estimated word count (only subtitle text): {word_count}")

    get_usage()

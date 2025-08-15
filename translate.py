import os
import re
import openai
import tiktoken
from dotenv import load_dotenv
from colorama import Fore, Style
import traceback
import time
from deep_translator import GoogleTranslator

load_dotenv()
MODEL_NAME = "gpt-4o-mini"
MAX_TOTAL_TOKENS = 4000  # max tokens for gpt-4o-mini, adjust as needed
MAX_RESPONSE_TOKENS = 500  # reserve tokens for the response
MAX_PROMPT_TOKENS = MAX_TOTAL_TOKENS - MAX_RESPONSE_TOKENS
delay_seconds = 0.1   # Delay between google translations

enc = tiktoken.encoding_for_model(MODEL_NAME)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# translate_log_dir = "result/log/translating_log.txt"
# os.makedirs(translate_log_dir, exist_ok=True)


def count_tokens(text):
    return len(enc.encode(text))


def extract_subtitle_lines(vtt_text):
    """
    Extract subtitle text lines, excluding metadata like timestamps and cues.
    Return list of (line_number, text).
    """
    lines = vtt_text.splitlines()
    subtitle_lines = []
    line_num = 0
    for line in lines:
        # Skip empty lines, metadata (like WEBVTT, timestamps, cue numbers)
        if not line.strip():
            continue
        if re.match(r"^\d+$", line):  # Cue number
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line):
            continue
        if line.strip().upper() == "WEBVTT":
            continue
        # This is subtitle text line
        subtitle_lines.append((line_num, line))
        line_num += 1
    return subtitle_lines


def build_prompt(block_lines, to_lang):
    """
    Build a translation prompt for the block with line markers.
    Format each line as: __LINE_<line_number>__ text
    """
    text_block = ""
    for line_num, text in block_lines:
        text_block += f"__LINE_{line_num}__ {text}\n"

    prompt = (
        f"You are a helpful assistant that translates English text to {to_lang}.\n"
        "Translate ONLY the text after each marker, preserving the markers.\n"
        "Do not add or remove any markers or lines.\n"
        "Provide the translated text in the same format, with markers intact.\n\n"
        f"Here is the text to translate:\n{text_block}"
    )
    return prompt


def chunk_lines_token_aware(lines, max_prompt_tokens=MAX_PROMPT_TOKENS):
    """
    Yield chunks of lines so that the token count of the prompt text
    stays within max_prompt_tokens.
    """
    chunk = []
    chunk_tokens = 0

    # Estimate overhead tokens for prompt instructions (conservative)
    overhead_tokens = count_tokens(
        "You are a helpful assistant that translates English text to LANG.\n"
        "Translate ONLY the text after each marker, preserving the markers.\n"
        "Do not add or remove any markers or lines.\n"
        "Provide the translated text in the same format, with markers intact.\n\n"
        "Here is the text to translate:\n"
    )

    for line_num, text in lines:
        line_text = f"__LINE_{line_num}__ {text}\n"
        tokens = count_tokens(line_text)

        if chunk_tokens + tokens + overhead_tokens > max_prompt_tokens and chunk:
            yield chunk
            chunk = []
            chunk_tokens = 0

        chunk.append((line_num, text))
        chunk_tokens += tokens

    if chunk:
        yield chunk


def parse_translated_text(translated_text):
    """
    Extract translated lines by marker.
    Return dict {line_num: translated_line}
    """
    pattern = re.compile(r"__LINE_(\d+)__\s*(.*)")
    result = {}
    for line in translated_text.splitlines():
        match = pattern.match(line)
        if match:
            line_num = int(match.group(1))
            text = match.group(2)
            result[line_num] = text
    return result


def translate_block(block_lines, to_lang):
    prompt = build_prompt(block_lines, to_lang)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful translation assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_RESPONSE_TOKENS,
        temperature=0.3,
    )
    translated_text = response['choices'][0].message.content
    return parse_translated_text(translated_text)


def translate_with_gpt(vtt_text, to_lang):
    subtitle_lines = extract_subtitle_lines(vtt_text)
    translated_lines = {}

    for block in chunk_lines_token_aware(subtitle_lines):
        translated_block = translate_block(block, to_lang)
        translated_lines.update(translated_block)

    # Reconstruct VTT with translated lines
    output_lines = []
    lines = vtt_text.splitlines()
    line_index = 0

    for line in lines:
        # Keep metadata lines intact
        if not line.strip() or \
                re.match(r"^\d+$", line) or \
                re.match(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line) or \
                line.strip().upper() == "WEBVTT":
            output_lines.append(line)
        else:
            # Replace with translated text if available
            translated = translated_lines.get(line_index, line)
            output_lines.append(translated)
            line_index += 1

    return "\n".join(output_lines)


def is_metadata_line(line):
    return (
        not line.strip() or
        line.startswith("WEBVTT") or
        line.startswith("Kind:") or
        line.startswith("Language:") or
        "-->" in line
    )


def translate_with_google(input_path, output_path, to_lang, is_debugging):
    print(Fore.GREEN + "Translating with Google ..." + Style.RESET_ALL)
    translator = GoogleTranslator(source='auto', target=to_lang)
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if is_metadata_line(line):
                outfile.write(line)
            else:
                try:
                    translated = translator.translate(line.strip())
                    outfile.write(translated + "\n")
                    time.sleep(delay_seconds)
                except Exception as e:
                    if is_debugging:
                        print(f"Translation failed for line: {line.strip()}")
                        print(Fore.RED + f"{e}" + Style.RESET_ALL)
                        traceback.print_exc()
                    outfile.write(line)  # fallback: write original


def translate_vtt(input_file, output_file, to_lang, is_debugging):
    try:
        print(Fore.GREEN + "Translating with GPT ..." + Style.RESET_ALL)
        with open(input_file, "r", encoding="utf-8") as f:
            vtt_text = f.read()

        translated_vtt = translate_with_gpt(vtt_text, to_lang)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(translated_vtt)
    except Exception as e:
        print(Fore.RED + f"Fail while translating with GPT" + Style.RESET_ALL)
        if is_debugging:
            print(Fore.RED + f"{e}" + Style.RESET_ALL)
            traceback.print_exc()
        print(Fore.GREEN + "Translating with Google Translate ..." + Style.RESET_ALL)
        translate_with_google (input_file, output_file, to_lang, is_debugging)

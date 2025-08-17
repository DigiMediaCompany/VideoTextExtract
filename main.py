import os
import re
import sys
import socket
import requests
import glo
from yt_dlp import YoutubeDL
# import whisper
from gtts import gTTS
# from pydub import AudioSegment
from colorama import Fore, Style
from config import youtube_link, is_debugging, output_dir, to_lang, central_lang
from translate import translate_srt
from utils import print_error


# Validate YouTube link format
def is_valid_youtube_url_format(url):
    pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return re.match(pattern, url) is not None


# Check for internet connectivity
def check_internet_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


# Check if the YouTube link actually exists
def check_url_reachable(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False


# Validate input link
def validate_youtube_url(url):
    if not is_valid_youtube_url_format(url):
        print(Fore.RED + "Invalid YouTube URL format" + Style.RESET_ALL)
        return False
    if not check_internet_connection():
        print(Fore.RED + "No internet connection" + Style.RESET_ALL)
        return False
    if not check_url_reachable(url):
        print(Fore.RED + "YouTube link is either not reachable, private or doesn't exist" + Style.RESET_ALL)
        return False
    return True


if validate_youtube_url(youtube_link):
    print(Fore.GREEN + "Link is good to go" + Style.RESET_ALL)
else:
    sys.exit()


# Download sub file
def extract_video_id(youtube_url):
    # Common YouTube URL formats
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None


video_id = extract_video_id(youtube_link)
ydl_opts = {
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'quiet': True,
    'no_warnings': not is_debugging,
    "cookies": "cookies.txt",
}
# en_audio_path = os.path.join(output_dir, f"{video_id}.en.mp3")
required_translation = False

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(youtube_link, download=False)
    subtitles = info.get('subtitles', {})
    auto_subs = info.get('automatic_captions', {})


def download(code, output_path, auto_sub=False):
    second_ydl_opts = {
        'skip_download': True,
        'writesubtitles': not auto_sub,
        'writeautomaticsub': auto_sub,
        'subtitleslangs': [code],
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': not is_debugging,
        "cookies": "cookies.txt",
        "overwrites": False,
        'subtitlesformat': 'srt/best'
    }
    with YoutubeDL(second_ydl_opts) as ydl2:
        ydl2.download([youtube_link])


attempts = [
    (to_lang, False),  # Manual to_lang
    # (to_lang, True),  # Auto to_lang
    (central_lang, False),  # Manual central_lang (en)
    (central_lang, True),  # Auto central_lang (en)
]

success = False

for lang_code, auto in attempts:
    path = os.path.join(output_dir, f"{video_id}.%(ext)s")
    available = auto_subs if auto else subtitles
    if lang_code in available:
        glo.job = f"Downloading {'auto-generated' if auto else 'manual'} subtitle in {lang_code}"
        print(Fore.GREEN + glo.job + Style.RESET_ALL)
        try:
            download(lang_code, path, auto)
            if lang_code == central_lang and lang_code != to_lang:
                required_translation = True
            success = True
            break
        except Exception as e:
            print_error(e)
            continue

# if not success:
#     job = "Downloading audio for transcription"
#     print(Fore.GREEN + job + Style.RESET_ALL)
#     print(Fore.YELLOW + "WARNING: if the video is not in English, this will NOT work" + Style.RESET_ALL)
#     try:
#         audio_ydl_opts = {
#             'format': 'bestaudio/best',
#             'outtmpl': en_audio_path,
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '192',
#             }]
#         }
#         with YoutubeDL(audio_ydl_opts) as audio_ydl:
#             audio_ydl.download([youtube_link])
#
#         # Transcribe
#         model = whisper.load_model("base")
#         result = model.transcribe(en_audio_path, language="en")
#         with open(central_sub_path, 'w', encoding='utf-8') as f:
#             f.write(result['text'])
#         required_translation = True
#         success = True
#     except Exception as e:
#         print_error(e)

if not success:
    sys.exit("No subtitles or transcription available.")

# Translate file if needed
if required_translation:
    untranslated = os.path.join(output_dir, f"{video_id}.{central_lang}.srt")
    translated = os.path.join(output_dir, f"{video_id}.{to_lang}.srt")
    if not os.path.exists(translated):
        translate_srt(untranslated, translated)

# Convert to audio using gTTS
# print("Converting to audio...")
# tts = gTTS(translated_text, lang=to_lang)
# audio_out_path = os.path.join(output_dir, f"{video_id}.{to_lang}.mp3")
# tts.save(audio_out_path)
#
# print(f"✅ Done! Translated audio saved to {audio_out_path}")

print(Fore.GREEN + "Done" + Style.RESET_ALL)
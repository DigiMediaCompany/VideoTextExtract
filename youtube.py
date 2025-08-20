import os
import re
import socket
import requests
from colorama import Fore, Style
from yt_dlp import YoutubeDL

import glo
from config import youtube_link, is_debugging, to_lang, central_lang, output_dir, cookie_file
from utils import print_error


base_opts = {
    'skip_download': True,
    # 'quiet': True,
    # 'no_warnings': True,
    "cookies": cookie_file,
    "overwrites": False,
}


def check_url_reachable(url):
    glo.job = "Checking URL reachability"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    return response.status_code == 200


def is_valid_youtube_url_format(url):
    glo.job = "Checking URL format"
    pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return re.match(pattern, url) is not None


def check_internet_connection():
    glo.job = "Checking internet connection"
    socket.create_connection(("8.8.8.8", 53), timeout=5)
    return True


def validate_youtube_url():
    if not is_valid_youtube_url_format(youtube_link):
        print(Fore.RED + "Invalid YouTube URL format" + Style.RESET_ALL)
        return False
    if not check_internet_connection():
        print(Fore.RED + "No internet connection" + Style.RESET_ALL)
        return False
    if not check_url_reachable(youtube_link):
        print(Fore.RED + "YouTube link is either not reachable, private or doesn't exist" + Style.RESET_ALL)
        return False
    return True


def extract_video_id():
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_link)
    if match and match.group(1):
        return match.group(1)
    else:
        raise Exception("Cannot extract video id")


def download(code, output_path, auto_sub=False):
    print(Fore.GREEN + glo.job + Style.RESET_ALL)
    second_ydl_opts = {
        **base_opts,
        'writesubtitles': not auto_sub,
        'writeautomaticsub': auto_sub,
        'subtitleslangs': [code],
        'outtmpl': output_path,
        'subtitlesformat': 'srt/best'
    }
    with YoutubeDL(second_ydl_opts) as ydl2:
        ydl2.download([youtube_link])


def download_subtitle():
    if validate_youtube_url():
        print(Fore.GREEN + "Link is good to go" + Style.RESET_ALL)
    else:
        raise Exception("Bad YouTube URL")

    required_translation = False
    glo.video_id = extract_video_id()
    ydl_opts = {
        **base_opts,
        'writesubtitles': True,
        'writeautomaticsub': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_link, download=False)
        subtitles = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})

    attempts = [
        (to_lang, False),  # Manual to_lang
        # (to_lang, True),  # Auto to_lang (fuck auto translate is sooo bad)
        (central_lang, False),  # Manual central_lang (en)
        (central_lang, True),  # Auto central_lang (en)
    ]

    success = False
    for lang_code, auto in attempts:
        glo.job = f"Downloading {'auto-generated' if auto else 'manual'} subtitle in {lang_code}"
        path = os.path.join(output_dir, glo.video_id, f"sub.{lang_code}.srt")
        downloaded = False
        if os.path.exists(path):
            downloaded = True
        else:
            available = auto_subs if auto else subtitles
            if lang_code in available:
                try:
                    download(lang_code, path, auto)
                    downloaded = True
                except Exception as e:
                    print_error(e)
                    continue
        if downloaded:
            if lang_code == central_lang and lang_code != to_lang:
                required_translation = True
            success = True
            break
    return required_translation

    # if not success:
    #     glo.job = "Downloading audio for transcription"
    #     print(Fore.GREEN + glo.job + Style.RESET_ALL)
    #     print(Fore.YELLOW + "WARNING: if the video is not in English, this will NOT work" + Style.RESET_ALL)
        # audio_ydl_opts = {
        #     'format': 'bestaudio/best',
        #     'outtmpl': en_audio_path,
        #     'postprocessors': [{
        #         'key': 'FFmpegExtractAudio',
        #         'preferredcodec': 'mp3',
        #         'preferredquality': '192',
        #     }]
        # }
        # with YoutubeDL(audio_ydl_opts) as audio_ydl:
        #     audio_ydl.download([youtube_link])
        #
        # # Transcribe
        # model = whisper.load_model("base")
        # result = model.transcribe(en_audio_path, language="en")
        # with open(central_sub_path, 'w', encoding='utf-8') as f:
        #     f.write(result['text'])


import sys
# import whisper
from gtts import gTTS
from colorama import Fore, Style
from translate import translate_srt
from tts import text_to_speech
from utils import print_error
from youtube import download_subtitle


def main():
    try:
        required_translation = download_subtitle()
        if required_translation:
            translate_srt()
        text_to_speech()
        print(Fore.GREEN + "✅Done" + Style.RESET_ALL)
    except Exception as e:
        print_error(e)
        sys.exit()

if __name__ == "__main__":
    main()
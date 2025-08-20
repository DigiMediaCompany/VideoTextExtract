import sys
# import whisper
from gtts import gTTS
from colorama import Fore, Style
from translate import translate_srt, srt_to_txt
from tts import text_to_speech
from utils import print_error
from youtube import download_subtitle


def main():
    try:
        required_translation = download_subtitle()
        # if required_translation:
        #     translate_srt()
        # else:
        #     srt_to_txt()
        # text_to_speech()
        print(Fore.GREEN + "✅Done" + Style.RESET_ALL)
    except Exception as e:
        print_error(e)
        sys.exit()


if __name__ == "__main__":
    main()
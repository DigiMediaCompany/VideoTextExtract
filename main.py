import sys
# import whisper
from gtts import gTTS
from colorama import Fore, Style
from translate import translate_srt
from utils import print_error
from youtube import download_subtitle

# Text to speech
# if not os.path.exists(result_sub):

# print("Converting to audio...")
# tts = gTTS(translated_text, lang=to_lang)
# audio_out_path = os.path.join(output_dir, f"{video_id}.{to_lang}.mp3")
# tts.save(audio_out_path)

def main():
    try:
        required_translation = download_subtitle()
        # if required_translation:
        #     translate_srt()
        print(Fore.GREEN + "✅Done" + Style.RESET_ALL)
    except Exception as e:
        print_error(e)
        sys.exit()

if __name__ == "__main__":
    main()
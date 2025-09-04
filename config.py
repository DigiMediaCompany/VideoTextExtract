from dotenv import load_dotenv
import os


load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_CHARACTER_LIMIT = 2000
rest_time = 1
# Youtube
central_lang = "en"
to_lang = "en"
cookie_file = "cookies.txt"
# Common
output_dir = "result"
video_src_dir = "video"
os.makedirs(output_dir, exist_ok=True)
is_debugging = True
SUBTITLE_FORMAT = "srt"
VIDEO_FORMAT = "mp4"
AUDIO_FORMAT = "mp3"
sub_file_name = "sub"
audio_file_name = "audio"
script_file_name = "script"
asset_dir = "asset"
font_dir = "font"
temp_file = "temp.ini"
# Final output format
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
final_file_name = "final"
# Cloudflare
D1_URL = f"{os.getenv('D1_URL')}/article"
headers = {
    "Authorization": f"Bearer {os.getenv('D1_API_TOKEN')}",
    "Content-Type": "application/json"
}
job_id_key = "CURRENT_JOB_ID"
section_key = "Cloudflare"
check_jobs_interval = 60

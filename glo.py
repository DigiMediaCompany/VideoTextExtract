from config import OPENAI_API_KEY, temp_file
from openai import OpenAI

import configparser


config = configparser.ConfigParser()
config.read(temp_file)
job = ""
openai_client = OpenAI(api_key=OPENAI_API_KEY)
video_id = None
youtube_link = None

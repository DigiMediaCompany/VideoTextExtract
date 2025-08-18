from config import OPENAI_API_KEY
from openai import OpenAI

job = ""
openai_client = OpenAI(api_key=OPENAI_API_KEY)
video_id = None
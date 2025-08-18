import os
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_CHARACTER_LIMIT = 2000
# Youtube
youtube_link = "https://www.youtube.com/watch?v=eSjbvFBs5Ak&t=47s"
central_lang = "en"
to_lang = "vi"
cookie_file = "cookies.txt"
# Common
output_dir = "result"
os.makedirs(output_dir, exist_ok=True)
is_debugging = True


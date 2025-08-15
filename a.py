import yt_dlp
video_url = "https://www.youtube.com/watch?v=uWj4a6pZSaQ"

ydl_opts = {
    "skip_download": True,
    "writesubtitles": True,
    "writeautomaticsub": True,    # allow auto-generated subs
    "subtitleslangs": ["vi"],     # request Vietnamese
    "subtitlesformat": "srt",
    "outtmpl": "%(title)s.%(ext)s"
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])
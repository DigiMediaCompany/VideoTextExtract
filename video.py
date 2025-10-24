import os
import re
import pdb;
import subprocess
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip

import glo
from config import VIDEO_CODEC, AUDIO_CODEC, output_dir, to_lang, SUBTITLE_FORMAT, VIDEO_FORMAT, sub_file_name, \
    final_file_name, audio_file_name, AUDIO_FORMAT, asset_dir, font_dir


# VIDEO_FILE = "video.mp4"
# AUDIO_FILE = "audio.mp3"
# SRT_FILE   = "subs.srt"
# OUTPUT     = "output.mp4"
def parse_srt(srt_file):
    subtitles = []
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'\n\s*\n', content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            print(f"Skipping invalid block: {block}")
            continue
        # Kiểm tra dòng thời gian
        time_line = lines[1] if len(lines) > 1 and re.match(r"\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}", lines[1]) else None
        if not time_line:
            print(f"Invalid time format in block: {block}")
            continue
        start_str, end_str = time_line.split(" --> ")
        try:
            start_time = srt_time_to_seconds(start_str)
            end_time = srt_time_to_seconds(end_str)
            text = " ".join(lines[2:]) if len(lines) > 2 else ""
            subtitles.append((start_time, end_time, text))
        except ValueError as e:
            print(f"Error parsing time in block: {block}, Error: {e}")
            continue
    return subtitles
def srt_time_to_seconds(t):
    """Convert SRT time format (hh:mm:ss,ms) to seconds (float)."""
    if not re.match(r"\d{2}:\d{2}:\d{2},\d{3}", t):
        raise ValueError(f"Invalid SRT time format: {t}")
    try:
        h, m, rest = t.split(":")
        s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
    except ValueError as e:
        raise ValueError(f"Failed to parse time: {t}") from e


def combine_video():
    glo.job = "Combining video+audio+subtitles"
    pdb.set_trace()
    subtitle_path = os.path.join(output_dir, glo.video_id, f"{sub_file_name}.{to_lang}.{SUBTITLE_FORMAT}")
    audio_path = os.path.join(output_dir, glo.video_id, f"{audio_file_name}.{to_lang}.{AUDIO_FORMAT}")
    output_path = os.path.join(output_dir, glo.video_id, f"{final_file_name}.{to_lang}.{VIDEO_FORMAT}")
    input_path = os.path.join(output_dir, glo.video_id, f"video.{VIDEO_FORMAT}")

    font_path = os.path.join('.', asset_dir, font_dir, 'ARIAL.TTF')

    if not os.path.exists(output_path):
        subtitle_escaped = subtitle_path.replace("\\", "/").replace("'", "\\'")
        input_escaped = input_path.replace("\\", "/")
        output_escaped = output_path.replace("\\", "/")
        audio_escaped = audio_path.replace("\\", "/")
        cmd = [
        "ffmpeg",
        "-i", input_escaped,
        "-i", audio_escaped,
        "-filter_complex",
        f"[0:v]subtitles='{subtitle_escaped}:charenc=UTF-8':force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF&,OutlineColour=&H000000&,BorderStyle=3,Outline=2,Shadow=0'[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", VIDEO_CODEC,
        "-c:a", AUDIO_CODEC,
        "-y",  
        output_escaped
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ Video created: {output_path}")


import os
import re

import pysrt

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
    """
    Parses an .srt file and returns a list of (start_time, end_time, text).
    """
    subtitles = []
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newlines (separates subtitle blocks)
    blocks = re.split(r'\n\s*\n', content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 2:
            # Format: 00:00:01,600 --> 00:00:04,200
            time_line = lines[1] if re.match(r"\d+:\d+:\d+", lines[1]) else lines[0]
            text_lines = lines[2:] if re.match(r"\d+:\d+:\d+", lines[1]) else lines[1:]
            start_str, end_str = time_line.split(" --> ")
            start_time = srt_time_to_seconds(start_str)
            end_time = srt_time_to_seconds(end_str)
            text = " ".join(text_lines)
            subtitles.append((start_time, end_time, text))
    return subtitles

def srt_time_to_seconds(t):
    """Convert SRT time format (hh:mm:ss,ms) to seconds (float)."""
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0



def combine_video():
    glo.job = "Combining video+audio+subtitles"

    subtitle_path = os.path.join(output_dir, glo.video_id, f"{sub_file_name}.{to_lang}.{SUBTITLE_FORMAT}")
    audio_path = os.path.join(output_dir, glo.video_id, f"{audio_file_name}.{to_lang}.{AUDIO_FORMAT}")
    output_path = os.path.join(output_dir, glo.video_id, f"{final_file_name}.{to_lang}.{VIDEO_FORMAT}")
    input_path = os.path.join(output_dir, glo.video_id, f"video.{VIDEO_FORMAT}")

    font_path = os.path.join('.', asset_dir, font_dir, 'arial.ttf')

    if not os.path.exists(output_path):
        # def make_textclip_for_subtitle(subtitle_text):
        #     return TextClip(subtitle_text, fontsize=24, color='white', font='Arial-Bold', bg_color='black')
        # subtitles = SubtitlesClip("result/V_aD_Sa2Gzc/sub.vi.srt", make_textclip_for_subtitle, encoding='utf-8')

        subtitles = parse_srt(subtitle_path)

        subtitle_clips = []
        for start, end, text in subtitles:
            txt_clip = (
                TextClip(text=text, font_size=40, color='white')
                .with_position(("center", "bottom"))
                .with_start(start)
                .with_end(end))
            subtitle_clips.append(txt_clip)


        video = VideoFileClip(input_path).without_audio()
        audio = AudioFileClip(audio_path)
        video_with_subs = CompositeVideoClip([
            *subtitle_clips,
            video,
            # subtitles.set_pos(("center", "bottom"))
        ])

        final = video_with_subs.with_audio(audio)

        final.write_videofile(
            output_path,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            fps=video.fps,
            threads=4
        )


import configparser
import json
import os
from enum import Enum
from time import sleep

import glo
from config import D1_URL, headers, temp_file, job_id_key, section_key, check_jobs_interval, output_dir, central_lang, \
    R2_URL

import requests

from gpt import gpt_translate, ProjectType
from translate import translate_srt, srt_to_txt
from youtube import download_subtitle, extract_video_id


class ProgressStatus(str, Enum):
    GOING = "Going"
    SUCCESS = "Success"
    FAILED = "Failed"
    STANDBY = "Standby"


def is_processed(job_data: dict) -> bool:
    """Return True if job is already processed"""
    progress = job_data.get("progress", [])
    if not progress:
        return False

    # Condition 1: any Failed
    if any(p["status"] == ProgressStatus.FAILED for p in progress):
        return True

    # Condition 2: all Success
    if all(p["status"] == ProgressStatus.SUCCESS for p in progress):
        return True
    return False


def upload_file(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(R2_URL, files=files)

    try:
        response.raise_for_status()
        data = response.json()
        filename = data.get("filename")
        if filename:
            print(f"✅ Upload successful. Server stored as: {filename}")
            return filename
        else:
            print("⚠️ Upload successful but no filename returned.")
            return None
    except Exception as e:
        print(f"❌ Upload failed: {e} | Response: {response.text}")
        return None


def download_file(filename, save_path):
    try:
        resp = requests.get(f"{R2_URL}/{filename}", timeout=10)
        resp.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(resp.content)

        print(f"✅ Downloaded and saved to {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download file: {e}")
        return None


def handle_status_1(progress_item, job_data):
    try:
        detail = json.loads(job_data.get("detail"))
        download_subtitle()
        srt_to_txt()
        gpt_translate(ProjectType.CONTEXT)
        context_file = os.path.join(output_dir, glo.video_id, f"context.{central_lang}.txt")
        uploaded_file = upload_file(context_file)
        if uploaded_file:
            # patch_progress_status(progress_item.id, ProgressStatus.SUCCESS)
            detail["context_file"] = uploaded_file
            patch_job(job_data.get("id"), {
                "detail": json.dumps(detail)
            })
            return True
        return False
    except:
        return False


def handle_status_3(progress_item, job_data):
    try:
        detail = json.loads(job_data.get("detail"))
        context_file = os.path.join(output_dir, glo.video_id, f"context.{central_lang}.txt")
        download_file(detail.get("context_file"), context_file)
        glo.instruction = detail.get("instruction", None)
        gpt_translate(ProjectType.TITLE)
        gpt_translate(ProjectType.ARTICLE)
        article_file = os.path.join(output_dir, glo.video_id, f"article.{central_lang}.txt")
        uploaded_file = upload_file(article_file)
        if uploaded_file:
            detail["article_file"] = uploaded_file
            patch_job(job_data.get("id"), {
                "detail": json.dumps(detail)
            })
            return True
        return False
    except:
        return False


def handle_status_5(progress_item, job_data):
    try:
        return True
    except:
        return False



def handle_status_7(progress_item, job_data):
    try:
        detail = json.loads(job_data.get("detail"))
        download_subtitle()
        srt_to_txt()
        context_file = os.path.join(output_dir, glo.video_id, f"context.{central_lang}.txt")
        os.makedirs(os.path.dirname(context_file), exist_ok=True)
        with open(context_file, "w", encoding="utf-8") as f:
            f.write(detail.get("summary"))
        glo.instruction = detail.get("instruction", None)
        gpt_translate(ProjectType.TITLE)
        gpt_translate(ProjectType.ARTICLE)
        article_file = os.path.join(output_dir, glo.video_id, f"article.{central_lang}.txt")
        uploaded_file = upload_file(article_file)
        if uploaded_file:
            detail["article_file"] = uploaded_file
            patch_job(job_data.get("id"), {
                "detail": json.dumps(detail)
            })
            return True
        return False
    except:
        return False


def patch_job(job_id, body):
    url = f"{D1_URL}/jobs/{job_id}"
    resp = requests.patch(url, headers=headers, json=body)
    if resp.status_code == 200:
        print(f"Updated progress {job_id} .")
    else:
        print(f"Failed to update progress {job_id}.")


def patch_progress_status(progress_id, new_status: str) -> bool:
    url = f"{D1_URL}/progress/{progress_id}"
    resp = requests.patch(url, headers=headers, json={"status": new_status})
    if resp.status_code == 200:
        print(f"Updated progress {progress_id} to {new_status}.")
        return True
    else:
        print(f"Failed to update progress {progress_id} to {new_status}.")
        return False


def process_and_advance(progress_list, index, handler_fn, job_data) -> bool:
    """
    Run a handler for the current progress.
    If successful → mark current as Success and advance the next to Going.
    Otherwise, mark current as Failed.
    Returns True if processing should stop (always stop after handling one).
    """
    current = progress_list[index]
    progress_id = current["id"]

    if handler_fn(current, job_data):  # handler succeeded
        patch_progress_status(progress_id, ProgressStatus.SUCCESS)
        current["status"] = ProgressStatus.SUCCESS

        # Advance next if available
        if index + 1 < len(progress_list):
            next_progress = progress_list[index + 1]
            status = ProgressStatus.GOING
            if current["status_id"] in [5, 7]:
                status = ProgressStatus.SUCCESS

            patch_progress_status(next_progress["id"], status)
            next_progress["status"] = status
    else:
        patch_progress_status(progress_id, ProgressStatus.FAILED)
        current["status"] = ProgressStatus.FAILED
        return False

    return True


def handle_progress_in_job(job_data):
    print(f"Processing job {job_data.get("id", "")}.")
    progress_list = job_data.get("progress", [])
    detail = json.loads(job_data.get("detail"))
    glo.youtube_link = detail.get("link", None)
    glo.video_id = extract_video_id()

    # Map status_id → handler
    handlers = {
        1: handle_status_1,
        3: handle_status_3,
        5: handle_status_5,
        7: handle_status_7,
    }

    for i, current in enumerate(progress_list):
        status = current["status"]

        if status == ProgressStatus.FAILED:
            break

        if status == ProgressStatus.SUCCESS:
            continue

        if status == ProgressStatus.STANDBY:
            if not patch_progress_status(current["id"], ProgressStatus.GOING):
                break
            current["status"] = ProgressStatus.GOING

        if current["status"] == ProgressStatus.GOING:
            status_id = current.get("status_id")
            handler_fn = handlers.get(status_id)

            if handler_fn:
                result = process_and_advance(progress_list, i, handler_fn, job_data)
                if not result:
                    break
            else:
                break


def process_jobs():
    job_id = glo.config.getint("job", job_id_key, fallback=1)

    while True:
        url = f"{D1_URL}/jobs/{job_id}?include=progress"
        resp = requests.get(url, headers=headers)

        # TODO: handle errors/exceptions
        if resp.status_code != 200:
            print(f"Job {job_id} not found or error: {resp.status_code}")
            sleep(check_jobs_interval)
            job_id = glo.config.getint("job", job_id_key, fallback=1)
            continue

        job_data = resp.json()

        if not is_processed(job_data):
            handle_progress_in_job(job_data)
        else:
            config = configparser.ConfigParser()
            config[section_key] = {job_id_key: str(job_id)}
            with open(temp_file, "w") as f:
                config.write(f)
        job_id += 1

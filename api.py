import configparser
from enum import Enum
from time import sleep

import glo
from config import D1_URL, headers, temp_file, job_id_key, section_key, check_jobs_interval

import requests

from translate import translate_srt, srt_to_txt
from youtube import download_subtitle


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


def upload_file(file):
    pass


def handle_status_1(progress_item):
    return True


def handle_status_2(progress_item):
    try:
        # required_translation = download_subtitle()
        # if required_translation:
        #     translate_srt()
        # else:
        #     srt_to_txt()
        # upload_file()
        return True
    except:
        return False


def handle_status_4(progress_item):
    try:
        return True
    except:
        return False


def handle_status_6(progress_item):
    try:
        return True
    except:
        return False


def handle_status_8(progress_item):
    try:
        return True
    except:
        return False


def patch_progress_status(progress_id: int, new_status: str) -> bool:
    url = f"{D1_URL}/progress/{progress_id}"
    resp = requests.patch(url, headers=headers, json={"status": new_status})
    if resp.status_code == 200:
        print(f"Updated progress {progress_id} to {new_status}.")
        return True
    else:
        print(f"Failed to update progress {progress_id} to {new_status}.")
        return False


def process_and_advance(progress_list, index, handler_fn) -> bool:
    """
    Run a handler for the current progress.
    If successful → mark current as Success and advance the next to Going.
    Otherwise → mark current as Failed.
    Returns True if processing should stop (always stop after handling one).
    """
    current = progress_list[index]
    progress_id = current["id"]

    if handler_fn(current):  # handler succeeded
        patch_progress_status(progress_id, ProgressStatus.SUCCESS)
        current["status"] = ProgressStatus.SUCCESS

        # Advance next if available
        if index + 1 < len(progress_list):
            next_progress = progress_list[index + 1]
            patch_progress_status(next_progress["id"], ProgressStatus.GOING)
            next_progress["status"] = ProgressStatus.GOING
    else:
        patch_progress_status(progress_id, ProgressStatus.FAILED)
        current["status"] = ProgressStatus.FAILED

    return True


def handle_progress_in_job(job_data):
    progress_list = job_data.get("progress", [])
    glo.youtube_link = job_data.get("raw_youtube_link", None)

    # Map status_id → handler
    handlers = {
        1: handle_status_1,
        2: handle_status_2,
        4: handle_status_4,
        6: handle_status_6,
        8: handle_status_8,
    }

    for i, current in enumerate(progress_list):
        status = current["status"]

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
                process_and_advance(progress_list, i, handler_fn)
            else:
                break


def process_jobs():
    job_id = glo.config.getint("job", job_id_key, fallback=1)

    while True:
        url = f"{D1_URL}/jobs/{job_id}"
        resp = requests.get(url, headers=headers)

        # TODO: handle errors/exceptions
        if resp.status_code != 200:
            print(f"Job {job_id} not found or error: {resp.status_code}")
            sleep(check_jobs_interval)
            continue

        job_data = resp.json()

        if not is_processed(job_data):
            handle_progress_in_job(job_data)
            config = configparser.ConfigParser()
            config[section_key] = {job_id_key: str(job_id)}
            with open(temp_file, "w") as f:
                config.write(f)
        job_id += 1

import configparser
from enum import Enum

import glo
from config import D1_URL, headers, temp_file, job_id_key, section_key

import requests


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


def find_next_unprocessed_job():
    job_id = glo.config.getint("job", job_id_key, fallback=1)

    while True:
        url = f"{D1_URL}/jobs/{job_id}"
        resp = requests.get(url, headers=headers)

        # TODO: handle errors/exceptions
        if resp.status_code != 200:
            print(f"Job {job_id} not found or error: {resp.status_code}")
            break

        job_data = resp.json()

        if is_processed(job_data):
            job_id += 1
        else:
            config = configparser.ConfigParser()
            config[section_key] = {job_id_key: str(job_id)}

            with open(temp_file, "w") as f:
                config.write(f)

            break

import datetime
import json
import logging
import os
import queue
import shutil
import threading
import traceback
import time
import zipfile

import requests

from django.conf import settings

from .models import Target, Task

logger = logging.getLogger(__name__)
_thread_created = False
_thread_creation_lock = threading.Lock()
_task_queue = queue.Queue()


def enqueue_task(task: Task):
    _task_queue.put(task)


def _get_artifacts_url(repo, token, run_id, artifact_name):
    sleep_time = 2
    for _ in range(5):
        r = requests.get(f'https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts', headers={
            'Authorization': f'token {token}'
        })

        data = r.json()
        if 'artifacts' not in data:
            if settings.DEBUG:
                print('Artifact is not found.')
                print(data)
            return

        for artifact in data['artifacts']:
            if artifact['name'] == artifact_name:
                return artifact['archive_download_url']

        if settings.DEBUG:
            print('Sleep %d secs to wait artifact.' % int(sleep_time))
        time.sleep(sleep_time)
        sleep_time *= 2

    if settings.DEBUG:
        print('Artifact is not found.')
        print(data)


def _download_file(url, token, local_path):
    with requests.get(url, headers={
        'Authorization': f'token {token}'
    }, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def _remove_dir_content(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def _process_task_gh(task: Task):
    task_data = json.loads(task.data)
    target = Target.objects.get(name=task.target_name)
    deploy_path = os.path.join(settings.DEPLOY_ROOT, target.path)

    task.status = Task.Status.DOWNLOADING
    task.message = 'Getting information of the run'
    task.save()

    url = _get_artifacts_url(task_data['repo'], settings.GITHUB_TOKEN, task_data['run_id'], task_data['artifact'])
    if not url:
        task.status = Task.Status.FAILED
        task.message = 'Can\'t find artifact'
        task.save()
        return

    task.source = url
    task.message = 'Ready to download'
    task.save()

    download_folder = os.path.join(settings.BASE_DIR, '.downloads')
    download_path = os.path.join(download_folder, str(task_data['run_id']) + '.zip')
    os.makedirs(download_folder, exist_ok=True)
    _download_file(url, settings.GITHUB_TOKEN, download_path)

    task.status = Task.Status.DEPLOYING
    task.message = 'Deploying to %s' % deploy_path
    task.save()

    os.makedirs(deploy_path, exist_ok=True)
    _remove_dir_content(deploy_path)
    with zipfile.ZipFile(download_path, 'r') as zip:
        zip.extractall(deploy_path)
        
    task.status = Task.Status.FINISHED
    task.message = 'Finished'
    task.finish_time = datetime.datetime.now()
    task.save()


def _worker_thread():
    print('Background worker thread is started.')
    while True:
        task : Task = _task_queue.get()
        try:
            if task.source_type == Task.SourceType.GITHUB_ACTIONS:
                _process_task_gh(task)
        except Exception as e:
            traceback.print_exc()
            task.status = Task.Status.FAILED
            task.finish_time = datetime.datetime.now()
            task.message = str(e)
            try:
                task.save()
            except Exception as e:
                traceback.print_exc()
    

def check_background_worker():
    global _thread_created

    if _thread_created:
        return
    with _thread_creation_lock:
        if not _thread_created:
            t = threading.Thread(target=_worker_thread)
            t.start()
            _thread_created = True

import re
import json

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods

from .models import Identity, Target, Task
from . import worker


def task(request: WSGIRequest):
    return HttpResponse()


def get_client_addr(request: WSGIRequest):
    if settings.BEHIND_PROXY:
        addr = request.META.get('HTTP_X_FORWARDED_FOR')
        if addr:
            return addr
    addr = request.META.get('REMOTE_ADDR')
    return addr


@require_http_methods(['POST'])
def webhook(request: WSGIRequest):
    if 'token' not in request.POST:
        return HttpResponseForbidden('Error: token is not found.')
    token = request.POST['token']
    try:
        identity = Identity.objects.get(secret_key=token)
    except Identity.DoesNotExist as e:
        return HttpResponseForbidden('Error: token is not valid.')
    if not identity.valid:
        return HttpResponseForbidden('Error: token is not valid.')

    if 'type' not in request.GET:
        return HttpResponseBadRequest('Error: webhook type is not found')
    webhook_type = request.GET['type']
    if webhook_type != 'github-actions':
        return HttpResponseBadRequest('Error: webhook type is not valid')

    if 'repo' not in request.POST:
        return HttpResponseBadRequest('Error: repo is not found')
    if 'run_id' not in request.POST:
        return HttpResponseBadRequest('Error: run_id is not found')
    if 'artifact_name' not in request.POST:
        return HttpResponseBadRequest('Error: artifact_name is not found')
    if 'target' not in request.POST:
        return HttpResponseBadRequest('Error: target is not found')

    repo = request.POST['repo']
    run_id = request.POST['run_id']
    artifact_name = request.POST['artifact_name']
    target_name = request.POST['target']
    actor = request.POST['actor'] if 'actor' in request.POST else None
    commit_sha = request.POST['commit_sha'] if 'commit_sha' in request.POST else None
    commit_ref = request.POST['commit_ref'] if 'commit_ref' in request.POST else None

    try:
        target = Target.objects.get(name=target_name)
    except Target.DoesNotExist as e:
        return HttpResponseBadRequest('Error: target is not valid.')
    if not target.valid:
        return HttpResponseBadRequest('Error: target is not valid.')
    if not re.match('\w+/\w+', repo):
        return HttpResponseBadRequest('Error: repo is not valid')

    task_data = {
        'repo': repo,
        'run_id': run_id,
        'artifact': artifact_name,
        'target': target_name,
        'actor': actor,
        'commit_sha': commit_sha,
        'commit_ref': commit_ref,
    }

    task = Task()
    task.source_type = Task.SourceType.GITHUB_ACTIONS
    task.data = json.dumps(task_data)
    task.target_name = target_name
    task.creator_ip = get_client_addr(request)
    task.save()

    worker.check_background_worker()
    worker.enqueue_task(task)

    return HttpResponse('Task queued')

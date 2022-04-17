from django.db import models


class Target(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    path = models.CharField(max_length=1024)
    desc = models.TextField(default='')
    valid = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)


class Identity(models.Model):
    secret_key = models.CharField(max_length=128, primary_key=True)
    desc = models.TextField(default='')
    valid = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)


class Task(models.Model):
    class Status(models.IntegerChoices):
        QUEUED = 0, 'Queued'
        DOWNLOADING = 1, 'Downloading'
        DEPLOYING = 2, 'Deploying'
        FINISHED = 3, 'Finished'
        FAILED = 4, 'Failed'


    class SourceType(models.IntegerChoices):
        GITHUB_ACTIONS = 0, 'GitHub Actions'


    status = models.IntegerField(default=Status.QUEUED, choices=Status.choices)
    source_type = models.IntegerField(choices=SourceType.choices)
    data = models.TextField(default='')
    source = models.TextField(default='')
    message = models.TextField(default='')
    target_name = models.CharField(max_length=64)
    creation_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(blank=True, null=True)
    creator_ip = models.CharField(max_length=64, default='')

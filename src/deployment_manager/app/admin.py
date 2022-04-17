from django.contrib import admin

from .models import *


class TargetAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_time',)


class IdentityAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_time',)


class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_time', 'finish_time')


admin.site.register(Target, TargetAdmin)
admin.site.register(Identity, IdentityAdmin)
admin.site.register(Task, TaskAdmin)

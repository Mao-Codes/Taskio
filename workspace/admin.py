from django.contrib import admin
from .models import Client, Project, Task, Invoice, Comment

admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Invoice)
admin.site.register(Comment)
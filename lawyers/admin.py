from django.contrib import admin
from lawyers import models

admin.site.register(models.Lawyer)
admin.site.register(models.Comment)
admin.site.register(models.Transaction)
admin.site.register(models.Warning)
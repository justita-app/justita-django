from django.contrib import admin
from lawyers import models

class LawyerAdmin(admin.ModelAdmin):
    exclude = ['password']

admin.site.register(models.Lawyer, LawyerAdmin)
admin.site.register(models.Comment)
admin.site.register(models.Transaction)
admin.site.register(models.Warning)

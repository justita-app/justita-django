from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User , SmsVerificationCode , UserRegistrationIdentity

UserAdmin.fieldsets[1][1]['fields'] = ('first_name', 'last_name', 'email', 'city', 'introduction_method')

class SmsVerificationAdmin(admin.ModelAdmin) :
    list_display = [ "phone_number" , "code" , "created_at" , "get_expired" , "timeout_time"]
    list_filter = [ "created_at"]

    def get_expired(self, obj):
        return obj.is_expired()

    get_expired.short_description = 'Expired'


class UserRegistrationIdentityAdmin(admin.ModelAdmin):
    list_display = ["phone_number" , "created_at" , "is_valid"]
    list_filter = ["created_at"]


admin.site.register(User, UserAdmin)
admin.site.register(SmsVerificationCode , SmsVerificationAdmin)
admin.site.register(UserRegistrationIdentity , UserRegistrationIdentityAdmin)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SmsVerificationCode, UserRegistrationIdentity


class UserAdmin(BaseUserAdmin):
    # Define custom method to display full name
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'  # Customize column header


    list_display = [field for field in BaseUserAdmin.list_display if field not in ('email', 'first_name', 'last_name', 'is_staff')] + ['full_name', 'city', 'introduction_method', 'date_joined']
    ordering = ('-date_joined',)  

# Modify the fieldsets to exclude 'email' and 'is_staff' fields
UserAdmin.fieldsets[1][1]['fields'] = ('full_name', 'city', 'introduction_method')

# Define custom admin classes for other models
class SmsVerificationAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "code", "created_at", "get_expired", "timeout_time"]
    list_filter = ["created_at"]

    def get_expired(self, obj):
        return obj.is_expired()

    get_expired.short_description = 'Expired'

class UserRegistrationIdentityAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "created_at", "is_valid"]
    list_filter = ["created_at"]

# Register models with their corresponding admin classes
admin.site.register(User, UserAdmin)
admin.site.register(SmsVerificationCode, SmsVerificationAdmin)
admin.site.register(UserRegistrationIdentity, UserRegistrationIdentityAdmin)

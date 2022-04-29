from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import SignupForm

# Ver.1
# admin.site.register(User, UserAdmin)

# Ver.2
User = get_user_model()

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('img_profile', 'gender','nickname','birth_date')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('img_profile', 'gender','nickname','birth_date'),
        }),
    )
    add_form = SignupForm


admin.site.register(User, UserAdmin)
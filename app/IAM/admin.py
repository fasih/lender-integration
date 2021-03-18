from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin as DRFTokenAdmin
from rest_framework.authtoken.models import TokenProxy

from .forms import IAMUserCreationForm, IAMUserChangeForm
from .models import *
from base.admin import *
# Register your models here.



class IAMUserAdmin(BaseAdmin, UserAdmin):
    add_form = IAMUserCreationForm
    form = IAMUserChangeForm
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)



class TokenAdmin(DRFTokenAdmin):
    autocomplete_fields = ('user',)



admin.site.unregister(TokenProxy)
admin.site.register(User, IAMUserAdmin)
admin.site.register(TokenProxy, TokenAdmin)

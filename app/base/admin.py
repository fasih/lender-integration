from django.contrib import admin

from django_json_widget.widgets import JSONEditorWidget

from .models import *
# Register your models here.



class BaseAdmin(object):
    exclude = ('status', 'activate_date', 'deactivate_date')
    _list_display = ('created', 'status', 'modified')
    ordering = ('-status', '-modified')
    list_per_page = 10

    def get_list_display(self, request):
        list_display = tuple(super().get_list_display(request))
        return list_display + self._list_display



class ServiceBaseAdmin(object):
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'code')
        }),
        ('General API Settings', {
            'classes': ('collapse',),
            'fields': ('base_url', ('params', 'headers'), 'body')
        }),
        ('OAuth Settings', {
            'classes': ('collapse',),
            'fields': ('oauth_url', ('oauth_headers', 'oauth_body'))
        }),
        ('Credentials', {
            'classes': ('collapse',),
            'fields': ('api_key', 'username', 'password',)
        }),
    )


class JSONBaseAdmin(object):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class APIBaseAdmin(object):
    exclude = ('activate_date', 'deactivate_date')



class APIBaseInlineAdmin(object):
    exclude = ('params', 'headers', 'body') + BaseAdmin.exclude
    ordering = ('priority',)
    extra = 0




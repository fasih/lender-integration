from django.contrib import admin, messages
from django.utils.translation import ngettext

from django_json_widget.widgets import JSONEditorWidget

from .forms import *
from .models import *
# Register your models here.



class BaseAdmin(object):
    _list_display = ('status', 'modified', 'created')
    exclude = ('status', 'activate_date', 'deactivate_date')
    list_per_page = 20
    ordering = ('-status', '-modified')

    def get_list_display(self, request):
        list_display = tuple(super().get_list_display(request))
        return list_display + self._list_display

    def set_active(self, request, queryset):
        updated = queryset.update(status=1)
        self.message_user(request, ngettext(
            '%d item was successfully marked as active.',
            '%d items were successfully marked as active.',
            updated,
        ) % updated, messages.SUCCESS)
    set_active.short_description = 'Marked Selected as Active'

    def set_inactive(self, request, queryset):
        updated = queryset.update(status=0)
        self.message_user(request, ngettext(
            '%d item was successfully marked as inactive.',
            '%d items were successfully marked as inactive.',
            updated,
        ) % updated, messages.SUCCESS)
    set_inactive.short_description = 'Marked Selected as Inactive'

    actions = [set_active, set_inactive]



class ServiceBaseAdmin(object):
    search_fields = ('name',)
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
            'fields': ('api_key', ('username', 'password'))
        }),
    )
    #form = ServiceBaseForm


class JSONBaseAdmin(object):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class APIBaseAdmin(object):
    exclude = BaseAdmin.exclude
    search_fields = ('name',)
    towhom = 'name'

    def get_list_filter(self, request, obj=None):
        return (self.towhom_filter, 'method')

    def get_list_select_related(self, request, obj=None):
       return (self.towhom,)

    def get_list_display(self, request, obj=None):
       return (self.towhom, 'name', 'method', 'priority', 'api_calls') + \
                BaseAdmin._list_display

    def get_ordering(self, request, obj=None):
        return ('-status', self.towhom, 'priority')

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': (('path',), ('name', self.towhom, 'priority'),
                            ('method', 'auth_scheme', 'iterable'))
            }),
            ('HTTP Request Settings', {
                'classes': ('collapse',),
                'fields': ('body', ('params', 'headers'))
            }),
            ('Iterable Data Settings', {
                'classes': ('collapse',),
                'fields': ('iterable_data', 'iterable_filters')
            }),
        )
        return fieldsets

    def api_calls(self, obj):
        return obj.iterable and 'Multiple' or 'Single'
    api_calls.short_description = 'API Calls'
    api_calls.admin_order_field = 'iterable'



class APIBaseInlineAdmin(object):
    exclude = ('params', 'headers', 'body', 'iterable', 'iterable_data',
                'iterable_filters') + BaseAdmin.exclude
    ordering = ('priority',)
    extra = 0




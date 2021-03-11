from django.contrib import admin

from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import MFBaseAdmin
# Register your models here.



class LoanManagementSystemAPIInlineAdmin(MFBaseAdmin, admin.TabularInline):
    model = LoanManagementSystemAPI
    exclude = ('params', 'body') + MFBaseAdmin.exclude
    ordering = ('priority',)
    extra = 0



class LoanManagementSystemAPIAdmin(MFBaseAdmin, admin.ModelAdmin):
    model = LoanManagementSystemAPI
    fields = (('lms', 'name'), 'path', ('method', 'auth_scheme', 'priority'),
                ('params', 'body'))
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class LoanManagementSystemAdmin(MFBaseAdmin, admin.ModelAdmin):
    inlines = (LoanManagementSystemAPIInlineAdmin,)
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'code')
        }),
        ('General API Settings', {
            'classes': ('collapse',),
            'fields': ('base_url', 'api_key', 'username', 'password',
                        'jwt_obtain', 'jwt_refresh')
        }),
    )



class ChannelPartnersAdmin(MFBaseAdmin, admin.ModelAdmin):
    pass



admin.site.register(ChannelPartners, ChannelPartnersAdmin)
admin.site.register(LoanManagementSystem, LoanManagementSystemAdmin)
admin.site.register(LoanManagementSystemAPI, LoanManagementSystemAPIAdmin)

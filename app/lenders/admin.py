from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import MFBaseAdmin
# Register your models here.



class LoanDataAdmin(MFBaseAdmin, admin.ModelAdmin):
    model = LoanData
    fields = (('loan', 'lender_api', 'response_code'), ('request', 'response'))
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class LoanDataInlineAdmin(MFBaseAdmin, admin.TabularInline):
    model = LoanData
    exclude = ('app', 'request', 'response_code') + MFBaseAdmin.exclude
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    ordering = ('lender_api__priority',)
    max_num = 0
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False



class LoanAdmin(MFBaseAdmin, admin.ModelAdmin):
    fields = (('app', 'lender',),)
    inlines = (LoanDataInlineAdmin,)



class LenderSystemAPIAdmin(MFBaseAdmin, admin.ModelAdmin):
    model = LenderSystemAPI
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class LenderSystemAPIInlineAdmin(MFBaseAdmin, admin.TabularInline):
    model = LenderSystemAPI
    exclude = ('query_params', 'body') + MFBaseAdmin.exclude
    ordering = ('priority',)
    extra = 0



class LenderSystemAdmin(MFBaseAdmin, admin.ModelAdmin):
    inlines = (LenderSystemAPIInlineAdmin,)
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



admin.site.register(Loan, LoanAdmin)
admin.site.register(LoanData, LoanDataAdmin)
admin.site.register(LenderSystem, LenderSystemAdmin)
admin.site.register(LenderSystemAPI, LenderSystemAPIAdmin)

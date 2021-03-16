from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import *
# Register your models here.



class LoanApplicationDataAdmin(JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    model = LoanApplicationData
    search_fields = ('app__lmsid',)
    list_display = ('app', 'lms_api', 'svc_api', 'response_code')
    list_filter = ('lms_api', 'lms_api__lms', 'svc_api', 'svc_api__svc')
    list_select_related = ('app', 'lms_api', 'svc_api')

    def get_fields(self, request, obj=None):
        if obj and obj.lms_api:
            API = ('lms_api',)
        elif obj:
            API = ('svc_api',)
        else:
            API = ('lms_api', 'svc_api',)
        fields = (('app',) + API + ('response_code',), ('request', 'response'),
                    'response_file')
        return fields



class LoanApplicationDataInlineAdmin(JSONBaseAdmin, BaseAdmin, admin.TabularInline):
    model = LoanApplicationData
    exclude = ('request', 'response_code', 'response_file') + BaseAdmin.exclude
    #readonly_fields = ('lms_api', 'svc_api')
    ordering = ('lms_api__priority',)
    max_num = 0
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False



class LoanApplicationAdmin(BaseAdmin, admin.ModelAdmin):
    search_fields = ('pk', 'lmsid',)
    list_display = ('lmsid', 'lms')
    list_filter = ('lms',)
    list_select_related = ('lms',)

    autocomplete_fields = ('svc',)
    fields = (('lmsid', 'cp'), ('lms', 'lender'), 'svc')
    inlines = (LoanApplicationDataInlineAdmin,)



admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(LoanApplicationData, LoanApplicationDataAdmin)

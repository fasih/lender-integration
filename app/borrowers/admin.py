from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import *
from base.models import *
from lenders.filters import *
from platforms.filters import *
# Register your models here.



class LoanApplicationDataAdmin(JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    model = LoanApplicationData
    search_fields = ('app__lmsid', 'request', 'response')
    list_display = ('app', 'lms_api', 'svc_api', 'response_code')
    list_filter = (LMSAPIFilter, LMSNestedFilter, SVCAPIFilter, SVCNestedFilter)
    list_select_related = ('app', 'lms_api', 'svc_api')

    autocomplete_fields = ('app', 'lms_api', 'svc_api')

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
    ordering = ('lms_api__priority',)
    max_num = 0
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request).filter(is_success
                                        ).order_by('lms_api__priority')
        return queryset

    def has_delete_permission(self, request, obj=None):
        return False



class LoanApplicationAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('lmsid', 'lms', 'lender')
    list_filter = (LMSFilter, LenderFilter)
    list_select_related = ('lms',)
    search_fields = ('pk', 'lmsid',)

    autocomplete_fields = ('svc', 'cp', 'lms', 'lender')
    fields = (('lmsid', 'cp'), ('lms', 'lender'), 'svc')
    inlines = (LoanApplicationDataInlineAdmin,)



admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(LoanApplicationData, LoanApplicationDataAdmin)

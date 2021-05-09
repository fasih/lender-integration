from django.contrib import admin
from django.utils.safestring import SafeText
from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import *
from base.filters import *
from base.models import *
from borrowers.filters import *
from lenders.filters import *
from platforms.filters import *
# Register your models here.



class LoanApplicationDataAdmin(JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    model = LoanApplicationData
    search_fields = ('app__lmsid', 'request', 'response')
    list_display = ('app', 'lms_api', 'svc_api', 'response_code', 'process_status')
    list_filter = (SuccessFilter, AppFilter, LMSAPIFilter, LMSNestedFilter,
                    SVCAPIFilter, SVCNestedFilter)
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
        queryset = super().get_queryset(request).filter(is_success).active(
                                        ).order_by('lms_api__priority')
        return queryset

    def has_delete_permission(self, request, obj=None):
        return False



class LoanApplicationAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('lmsid', 'application_id', 'lms', 'lender')
    list_filter = (LMSFilter, LenderFilter)
    list_select_related = ('lms',)
    search_fields = ('pk', 'lmsid',)

    autocomplete_fields = ('svc', 'cp', 'lms', 'lender')
    fields = (('lmsid', 'cp'), ('lms', 'lender'), 'svc')
    inlines = (LoanApplicationDataInlineAdmin,)

    def application_id(self, obj):
        return SafeText(
            '''<span>{app_id}</span>
            <a class='copyClipboard' href='javascript:void();' data-copy='{app_id}'>
            <i style="font-size:14px;" class="material-icons">content_copy</i>
            </a>'''.format(app_id=obj.pk))
    application_id.admin_order_field = 'lmsid'
    application_id.short_description = 'ApplicationID'




admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(LoanApplicationData, LoanApplicationDataAdmin)

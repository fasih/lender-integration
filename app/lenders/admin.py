from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from .filters import *
from .models import *
from base.admin import *
from base.models import *
from borrowers.filters import *
# Register your models here.



class LoanDataAdmin(JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    list_display = ('app', 'lender_api', 'response_code')
    list_filter = (LenderAPIFilter, LenderNestedFilter)
    search_fields = ('app__lmsid',)

    autocomplete_fields = ('loan', 'lender_api')
    fields = (('loan', 'lender_api', 'response_code'), ('request', 'response'))




class LoanDataInlineAdmin(JSONBaseAdmin, BaseAdmin, admin.TabularInline):
    model = LoanData
    exclude = ('app', 'request', 'response_code') + BaseAdmin.exclude
    ordering = ('lender_api__priority',)
    max_num = 0
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request).filter(is_success
                                        ).order_by('lender_api__priority')
        return queryset

    def has_delete_permission(self, request, obj=None):
        return False



class LoanAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('app', 'lender')
    list_filter = (LenderFilter, LMSNestedFilter)
    search_fields = ('app__lmsid',)

    autocomplete_fields = ('app', 'lender')
    fields = (('app', 'lender',),)
    inlines = (LoanDataInlineAdmin,)



class LenderSystemAPIAdmin(APIBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    autocomplete_fields = ('lender',)
    towhom_filter = LenderFilter
    towhom = 'lender'



class LenderSystemAPIInlineAdmin(APIBaseInlineAdmin, BaseAdmin, admin.TabularInline):
    model = LenderSystemAPI



class LenderSystemAdmin(ServiceBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    inlines = (LenderSystemAPIInlineAdmin,)



admin.site.register(Loan, LoanAdmin)
admin.site.register(LoanData, LoanDataAdmin)
admin.site.register(LenderSystem, LenderSystemAdmin)
admin.site.register(LenderSystemAPI, LenderSystemAPIAdmin)

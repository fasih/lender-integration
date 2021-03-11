from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import MFBaseAdmin
# Register your models here.



class LoanApplicationDataAdmin(MFBaseAdmin, admin.ModelAdmin):
    model = LoanApplicationData
    fields = (('app', 'lms_api', 'response_code'), ('request', 'response'))
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class LoanApplicationDataInlineAdmin(MFBaseAdmin, admin.TabularInline):
    model = LoanApplicationData
    exclude = ('request', 'response_code') + MFBaseAdmin.exclude
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    ordering = ('lms_api__priority',)
    max_num = 0
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False



class LoanApplicationAdmin(MFBaseAdmin, admin.ModelAdmin):
    fields = (('lmsid', 'cp'), ('lms', 'lender'))
    inlines = (LoanApplicationDataInlineAdmin,)



admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(LoanApplicationData, LoanApplicationDataAdmin)

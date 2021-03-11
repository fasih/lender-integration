from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import MFBaseAdmin
# Register your models here.



class LoanApplicationDataAdmin(MFBaseAdmin, admin.ModelAdmin):
    model = LoanApplicationData
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class LoanApplicationDataInlineAdmin(MFBaseAdmin, admin.TabularInline):
    model = LoanApplicationData
    exclude = ('request',) + MFBaseAdmin.exclude
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    max_num = 0
    extra = 0



class LoanApplicationAdmin(MFBaseAdmin, admin.ModelAdmin):
    fields = (('lmsid', 'lms', 'cp'),)
    inlines = (LoanApplicationDataInlineAdmin,)



admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(LoanApplicationData, LoanApplicationDataAdmin)

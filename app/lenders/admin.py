from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from .models import *
from base.admin import MFBaseAdmin
# Register your models here.



class LoanDataAdmin(MFBaseAdmin, admin.TabularInline):
    model = LoanData
    exclude = ('request',) + MFBaseAdmin.exclude
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    max_num = 0
    extra = 0



class LoanAdmin(MFBaseAdmin, admin.ModelAdmin):
    fields = (('app', 'lender',),)
    inlines = (LoanDataAdmin,)



class LenderSystemAPIAdmin(MFBaseAdmin, admin.ModelAdmin):
    model = LenderSystemAPI
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }



class LenderSystemAPIInlineAdmin(MFBaseAdmin, admin.TabularInline):
    model = LenderSystemAPI
    exclude = ('query_params', 'body') + MFBaseAdmin.exclude
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
admin.site.register(LenderSystem, LenderSystemAdmin)
admin.site.register(LenderSystemAPI, LenderSystemAPIAdmin)

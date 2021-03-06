from django.contrib import admin

from .filters import *
from .models import *
from base.admin import *
# Register your models here.



class LoanManagementSystemAPIInlineAdmin(APIBaseInlineAdmin, BaseAdmin, admin.TabularInline):
    model = LoanManagementSystemAPI



class LoanManagementSystemAPIAdmin(APIBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    autocomplete_fields = ('lms',)
    towhom_filter = LMSFilter
    towhom = 'lms'



class LoanManagementSystemAdmin(ServiceBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    inlines = (LoanManagementSystemAPIInlineAdmin,)



class ChannelPartnersAdmin(BaseAdmin, admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



class PlatformServiceAPIInlineAdmin(APIBaseInlineAdmin, BaseAdmin, admin.TabularInline):
    model = PlatformServiceAPI



class PlatformServiceAPIAdmin(APIBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    autocomplete_fields = ('svc',)
    towhom_filter = SVCFilter
    towhom = 'svc'


class PlatformServiceAdmin(ServiceBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    inlines = (PlatformServiceAPIInlineAdmin,)



admin.site.register(ChannelPartners, ChannelPartnersAdmin)
admin.site.register(PlatformService, PlatformServiceAdmin)
admin.site.register(PlatformServiceAPI, PlatformServiceAPIAdmin)
admin.site.register(LoanManagementSystem, LoanManagementSystemAdmin)
admin.site.register(LoanManagementSystemAPI, LoanManagementSystemAPIAdmin)

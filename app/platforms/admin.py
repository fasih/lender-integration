from django.contrib import admin

from .models import *
from base.admin import *
# Register your models here.



class LoanManagementSystemAPIInlineAdmin(APIBaseInlineAdmin, BaseAdmin, admin.TabularInline):
    model = LoanManagementSystemAPI



class LoanManagementSystemAPIAdmin(APIBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    towhom = 'lms'



class LoanManagementSystemAdmin(ServiceBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    inlines = (LoanManagementSystemAPIInlineAdmin,)



class ChannelPartnersAdmin(BaseAdmin, admin.ModelAdmin):
    pass



class PlatformServiceAPIInlineAdmin(APIBaseInlineAdmin, BaseAdmin, admin.TabularInline):
    model = PlatformServiceAPI



class PlatformServiceAPIAdmin(APIBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    towhom = 'svc'


class PlatformServiceAdmin(ServiceBaseAdmin, JSONBaseAdmin, BaseAdmin, admin.ModelAdmin):
    search_fields = ('name',)
    inlines = (PlatformServiceAPIInlineAdmin,)



admin.site.register(ChannelPartners, ChannelPartnersAdmin)
admin.site.register(PlatformService, PlatformServiceAdmin)
admin.site.register(PlatformServiceAPI, PlatformServiceAPIAdmin)
admin.site.register(LoanManagementSystem, LoanManagementSystemAdmin)
admin.site.register(LoanManagementSystemAPI, LoanManagementSystemAPIAdmin)

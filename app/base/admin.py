from django.contrib import admin

# Register your models here.



class MFBaseAdmin(object):
    exclude = ('status', 'activate_date', 'deactivate_date')
    ordering = ('-status', '-modified')
    list_per_page = 10

    def get_list_display(self, request):
        list_display = tuple(super().get_list_display(request))
        return list_display + self.exclude

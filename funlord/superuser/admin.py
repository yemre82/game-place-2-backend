from django.contrib import admin
from superuser.models import Branchs, Company, News


class NewsAdmin(admin.ModelAdmin):
    list_display = ('id','title','short_description', 'description', 'image','created_at','update_at')
    search_fields = ('title', 'short_description')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(News, NewsAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name','image','created_at','update_at')
    search_fields = ('name', 'created_at')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Company, CompanyAdmin)



class BranchsAdmin(admin.ModelAdmin):
    list_display = ('id','city','country','maps_link','created_at','update_at')
    search_fields = ('id','city','country','maps_link')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Branchs, BranchsAdmin)

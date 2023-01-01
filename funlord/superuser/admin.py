from django.contrib import admin
from superuser.models import Branchs, Company, News, addingBalanceCampaigns
from users.models import JetonHistory


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



class addingBalanceCampaignsAdmin(admin.ModelAdmin):
    list_display = ('id','name','amount_money','is_active','gift_price','is_have_discount','discount_percentage','created_at','update_at')
    search_fields = ('id','name','amount_money','gift_price','discount_percentage')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(addingBalanceCampaigns, addingBalanceCampaignsAdmin)



class JetonHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','user','jeton_amount','is_added_jeton','created_at','updated_at')
    search_fields = ('id','user','jeton_amount','is_added_jeton')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(JetonHistory, JetonHistoryAdmin)
from django.contrib import admin
from personel.models import ChildsOfGames, Personel, PersonelsOfBranchs


class PersonelAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'surname','username','is_male','tel_no','created_at','update_at')
    search_fields = ('firstname','surname','username','tel_no','is_male','birthday')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Personel, PersonelAdmin)


class PersonelsOfBranchsAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch','created_at','update_at')
    search_fields = ('id', 'branch','company')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(PersonelsOfBranchs, PersonelsOfBranchsAdmin)


class ChildsOfGamesAdmin(admin.ModelAdmin):
    last_display = ('parent_name','parent_surname','phone','child_name','child_surname','birthday','is_male','price','started_at','ended_at','is_sent_email','city','branch','game_name','is_finished','created_at','update_at')
    search_fields = ('firstname','surname','')
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(ChildsOfGames, ChildsOfGamesAdmin)









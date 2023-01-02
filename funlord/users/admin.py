from django.contrib import admin
from users.models import Balance, BalanceHistory, CustomUser, Family, Game, Gift, GiftDetails, Jeton, JetonConverisonHistory, Min_Withdrawal_Amount, OTPChange,OTPForgotPassword, OTPGetChild, OTPRegister
from django.contrib.auth.admin import UserAdmin


class UserAdmin(UserAdmin):
    list_display = ('id', 'name', 'surname', 'username','created_at','updated_at',
                    'email', 'birthday','tel_no', 'country')
    ordering= ('name','surname')
    search_fields = ('name', 'surname')
    readonly_fields = ('id', 'created_at', 'updated_at')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(CustomUser, UserAdmin)


class OTPRegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'tel_no', 'otp', 'is_verified',
                    'created_at', 'updated_at')
    search_fields = ('user', 'otp')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OTPRegister, OTPRegisterAdmin)


class OTPForgotPasswordAdmin(admin.ModelAdmin):
    list_display = ('id','otp','is_verified', 'created_at', 'updated_at')
    search_fields = ('user', 'otp')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OTPForgotPassword, OTPForgotPasswordAdmin)


class OTPChangeAdmin(admin.ModelAdmin):
    list_display = ('id','phone','otp','description','created_at','updated_at')
    search_fields = ('user','phone','otp')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OTPChange, OTPChangeAdmin)


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('id','price')
    search_fields = ('id','price')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Balance, BalanceAdmin)


class BalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','is_gift','is_adding_balance','balance','company','branch','city','game_name','created_at','updated_at')
    search_fields = ('id','balance','company','branch','city')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(BalanceHistory, BalanceHistoryAdmin)



class JetonAdmin(admin.ModelAdmin):
    list_display = ('id','amount','total','created_at','updated_at')
    search_fields = ('id','amount','total')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Jeton, JetonAdmin)


class JetonConversionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','amount','created_at','updated_at')
    search_fields = ('id','amount','total')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(JetonConverisonHistory, JetonConversionHistoryAdmin)


class Min_Withdrawal_AmountAdmin(admin.ModelAdmin):
    list_display = ('min_amount','percantage','created_at','updated_at')
    search_fields = ('id','min_amount','percantage')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Min_Withdrawal_Amount, Min_Withdrawal_AmountAdmin)


class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id','firstname','lastname','birthday','is_male','is_parent','profile_image','phone','created_at','updated_at')
    search_fields = ('id','firstname','lastname','birthday','is_male','is_parent')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Family, FamilyAdmin)


class GameAdmin(admin.ModelAdmin):
    list_display = ('id','gamer','price','started_at','ended_at','is_finished','company','city','branch','game_name','created_at','updated_at')
    search_fields = ('id','gamer','price','started_at','ended_at','is_finished','company','city','branch','game_name')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Game, GameAdmin)


class OTPGetChildAdmin(admin.ModelAdmin):
    list_display = ('id','phone','otp','description','is_verified','created_at','updated_at')
    search_fields = ('id','firstname','lastname','birthday','is_male','is_parent')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(OTPGetChild, OTPGetChildAdmin)



class GiftAdmin(admin.ModelAdmin):
    list_display = ('gift_name','gift_description1','gift_description2','gift_description3','is_gift_added','number_of_gifts','number_of_gifts','jeton_amount_of_gifts','created_at','updated_at')
    search_fields = ('id','gift_description1','gift_description2','gift_description3','jeton_amount_of_gifts')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Gift, GiftAdmin)


class GiftDetailsAdmin(admin.ModelAdmin):
    list_display = ('id','address','created_at','updated_at')
    search_fields = ('id','gift_description1','gift_description2','gift_description3','jeton_amount_of_gifts')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(GiftDetails, GiftDetailsAdmin)

from django.contrib import admin
from users.models import Balance, BalanceHistory, CustomUser, Jeton, Min_Withdrawal_Amount,OTPForgotPassword, OTPRegister
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



class Min_Withdrawal_AmountAdmin(admin.ModelAdmin):
    list_display = ('min_amount','percantage','created_at','updated_at')
    search_fields = ('id','min_amount','percantage')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Min_Withdrawal_Amount, Min_Withdrawal_AmountAdmin)



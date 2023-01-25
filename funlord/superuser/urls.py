from django.urls import path
from superuser.views import general_type_login,super_user_forgot_password,super_user_forgot_password_validation,super_user_change_password,get_all_news,get_news
urlpatterns= [
    path('general-type-login',general_type_login),
    path('super-user-change-password',super_user_change_password),
    path('super-user-forgot-password',super_user_forgot_password),
    path('super-user-forgot-password-validation',super_user_forgot_password_validation),
    path('get-all-news',get_all_news),
    path('get-news/<int:news_id>',get_news)
]
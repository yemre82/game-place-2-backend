from django.urls import path
from superuser.views import  get_all_news,get_news, super_user_change_password, super_user_login
urlpatterns= [
    # path('add-news',add_news),
    path('get-all-news',get_all_news),
    path('get-news',get_news),
    # path('edit-news',edit_news),
    # path('delete-news',delete_news),
    path('super-user-login',super_user_login),
    path('super-user-change-password',super_user_change_password)
]
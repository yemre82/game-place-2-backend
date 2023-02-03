from django.urls import path
from superuser.views import add_branch, add_news, all_branchs_count, all_game_history, delete_branch, delete_news, edit_branch, edit_news, general_type_login, get_all_branchs, get_branch,super_user_forgot_password,super_user_forgot_password_validation,super_user_change_password,get_all_news,get_news
urlpatterns= [
    path('general-type-login',general_type_login),
    path('super-user-change-password',super_user_change_password),
    path('super-user-forgot-password',super_user_forgot_password),
    path('super-user-forgot-password-validation',super_user_forgot_password_validation),
    path('get-all-news',get_all_news),
    path('get-news/<int:news_id>',get_news),
    path('add-news',add_news),
    path('edit-news',edit_news),
    path('delete-news',delete_news),
    path('get-all-branchs',get_all_branchs),
    path('get-branch/<int:branch_id>',get_branch),
    path('add-branch',add_branch),
    path('all-branchs-count',all_branchs_count),
    path('delete-branch',delete_branch),
    path('edit-branch',edit_branch),
    path('all-game-history/started=<int:started>&limit=<int:limit>&filtering=<str:filtering>',all_game_history)
]
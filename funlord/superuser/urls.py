from django.urls import path
from superuser.views import add_branch, add_news, add_personel, add_personel_to_branch, all_branchs_count, all_female_personel_count, all_game_history, all_male_personel_count, all_personels_count, birthday_personel, delete_branch, delete_news, delete_personel, delete_personel_of_branch, edit_branch, edit_news, edit_personel, general_type_login, get_all_branchs, get_all_personels, get_branch, get_branch_personels_count, get_personel_of_branch, get_personels_of_branch,super_user_forgot_password,super_user_forgot_password_validation,super_user_change_password,get_all_news,get_news
urlpatterns= [
    path('general-type-login',general_type_login),
    path('super-user-change-password',super_user_change_password),
    path('super-user-forgot-password',super_user_forgot_password),
    path('super-user-forgot-password-validation',super_user_forgot_password_validation),
    path('get-all-news/started=<int:started>&limit=<int:limit>&filtering=<str:filtering>&company_name=<str:company_name>', get_all_news),
    path('get-news/<int:news_id>',get_news),
    path('add-news',add_news),
    path('edit-news',edit_news),
    path('delete-news',delete_news),
    path('get-all-branchs/started=<int:started>&limit=<int:limit>&filtering=<str:filtering>&company_name=<str:company_name>',get_all_branchs),
    path('get-branch/<int:branch_id>',get_branch),
    path('add-branch',add_branch),
    path('all-branchs-count',all_branchs_count),
    path('delete-branch',delete_branch),
    path('edit-branch',edit_branch),
    path('get-all-personels/started=<int:started>&limit=<int:limit>&filtering=<str:filtering>&company_name=<str:company_name>',get_all_personels),
    path('get-personel-of-branch',get_personel_of_branch),
    path('add-personel',add_personel),
    path('add-personel-to-branch',add_personel_to_branch),
    path('edit-personel',edit_personel),
    path('delete-personel',delete_personel),
    path('delete-personel-of-branch',delete_personel_of_branch),
    path('all-personels-count',all_personels_count),
    path('all-male-personel-count',all_male_personel_count),
    path('all-female-personel-count',all_female_personel_count),
    path('birthday-personel',birthday_personel),
    path('get-personels-of-branch',get_personels_of_branch),
    path('get-branch-personels-count',get_branch_personels_count),
    path('all-game-history/started=<int:started>&limit=<int:limit>&filtering=<str:filtering>',all_game_history),
]
from django.urls import path
from users.views import add_balance, game_info, get_all_branchs, get_all_news, get_balance, get_balance_history, get_branch,get_news, get_or_create_jeton, jeton_conversion,create_otp,register,login,forgot_password,forgot_password_verification,change_password, verify_otp

urlpatterns= [
    path("create-otp",create_otp),
    path("verify-otp",verify_otp),
    path("register",register),
    path("login",login),
    path("forgot-password",forgot_password),
    path("forgot-password-verification",forgot_password_verification),
    path("change-password",change_password),
    path('get-all-news/<str:filtering>',get_all_news),
    path('get-news/<int:news_id>',get_news),
    path('get-all-branchs/<str:filtering>',get_all_branchs),
    path('get-branch/<int:branch_id>',get_branch),
    path('get-balance',get_balance),
    path('add-balance',add_balance),
    path('get-balance-history/<str:filter_type>',get_balance_history),
    path('get-or-create-jeton',get_or_create_jeton),
    path('jeton-conversion',jeton_conversion),
    path('game-info/<str:qr_code>',game_info)
]
from django.urls import path
from superuser.views import  add_news,get_all_news,get_news,edit_news,delete_news
urlpatterns= [
    path("add-news",add_news),
    path("get-all-news",get_all_news),
    path("get-news",get_news),
    path("edit-news",edit_news),
    path("delete-news",delete_news)
]
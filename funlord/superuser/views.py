from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from funlord.responses import response_200, response_400
from users.models import CustomUser,OTPForgotPassword,OTPRegister
from users.utils import register_parameters,email_exist,generate_random_num,is_password_match,password_is_valid,send_email
from superuser.models import Company, News


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_news(request):
    if not request.user.is_admin:
        return response_400('you can not add news')
    company_name=request.data.get('company_name')
    try:
        com_obj=Company.objects.get(name=company_name)
    except ObjectDoesNotExist as e:
        return response_400('there is no such company')
    title=request.data.get('title')
    short_description=request.data.get('short_description')
    description=request.data.get('description')
    image=request.data.get('image')
    is_campaign=request.data.get('is_campaign')
    price=request.data.get('price')
    News.objects.create(
        company=com_obj,
        title=title,
        short_description=short_description,
        description=description,
        image=image,
        is_campaign=is_campaign,
        price=price
    )
    return response_200('success')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_news(request):
    news_obj = News.objects.all().order_by('-id')[:20]
    news_list = []
    for news in news_obj:
        return_obj = {
            "id":news.id,
            "title": news.title,
            "short_description": news.short_description,
            "description": news.description,
            "image": "/media/"+str(news.image),
            "created_at":news.created_at
        }
        news_list.append(return_obj)
    return response_200(news_list)



api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request,news_id):
    if not email_exist(request.user.email):
        return response_400('there is no such user')
    try:
        news_obj=News.objects.get(id=news_id)
    except ObjectDoesNotExist as e:
        return response_400('there no such news')
    return_obj={
        "id":news_obj.id,
        "title": news_obj.title,
        "short_description": news_obj.short_description,
        "description": news_obj.description,
        "image": "/media/"+str(news_obj.image),
        "created_at":news_obj.created_at
    }
    return response_200(return_obj)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_news(request,news_id):
    if not email_exist(request.user.email):
        return response_400('there is no such user')
    try:
        news_obj=News.objects.get(id=news_id)
    except ObjectDoesNotExist as e:
        return response_400('there no such news')
    title=request.data.get('title')
    short_description=request.data.get('short_description')
    description=request.data.get('description')
    image=request.data.get('image')
    news_obj.title=title
    news_obj.short_description=short_description
    news_obj.description=description
    news_obj.image=image
    news_obj.save()
    return response_200('success')



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_news(request):
    if not email_exist(request.user.email):
        return response_400('tehre is no such user')
    id=request.data.get('id')
    try:
        news_obj=News.objects.get(id=id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such news')
    news_obj.delete()
    return response_200('success')


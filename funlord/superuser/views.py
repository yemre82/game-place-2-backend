from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from funlord.responses import response_200, response_400
from users.models import CustomUser,OTPForgotPassword,OTPRegister
from users.utils import is_verified, register_parameters,email_exist,generate_random_num,is_password_match,password_is_valid,send_email, sendSMSVerification
from superuser.models import Branchs, Company, News


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def add_news(request):
#     if not request.user.is_admin:
#         return response_400('you can not add news')
#     company_name=request.data.get('company_name')
#     try:
#         com_obj=Company.objects.get(name=company_name)
#     except ObjectDoesNotExist as e:
#         return response_400('there is no such company')
#     title=request.data.get('title')
#     short_description=request.data.get('short_description')
#     description=request.data.get('description')
#     image=request.data.get('image')
#     is_campaign=request.data.get('is_campaign')
#     price=request.data.get('price')
#     News.objects.create(
#         company=com_obj,
#         title=title,
#         short_description=short_description,
#         description=description,
#         image=image,
#         is_campaign=is_campaign,
#         price=price
#     )
#     return response_200('success')


# api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_news(request,news_id):
#     if not email_exist(request.user.email):
#         return response_400('there is no such user')
#     try:
#         news_obj=News.objects.get(id=news_id)
#     except ObjectDoesNotExist as e:
#         return response_400('there no such news')
#     return_obj={
#         "id":news_obj.id,
#         "title": news_obj.title,
#         "short_description": news_obj.short_description,
#         "description": news_obj.description,
#         "image": "/media/"+str(news_obj.image),
#         "created_at":news_obj.created_at
#     }
#     return response_200(return_obj)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def edit_news(request,news_id):
#     if not email_exist(request.user.email):
#         return response_400('there is no such user')
#     try:
#         news_obj=News.objects.get(id=news_id)
#     except ObjectDoesNotExist as e:
#         return response_400('there no such news')
#     title=request.data.get('title')
#     short_description=request.data.get('short_description')
#     description=request.data.get('description')
#     image=request.data.get('image')
#     news_obj.title=title
#     news_obj.short_description=short_description
#     news_obj.description=description
#     news_obj.image=image
#     news_obj.save()
#     return response_200('success')


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def delete_news(request):
#     if not email_exist(request.user.email):
#         return response_400('tehre is no such user')
#     id=request.data.get('id')
#     try:
#         news_obj=News.objects.get(id=id)
#     except ObjectDoesNotExist as e:
#         return response_400('there is no such news')
#     news_obj.delete()
#     return response_200('success')


@api_view(['POST'])
@permission_classes([AllowAny])
def super_user_login(request):
    username = request.data.get("username")
    try:
        user_obj = CustomUser.objects.get(username=username)
    except ObjectDoesNotExist as e:
        return response_400('there is no such user')
    if not user_obj.is_admin:
        return response_400('the user is not an superuser')
    password = request.data.get("password")
    if not user_obj.check_password(password):
        return response_400('the password is not true')
    token, _ = Token.objects.get_or_create(user=user_obj)
    return_obj = {
        'token': token.key,
        'is_staff':user_obj.is_staff,
        'is_personel':user_obj.is_personel,
        'is_can_write':user_obj.is_can_write,
        'is_company':user_obj.is_company
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def super_user_change_password(request):
    old_password=request.data.get('old_password')
    if not request.user.check_password(old_password):
        return response_400('your old password does not match your password')
    password=request.data.get('password')
    password_a=request.data.get('password_a')
    if len(password)<8:
        return response_400('weak password')
    if password != password_a:
        return response_400("the passwords are not match")
    request.user.set_password(password)
    request.user.save()
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def super_user_forgot_password(request):
    tel_no=request.data.get('tel_no')
    try:
        user_obj=CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('this user does not valid')
    otp=generate_random_num()
    # sendSMSVerification(otp,[tel_no])
    OTPForgotPassword.objects.create(
        user=request.user,
        otp=otp,
        is_verified=False
    )
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def super_user_forgot_password_validation(request):
    tel_no=request.data.get('tel_no')
    otp=request.data.get('otp')
    try:
        user_obj=CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('this user does not valid')
    otp_obj=OTPForgotPassword.objects.filter(user=request.user,otp=otp,is_verified=False).order_by('-id')
    if len(otp_obj) == 0:
        return response_400('you have not any otp')
    for i in otp_obj:
        if i.is_verified == True:
            return response_400('your otp already verified')
        else:
            if i.otp != otp:
                return response_400('this otp is wrong')
            else:
                i.is_verified=True
                i.save()
                return response_200(None)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_news(request,filtering):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    list=[]
    if filtering == 'all':
        news_obj=News.objects.all().order_by('-id')
    if filtering != 'all':
        try:
            company_obj=Company.objects.get(company=filtering)
        except ObjectDoesNotExist as e:
            return response_400('there is no such company')
        for i in news_obj:
            return_obj={
                'id':i.id,
                'title':i.title,
                'short_description':i.short_description,
                'description':i.description,
                'image': '/media/'+str(i.image),
                'is_campaign':i.is_campaign,
                'price':i.price,
                'created_at':i.created_at
            }
            list.append(return_obj)
    return response_200(list)

    









from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from funlord.responses import response_200, response_400
from users.models import CustomUser,OTPForgotPassword
from users.utils import is_verified,generate_random_num,sendSMSVerification
from superuser.models import Company, News


@api_view(['POST'])
@permission_classes([AllowAny])
def general_type_login(request):
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
    sendSMSVerification(otp,[tel_no])
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
def get_all_news(request):
    if not request.user.is_admin:
        return response_400('this user is not admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    news_obj = News.objects.all().order_by('-id')
    list = []
    for i in news_obj:
        return_obj = {
            'id': i.id,
            'title': i.title,
            'short_description': i.short_description,
            'description': i.description,
            'image': '/media/'+str(i.image),
            'is_campaign': i.is_campaign,
            'created_at': i.created_at,
            'price': i.price,
        }
        list.append(return_obj)
    return response_200(list)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request, news_id):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    try:
        news_obj = News.objects.get(id=news_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such news')
    list = []
    return_obj = {
        'id': news_obj.id,
        'title': news_obj.title,
        'short_description': news_obj.short_description,
        'description': news_obj.description,
        'image': '/media/' + str(news_obj.image),
        'is_campaign': news_obj.is_campaign,
        'price': news_obj.price,
    }
    list.append(return_obj)
    return response_200(list)

 







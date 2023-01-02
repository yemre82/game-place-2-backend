from django.utils.timezone import localtime
import requests
import iyzipay
import json
from django.shortcuts import render
from datetime import datetime, timedelta
from urllib.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from funlord.responses import response_200, response_400
from users.models import Balance, BalanceHistory, CustomUser, Family, Game, Gift, GiftDetails, Jeton, JetonConverisonHistory, JetonHistory, Min_Withdrawal_Amount, OTPChange, OTPForgotPassword, OTPGetChild,OTPRegister
from users.utils import generate_sha256, generate_sha256_for_transactionId, generate_sha256_for_user, is_verified, register_parameters,generate_random_num,is_password_match,password_is_valid, sendSMSVerification
from superuser.models import Branchs, ChildOfGames, News,Company, addingBalanceCampaigns


@api_view(['POST'])
@permission_classes([AllowAny])
def create_otp(request):
    now_2_min = datetime.now() - timedelta(minutes=2)
    tel_no=request.data.get('tel_no')
    try:
        user_obj=OTPRegister.objects.get(tel_no=tel_no,created_at__lt=now_2_min)
        return response_400("The user is already obtained")
    except ObjectDoesNotExist as e:
        otp = generate_random_num()
        sendSMSVerification(otp,[tel_no])
        OTPRegister.objects.create(
            tel_no=tel_no,
            otp=otp,
        )
        return response_200('success')


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    otp=request.data.get('otp')
    tel_no=request.data.get('tel_no')
    try:
        otp_obj=OTPRegister.objects.get(otp=otp,tel_no=tel_no,is_verified=False)
    except ObjectDoesNotExist as e:
        return response_400('this user has not this otp')
    otp_obj.is_verified=True
    otp_obj.save()
    return response_200('success')

        
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if not register_parameters(request.data):
        return response_400('your informations are not enough')
    tel_no=request.data.get('tel_no')
    name=request.data.get('name')
    surname=request.data.get('surname')
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    gender=request.data.get('gender')
    member_id=request.data.get('member_id')
    try:
        user_obj=CustomUser.objects.get(tel_no=tel_no)
        return response_400('this user is already obtained')
    except ObjectDoesNotExist as e:
        try:
            otp_obj=OTPRegister.objects.get(tel_no=tel_no,is_verified=True)
        except ObjectDoesNotExist as e:
            return response_400('you must be entering')
        password=request.data.get('password')
        password_a=request.data.get('password_a')
        if not password_is_valid(password):
            return response_400('your password does not valid')
        if not is_password_match(password,password_a):
            return response_400('these passwords are not match')    
        return_obj=CustomUser.objects.create(
            name=name,
            surname=surname,
            birthday=birthday,
            tel_no=tel_no,
            gender=gender,
            member_id=generate_sha256_for_user(tel_no,datetime.now())
        )
        return_obj.set_password(password)
        return_obj.save()
        Balance.objects.create(
            user=return_obj  
        )
        if gender=="erkek":
            is_male=True
        else:
            is_male=False
        Family.objects.create(
            parent=return_obj,
            firstname=name,
            lastname=surname,
            birthday=birthday,
            is_male=is_male,
            is_parent=True,
            phone=tel_no
        )
        return response_200('success')


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    tel_no = request.data.get('tel_no')
    try:
        user_obj=CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('there is no such user')
    password = request.data.get("password")
    try:
        otp_obj=OTPRegister.objects.get(tel_no=tel_no,is_verified=True)
    except ObjectDoesNotExist as e:
        return response_400('there is no such user')
    if not user_obj.check_password(password):
        return response_400('the password is not true')
    token, _ = Token.objects.get_or_create(user=user_obj)
    return_obj = {
        "token": token.key,
        "qr_code": user_obj.qr_code,
        "name": user_obj.name,
        "surname":user_obj.surname,
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    tel_no = request.data.get('tel_no')
    try:
        user_obj = CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('there is no such email')
    otp = generate_random_num()
    sendSMSVerification(otp,[tel_no])
    OTPForgotPassword.objects.create(
        user=user_obj,
        otp=otp,
        is_verified=False
    )
    return response_200(None)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_verification(request):
    tel_no=request.data.get('tel_no')
    otp=request.data.get('otp')
    try:
        user_obj=CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('this user already obtained')
    otp_obj=OTPForgotPassword.objects.filter(otp=otp,user=user_obj).order_by('-id')
    if len(otp_obj)==0:
        return response_400("there is no such otp")
    for i in otp_obj:
        if i.is_verified==True:
            return response_400("This otp is verified already get")
        else:
            if i.otp!=otp:
                return response_400("This otp is not true")
            else:
                i.is_verified = True
                i.save()
                return response_200(None)
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def change_password(request):
    tel_no=request.data.get('tel_no')
    try:
        user_obj=CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('there is no such user')
    password=request.data.get("password")
    password_a=request.data.get("password_a")
    if not is_password_match(password,password_a):
        return response_400("the passwords are not match")
    user_obj.set_password(password)
    user_obj.save()
    return response_200(None)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_news(request,filtering):
    liste=[]
    if filtering == 'all':
        news_obj = News.objects.all().order_by('-id')
    if filtering != 'all':
        try:
            company_obj=Company.objects.get(name=filtering)
        except ObjectDoesNotExist as e:
            return response_400("this company does not exist")
        news_obj = News.objects.filter(company=company_obj)
    for news in news_obj:
        return_obj = {
            "id":news.id,
            "company":news.company.name,
            "title": news.title,
            "short_description": news.short_description,
            "description": news.description,
            "image": "/media/"+str(news.image),
            "is_campaign":news.is_campaign,
            "price":news.price,
            "created_at":localtime(news.created_at)
        }
        liste.append(return_obj)
    return response_200(liste)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request,news_id):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    try:
        otp_obj=OTPRegister.objects.get(tel_no=request.user.tel_no,is_verified=True)
    except ObjectDoesNotExist as e:
        return response_400('this user is not verified')
    try:
        news_obj=News.objects.get(id=news_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such news')
    return_obj={
        "id":news_obj.id,
        "company":news_obj.company.name,
        "title": news_obj.title,
        "short_description": news_obj.short_description,
        "description": news_obj.description,
        "image": "/media/"+str(news_obj.image),
        "is_campaign":news_obj.is_campaign,
        "price":news_obj.price,
        "created_at":localtime(news_obj.created_at)
    }
    return response_200(return_obj)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_branchs(request,filtering):
    liste=[]
    if filtering=='all':
        comp_obj=Company.objects.all().order_by('-id')
    else:
        comp_obj=Company.objects.filter(name=filtering).order_by('-id')
    for comp in comp_obj:
        branch_obj=Branchs.objects.filter(company=comp)
        for i in branch_obj:
            return_obj={
                "id":i.id,
                "company":i.company.name,
                "branch":i.branch,
                "city":i.city,
                "country":i.country,
                "maps_link":i.maps_link
            }
            liste.append(return_obj)
    return response_200(liste)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branch(request,branch_id):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    try:
        otp_obj=OTPRegister.objects.get(tel_no=request.user.tel_no,is_verified=True)
    except ObjectDoesNotExist as e:
        return response_400('there is no such user')
    try:
        branch_obj=Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such branch')
    return_obj={
        "id":branch_obj.id,
        "company":branch_obj.company.name,
        "branch":branch_obj.branch,
        "city":branch_obj.city,
        "country":branch_obj.country,
        "maps_link":branch_obj.maps_link,
        "created_at":localtime(branch_obj.created_at)
    }
    return response_200(return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    try:
        balance_obj=Balance.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        return response_400('this user has not any balance')
    return_obj={
        "balance":balance_obj.price
    }
    return response_200(return_obj)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def add_balance(request):
#     price=request.data.get('price')
#     campaigns_obj=addingBalanceCampaigns.objects.filter(is_active=True,is_have_discount=True).order_by('-amount_money')
#     if len(campaigns_obj)==0:
#         return response_200('burada indirim yoktur')
#     else:
#         liste=[]
#         for i in campaigns_obj:
#             if price >= i.amount_money:
#                 return_obj={
#                     "discount_percentage":i.discount_percentage,
#                     "name":i.name
#                 }
#                 liste.append(return_obj)
#         return response_200(liste)
#     for i in campaigns_obj:
#         if i.amount_money <= price:
#             if i.is_have_discount:
#                 basket_items = [
#                 {
#                     "id": "bakiye"+str(price*i.discount_percentage),
#                     "price": str(price*i.discount_percentage),
#                     "name": "bakiye"+str(price*i.discount_percentage),
#                     "category1": "bakiye",
#                     "itemType": "VIRTUAL"
#                 }
#                 ]
#             else:
#                 basket_items = [
#                 {
#                     "id": "bakiye"+str(price),
#                     "price": str(price),
#                     "name": "bakiye"+str(price),
#                     "category1": "bakiye",
#                     "itemType": "VIRTUAL"
#                 }
#                 ]
#                 break
#             break
#         break

    #if payment_json["status"]=='success':
#         BalanceHistory.objects.create(
#             user=request.user,
#             is_gift=False,
#             is_adding_balance=True,
#             balance=price,
#         )
#         try:
#             balance_obj=Balance.objects.get(user=request.user)
#         except ObjectDoesNotExist as e:
#             return response_400('this usern does not added price')
#         balance_obj.price += price
#         balance_obj.save()
#         campaigns_obj=addingBalanceCampaigns.objects.filter(is_active=True).order_by('-amount_money')
#         if len(campaigns_obj)==0:
#             return response_200(None)
#         for i in campaigns_obj:
#             if i.amount_money <= price:
#                 if i.is_have_discount==False:
#                     balance_obj.price += i.gift_price
#                     balance_obj.save()
#                     BalanceHistory.objects.create(
#                         user=request.user,
#                         is_gift=True,
#                         is_adding_balance=True,
#                         balance=i.gift_price,
#                     )
#                     return response_200(None)
#     return response_400(payment_json["status"])



#     return response_200('success')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance_history(request,filter_type):
    this_time=datetime.timestamp(datetime.now())
    if not is_verified(request.user.tel_no):
        return response_400("the user is not verified")
    if filter_type=="24s":
        filter_time=this_time-86400
    elif filter_type=="7g":
        filter_time=this_time-604800
    elif filter_type=="30g":
        filter_time=this_time-2592000
    filter_time=datetime.fromtimestamp(filter_time)
    history_obj = BalanceHistory.objects.filter(
        user=request.user,created_at__gt=filter_time).order_by('-created_at')
    history_list = []
    for i in history_obj:
        return_obj = {
            "user": i.user.name+" "+i.user.surname,
            "history": i.balance,
            "is_gift":i.is_gift,
            "is_adding_balance": i.is_adding_balance,
            "company":i.company,    
            "city": i.city,
            "branch": i.branch,
            "game_name": i.game_name,
            "created_at": localtime(i.created_at),
            "updated_at": localtime(i.updated_at)
        }
        history_list.append(return_obj)
    return response_200(history_list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_or_create_jeton(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    try:
        jeton_obj=Jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        user_obj=Jeton.objects.create(
            user=request.user,
        )
    return_obj = {
        "jeton_amount":jeton_obj.amount,
        "conversional_jeton":jeton_obj.total
    }
    return response_200(return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_jeton_history(request,ended):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    jeton_obj=JetonHistory.objects.filter(user=request.user).order_by('-created_at')[:ended]
    history_list=[]
    for i in jeton_obj:
        return_obj={
            'user': i.user.name+" "+i.user.surname,
            'jeton_amount':i.jeton_amount,
            'is_added_jeton':i.is_added_jeton,
            'created_at':localtime(i.created_at),
            'updated_at':localtime(i.updated_at)
        }
        history_list.append(return_obj)
    return response_200(history_list)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jeton_conversion(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    try:
        jeton_obj=Jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        return response_400('there is no such user')
    try:
        amount_obj=Min_Withdrawal_Amount.objects.get(id=1)
    except ObjectDoesNotExist as e:
        return response_400('there is not exist jeton conversion')
    amount=request.data.get('amount')
    if not amount_obj.min_amount < amount:
        return response_400('your amount must greater than min_amount')
    if jeton_obj.amount < amount:
        return response_400("the balance is not enough")
    jeton_obj.amount -= amount 
    jeton_obj.save()
    try:
        balance_obj=Balance.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        balance_obj=Balance.objects.create(user=request.user)
    balance_obj.price += (amount)/amount_obj.tl_to_jeton
    balance_obj.price.save()
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_jeton_conversion_history(request,ended):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    jeton_obj=JetonConverisonHistory.objects.filter(user=request.user).order_by('-created_at')[:ended]
    history_obj=[]
    for i in jeton_obj:
        return_obj={
            "user": i.user.name+" "+i.user.surname,
            "amount":i.amount,
            "conversion_jeton":i.is_conversion_jeton,
            "created_at":localtime(i.created_at),
            "updated_at":localtime(i.updated_at)
        }
        history_obj.append(return_obj)
    return response_200(history_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    return_obj={
        "name":request.user.name,
        "surname":request.user.surname,
        "birthday":request.user.birthday,
        "tel_no":request.user.tel_no,
        "gender":request.user.gender
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_family(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    family_obj=Family.objects.filter(parent=request.user)
    family_list=[]
    for family in family_obj:
        birthday_day=str((family.birthday).day)
        if len(birthday_day)==1:
            birthday_day="0"+birthday_day
        birthday_month=str((family.birthday).month)
        if len(birthday_month)==1:
            birthday_month="0"+birthday_month
        return_obj = {
            "id": family.id,
            "name": family.firstname,
            "surname": family.lastname,
            "birthday":birthday_day+"."+birthday_month+"."+str((family.birthday).year) ,
            "is_male":family.is_male,
            "is_parent": family.is_parent,
            "phone":family.phone,
            "profile_image":"/media/"+str(family.profile_image)
        }
        family_list.append(return_obj)
    return response_200(family_list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_child_family_member(request):
    if not is_verified(request.user.tel_no):
        return response_400("the user is not verified")
    name = request.data.get("name")
    surname = request.data.get("surname")
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    is_male = request.data.get("is_male")
    if is_male=="True" or is_male=="true" or is_male==True:
        is_male=True
    else:
        is_male=False
    profile_image=request.data.get("profile_image")
    Family.objects.create(
        parent=request.user,
        firstname=name,
        lastname=surname,
        birthday=birthday,
        is_male=is_male,
        profile_image=profile_image
    )
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_member_from_family(request):
    if not is_verified(request.user.tel_no):
        return response_400("the user is not verified")
    family_id = request.data.get("id")
    try:
        family_obj = Family.objects.get(id=family_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such family")
    if family_obj.parent != request.user:
        return response_400("you can't remove this family")
    if family_obj.phone==request.user.tel_no:
        return response_400("you can't remove yourself")
    family_obj.delete()
    return response_200("success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_member_from_family(request):
    if not is_verified(request.user.tel_no):
        return response_400("the user is not verified")
    family_id = request.data.get("id")
    try:
        family_obj = Family.objects.get(id=family_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such family")
    if family_obj.parent != request.user:
        return response_400("you can't edit this family")
    if family_obj.phone==request.user.tel_no:
        return response_400("you can't edit yourself. Please go to ChangeNameSurname Api")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    is_male = request.data.get("is_male")
    phone=request.data.get("phone")
    is_parent=False
    if len(phone)==0:
        is_parent=True
    family_obj.firstname=firstname
    family_obj.lastname=lastname
    family_obj.birthday=birthday
    family_obj.is_male=is_male
    family_obj.phone=phone
    family_obj.is_parent=is_parent
    family_obj.save()
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_name_surname(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    firstname=request.data.get("firstname")
    lastname=request.data.get("lastname")
    if len(firstname)==0:
        return response_400("the firstname must be at least 1 letter")
    if len(lastname)==0:
        return response_400("the lastname must be at least 1 letter")
    request.user.name=firstname
    request.user.surname=lastname
    request.user.save()
    try:
        family_obj=Family.objects.get(parent=request.user,phone=request.user.tel_no)
    except ObjectDoesNotExist as e:
        return response_400("there is no such family")
    family_obj.firstname=firstname
    family_obj.lastname=lastname
    family_obj.save()
    return response_200("success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_birthday(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    try:
        family_obj=Family.objects.get(
            parent=request.user,
            firstname=request.user.firstname,
            lastname=request.user.lastname,
            phone=request.user.phone
        )
    except ObjectDoesNotExist as e:
        return response_400("family object is not valid")
    request.user.birthday=birthday
    request.user.save()
    family_obj.birthday=birthday
    family_obj.save()

    return response_200("success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_phone(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    tel_no=request.data.get("phone")
    otp = generate_random_num()
    sendSMSVerification(otp,[tel_no])
    description = "verification"
    OTPChange.objects.create(
        user=request.user,
        phone=tel_no,
        otp=otp,
        description=description
    )
    return response_200("success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_phone_verification(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    change_phone_obj=OTPChange.objects.filter(user=request.user,is_verified=False).order_by("-id")
    otp=request.data.get("otp")
    if len(change_phone)==0:
        return response_400("there is no such otp")
    for i in change_phone_obj:
        if i.otp!=otp:
            return response_400("otp is not match")
        try:
            family_obj=Family.objects.get(
                parent=request.user,
                firstname=request.user.firstname,
                lastname=request.user.lastname,
                phone=request.user.phone
            )
        except ObjectDoesNotExist as e:
            return response_400("family object is not valid")
        request.user.phone=i.phone
        request.user.save()
        family_obj.phone=i.phone
        family_obj.save()
        OTPRegister.objects.create(
            tel_no=i.phone,
            otp=otp,
            is_verified=True
        )
        i.is_verified=True
        i.save()
        return response_200("success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_in_application(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    old_password=request.data.get("old_password")
    if not request.user.check_password(old_password):
        return response_400("your old password is wrong")
    password = request.data.get("password")
    password_a = request.data.get("password_again")
    if len(password) < 8:
        return response_400("your password digits number must be at least 8")
    if password != password_a:
        return response_400("Gönderdiğiniz şifreler birbirleri ile aynı değiller.")
    request.user.set_password(password)
    request.user.save()
    return response_200("success")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_child_in_game(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    this_time=datetime.now()
    game_obj=Game.objects.filter(user=request.user,is_finished=False).order_by("-id")
    returning_list=[]
    for i in game_obj:
        remaining_time_ts=datetime.timestamp(i.ended_at)-datetime.timestamp(this_time)
        how_much_ticket_played=(datetime.timestamp(i.ended_at)-datetime.timestamp(i.started_at))/1800
        one_ticket_price=(i.price)/how_much_ticket_played
        return_obj={
            "game_id":i.id,
            "user":i.user.firstname + " "+ i.user.lastname,
            "gamer":i.gamer.firstname+ " "+ i.gamer.lastname,
            "gamer_id":i.gamer.id,
            "price":one_ticket_price,
            "started_at":localtime(i.started_at),
            "ended_at":localtime(i.ended_at),
            "created_at":localtime(i.created_at),
            "update_at":localtime(i.update_at),
            "remaining_time":remaining_time_ts,
            "city":i.city,
            "branch":i.branch,
            "game_name":i.game_name
        }
        returning_list.append(return_obj)
    return response_200("success",returning_list)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_child_from_game(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    this_time=datetime.now()
    game_obj=Game.objects.filter(user=request.user,started_at__gl=this_time,ended_at__gt=this_time).order_by("-id")
    if len(game_obj)==0:
        return response_400("the user has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=Game.objects.get(user=request.user,is_finished=False,id=game_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such game")
    otp = generate_random_num()
    description="get-child"
    OTPGetChild.objects.create(
        user=request.user,
        phone=request.user.phone,
        otp=otp,
        description=description,
    )
    return response_200("success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extend_child_in_game(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    this_time=datetime.now()
    game_obj=Game.objects.filter(user=request.user,started_at__lt=this_time,ended_at__gt=this_time,is_finished=False).order_by("-id")
    if len(game_obj)==0:
        return response_400("the user has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=ChildOfGames.objects.get(user=request.user,started_at__lt=this_time,ended_at__gt=this_time,id=game_id,is_finished=False)
    except ObjectDoesNotExist as e:
        return response_400("there is no such game")
    how_much_ticket_played=(datetime.timestamp(game_obj.ended_at)-datetime.timestamp(game_obj.started_at))/1800
    one_ticket_price=(game_obj.price)/how_much_ticket_played
    ticket=int(request.data.get("ticket"))
    if request.user.balance<(one_ticket_price*ticket):
        return response_400("the balance is not enough")
    request.user.balance-=(one_ticket_price*ticket)
    request.user.save()
    game_obj.ended_at=datetime.fromtimestamp(datetime.timestamp(game_obj.ended_at)+(ticket*1800))
    game_obj.price=game_obj.price+(one_ticket_price*ticket)
    game_obj.is_sent_email=False
    game_obj.save()
    BalanceHistory.objects.create(
        user=request.user,
        balance=(one_ticket_price*ticket),
        adding_balance=False,
        city=None,
        branch=None,
        game_name=game_obj.game_name
    )
    return response_200("success",None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_email_valid(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    if request.user.email=="" or request.user.email==None:
        return response_400("email girilmemiş")
    return response_200("success",str(request.user.email))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_or_edit_email(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    email=request.data.get("email")
    request.user.email=email
    request.user.save()
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def iyzipay(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    options = {
        'api_key': 'OdaEJF6EjJrapo7jlmkYeQlsC22OrLdW',
        'secret_key': 'tPVrpRL2YbKDZu6mijylSwasSJIwhqrW',
        'base_url': "api.iyzipay.com"
    }
    cardNumber=request.data.get('cardNumber')
    expireMonth=request.data.get('expireMonth')
    expireYear=request.data.get('expireYear')
    cvc=request.data.get('cvc')
    price=request.data.get('price')
    payment_card = {
        'cardHolderName':request.user.name+' '+ request.user.surname,
        'cardNumber': cardNumber,
        'expireMonth': expireMonth,
        'expireYear': expireYear,
        'cvc':cvc ,
        'registerCard': '0'
    }

    buyer = {
        'id': request.user.id,
        'name': request.user.name,
        'surname': request.user.surname,
        'gsmNumber': request.user.tel_no,
        'email': request.user.email,
        'identityNumber': '11111111111',
        'lastLoginDate': str(datetime.now()),
        'registrationDate': str(datetime.now()),
        'registrationAddress': 'Istanbul',
        'ip': ip,
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34000'
    }

    address = {
        'contactName': request.user.name+ ' '+ request.user.surname,
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Istanbul',
        'zipCode': '34000'
    }
    basket_items = [
        {
            "id": "bakiye"+str(price),
            "price": str(price),
            "name": "bakiye"+str(price),
            "category1": "bakiye",
            "itemType": "VIRTUAL"
        }
        ]
    campaigns_obj=addingBalanceCampaigns.objects.filter(is_active=True,is_have_discount=True).order_by('-amount_money')
    if len(campaigns_obj)==0:
        basket_items = [
        {
            "id": "bakiye"+str(price),
            "price": str(price),
            "name": "bakiye"+str(price),
            "category1": "bakiye",
            "itemType": "VIRTUAL"
        }
        ]
    for i in campaigns_obj:
        if i.amount_money <= price:
            basket_items = [
            {
                "id": "bakiye"+str(price*i.discount_percentage),
                "price": str(price*i.discount_percentage),
                "name": "bakiye"+str(price*i.discount_percentage),
                "category1": "bakiye",
                "itemType": "VIRTUAL"
            }
            ]
            break
        break
            

    request = {
        'locale': 'tr',
        'conversationId':"bakiye"+str(price), 
        'price': str(price),
        'paidPrice': str(price),
        'currency': 'TRY',
        'installment': '1',
        'basketId': "bakiye"+str(price),
        'paymentChannel': 'WEB',
        'paymentGroup': 'OTHER',
        'paymentCard': payment_card,
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items
    }
    payment = iyzipay.Payment().create(request, options)
    payment_json=json.loads(payment.read())
    if payment_json["status"]=='success':
        BalanceHistory.objects.create(
            user=request.user,
            is_gift=False,
            is_adding_balance=True,
            balance=price,
        )
        try:
            balance_obj=Balance.objects.get(user=request.user)
        except ObjectDoesNotExist as e:
            return response_400('this usern does not added price')
        balance_obj.price += price
        balance_obj.save()
        campaigns_obj=addingBalanceCampaigns.objects.filter(is_active=True,discount_percentage=False).order_by('-amount_money')
        if len(campaigns_obj)==0:
            return response_200(None)
        for i in campaigns_obj:
            if i.amount_money <= price:
                balance_obj.price += i.gift_price
                balance_obj.save()
                BalanceHistory.objects.create(
                    user=request.user,
                    is_gift=True,
                    is_adding_balance=True,
                    balance=i.gift_price,
                )
                return response_200(None)
    return response_400(payment_json["status"])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def game_info(request,qr_code):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    data={
        'machineCode':str(qr_code),
        'memberId':request.user.member_id,
        'transactionId':generate_sha256_for_transactionId(request.user.tel_no,datetime.now()),
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    response = requests.post('https://api.playland.sade.io/Device/GetPrice', headers=headers, json=data)
    response_obj=response.json()
    try:
        balance_obj=Balance.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        balance_obj=Balance.objects.create(
            user=request.user
        )
    if response_obj["status"]==False:
        return response_400("the machine has an error")
    for_child=False
    is_money_enough=True
    if response_obj["machineType"]=="SOFT PLAY2":
        for_child=True
    if balance_obj.balance<response_obj["price"]:
        is_money_enough=False
    if response_obj["price"]==0:
        return response_400("this machine for personels")
    
    return_obj={
        "machine_type":response_obj["machineType"],
        "machine_name":response_obj["machineName"],
        "price":response_obj["price"],
        "for_child":for_child,
        "is_money_enough":is_money_enough,
        "your_price":balance_obj.balance,
        "machine_store": response_obj["machineStore"]
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def play_game(request,qr_code):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    try:
        jeton_obj=Jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        jeton_obj=Jeton.objects.create(
            user=request.user
        )
    try:
        min_withdrawal_amount_obj=Min_Withdrawal_Amount.objects.get(id=1)
    except ObjectDoesNotExist as e:
        return response_400('min withdrawal amount does not get')
    data={
        'machineCode':str(qr_code),
        'memberId':request.user.member_id,
        'transactionId':generate_sha256_for_transactionId(request.user.tel_no,datetime.now()),
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    response = requests.post('https://api.playland.sade.io/Device/GetPrice', headers=headers, json=data)
    response_obj=response.json()
    if response_obj["status"] == False:
        return response_400('this machine has an error')
    try:
        balance_obj=Balance.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        return response_400('this user has not any balance')
    if balance_obj.price < response_obj["price"]:
        return response_400('your balance is not enough')
    if response_obj["machineType"] == "SOFT PLAY":
        family_id=request.data.get('family_id')
        try:
            family_obj=Family.objects.get(parent=request.user,id=family_id,is_parent=False)
        except ObjectDoesNotExist as e:
            return response_400('this is not child')
        now=datetime.timestamp(datetime.now())
        child_timestamp=datetime.timestamp(family_obj.birthday)
        if now - child_timestamp > 378432000:
            return response_400("this child can't play this game")
        price=balance_obj.price
        if price >= 500:
            price=499
        data={
            "machineCode":str(qr_code),
            "memberId":request.user.member_id,
            "transactionId":generate_sha256_for_transactionId(request.user.tel_no,datetime.now()),
            "memberBalance": price
        }
        response = requests.post('https://api.playland.sade.io/Device/StartGame', headers=headers, json=data)
        response_obj2=response.json()
        if "20 dk" in response_obj["machineName"]:
            adding_time=1200
        elif "30 dk" in response_obj["machineName"]:
            adding_time=1800
        elif "45 dk" in response_obj["machineName"]:
            adding_time=2700
        elif "60 dk" in response_obj["machineName"]:
            adding_time=3600
        elif "90 dk" in response_obj["machineName"]:
            adding_time=5400
        elif "120 dk" in response_obj["machineName"]:
            adding_time=7200
        else:
            return response_400("I don't get time of machine")

        if response_obj2["status"] == True:
            Game.objects.create(
                user=request.user,
                gamer=family_obj,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(now),
                ended_at=datetime.fromtimestamp(now+adding_time),
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                company=response_obj["company"]
            )
            BalanceHistory.objects.create(
                user=request.user,
                balance=response_obj["price"],
                company=response_obj["company"],
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            ChildOfGames.objects.create(
                parent_name=request.user.name,
                parent_surname=request.user.surname,
                tel_no=request.user.tel_no,
                child_name=family_obj.firstname,
                child_surname=family_obj.lastname,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(now),
                ended_at=datetime.fromtimestamp(now+adding_time),
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                company=response_obj["company"]
            )
            jeton_obj.amount += response_obj["price"] * min_withdrawal_amount_obj.percantage
            jeton_obj.save()
            JetonHistory.objects.create(
                user=request.user,
                jeton_amount=response_obj["price"] * min_withdrawal_amount_obj.percantage,
                is_added_jeton=True
            )
            return response_200(None)
        else:
            return response_400('this machine has an error')
    else:
        data={
            "machineCode":str(qr_code),
            "memberId":request.user.member_id,
            "transactionId":generate_sha256_for_transactionId(request.user.tel_no,datetime.now()),
            "memberBalance": price
        }
        response = requests.post('https://api.playland.sade.io/Device/StartGame', headers=headers, json=data)
        response_obj3=response.json()
        if response_obj3["status"] == True:
            Game.objects.create(
                user=request.user,
                gamer=family_obj,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(now),
                ended_at=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                company=response_obj["company"]
            )
            BalanceHistory.objects.create(
                user=request.user,
                balance=response_obj["price"],
                company=response_obj["company"],
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            ChildOfGames.objects.create(
                parent_name=request.user.name,
                parent_surname=request.user.surname,
                tel_no=request.user.tel_no,
                child_name=family_obj.firstname,
                child_surname=family_obj.lastname,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(now),
                ended_at=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                company=response_obj["company"]
            )
            jeton_obj.amount += response_obj["price"] * min_withdrawal_amount_obj.percantage
            jeton_obj.save()
            JetonHistory.objects.create(
                user=request.user,
                jeton_amount=response_obj["price"] * min_withdrawal_amount_obj.percantage,
                is_added_jeton=True
            )
            return response_200(None)
        else:
            return response_400('this machine has an error')
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_gifts(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    try:
        jeton_obj=Jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        return response_400('this user has not jeton')
    gift_obj=Gift.objects.all().order_by('jeton_amount_of_gifts')
    list=[]
    for i in gift_obj:
        is_money_enough=True
        if jeton_obj.amount < gift_obj.jeton_amount_of_gifts:
            is_money_enough=False
        return_obj={
            "id":i.id,
            "gift_name":i.gift_name,
            "gift_description1":i.gift_description1,
            "gift_description2":i.gift_description2,
            "gift_description3":i.gift_description3,
            "number_of_gifts":i.number_of_gifts,
            "jeton_amount_of_gifts":i.jeton_amount_of_gifts,
            "created_at":localtime(i.created_at),
            "updated_at":localtime(i.updated_at),
            "is_money_enough":is_money_enough
        } 
        list.append(return_obj)
    return response_200(list)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gift_delivery_address_check(request):
    if not is_verified(request.user.tel_no):
        return response_400('this user does not valid')
    delivery_of_person=request.data.get('delivery_of_person')
    address=request.data.get('address')
    try:
        gift_obj=GiftDetails.objects.get(delivery_of_person=delivery_of_person,address=address)
    except ObjectDoesNotExist as e:
        return response_400("this user's information is wrong")
    GiftDetails.objects.create(
        delivery_of_person=delivery_of_person,
        address=address
    )
    return response_200('success')






import json
from django.shortcuts import render
from datetime import datetime, timedelta
from urllib.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from funlord.responses import response_200, response_400
from users.models import Balance, BalanceHistory, CardInfo, CustomUser, Family, Game, Jeton, Min_Withdrawal_Amount, OTPChange, OTPForgotPassword, OTPGetChild,OTPRegister
from users.utils import generate_sha256, is_verified, register_parameters,generate_random_num,is_password_match,password_is_valid
from superuser.models import Branchs, News,Company


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
        #burada sms gönderilecek
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
            gender=gender
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
    #burada sms gönderilecek
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
            return response_400("This otp is verified already")
        else:
            if i.otp!=otp:
                return response_400("This otp is not true")
            else:
                otp_obj.is_verified = True
                otp_obj.save()
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
            "created_at":news.created_at
        }
        liste.append(return_obj)
    return response_200(liste)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request,news_id):
    try:
        otp_obj=OTPRegister.objects.get(tel_no=request.user.tel_no,is_verified=True)
    except ObjectDoesNotExist as e:
        return response_400('this user is not verified')
    try:
        news_obj=News.objects.get(id=news_id)
    except ObjectDoesNotExist as e:
        return response_400('there no such news')
    return_obj={
        "id":news_obj.id,
        "company":news_obj.company.name,
        "title": news_obj.title,
        "short_description": news_obj.short_description,
        "description": news_obj.description,
        "image": "/media/"+str(news_obj.image),
        "is_campaign":news_obj.is_campaign,
        "price":news_obj.price,
        "created_at":news_obj.created_at
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
        "created_at":branch_obj.created_at
    }
    return response_200(return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    return_obj={
        "balance":request.user.budget
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_balance(request):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    adding_balance=request.data.get('adding_balance')
    if int(adding_balance) <= 0:
        return response_400("you don't load negative amount")
    now = request.data.get("datetime")
    sha256_proof = request.data.get("sha256_proof")
    if sha256_proof != generate_sha256(adding_balance,now):
        return response_400("sha256 proof is not match")
    #iyizipay buraya gelecek.
    BalanceHistory.objects.create(
        user=request.user,
        balance=adding_balance,
        is_adding_balance=True
    )
    request.user.balance += adding_balance
    request.user.save()
    return response_200('success')


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
            "user": i.user.firstname+" "+i.user.lastname,
            "history": i.balance,
            "is_gift":i.is_gift,
            "is_adding_balance": i.is_adding_balance,
            "company":i.company,    
            "city": i.city,
            "branch": i.branch,
            "game_name": i.game_name,
            "created_at": i.created_at,
            "updated_at": i.updated_at
        }
        history_list.append(return_obj)
    return response_200(history_list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_or_create_jeton(request):
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jeton_conversion(request):
    try:
        jeton_obj=Jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        return response_400('there is no such user')
    try:
        amount_obj=Min_Withdrawal_Amount.objects.get(id=1)
    except ObjectDoesNotExist as e:
        return response_400('there is not exist jeton conversion')
    amount=request.data.get('amount')
    if not float(amount_obj.min_amount) < float(amount):
        return response_400('your amount must greater than min_amount')
    if jeton_obj.amount < amount:
        return response_400("the balance is not enough")
    jeton_obj.amount -= amount 
    jeton_obj.save()
    try:
        balance_obj=Balance.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        balance_obj=Balance.objects.create(user=request.user)
    balance_obj.price += (float(amount)/amount_obj.tl_to_jeton)
    balance_obj.price.save()
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    if not is_verified(request.user.tel_no):
        return response_400('there is no such user')
    return_obj={
        "name":request.user.name,
        "surname":request.user.surname
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
    phone=request.data.get("phone")
    otp = generate_random_num()
    #sms gönderilecek
    description = "verification"
    OTPChange.objects.create(
        user=request.user,
        phone=phone,
        otp=otp,
        description=description
    )
    return response_200("success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_phone_verification(request):
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
def change_password(request):
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
            "started_at":i.started_at,
            "ended_at":i.ended_at,
            "created_at":i.created_at,
            "update_at":i.update_at,
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
    this_time=datetime.now()
    game_obj=Game.objects.filter(user=request.user,started_at__lt=this_time,ended_at__gt=this_time,is_finished=False).order_by("-id")
    if len(game_obj)==0:
        return response_400("the user has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=Game.objects.get(user=request.user,started_at__lt=this_time,ended_at__gt=this_time,id=game_id,is_finished=False)
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
    if request.user.email=="" or request.user.email==None:
        return response_400("email girilmemiş")
    return response_200("success",str(request.user.email))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_or_edit_email(request):
    email=request.data.get("email")
    request.user.email=email
    request.user.save()
    return response_200("success",None)




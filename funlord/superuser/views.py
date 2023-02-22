import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from funlord.responses import response_200, response_400
from personel.models import Personel, PersonelsOfBranchs
from users.models import CustomUser, OTPForgotPassword
from users.utils import generate_random_num, sendSMSVerification
from superuser.models import ChildOfGames, Company, News, Branchs


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
        'is_staff': user_obj.is_staff,
        'is_personel': user_obj.is_personel,
        'is_can_write': user_obj.is_can_write,
        'is_company': user_obj.is_company
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def super_user_change_password(request):
    old_password = request.data.get('old_password')
    if not request.user.check_password(old_password):
        return response_400('your old password does not match your password')
    password = request.data.get('password')
    password_a = request.data.get('password_a')
    if len(password) < 8:
        return response_400('weak password')
    if password != password_a:
        return response_400("the passwords are not match")
    request.user.set_password(password)
    request.user.save()
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def super_user_forgot_password(request):
    tel_no = request.data.get('tel_no')
    try:
        user_obj = CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('this user does not valid')
    otp = generate_random_num()
    sendSMSVerification(otp, [tel_no])
    OTPForgotPassword.objects.create(
        user=request.user,
        otp=otp,
        is_verified=False
    )
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def super_user_forgot_password_validation(request):
    tel_no = request.data.get('tel_no')
    otp = request.data.get('otp')
    try:
        user_obj = CustomUser.objects.get(tel_no=tel_no)
    except ObjectDoesNotExist as e:
        return response_400('this user does not valid')
    otp_obj = OTPForgotPassword.objects.filter(
        user=request.user, otp=otp, is_verified=False).order_by('-id')
    if len(otp_obj) == 0:
        return response_400('you have not any otp')
    for i in otp_obj:
        if i.is_verified == True:
            return response_400('your otp already verified')
        else:
            if i.otp != otp:
                return response_400('this otp is wrong')
            else:
                i.is_verified = True
                i.save()
                return response_200(None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_news(request,started,limit,filtering,company_name):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    try:
        company_obj=Company.objects.get(name=company_name)
    except ObjectDoesNotExist as e:
        return response_400('there is no such company')
    news_obj=News.objects.all().order_by('-id')[started:started+limit]
    news_list=[]
    for news in news_obj:
        if filtering == 'all':
            return_obj={
                'company':news.company.name,
                'title':news.title,
                'short_description':news.short_description,
                'description':news.description,
                'image': '/media/' + str(news_obj.image),
                'is_campaign':news.is_campaign,
                'price':news.price
            }
            news_list.append(return_obj)
        elif filtering in str(news.title).lower() or filtering in str(news.short_description).lower() or filtering in str(news.description):
            return_obj={
                'company':news.company.name,
                'title':news.title,
                'short_description':news.short_description,
                'description':news.description,
                #'profile_image': "/media/"+str(news.profile_image),
                'is_campaign':news.is_campaign,
                'price':news.price
            }
            news_list.append(return_obj)
    if float(len(news_obj)/limit) > int(len(news_obj)/limit):
            page_count = int(len(news_obj)/limit)+1
    else:
        if len(news_obj) == 0:
            page_count = 1
        else:
            page_count = int(len(news_obj)/limit)
    if float(started/limit) > int(started/limit):
        current_page = int(started/limit)+1
    else:
        if started == 0:
            current_page = 1
        else:
            current_page = int(started/limit)
    return_obj = {
        "games_history": news_list,
        "total_page_count": page_count,
        "current_page": current_page
    }
    return response_200(return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request, news_id):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_news(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superadmin')
    news_id = request.data.get('news_id')
    try:
        news_obj = News.objects.get(id=news_id)
    except ObjectDoesNotExist as e:
        return response_400('this company does not valid')
    title = request.data.get('title')
    short_description = request.data.get('short_description')
    description = request.data.get('description')
    image = request.data.get('image')
    is_campaign = request.data.get('is_campaign')
    price = request.data.get('price')
    if request.user.is_can_write:
        list = []
        news_obj = News.objects.create(
            company=news_obj,
            title=title,
            short_description=short_description,
            description=description,
            image=image,
            is_campaign=is_campaign,
            price=price,
        )
        list.append(news_obj)
    else:
        return response_400('only superusers can add news')
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_news(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superadmin')
    id = request.data.get('id')
    try:
        news_obj = News.objects.get(id=id)
    except ObjectDoesNotExist as e:
        return response_400('there is no news available')
    title = request.data.get('title')
    short_description = request.data.get('short_description')
    description = request.data.get('description')
    image = request.data.get('image')
    is_campaign = request.data.get('is_campaign')
    price = request.data.get('price')
    news_obj.title = title
    news_obj.short_description = short_description
    news_obj.description = description
    news_obj.image = image
    news_obj.is_campaign = is_campaign
    news_obj.price = price
    news_obj.save()
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_news(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    id = request.data.get('id')
    try:
        news_obj = News.objects.get(id=id)
    except ObjectDoesNotExist as e:
        return response_400('there is not a news these id')
    news_obj.delete()
    return response_200('success')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_branchs(request,started,limit,filtering,company_name):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    try:
        company_obj=Company.objects.get(name=company_name)
    except ObjectDoesNotExist as e:
        return response_400('there is no such company')
    branch_obj=Branchs.objects.all().order_by('-id')[started:started+limit]
    branch_list=[]
    for i in branch_obj:
        if filtering == 'all':
            return_obj={
                'company':i.company.name,
                'branch_name':i.branch_name,
                'city':i.city,
                'country':i.country,
                'maps_link':i.maps_link,
                'created_at':i.created_at,
            }
            branch_list.append(return_obj)
        if filtering in str(i.company.name).lower() or filtering in str(i.branch_name):
            return_obj={
                'company':i.company.name,
                'branch_id':i.id,
                'city':i.city,
                'country':i.country,
                'maps_link':i.maps_link,
                'created_at':i.created_at,
            }
            branch_list.append(return_obj)
    if float(started/limit) > int(started/limit):
        current_page= len(int(started/limit)) + 1
    else:
        current_page= int(started/limit)
    if float(len(branch_obj))/limit > int(len(branch_obj))/limit:
        page_count= len(int(branch_obj))/limit + 1
    else: 
        if float(len(branch_obj))/limit == 0:
            page_count= 0
        else:
            page_count= int(len(branch_obj))/limit 
    returning_obj={
        'current_page': current_page,
        'page_count': page_count,
        'games_history':branch_list
    }
    return response_200(returning_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branch(request, branch_id):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such branch')
    list = []
    return_obj = {
        'id': branch_obj.id,
        'company_name': branch_obj.company.name,
        'branch': branch_obj.branch,
        'city': branch_obj.city,
        'country': branch_obj.country,
        'maps_link': branch_obj.maps_link,
        'created_at': branch_obj.created_at
    }
    list.append(return_obj)
    return response_200(list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_branch(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    company_name = request.data.get('company_name')
    try:
        company_obj = Company.objects.get(name=company_name)
    except ObjectDoesNotExist as e:
        return response_400('this company is not valid')
    branch_name = request.data.get('branch_name')
    country = request.data.get('country')
    city = request.data.get('city')
    location = request.data.get('location')
    if location == None:
        branch_obj = Branchs.objects.create(
            company=company_obj,
            branch=branch_name,
            country=country,
            city=city
        )
    else:
        branch_obj = Branchs.objects.create(
            company=company_obj,
            branch=branch_name,
            country=country,
            city=city,
            maps_link=location
        )
    return response_200(None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def all_branchs_count(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branchs_obj = Branchs.objects.all()
    return response_200(len(branchs_obj))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_game_history(request, started, limit, filtering):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    games = ChildOfGames.objects.all().order_by("-id")[started:started+limit]
    games_list = []
    for i in games:
        if filtering == 'all':
            return_obj = {
                "id": i.id,
                "parent_name": i.parent_name,
                "parent_surname": i.parent_surname,
                "phone": i.tel_no,
                "child_name": i.child_name,
                "child_surname": i.child_surname,
                "is_male": i.is_male,
                "birthday": i.birthday,
                "price": i.price,
                "started_at": i.started_at,
                "ended_at": i.ended_at,
                "is_sent_email": i.is_sent_email,
                "city": i.city,
                "branch": i.branch,
                "game_name": i.game_name,
                "is_finished": i.is_finished,
                "created_at": i.created_at,
                "update_at": i.update_at,
                "profile_image": "/media/"+str(i.profile_image)
            }
            games_list.append(return_obj)
        elif filtering in i.tel_no or filtering in str(i.parent_name).lower() or filtering in str(i.parent_surname).lower() or filtering in str(i.child_name).lower() or filtering in str(i.child_surname).lower() or filtering in str(i.company).lower() or filtering in str(i.game_name).lower() or filtering in str(i.branch).lower():
            return_obj = {
                "id": i.id,
                "parent_name": i.parent_name,
                "parent_surname": i.parent_surname,
                "phone": i.tel_no,
                "child_name": i.child_name,
                "child_surname": i.child_surname,
                "is_male": i.is_male,
                "birthday": i.birthday,
                "price": i.price,
                "started_at": i.started_at,
                "ended_at": i.ended_at,
                "is_sent_email": i.is_sent_email,
                "city": i.city,
                "branch": i.branch,
                "game_name": i.game_name,
                "is_finished": i.is_finished,
                "created_at": i.created_at,
                "update_at": i.update_at,
                "profile_image": "/media/"+str(i.profile_image)
            }
            games_list.append(return_obj)
    if float(len(games)/limit) > int(len(games)/limit):
        page_count = int(len(games)/limit)+1
    else:
        if len(games) == 0:
            page_count = 1
        else:
            page_count = int(len(games)/limit)
    if float(started/limit) > int(started/limit):
        current_page = int(started/limit)+1
    else:
        if started == 0:
            current_page = 1
        else:
            current_page = int(started/limit)
    return_obj = {
        "games_history": games_list,
        "total_page_count": page_count,
        "current_page": current_page
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_branch(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    branch_id = request.data.get('branch_id')
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400('this branch does not valid')
    branch_obj.delete()
    return response_200(None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_branch(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    branch_id = request.data.get('branch_id')
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such branch')
    company_id = request.data.get('company_id')
    try:
        company_obj = Company.objects.get(id=company_id)
    except ObjectDoesNotExist as e:
        return response_400('this company does not valid')
    branch_name = request.data.get('branch_name')
    city = request.data.get('city')
    country = request.data.get('country')
    maps_link = request.data.get('maps_link')
    created_at = request.data.get('created_at')
    branch_obj.company = company_obj
    branch_obj.branch = branch_name
    branch_obj.city = city
    branch_obj.country = country
    branch_obj.maps_link = maps_link
    branch_obj.created_at = created_at
    branch_obj.save()
    return response_200(None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_personels(request,filtering,company_name,started,limit):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    try:
        company_obj=Company.objects.get(name=company_name)
    except ObjectDoesNotExist as e:
        return response_400('ther eis no such company')
    try:
        personel_obj=Personel.objects.all().order_by('-id')[started:started+limit]
    except ObjectDoesNotExist as e:
        return response_400('there is no such personel')   
    personel_list=[]
    for i in personel_obj:
        if filtering == 'all':
            return_obj={
                'id':i.id,
                'firstname':i.firstname,
                'surname':i.surname,
                'username':i.username,
                'birthday':i.birthday,
                'is_male':i.is_male,
                'tel_no':i.tel_no,
                'started_at':i.started_at,
                'created_at':i.created_at,
                'update_at':i.update_at
                }
        personel_list.append(return_obj)
        if filtering in str(personel_obj.firstname).lower() or filtering  in str(personel_obj.surname).lower() or filtering in str(personel_obj.username) or filtering in str(personel_obj.tel_no):
            return_obj={
                'id':i.id,
                'firstname':i.firstname,
                'surname':i.surname,
                'username':i.username,
                'birthday':i.birthday,
                'is_male':i.is_male,
                'tel_no':i.tel_no,
                'started_at':i.started_at,
                'created_at':i.created_at,
                'update_at':i.update_at
                }
        personel_list.append(return_obj)
    if float(started/limit) > int(started/limit):
        current_page= int(started/limit) + 1
    else:
        if float(started/limit) == 0:
            current_page = 1
        else:
            current_page= int(started/limit)
    if float(len(personel_obj)/limit) > int(len(personel_obj)/limit):
        page_count= int(int(personel_obj/limit)) + 1
    else:
        page_count= int(len(personel_obj)/limit)
    returning_obj={
        'current_page': current_page,
        'page_count': page_count,
        'games_history': personel_list
    }
    return response_200(returning_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_personel_of_branch(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    personel_id= request.data.get('personel_id')
    try:
        personel_obj=Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400('this person is not a personel')
    try:
        personel_obj2= PersonelsOfBranchs.objects.get(personel=personel_obj)
        branch_id=personel_obj2.branch.id
        branch_name=personel_obj2.branch.branch_name
    except ObjectDoesNotExist as e:
        branch_id= 'None'
        branch_name= 'None'
    list=[]
    return_obj={
        'id':personel_obj2.id,
        'personel_firstname':personel_obj.firstname,
        'personel_surname':personel_obj.surname,
        'personel_username':personel_obj.username,
        'branch_id':branch_id,
        'branch_name':branch_name,
        'birthday':personel_obj.birthday,
        'is_male':personel_obj.is_male,
        'tel_no':personel_obj.tel_no,
        'started_at':personel_obj.started_at,
        'created_at':personel_obj.created_at 
    }
    list.append(return_obj)
    return response_200(list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_personel(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    firstname=request.data.get('firstname')
    surname=request.data.get('surname')
    username=request.data.get('username')
    try:
        personel_obj=Personel.objects.get(firstname=firstname,surname=surname,username=username)
        return response_400('this personel already obtained')    
    except ObjectDoesNotExist as e:
        password=request.data.get('password')
        birthday=datetime.datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
        is_male=request.data.get('is_male')
        tel_no=request.data.get('tel_no')
        started_at=datetime.datetime.strptime(request.data.get("started_at"), "%Y-%m-%d")
        Personel.objects.create(
            firstname=firstname,
            surname=surname,
            username=username,
            birthday=birthday,
            is_male=is_male,
            tel_no=tel_no,
            started_at=started_at
        )
        user_obj=CustomUser.objects.create(
            name= firstname,
            surname=surname,
            username=username,
            birthday=birthday,
            tel_no=tel_no,
            is_personel=True
        )
        user_obj.set_password(password)
        user_obj.save()
        return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_personel_to_branch(request):
    if not request.user.is_admin:
        return response_400('the user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superadmin')
    branch_id = request.data.get('id')
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such branch')
    personel_username=request.data.get('personel_username')
    try:
        personel_obj=Personel.objects.get(username=personel_username)
    except ObjectDoesNotExist as e:
        return response_400('there is no such personel')
    try:
        personel_obj2=PersonelsOfBranchs.objects.get(personel=personel_obj)
        return response_400('this personel already obtained for this branch')
    except ObjectDoesNotExist as e:
        PersonelsOfBranchs.objects.create(
            branch=branch_obj,
            personel=personel_obj
        )
        return response_200(None
        )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_personel(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    if not request.user.is_can_write:
        return response_400('this user is not a superuser')
    id=request.data.get('id')
    try:
        personel_obj= Personel.objects.get(id=id)
    except ObjectDoesNotExist as e:
        return response_400('this personel does not exist')
    firstname= request.data.get('firstname')
    surname= request.data.get('surname')
    username= request.data.get('username')
    birthday= request.data.get('birthday')
    is_male=  request.data.get('is_male')
    tel_no= request.data.get('tel_no')
    started_at= request.data.get('started_at')
    personel_obj.firstname=firstname
    personel_obj.surname= surname
    personel_obj.username= username
    personel_obj.birthday= birthday
    personel_obj.is_male= is_male
    personel_obj.tel_no= tel_no
    personel_obj.started_at= started_at
    personel_obj.save()
    return response_200('success')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_personel(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')    
    if not request.user.is_can_write:
        return response_400('this user is not a superadmin')
    personel_id=request.data.get('personel_id')
    try:
        personel_obj=Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such personel')
    personel_obj.delete()
    return response_200(None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_personel_of_branch(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')    
    if not request.user.is_can_write:
        return response_400('this user is not a superadmin')    
    personel_id=request.data.get('personel_id')
    try:
        personel_obj=Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400('there is no such personel')
    try:
        personel_obj2=PersonelsOfBranchs(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400('the personel is already none branch')
    personel_obj2.delete()
    return response_200(None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def all_personels_count(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    try:
        personel_obj=Personel.objects.all()
    except ObjectDoesNotExist as e:
        response_400('there is no such personel')
    return response_200(len(personel_obj))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def all_male_personel_count(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    male_obj=Personel.objects.filter(is_male=True)
    return response_200(len(male_obj))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def all_female_personel_count(request):
    if not request.user.is_admin:
        return response_400('this user is not an admin')
    female_obj=Personel.objects.filter(is_male=False)
    return response_200(len(female_obj))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def birthday_personel(request):
    if not request.user.is_admin:
        return response_400('the user is not an admin')
    this_time=datetime.datetime.strptime(str(datetime.date.today()),'%Y-%m-%d')
    personels_obj = Personel.objects.filter(birthday=this_time)
    returning_list=[]
    for i in personels_obj:
        try:
            personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=i)
            branch_id=personel_of_branch_obj.branch.id
            branch_name=personel_of_branch_obj.branch.name
        except ObjectDoesNotExist as e:
            branch_id="None"
            branch_name="None"
        return_obj={
            "id":i.id,
            "branch": branch_name,
            "branch_id": branch_id,
            "firstname":i.firstname,
            "surname":i.surname,
            "username":i.username,
            "birthday":i.birthday,
            "is_male":i.is_male,
            "tel_no":i.tel_no,
            "started_at":i.started_at,
            "created_at":i.created_at,
            "update_at":i.update_at
        }
        returning_list.append(return_obj)
    return_obj={
        "birthday_personel_count":len(personels_obj),
        "personels":returning_list
    }
    return response_200(return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_personels_of_branch(request):
    if not request.user.is_admin:
        return response_400('the user is not an admin')
    branch_id=request.data.get('branch_id')
    try:
        personel_obj=PersonelsOfBranchs.objects.filter(id=branch_id).order_by('-id')
    except ObjectDoesNotExist as e:
        return response_400('there is no such personel in this branch')
    list=[]
    for i in personel_obj:
        return_obj={
            'id':i.id,
            'company':i.company.name,
            'branch_id':i.branch.id,
            'branch_name':i.branch,
            'created_at':i.created_at        
        }    
        list.append(return_obj)
    return response_200(list)

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch_personels_count(request):
    if not request.user.is_admin:
        return response_400('the user is not an admin')
    branch_id=request.data.get('branch_id')
    try:
        branch_obj=Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400('this branch does not exist')
    personel_obj=PersonelsOfBranchs.objects.filter(branch=branch_obj)
    return response_200(len(personel_obj))


















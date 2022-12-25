import hashlib
import math
import random
import time
from users.models import CustomUser, OTPRegister
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from funlord import settings


def register_parameters(data):
    if len(data) != 7:
        return False
    if 'tel_no' not in data or 'name' not in data or 'surname' not in data or 'birthday' not in data or 'gender' not in data or 'password' not in data or 'password_a' not in data:
        return False
    return True


def tel_no_exist(data):
    try:
        CustomUser.objects.get(tel_no=data)
        return True
    except ObjectDoesNotExist as e:
        return False


def generate_sha256_for_user(data, now):
    string = str(data)+str(now)+"playland_created_by_yemre"
    hash = hashlib.sha256(f'{string}'.encode()).hexdigest()
    return hash[:8]


def email_exist(data):
    try:
        CustomUser.objects.get(email=data)
        return True
    except ObjectDoesNotExist as e:
        return False


def nickname_exist(data):
    try:
        CustomUser.objects.get(nickname=data)
        return True
    except ObjectDoesNotExist as e:
        return False


def password_is_valid(data):
    if len(data) < 8:
        return False
    return True


def is_password_match(data, data2):
    if data != data2:
        return False
    return True


def generate_sha256(data):
    string = str(data)+str(time.time())+"funlord_created_by_atk"
    hash = hashlib.sha256(f'{string}'.encode()).hexdigest()
    return hash[0:8]


def send_email(to_email, otp, subject):
    otp = str(otp)
    subject, from_email, to_email = subject, settings.EMAIL_HOST_USER, to_email
    text_content = 'Here is your one time password :' + otp
    html_content = '<p>Here is your one time password :</p> <h3>' + otp + '</h3>'
    msg = EmailMultiAlternatives(
        subject, text_content, 'USECO <' + from_email+'>', [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def generate_random_num():
    random_str = ""
    digits = [i for i in range(0, 10)]
    for i in range(6):
        index = math.floor(random.random()*10)
        random_str += str(digits[index])
    return random_str


def is_verified(data):
    try:
        OTPRegister.objects.get(tel_no=data,is_verified=True)
        return True
    except ObjectDoesNotExist as e:
        return False

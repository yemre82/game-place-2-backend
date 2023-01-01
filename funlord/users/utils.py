import xml.etree.ElementTree as ET
import requests
import hashlib
import math
import random
import time
from funlord.responses import response_200
from users.models import CustomUser, OTPRegister
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from funlord import settings


def register_parameters(data):
    if len(data) != 8:
        return False
    if 'tel_no' not in data or 'name' not in data or 'surname' not in data or 'birthday' not in data or 'gender' not in data or 'password' not in data or 'password_a' not in data or 'member_id' not in data:
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

def generate_sha256_for_transactionId(data, now):
    string = str(data)+str(now)+"playland_created_by_yemre"
    hash = hashlib.sha256(f'{string}'.encode()).hexdigest()
    return hash[:12]


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


def sendSMSVerification(verification_code, nums):
    data="/home/ubuntu/be/be/sms_verification.xml"
    mytree = ET.parse(data)
    myroot = mytree.getroot()

    for sms_text in myroot.iter('metin'):
        sms_text.text = " Playland mobil uygulamasi icin onay numaraniz: "+verification_code+"."
    string_obj=""
    for num_text in myroot.iter('nums'):
        i=0
        for num in nums:
            i+=1
            string_obj += str(num)
            if i!=len(nums):
                string_obj+=","
    num_text.text=string_obj
    mytree.write('/home/ubuntu/be/be/new.xml')
    with open("/home/ubuntu/be/be/new.xml","rb") as file:
        data=file.readlines()
    string_asd=""
    for i in data:
        string_asd+=i.decode("utf-8")
    headers={'Content-Type':'text/xml; charset=UTF-8'}
    r=requests.post("https://smsgw.mutlucell.com/smsgw-ws/sndblkex",data=string_asd,headers=headers)
    return response_200(str(r),None)
import xml.etree.ElementTree as ET
import requests
import hashlib
import math
import random
import time
from funlord.responses import response_200
from users.models import CustomUser, OTPRegister
from django.core.exceptions import ObjectDoesNotExist


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
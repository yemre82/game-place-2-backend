from requests import request
from company.models import FunparaPercentage, WithdrawalAmount
from superuser.models import Company
from django.core.exceptions import ObjectDoesNotExist
from funlord.responses import response_200, response_400
from users.models import Jeton,JetonHistory


def find_earn_funpara(amount,user_obj,company_name):
    try:
        comp_obj=Company.objects.get(name=company_name)
    except ObjectDoesNotExist as e:
        return response_400('there is no such company')
    spent_amount_obj= WithdrawalAmount.objects.filter(user=user_obj,company=comp_obj)
    price=0
    for i in spent_amount_obj:
        price += i.amount
    funpara_percentage_obj=FunparaPercentage.objects.filter(company=comp_obj).order_by('step')
    total_funpara_percentage_amount = 0
    for i in funpara_percentage_obj:
        total_funpara_percentage_amount += i.amount
    price=price % total_funpara_percentage_amount
    total_funpara= 0
    total_funpara_percentage_amount_price = total_funpara_percentage_amount
    try:
            jeton_obj=Jeton.objects.get(user=user_obj)
    except ObjectDoesNotExist as e:
            Jeton.objects.create(
                user=user_obj,
            )
    for i in funpara_percentage_obj:
        total_funpara_percentage_amount += i.amount
        if total_funpara_percentage_amount - price >0 and amount>0:
            remaining_money = total_funpara_percentage_amount - price
            if amount > remaining_money and amount>0:
                total_funpara += (remaining_money * i.percentage) /100
                amount -= remaining_money
                price += remaining_money
            elif amount < remaining_money and amount>0:
                total_funpara += (amount * i.percentage) /100
                amount -= amount
                price += amount
                remaining_money =0
        total_funpara_percentage_amount = total_funpara_percentage_amount % total_funpara_percentage_amount_price
        if total_funpara_percentage_amount == 0:
            jeton_obj.amount += i.total_funpuan
            jeton_obj.save()
        JetonHistory.objects.create(
            user=user_obj,
            jeton_amount=jeton_obj.amount,
            is_added_jeton=True
        )
        if total_funpara_percentage_amount == 0:
            price=0
            remaining_money=0
            for j in funpara_percentage_obj:
                total_funpara_percentage_amount += j.amount
                if total_funpara_percentage_amount - price >0 and amount>0:
                    remaining_money = total_funpara_percentage_amount - price
                    if amount > remaining_money and amount>0:
                        total_funpara += (remaining_money * j.percentage) /100
                        amount -= remaining_money
                        price += remaining_money
                    elif amount < remaining_money and amount>0:
                        total_funpara += (amount * j.percentage) /100
                        amount -= amount
                        price += amount
                        remaining_money =0
                total_funpara_percentage_amount = total_funpara_percentage_amount % total_funpara_percentage_amount_price
    return total_funpara











from django.db import models
from superuser.models import Company
from users.models import CustomUser

class FunparaPercentage(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    step= models.IntegerField(default=1)
    percentage=models.IntegerField(default=0)
    total_funpuan=models.FloatField(default=0)
    amount=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.company)


class WithdrawalAmount(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    amount=models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class EarnedMoneyForCompany(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    balance= models.FloatField(default=0)
    month=models.IntegerField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.company)
    










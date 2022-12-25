from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

class MyUserManager(BaseUserManager):
    def create_user(self,username, tel_no, password=None):
        if not tel_no:
            raise ValueError("Users must have an tel_no address")

        user = self.model(
            tel_no=tel_no,
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,username, tel_no, password=None):
        user = self.create_user(
            tel_no=tel_no,
            username=username
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return 


class CustomUser(AbstractBaseUser):
    name = models.CharField(blank=False, max_length=100)
    surname = models.CharField(blank=False, max_length=100)
    username = models.CharField(blank=True, max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    birthday = models.DateField(blank=True, null=True)
    tel_no = models.IntegerField(blank=False, null=True )
    country = models.CharField(blank=True, null=True, max_length=100)
    created_at = models.DateTimeField(
        verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="update at", auto_now=True)
    qr_code = models.CharField(blank=False, max_length=200)
    gender=models.CharField(blank=False,max_length=10)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_personel = models.BooleanField(default=False)
    member_id = models.CharField(blank=False, max_length=10)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['tel_no']

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class OTPRegister(models.Model):
    tel_no = models.CharField(blank=False, max_length=100)
    otp = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.tel_no)

class OTPChange(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    phone = models.CharField(blank=False, max_length=100)
    otp = models.CharField(blank=False, max_length=10)
    description = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class OTPForgotPassword(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class Balance(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price=models.FloatField(default=0)

    def __str__(self):
        return str(self.user)
    

class BalanceHistory(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_gift=models.BooleanField(default=False)
    is_adding_balance=models.BooleanField(default=False)
    balance=models.FloatField(blank=False)
    company=models.CharField(blank=True,null=True,max_length=50)
    branch=models.CharField(blank=True,null=True,max_length=50)
    city=models.CharField(blank=True,null=True,max_length=50)
    game_name=models.CharField(blank=True,null=True,max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class Jeton(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    amount=models.FloatField(default=0,blank=False)
    total=models.FloatField(default=0,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user)

class Min_Withdrawal_Amount(models.Model):
    min_amount=models.FloatField(default=0,blank=False)
    percantage=models.FloatField(default=0,blank=False)
    tl_to_jeton= models.IntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.min_amount)



def get_profile_image_filepath(self, filename):
    return f'profile/images/{self.pk}/{"profile_image.png"}'


def get_default_profile_image():
    return "codingwithmitch/no-pp.png"


class Family(models.Model):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    firstname = models.CharField(blank=False, max_length=100)
    lastname = models.CharField(blank=False, max_length=100)
    birthday = models.DateField(blank=False)
    is_male = models.BooleanField(blank=False)
    is_parent = models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True,null=True,
        max_length=100, upload_to=get_profile_image_filepath,default=get_default_profile_image)
    phone = models.CharField(blank=True, null=True, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.parent)


class Game(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    gamer=models.ForeignKey(Family,on_delete=models.CASCADE)
    price=models.FloatField(blank=False)
    started_at=models.DateTimeField(blank=False)
    ended_at=models.DateTimeField(blank=True,null=True)
    is_finished=models.BooleanField(default=False)
    city=models.CharField(blank=True,max_length=100,null=True)
    branch=models.CharField(blank=True,max_length=100,null=True)
    game_name=models.CharField(blank=True,null=True,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class OTPGetChild(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    phone = models.CharField(blank=False, max_length=100)
    otp = models.CharField(blank=False, max_length=10)
    description = models.CharField(blank=False, max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.phone)
from django.db import models



def Company_image_filepath(self, filename):
    return f'Company/images/{self.pk}/{"Company_image.png"}'
def get_default_Company_image():
    return "codingwithmitch/no-pp.png"

class Company(models.Model):
    name=models.CharField(blank=False,max_length=100)
    image = models.ImageField(
        max_length=100, upload_to=Company_image_filepath, null=True, blank=True, default=get_default_Company_image)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def get_news_image_filepath(self, filename):
    return f'news/images/{self.pk}/{"news_image.png"}'
def get_default_news_image():
    return "codingwithmitch/no-pp.png"


class News(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE,null=True)
    title = models.CharField(blank=False, max_length=100)
    short_description = models.CharField(blank=False, max_length=100,null=True)
    description = models.CharField(blank=False, max_length=400)
    image = models.ImageField(
        max_length=100, upload_to=get_news_image_filepath, null=True, blank=True, default=get_default_news_image)
    is_campaign=models.BooleanField(default=False,blank=False)
    price=models.IntegerField(default=0,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Branchs(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    branch=models.CharField(blank=False,max_length=100)
    city=models.CharField(blank=False,max_length=100)
    country=models.CharField(blank=False,max_length=100)
    maps_link=models.CharField(blank=True,null=True,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city

# Generated by Django 4.1.4 on 2023-01-20 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_giftdetails_gift_giftdetails_jeton_amount_of_gifts_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_can_write',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_company',
            field=models.BooleanField(default=False),
        ),
    ]

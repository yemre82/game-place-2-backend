# Generated by Django 4.1.4 on 2023-01-02 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_jetonconverisonhistory_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='family',
            old_name='update_at',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='update_at',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='giftdetails',
            old_name='update_at',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='otpchange',
            old_name='update_at',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='otpgetchild',
            old_name='update_at',
            new_name='updated_at',
        ),
    ]

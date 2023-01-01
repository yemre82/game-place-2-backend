# Generated by Django 4.1.4 on 2022-12-27 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_family_min_withdrawal_amount_otpregister_otpgetchild_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JetonConverisonHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('is_conversion_jeton', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.jeton')),
            ],
        ),
        migrations.CreateModel(
            name='JetonHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jeton_amount', models.FloatField()),
                ('is_added_jeton', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.jeton')),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='budget',
        ),
        migrations.AddField(
            model_name='min_withdrawal_amount',
            name='tl_to_jeton',
            field=models.IntegerField(default=15),
        ),
        migrations.DeleteModel(
            name='CardInfo',
        ),
    ]
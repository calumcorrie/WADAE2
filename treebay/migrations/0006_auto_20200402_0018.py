# Generated by Django 2.2.3 on 2020-04-01 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treebay', '0005_auto_20200401_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='picture',
            field=models.ImageField(blank=True, default='default_plant.png', upload_to='plant_images'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(blank=True, default='default.png', upload_to='profile_images'),
        ),
    ]

# Generated by Django 2.2 on 2021-01-14 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseorg',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='org/%Y/%m', verbose_name='logo'),
        ),
    ]

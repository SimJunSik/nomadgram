# Generated by Django 2.0.13 on 2019-03-12 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20190312_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('female', 'Female'), ('not-specified', 'Not specified'), ('male', 'Male')], max_length=80, null=True),
        ),
    ]
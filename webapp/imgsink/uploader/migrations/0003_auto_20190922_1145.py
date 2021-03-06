# Generated by Django 2.2.5 on 2019-09-22 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0002_imageversion_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageversion',
            name='bucket',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imageversion',
            name='height',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imageversion',
            name='key',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imageversion',
            name='width',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='imageversion',
            name='name',
            field=models.CharField(max_length=1024),
        ),
    ]

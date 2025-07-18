# Generated by Django 4.1.5 on 2023-02-23 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imdb', '0011_mockmodel'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='movieview',
            constraint=models.UniqueConstraint(fields=('movie', 'user'), name='movie_user_unique_view', violation_error_message='Movie view should be unique for each user and movie'),
        ),
    ]

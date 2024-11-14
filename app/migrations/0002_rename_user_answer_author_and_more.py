# Generated by Django 5.1.3 on 2024-11-13 11:37

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='user',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='answerlike',
            old_name='user',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='user',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='questionlike',
            old_name='user',
            new_name='author',
        ),
        migrations.AlterUniqueTogether(
            name='answerlike',
            unique_together={('answer', 'author')},
        ),
        migrations.AlterUniqueTogether(
            name='questionlike',
            unique_together={('question', 'author')},
        ),
    ]

# Generated by Django 4.1.4 on 2023-05-25 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('StudyGuidelinePortal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='StudyGuidelinePortal.department'),
        ),
    ]

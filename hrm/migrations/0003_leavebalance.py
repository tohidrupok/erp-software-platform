# Generated by Django 5.1.2 on 2024-12-22 05:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0002_holiday'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.DateField(default=2024)),
                ('total_leaves', models.IntegerField(default=24)),
                ('used_leaves', models.IntegerField(default=0)),
                ('carry_forward', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='leave_balance', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

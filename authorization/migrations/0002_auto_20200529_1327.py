# Generated by Django 3.0.6 on 2020-05-29 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='tags',
            field=models.JSONField(blank=True, null=True, default=list),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_roles',
            field=models.CharField(choices=[('researcher', 'Researcher'), ('lecturer_senior', 'Lecturer - Senior Lecturer'), ('lecturer', 'Lecturer'), ('professor', 'Professor'), ('librarian', 'Librarian'), ('student_doctoral', 'Student - Doctoral Student'), ('student_master', 'Student - Master'), ('student_bachelor', 'Student - Bachelor'), ('student_phd', 'Student - Ph. D. Student'), ('other', 'Other')], max_length=20),
        ),
    ]

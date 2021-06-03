from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.contrib.postgres import fields
from django.db.models.signals import post_save,post_delete

from .managers import Manager
from api import models as api
from frontend.reccom import get_similar_items
# Create your models here.

USER_ROLES = (
    ('researcher','Researcher'),
    ('lecturer_senior','Lecturer - Senior Lecturer'),
    ('lecturer','Lecturer'),
    ('professor','Professor'),
    ('librarian','Librarian'),
    ('student_doctoral','Student - Doctoral Student'),
    ('student_master','Student - Master'),
    ('student_bachelor','Student - Bachelor'),
    ('student_phd','Student - Ph. D. Student'),
    ('other','Other')
)

class User(AbstractBaseUser,PermissionsMixin):
    full_name = models.CharField(max_length=100,default="")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    email = models.EmailField(unique=True)
    user_roles = models.CharField(choices=USER_ROLES,max_length=20,blank=True,null=True)

    tags = fields.ArrayField(base_field=models.CharField(max_length=50),null=True,blank=True)
    keywords = fields.ArrayField(base_field=models.CharField(max_length=50),null=True,blank=True)
    authors = fields.ArrayField(base_field=models.CharField(max_length=50),null=True,blank=True)

    objects = Manager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name','user_roles']

    class Meta:
        ordering = ['email']




# def update_user_post_save(sender,instance,**kwargs):
#     library = list(api.Library.objects.all().filter(user = instance))
#     if len(library) == 0:
#         library = api.Library(user = instance,articles=[])
#         library.save()
#
# def update_user_post_delete(sender,instance,**kwargs):
#     library = api.Library.objects.all().filter(user = instance)
#     library.delete()
#
#
# post_save.connect(update_user_post_save,sender=User)
# post_delete.connect(update_user_post_delete,sender=User)

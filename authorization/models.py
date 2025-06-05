from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.db.models.signals import post_save, post_delete

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

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as username."""
    full_name = models.CharField(max_length=100,default="")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    email = models.EmailField(unique=True)
    user_roles = models.CharField(choices=USER_ROLES,max_length=20,blank=True,null=True)

    tags = models.JSONField(default=list, null=True, blank=True)
    keywords = models.JSONField(default=list, null=True, blank=True)
    authors = models.JSONField(default=list, null=True, blank=True)

    objects = Manager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name','user_roles']

    class Meta:
        ordering = ['email']



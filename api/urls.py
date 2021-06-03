from django.urls import path
from . import views

urlpatterns = [
    path('index/',views.index),
    path('oauth/',views.auth_return,name='oauth'),
    path('listDocuments/',views.list_documents,name='list_documents'),
    path('document/',views.get_document,name="document")
]

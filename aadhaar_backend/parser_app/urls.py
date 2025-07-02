from django.urls import path
from . import views
from .views import upload_and_parse_image
from django.views.generic import TemplateView

urlpatterns=[
    path('', views.home, name='home'),
    path('parse/', views.parse_view, name='parse_view'),
    path("api/upload/", upload_and_parse_image, name='upload_and_parse_image'),
]
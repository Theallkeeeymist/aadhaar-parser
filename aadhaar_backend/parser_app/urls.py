from django.urls import path
from . import views
from .views import upload_and_parse_image

urlpatterns=[
    path("upload/", upload_and_parse_image, name='upload_and_parse_image'),
]
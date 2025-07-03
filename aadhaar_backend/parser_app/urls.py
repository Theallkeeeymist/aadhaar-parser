from django.urls import path
from . import views
from .views import upload_and_parse_image,save_aadhaar_data,home

urlpatterns=[
    path('', views.home, name='home'),
    path('parse/', views.parse_view, name='parse_view'),
    path('api/upload/', upload_and_parse_image, name='upload_and_parse_image'),
    path('api/save/', views.save_aadhaar_data, name='save_aadhaar_data'),
    # path('api/login/', obtain_auth_token, name='api_token_auth')
]
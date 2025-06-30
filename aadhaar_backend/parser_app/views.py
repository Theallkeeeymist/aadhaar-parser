from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from .utils import parse_from_image
from .models import AadhaarData
import json

# Create your views here.
@csrf_exempt
def upload_and_parse_image(request):
    if request.method=='POST' and request.FILES.get('aadhaar_image'):
        image_file=request.FILES['aadhaar_image']

        save_path=default_storage.save(f'temp/{image_file.name}', image_file)
        image_path=os.path.join(settings.MEDIA_ROOT, save_path)

        extracted_info,_=parse_from_image(image_path)

        return JsonResponse(extracted_info)

    return JsonResponse({'error': 'No image uploaded'}, status=400)





# def save_aadhaar_data(request):
#     if request.method=="POST":
#         data=json.loads(request.body)
#         AadhaarData.objects.create(
#             NAME=data.get("name"),
#             AADHAAR_NUMBER=data.get("number"),
#             DATE_OF_BIRTH=data.get("date_of_birth"),
#             GENDER=data.get("gender")
#         )
#         return JsonResponse({"message": "Data Saved!"})
#     else:
#         return JsonResponse({"oops": "Invalid request"}, status=400)
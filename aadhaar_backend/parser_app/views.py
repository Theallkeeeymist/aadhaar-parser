from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import os
from .utils import parse_from_image
from .models import AadhaarData
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
# user=User.objects.get(username='sudhanshuanand')
# token, created=Token.objects.get_or_create(user=user)
# print(token.key)

# @api_view(['POST'])
@csrf_exempt
def upload_and_parse_image(request):
    if request.method=='POST' and request.FILES.get('image'):
        image_file=request.FILES['image']

        save_path=default_storage.save(f'temp/{image_file.name}', image_file)
        image_path=os.path.join(settings.MEDIA_ROOT, save_path)

        extracted_info,_=parse_from_image(image_path)

        return JsonResponse(extracted_info)

    return JsonResponse({'error': 'No image uploaded'}, status=400)

def home(request):
    return render(request, 'index.html')

def parse_view(request):
    if request.method=="POST" and request.FILES.get('image'):
        image_file=request.FILES['image']
    else:
        return JsonResponse({"error" : "No image uploaded"})

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
def save_aadhaar_data(request):
    if request.method=="POST":
        try:
            data=json.loads(request.body.decode('utf-8'))
            # data=request.data

            name = data.get("name")
            aadhaar = data.get("aadhaar")
            dob = data.get("date_of_birth")
            gender = data.get("gender")

            if AadhaarData.objects.filter(aadhaar_number=aadhaar).exists():
                return JsonResponse({"error": "Aadhaar Number already exists."}, status=400)

            AadhaarData.objects.create(
                name=name,
                aadhaar_number=aadhaar,
                date_of_birth=dob,
                gender=gender
            )
            return JsonResponse({"message": "Data Saved!"})
        except Exception as e:
            return JsonResponse({"error" : str(e)}, status=400)

    return JsonResponse({"oops": "Invalid request"}, status=400)
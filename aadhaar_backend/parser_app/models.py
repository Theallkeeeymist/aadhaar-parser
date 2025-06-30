from django.db import models

# Create your models here.
class AadhaarData(models.Model):
    name=models.CharField(max_length=1000, null=True, blank=True),
    gender=models.CharField(max_length=15, null=True, blank=True),
    aadhaar_number=models.CharField(max_length=15, unique=True),
    date_of_birth=models.CharField(max_length=10, null=True, blank=True) #CHar field is safer than date for OCR inputs


    def __str__(self):
        return f"{self.name} - {self.aadhaar_number}"
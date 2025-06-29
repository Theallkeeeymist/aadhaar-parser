import requests
import os

# List of URLs (use only sample/demo card images)
image_urls = [
    "https://img.etimg.com/thumb/msid-67586673,width-1200,height-900,imgsize-27204,overlay-etpanache/photo.jpg",
    "https://www.fakedocument.net/uploads/design/aadhaar-card-front.jpg",
    "https://i0.wp.com/www.techymob.com/wp-content/uploads/2020/06/Aadhaar.jpg",
    "https://idtempl.com/wp-content/uploads/2022/12/India-Aadhar-Card-Template-PSD-Front.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/3e/Aadhaar_card.jpg"
]

# Directory to save the images
os.makedirs("aadhaar_samples", exist_ok=True)

# Download images
for idx, url in enumerate(image_urls):
    try:
        response = requests.get(url)
        with open(f"aadhaar_samples/sample_{idx+1}.jpg", "wb") as f:
            f.write(response.content)
        print(f"Downloaded: sample_{idx+1}.jpg")
    except Exception as e:
        print(f"Failed to download from {url}: {e}")

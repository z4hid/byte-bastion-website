from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import requests
from PIL import Image

from .models import APIRequestLog

class ImageConverter:
    def create_rgb_image(self, file_path):
        with open(file_path, 'rb') as f:
            binary_data = f.read()

        rgb_data = []
        for i in range(0, len(binary_data), 3):
            r = binary_data[i] if i < len(binary_data) else 0
            g = binary_data[i+1] if i+1 < len(binary_data) else 0
            b = binary_data[i+2] if i+2 < len(binary_data) else 0
            rgb_data.append((r, g, b))

        size = self.get_size(len(rgb_data))
        image = Image.new('RGB', size)
        image.putdata(rgb_data)
        return image

    def get_size(self, data_length):
        if data_length < 10240:
            width = 32
        elif 10240 <= data_length <= 10240 * 3:
            width = 64
        elif 10240 * 3 < data_length <= 10240 * 6:
            width = 128
        elif 10240 * 6 < data_length <= 10240 * 10:
            width = 256
        else:
            width = 512
        
        height = (data_length // width) + 1
        return (width, height)


def upload_page(request):
    """
    Handles the upload of a file and redirects to the malware detection page.
    Expects a 'file' field in the request FILES dictionary.
    If the request is not a POST, simply renders the malware-detect.html template.

    If the request is a POST, saves the original file to the 'original' directory,
    converts the file to RGB image, saves the image as PNG to the 'converted'
    directory, and sends the PNG file to the FastAPI as a multipart/form-data.
    Logs the request and response details in the APIRequestLog model.

    If the request is successful, renders the malware-detect.html template with
    the prediction result. If the request fails, renders the template with an
    error message.
    """
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        file = request.FILES['file']

        # Save the original uploaded file permanently
        original_file_name = default_storage.save(f"original/{file.name}", file)
        original_file_path = os.path.join(settings.MEDIA_ROOT, original_file_name)

        # Convert the file to RGB image and save as PNG
        converter = ImageConverter()
        rgb_image = converter.create_rgb_image(original_file_path)
        png_file_name = f"{os.path.splitext(file.name)[0]}.png"

        # Ensure the 'converted' directory exists
        converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
        if not os.path.exists(converted_dir):
            os.makedirs(converted_dir)  # Create the directory if it doesn't exist

        png_file_path = os.path.join(converted_dir, png_file_name)
        rgb_image.save(png_file_path, format='PNG')

        # Send the PNG file to FastAPI as a multipart/form-data
        fastapi_url = 'https://z4hid-hf-cloud-fastapi.hf.space/predict'
        try:
            with open(png_file_path, 'rb') as f:
                files = {'file': (os.path.basename(png_file_path), f, 'image/png')}
                response = requests.post(fastapi_url, files=files)
                response.raise_for_status()
                result = response.json()

                # Extract the prediction from the response
                prediction = result.get('prediction', 'Unknown')

                # Log the request and response details
                APIRequestLog.objects.create(
                    image_name=os.path.basename(png_file_path),
                    response_status=response.status_code,
                    response_data=prediction,
                    error_message=None
                )

            return render(request, 'malware-detect.html', {'result': result})

        except requests.RequestException as e:
            error_message = f'Error communicating with the API: {str(e)}'

            # Log the error details
            APIRequestLog.objects.create(
                image_name=os.path.basename(png_file_path),
                response_status=500,
                response_data=None,
                error_message=error_message
            )

            return render(request, 'malware-detect.html', {'error': error_message})

    return render(request, 'malware-detect.html')

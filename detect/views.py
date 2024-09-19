from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import requests

# def upload_page(request):
#     if request.method == 'POST':
#         if 'image' not in request.FILES:
#             return JsonResponse({'error': 'No image file uploaded'}, status=400)

#         image_file = request.FILES['image']

#         # Save the uploaded file temporarily
#         file_name = default_storage.save(image_file.name, image_file)
#         file_path = os.path.join(settings.MEDIA_ROOT, file_name)

#         # Send the file to FastAPI as a multipart/form-data
#         fastapi_url = 'https://z4hid-hf-cloud-fastapi.hf.space/predict'
#         try:
#             with open(file_path, 'rb') as f:
#                 files = {'file': (file_name, f, image_file.content_type)}
#                 response = requests.post(fastapi_url, files=files)
#                 response.raise_for_status()
#                 result = response.json()

#             # Delete the temporary file after processing
#             default_storage.delete(file_name)

#             return render(request, 'upload_form.html', {'result': result})
#         except requests.RequestException as e:
#             default_storage.delete(file_name)
#             error_message = f'Error communicating with the API: {str(e)}'
#             return render(request, 'upload_form.html', {'error': error_message})

#     return render(request, 'upload_form.html')
from .models import APIRequestLog

def upload_page(request):
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file uploaded'}, status=400)

        image_file = request.FILES['image']

        # Save the uploaded file temporarily
        file_name = default_storage.save(image_file.name, image_file)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Send the file to FastAPI as a multipart/form-data
        fastapi_url = 'https://z4hid-hf-cloud-fastapi.hf.space/predict'
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, image_file.content_type)}
                response = requests.post(fastapi_url, files=files)
                response.raise_for_status()
                result = response.json()
                
                # Extract the prediction from the response
                prediction = result.get('prediction', 'Unknown')

                # Log the request and response details
                APIRequestLog.objects.create(
                    image_name=file_name,
                    response_status=response.status_code,
                    response_data=prediction
                )

            # Delete the temporary file after processing
            default_storage.delete(file_name)

            return render(request, 'malware-detect.html', {'result': result})

        except requests.RequestException as e:
            error_message = f'Error communicating with the API: {str(e)}'

            # Log the error details
            APIRequestLog.objects.create(
                image_name=file_name,
                response_status=500,
                response_data=None,
                error_message=error_message
            )

            # Delete the temporary file in case of error
            default_storage.delete(file_name)
            return render(request, 'malware-detect', {'error': error_message})

    return render(request, 'malware-detect.html')

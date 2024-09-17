from django.contrib import admin
from .models import APIRequestLog

@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ('image_name', 'timestamp', 'response_status', 'response_data', 'error_message')
    list_filter = ('timestamp', 'response_status')
    search_fields = ('image_name', 'response_data', 'error_message')

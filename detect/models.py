from django.db import models

class APIRequestLog(models.Model):
    image_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_status = models.IntegerField()
    response_data = models.TextField()
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.image_name} - {self.timestamp}"

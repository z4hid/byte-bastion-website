from django.urls import path
from .views import HomepageView, AboutPageView, DownloadPageView, ProductPageView

urlpatterns = [
    path('', HomepageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('download/', DownloadPageView.as_view(), name='download'),
    path('product/', ProductPageView.as_view(), name='product'),
]

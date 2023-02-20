from django.urls import path, include
from img_api.views import BasicViewSet, GetThumbnailsView
from django.conf import settings
from django.conf.urls.static import static

dev_settings = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG == True else []

urlpatterns = [
    path('', include('rest_framework.urls')),
    path('', BasicViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('test', GetThumbnailsView.as_view())
] + dev_settings
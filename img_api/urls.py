from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from img_api.views import ImageView, ImgApiViewSet

dev_settings = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG == True else []
router = DefaultRouter()
router.register('api', ImgApiViewSet, basename='api')

urlpatterns = [
    path('', include('rest_framework.urls')), # For login/logout using browsable api
    path('media/<int:pk>/images/<path:filename>/', ImageView.as_view(), name='image_view'),
    path('', include(router.urls))
]
# + dev_settings
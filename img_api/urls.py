from django.urls import path, include
from img_api.views import ImageView, ImgApiViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

dev_settings = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG == True else []
router = DefaultRouter()
router.register('api', ImgApiViewSet, basename='api')
# router.register('imgapi', ApiViewSet, basename='apiview')

urlpatterns = [
    path('', include('rest_framework.urls')), # For login/logout using browsable api
    path('media/<int:pk>/images/<path:filename>/', ImageView.as_view()),
    ] + router.urls 
# + dev_settings
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from rest_framework import viewsets, views
from rest_framework.authentication import (SessionAuthentication,
                                           BasicAuthentication)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from img_api.models import Image, CustUser, Tier
from img_api.serializers import ImageSerializer, ImSer

# Create your views here.
   

class BasicViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # Getting images of loggedin user only
    # def get_queryset(self):
    #     queryset = Image.objects.filter(created_by=self.request.user.id)
    #     return queryset

class GetThumbnailsView(views.APIView):

    def get_queryset(self, request):
        # return Image.objects.all()
        user = request.user.id
        return Image.objects.filter(created_by__user__id=user)
    

    def get(self, request):
        # print(request.build_absolute_uri(Image.objects.get(id=4).image.url))
        user = request.user.id
        tier = Tier.objects.get(custuser__user__id=user)

        context = {
            'request': request,
            'name': tier.name,
            'options': tier.options
        }

        serializer = ImSer(self.get_queryset(request), many=True, context=context)

        return Response(serializer.data)
    
    def post(self, request):
        serializer = ImSer()


class ImageView(views.APIView):
    def get(self, request, *args, **kwargs):
        user = kwargs.get('pk')
        filename = kwargs.get('filename')
        print(user)
        print('TETETE')
        print(filename)
        full_path = str(settings.MEDIA_ROOT) + '/' + str(user) + '/images/' + filename
        print(HttpResponse.__dict__)
        im = open(full_path, 'rb')
        return FileResponse(im)
        # return HttpResponse(im)
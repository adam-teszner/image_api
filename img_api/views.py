from datetime import datetime, timedelta
from urllib.parse import urlparse
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.core.signing import Signer, BadSignature
from django.views.generic import View
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, views
from rest_framework.authentication import (SessionAuthentication,
                                           BasicAuthentication)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from img_api.models import Image, CustUser, Tier
from img_api.serializers import ImageSerializer, ImgSerializer, ImgUploadSerializer

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

        serializer = ImgSerializer(self.get_queryset(request), many=True, context=context)

        return Response(serializer.data)
    
    def post(self, request):
        serializer = ImgSerializer()

class ImgApiViewSet(viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self, request):
        user = request.user.id
        return Image.objects.filter(created_by__user__id=user)    
    

    def list(self, request):
        user = request.user.id
        tier = Tier.objects.get(custuser__user__id=user)

        context = {
            'request': request,
            'name': tier.name,
            'options': tier.options
        }
        serializer = ImgSerializer(self.get_queryset(request), many=True, context=context)

        return Response(data=serializer.data)


    def retrieve(self, request, pk=None):
        user = request.user.id
        tier = Tier.objects.get(custuser__user__id=user)
        image = get_object_or_404(self.get_queryset(request), pk=pk)
        

        context = {
            'request': request,
            'name': tier.name,
            'options': tier.options
        }
        serializer = ImgSerializer(image, context=context)

        return Response(data=serializer.data)

    def create(self, request):
        serializer = ImgSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ImageView(views.APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        '''
        Serves the image, binary image or a thumbnail - when user is
        authenticated and is the image owner or if user has signed, timestamped
        url.
        '''
        user = kwargs.get('pk')
        filename = kwargs.get('filename')
        full_path = str(settings.MEDIA_ROOT) + '/' + str(user) + '/images/' + filename
        cust_user = CustUser.objects.get(id=user)
        
        # Serve image if user is uploader of requested image and is logged in
        if self.request.user.is_authenticated and self.request.user.id == cust_user.user.id:
            return FileResponse(open(full_path, 'rb'), status=status.HTTP_200_OK)
        
        # If user isn't logged in check signature, timestamp, if valid open image
        if not self.request.user.is_authenticated:
            signer = Signer(sep='&signed=')
            url = request.build_absolute_uri()

            # If signature is valid and timestamp is valid - serve the file
            try:
                expiration_date = datetime.strptime(
                    request.query_params.get('expires'),"%Y-%m-%d-%H-%M-%S")
            except TypeError:
                raise AuthenticationFailed
                        
            try:
                signer.unsign(url)
            except BadSignature:
                raise AuthenticationFailed('Bad signature')
            
            if expiration_date < datetime.now():
                raise PermissionDenied('Link has expired')
            


            return FileResponse(open(full_path, 'rb'), status=status.HTTP_200_OK)

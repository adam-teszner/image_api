from datetime import datetime, timedelta

from django.conf import settings
from django.core.signing import BadSignature, Signer
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.decorators import action
from rest_framework.exceptions import (AuthenticationFailed, NotFound,
                                       PermissionDenied)
from rest_framework.parsers import (FileUploadParser, FormParser,
                                    MultiPartParser)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from img_api.models import CustUser, Image, Tier
from img_api.serializers import ExpiringLinkSerializer, PrimaryImageSerializer


class ImgApiViewSet(viewsets.ViewSet):
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = PrimaryImageSerializer


    def get_queryset(self, request):
        user = request.user.id
        return Image.objects.filter(created_by__user__id=user)

    def get_context_data(self, request, *args, **kwargs):
        user = request.user.id
        tier = Tier.objects.get(custuser__user__id=user)
        context = {
            'request': request,
            'name': tier.name,
            'options': tier.options,
            'original_link': tier.original_link,
            'bin_img_exp_link': tier.bin_img_exp_link
        }

        return context
    

    def list(self, request):
        user = request.user.id
        tier = Tier.objects.get(custuser__user__id=user)
        if tier.list_details == True:
            context = self.get_context_data(request)
        else:
            context = {'request': request}
        serializer = PrimaryImageSerializer(self.get_queryset(request),
                            many=True, context=context)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request): 
        cust_user = CustUser.objects.get(user=request.user.id)
        context = {'created_by': cust_user}  
        serializer = PrimaryImageSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()        
            return self.retrieve(request, pk=serializer.instance.id,
                            created=True)
        
        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None, created=None):
        user = request.user.id
        tier = Tier.objects.get(custuser__user__id=user)
        image = get_object_or_404(self.get_queryset(request), pk=pk)
        status_code = status.HTTP_201_CREATED if created==True else status.HTTP_200_OK
        context = self.get_context_data(request)
        serializer = PrimaryImageSerializer(image, context=context)
        return Response(data=serializer.data, status=status_code)
    
    @action(detail=True, methods=['POST', 'GET'])
    def generate_expiring_url(self, request, *args, **kwargs):
        self.serializer_class = ExpiringLinkSerializer
        user = request.user.id
        tier = Tier.objects.get(custuser__user__id=user)
        image = get_object_or_404(self.get_queryset(request), pk=kwargs.get('pk'))
        status_code = status.HTTP_200_OK
        if tier.bin_img_exp_link == None or tier.bin_img_exp_link == 0:
            raise PermissionDenied('You dont have permissions to generate urls')

        context = {
            'request': request,
            'bin_img_exp_link': tier.bin_img_exp_link,
            'object': image
        }
        serializer = ExpiringLinkSerializer(request, context=context)
        return Response(data=serializer.data, status=status_code)


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
        if self.request.user.is_authenticated:
            if self.request.user.id == cust_user.user.id or self.request.user.is_superuser:
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
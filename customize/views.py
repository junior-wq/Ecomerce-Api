from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import ( Logo,About,FooterColumn,Banner )

from .serializers import ( LogoSerializer,BannerSerializer,AboutSerializer,FooterColumnSerializer)
from rest_framework.permissions import AllowAny

class LogoViewSet(ReadOnlyModelViewSet):
    queryset = Logo.objects.all()
    serializer_class = LogoSerializer

class BannerViewSet(ReadOnlyModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


class AboutViewSet(ReadOnlyModelViewSet):
    permission_classes=[AllowAny]
    queryset = About.objects.all()
    serializer_class = AboutSerializer


class FooterColumnViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = FooterColumn.objects.all()
    serializer_class = FooterColumnSerializer






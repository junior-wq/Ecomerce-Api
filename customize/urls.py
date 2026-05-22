from django.urls import path, include
from rest_framework.routers import DefaultRouter  # Changed from SimpleRouter
from .views import (
    LogoViewSet,
    BannerViewSet,
    AboutViewSet,
    FooterColumnViewSet
)

router = DefaultRouter()  # Changed to DefaultRouter
router.register('logo', LogoViewSet, basename='logo')
router.register('banners', BannerViewSet, basename='banners')
router.register('about', AboutViewSet, basename='about')
router.register('footer', FooterColumnViewSet, basename='footer')

urlpatterns = [
    path('', include(router.urls)),
]
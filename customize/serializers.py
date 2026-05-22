from rest_framework import serializers
from .models import (
    Logo,
    Banner,
    About,
    FooterColumn,
    FooterListItem
)


class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logo
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'



class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = About
        fields = '__all__'


class FooterListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterListItem
        fields = ['id', 'name']


class FooterColumnSerializer(serializers.ModelSerializer):
    footer_list_item = FooterListItemSerializer(many=True, read_only=True)

    class Meta:
        model = FooterColumn
        fields = ['id', 'title', 'footer_list_item']

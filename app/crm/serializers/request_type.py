from rest_framework import serializers

from ..models import RequestType

class RequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestType
        fields = ['id', 'name', 'description']
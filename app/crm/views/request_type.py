from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, mixins

from ..models import RequestType
from ..serializers import RequestTypeSerializer


@extend_schema(tags=['request type'])
@extend_schema_view(
    list=extend_schema(
        summary="Список типов заявок",
    ),
)
class RequestTypeViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin):
    queryset = RequestType.objects.filter(is_active=True)
    serializer_class = RequestTypeSerializer

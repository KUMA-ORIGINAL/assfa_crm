from rest_framework import viewsets, mixins
from crm.models import Request
from crm.serializers import RequestSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema(tags=['request'])
@extend_schema_view(
    create=extend_schema(
        summary="Создание заявки",
        description="Создает новую заявку. Статус по умолчанию — 'new'.",
    ),
)
class RequestViewSet(viewsets.GenericViewSet,
                    mixins.CreateModelMixin):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

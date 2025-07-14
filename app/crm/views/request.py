from django.contrib.admin.utils import quote
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.views import APIView

from crm.models import Request
from crm.serializers import RequestSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

from crm.services.document_generate import fill_template_to_bytes


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


class RequestDocxGenerateView(APIView):

    def get(self, request, pk, format=None):
        req = get_object_or_404(Request, pk=pk)

        data_to_fill = {
            "[ФИО]": req.full_name_or_org,
            "[адрес]": req.actual_address,
            "[телефон]": req.phone_number,
            "[описание]": req.description,
            "[сумма]": f"{req.requested_amount} сом",
            "[реквизит]": req.requisites or "",
            "[дата и время]": req.created_at.strftime("%d.%m.%Y"),
        }

        template_path = "static/Пример заявления.docx"
        file_bytes = fill_template_to_bytes(template_path, data_to_fill)
        filename = f"Заявление_{req.id}.docx"
        quoted_filename = quote(filename)

        response = HttpResponse(
            file_bytes,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{quoted_filename}"
        return response

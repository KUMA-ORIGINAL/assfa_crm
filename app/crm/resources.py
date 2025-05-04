from import_export import resources, widgets, fields
from import_export.widgets import ForeignKeyWidget
from .models import Request, RequestType

# Словарь для преобразования статусов
STATUS_DISPLAY = dict(Request._meta.get_field('status').choices)
SUBJECT_TYPE_DISPLAY = dict(Request._meta.get_field('subject_type').choices)


class RequestResource(resources.ModelResource):
    id = fields.Field(attribute='id', column_name='ID')

    subject_type = fields.Field(
        column_name='Тип субъекта',
        attribute='subject_type',
        widget=widgets.Widget()
    )

    full_name_or_org = fields.Field(attribute='full_name_or_org', column_name='ФИО или название учреждения')
    phone_number = fields.Field(attribute='phone_number', column_name='Номер телефона')
    actual_address = fields.Field(attribute='actual_address', column_name='Фактический адрес')
    registration_address = fields.Field(attribute='registration_address', column_name='Адрес прописки')

    request_type = fields.Field(
        column_name='Тип заявки',
        attribute='request_type',
        widget=ForeignKeyWidget(RequestType, 'name')
    )

    description = fields.Field(attribute='description', column_name='Описание ситуации / комментарий')
    requested_amount = fields.Field(attribute='requested_amount', column_name='Запрашиваемая сумма')
    approved_amount_director = fields.Field(attribute='approved_amount_director', column_name='Сумма, одобренная директором')
    approved_amount_chairman = fields.Field(attribute='approved_amount_chairman', column_name='Сумма, одобренная председателем')

    status = fields.Field(
        column_name='Статус',
        attribute='status',
        widget=widgets.Widget()
    )

    created_at = fields.Field(attribute='created_at', column_name='Дата подачи')
    updated_at = fields.Field(attribute='updated_at', column_name='Дата обновления')

    def dehydrate_subject_type(self, obj):
        return SUBJECT_TYPE_DISPLAY.get(obj.subject_type, obj.subject_type)

    def dehydrate_status(self, obj):
        return STATUS_DISPLAY.get(obj.status, obj.status)

    def dehydrate_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def dehydrate_updated_at(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Request
        import_id_fields = ('id',)
        fields = (
            'id',
            'subject_type',
            'full_name_or_org',
            'phone_number',
            'actual_address',
            'registration_address',
            'request_type',
            'description',
            'requested_amount',
            'approved_amount_director',
            'approved_amount_chairman',
            'status',
            'created_at',
            'updated_at',
        )
        export_order = fields
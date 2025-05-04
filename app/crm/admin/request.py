from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from unfold.contrib.filters.admin import RangeDateTimeFilter, ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.contrib.import_export.forms import ExportForm

from common.admin import BaseModelAdmin
from ..models import Request
from ..resources import RequestResource


@admin.register(Request)
class RequestAdmin(SimpleHistoryAdmin, BaseModelAdmin, ExportActionModelAdmin):
    list_display = (
        'id',
        'full_name_or_org',
        'subject_type',
        'request_type',
        'requested_amount',
        'status',
        'created_at',
        'detail_link'
    )
    list_filter = (
        'subject_type',
        ('status', ChoicesDropdownFilter),
        ('request_type', RelatedDropdownFilter),
        ('created_at', RangeDateTimeFilter)
    )
    list_filter_submit = True
    search_fields = ('full_name_or_org', 'phone_number', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25

    export_form_class = ExportForm
    resource_class = RequestResource

    list_select_related = ('request_type',)

    fieldsets = (
        (None, {
            'fields': (
                'subject_type', 'full_name_or_org', 'phone_number',
                'actual_address', 'registration_address',
                'description', 'request_type', 'status',
            )
        }),
        ("Финансовая информация", {
            'fields': (
                'requested_amount',
                'approved_amount_director',
                'approved_amount_chairman',
            )
        }),
        ("Документы и вложения", {
            'fields': (
                'incoming_letter', 'attachments',
            )
        }),
        ("Служебная информация", {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

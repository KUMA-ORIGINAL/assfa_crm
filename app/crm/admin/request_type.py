from django.contrib import admin

from common.admin import BaseModelAdmin
from ..models import RequestType


@admin.register(RequestType)
class RequestTypeAdmin(BaseModelAdmin):
    list_display = ('id', 'name', 'description', 'is_active', 'detail_link')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)

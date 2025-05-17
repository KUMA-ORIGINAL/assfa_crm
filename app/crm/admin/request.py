from typing import Union

from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from import_export.admin import ExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from unfold.contrib.filters.admin import RangeDateTimeFilter, ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.contrib.import_export.forms import ExportForm
from unfold.decorators import action

from common.admin import BaseModelAdmin
from ..models import Request, ROLE_SPECIALIST, ROLE_DIRECTOR, ROLE_CHAIRMAN, ROLE_ACCOUNTANT
from ..resources import RequestResource
from ..services.notifications import notify_status_change


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
    actions_detail = [
        "approve_specialist",
        "reject_specialist",
        "approve_director",
        "reject_director",
        'send_to_chairman',
        "approve_chairman",
        "reject_chairman",
        "mark_as_awaiting_payment",
        "mark_as_paid",
    ]
    history_list_display = ["status"]

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
                'requisites',
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

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields

        base_fields = [
            'subject_type',
            'full_name_or_org',
            'phone_number',
            'actual_address',
            'registration_address',
            'description',
            'incoming_letter',
            'requisites',
            'requested_amount',
            'request_type',
            'status',
            'created_at',
            'updated_at',
            'attachments',
        ]

        if request.user.role in (ROLE_SPECIALIST, ROLE_ACCOUNTANT):
            return base_fields + ['approved_amount_director', 'approved_amount_chairman']
        elif request.user.role == ROLE_DIRECTOR:
            return base_fields + ['approved_amount_chairman']
        elif request.user.role == ROLE_CHAIRMAN:  # Пример на случай, если вы хотели добавить ещё одну роль
            return base_fields + ['approved_amount_director']

        return base_fields  # По умолчанию — можно оставить только базовые поля

    @action(
        description=_("✅ Одобрить (Специалист)"),
        url_path="approve-specialist",
        permissions=["approve_specialist"],
    )
    def approve_specialist(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'approved_by_specialist'
        obj.save()
        notify_status_change(role=ROLE_DIRECTOR, request_obj=obj, new_status=obj.get_status_display())
        messages.success(request, _("Заявка одобрена специалистом."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_approve_specialist_permission(self, request: HttpRequest, object_id: Union[str, int]) -> bool:
        return request.user.role == ROLE_SPECIALIST

    @action(
        description=_("❌ Отклонить (Специалист)"),
        url_path="reject-specialist",
        permissions=["reject_specialist"],
    )
    def reject_specialist(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'rejected_by_specialist'
        obj.save()
        messages.success(request, _("Заявка отклонена специалистом."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_reject_specialist_permission(self, request: HttpRequest, object_id: Union[str, int]) -> bool:
        return request.user.role == ROLE_SPECIALIST

    # ==== ДИРЕКТОР ====

    # @action(
    #     description=_("✅ Одобрить (Директор)"),
    #     url_path="approve-director",
    #     permissions=["approve_director"],
    # )
    # def approve_director(self, request, object_id):
    #     obj = get_object_or_404(Request, pk=object_id)  # замените на вашу модель
    #
    #     class ApproveDirectorForm(forms.Form):
    #         approved_amount_director = forms.DecimalField(
    #             label=_("Сумма, утвержденная директором"),
    #             min_value=0,
    #             decimal_places=2,
    #             max_digits=12,
    #             widget=UnfoldAdminTextInputWidget(attrs={"placeholder": _("Введите сумму")}),
    #         )
    #
    #         class Media:
    #             js = [
    #                 "admin/js/vendor/jquery/jquery.js",
    #                 "admin/js/jquery.init.js",
    #                 "admin/js/calendar.js",
    #                 "admin/js/admin/DateTimeShortcuts.js",
    #                 "admin/js/core.js",
    #             ]
    #
    #     form = ApproveDirectorForm(request.POST or None)
    #
    #     if request.method == "POST" and form.is_valid():
    #         # Сохраняем сумму и комментарий
    #         obj.approved_amount_director = form.cleaned_data["approved_amount_director"]
    #         obj.status = "approved_by_director"
    #         # можно сохранить комментарий в поле, если оно есть
    #         # obj.director_comment = form.cleaned_data["comment"]
    #         obj.save(update_fields=["approved_amount_director", "status"])
    #
    #         messages.success(request, _("Заявка одобрена директором и сумма утверждена."))
    #         return redirect(reverse_lazy("admin:crm_request_change", args=[obj.pk]))
    #
    #     return render(
    #         request,
    #         "crm/director_approve_form.html",  # шаблон формы
    #         {
    #             "form": form,
    #             "object": obj,
    #             "title": _("Одобрение заявки директором"),
    #             **self.admin_site.each_context(request),
    #         },
    #     )

    @action(
        description=_("✅ Одобрить (Директор)"),
        url_path="approve-director",
        permissions=["approve_director"],
    )
    def approve_director(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'approved_by_director'
        obj.save()
        notify_status_change(role=ROLE_ACCOUNTANT, request_obj=obj, new_status=obj.get_status_display())
        messages.success(request, _("Заявка одобрена директором."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_approve_director_permission(self, request, object_id=None):
        return request.user.role == ROLE_DIRECTOR

    @action(
        description=_("❌ Отклонить (Директор)"),
        url_path="reject-director",
        permissions=["reject_director"],
    )
    def reject_director(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'rejected_by_director'
        obj.save()
        messages.success(request, _("Заявка отклонена директором."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_reject_director_permission(self, request, object_id=None):
        return request.user.role == ROLE_DIRECTOR

    @action(
        description=_("📨 Направить председателю"),
        url_path="send-to-chairman",
        permissions=["send_to_chairman"],
    )
    def send_to_chairman(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'sent_to_chairman'
        obj.save()
        notify_status_change(role=ROLE_CHAIRMAN, request_obj=obj, new_status=obj.get_status_display())
        messages.success(request, _("Заявка направлена председателю."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_send_to_chairman_permission(self, request, object_id=None):
        return request.user.role == ROLE_DIRECTOR

    # ==== ПРЕДСЕДАТЕЛЬ ====

    @action(
        description=_("✅ Одобрить (Председатель)"),
        url_path="approve-chairman",
        permissions=["approve_chairman"],
    )
    def approve_chairman(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'approved_by_chairman'
        obj.save()
        notify_status_change(role=ROLE_ACCOUNTANT, request_obj=obj, new_status=obj.get_status_display())
        messages.success(request, _("Заявка одобрена председателем."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_approve_chairman_permission(self, request, object_id=None):
        return request.user.role == ROLE_CHAIRMAN

    @action(
        description=_("❌ Отклонить (Председатель)"),
        url_path="reject-chairman",
        permissions=["reject_chairman"],
    )
    def reject_chairman(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'rejected_by_chairman'
        obj.save()
        messages.success(request, _("Заявка отклонена председателем."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_reject_chairman_permission(self, request, object_id=None):
        return request.user.role == ROLE_CHAIRMAN

    # ==== БУХГАЛТЕР ====

    @action(
        description=_("💰 Выплачено"),
        url_path="mark-paid",
        permissions=["mark_as_paid"],
    )
    def mark_as_paid(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'paid'
        obj.save()
        messages.success(request, _("Заявка выплачена."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_mark_as_paid_permission(self, request, object_id=None):
        return request.user.role == ROLE_ACCOUNTANT

    @action(
        description=_("⏳ Ожидает выплаты"),
        url_path="mark-awaiting-payment",
        permissions=["mark_as_awaiting_payment"],
    )
    def mark_as_awaiting_payment(self, request: HttpRequest, object_id: int):
        obj = self.model.objects.get(pk=object_id)
        obj.status = 'awaiting_payment'
        obj.save()
        messages.success(request, _("Заявка помечена как 'Ожидает выплаты'."))
        return redirect(reverse_lazy("admin:crm_request_change", args=[object_id]))

    def has_mark_as_awaiting_payment_permission(self, request, object_id=None):
        return request.user.role == ROLE_ACCOUNTANT
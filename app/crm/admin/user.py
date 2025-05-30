from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm as BaseUserChangeForm, UserCreationForm, \
    UnfoldReadOnlyPasswordHashWidget

from common.admin import BaseModelAdmin
from ..models import User, ROLE_SPECIALIST, ROLE_DIRECTOR, ROLE_CHAIRMAN, ROLE_ACCOUNTANT

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(GroupAdmin, UnfoldModelAdmin):
    pass


class MaskedPasswordWidget(UnfoldReadOnlyPasswordHashWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        usable_password = value and not value.startswith(UNUSABLE_PASSWORD_PREFIX)

        if usable_password:
            context["summary"] = [
                {"label": "*****************************************************************************************"},
            ]
        else:
            context["summary"] = [
                {"label": _("No password set.")},
            ]

        context["button_label"] = (
            _("Reset password") if usable_password else _("Set password")
        )
        return context


class UserChangeForm(BaseUserChangeForm):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password"].widget = MaskedPasswordWidget()


@admin.register(User)
class UserAdmin(UserAdmin, BaseModelAdmin):
    model = User
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm
    add_form = UserCreationForm

    list_display_links = ('id', 'email')
    search_fields = ('email', 'first_name', 'last_name', 'role')
    ordering = ('-date_joined',)
    autocomplete_fields = ('groups',)
    list_per_page = 20

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', "first_name", "last_name",),
        }),
    )

    def get_list_filter(self, request):
        list_filter = ('role', 'is_active', 'is_staff',)
        if request.user.is_superuser:
            pass
        return list_filter

    def get_list_display(self, request):
        list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'tg_phone_number', 'detail_link')
        if request.user.is_superuser:
            pass
        return list_display

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets

        fieldsets = [
            (None, {
                "fields": ("email", "password"),
            }),
            ("Права доступа", {
                "fields": ("is_staff", "is_active", "is_superuser", "groups",),
            }),
            ("Даты", {
                "fields": ("last_login", "date_joined"),
            }),
            ("Личная информация", {
                "fields": (
                    "first_name", "last_name", "patronymic", "role",
                ),
            }),
            ("Telegram", {
                "fields": (
                    'tg_phone_number', 'tg_chat_id'
                ),
            }),
        ]
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_SPECIALIST, ROLE_DIRECTOR, ROLE_CHAIRMAN, ROLE_ACCOUNTANT):
            fieldsets = [fs for fs in fieldsets if fs[0] != 'Права доступа']
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs

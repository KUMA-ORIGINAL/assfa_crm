from django.db import models
from simple_history.models import HistoricalRecords

from config.settings import REQUEST_STATUSES


class Request(models.Model):
    SUBJECT_TYPES = (
        ('individual', 'Физическое лицо'),
        ('organization', 'Юридическое лицо'),
    )

    subject_type = models.CharField("Тип субъекта", max_length=20, choices=SUBJECT_TYPES)
    full_name_or_org = models.CharField("ФИО или название учреждения", max_length=255)
    phone_number = models.CharField("Номер телефона", max_length=20)
    actual_address = models.CharField("Фактический адрес", max_length=255)
    registration_address = models.CharField("Адрес прописки", max_length=255)
    description = models.TextField("Описание ситуации / комментарий")
    incoming_letter = models.FileField("Входящее письмо", upload_to='letters/', blank=True, null=True)
    requisites = models.CharField("Реквизиты", blank=True, null=True)
    requested_amount = models.DecimalField("Запрашиваемая сумма", max_digits=12, decimal_places=2)
    approved_amount_director = models.DecimalField("Сумма, одобренная директором", max_digits=12, decimal_places=2, null=True, blank=True)
    approved_amount_chairman = models.DecimalField("Сумма, одобренная председателем", max_digits=12, decimal_places=2, null=True, blank=True)
    request_type = models.ForeignKey('RequestType', verbose_name="Тип заявки", on_delete=models.SET_NULL, null=True)
    status = models.CharField("Статус", max_length=50, choices=REQUEST_STATUSES, default='new')
    created_at = models.DateTimeField("Дата подачи", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    attachments = models.FileField("Приложения", upload_to='attachments/', blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name_or_org} - {self.request_type}"

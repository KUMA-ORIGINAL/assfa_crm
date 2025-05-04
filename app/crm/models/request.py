from django.db import models
from simple_history.models import HistoricalRecords

REQUEST_STATUSES = (
    ('new', 'Новый'),
    ('specialist_review', 'На проверке у специалиста'),
    ('approved_by_specialist', 'Одобрено специалистом'),
    ('director_review', 'На рассмотрении у Генерального директора'),
    ('rejected_by_director', 'Отклонено директором'),
    ('approved_by_director', 'Одобрено директором'),
    ('chairman_review', 'На рассмотрении у председателя'),
    ('rejected_by_chairman', 'Отклонено председателем'),
    ('approved_by_chairman', 'Одобрено председателем'),
    ('awaiting_payment', 'Ожидает выплаты'),
    ('paid', 'Выплачено'),
    ('payment_pending', 'Выплата в ожидании'),
)

class Request(models.Model):
    SUBJECT_TYPES = (
        ('individual', 'Физическое лицо'),
        ('organization', 'Юридическое лицо'),
    )

    subject_type = models.CharField("Тип субъекта", max_length=20, choices=SUBJECT_TYPES)
    full_name_or_org = models.CharField("ФИО или название учреждения", max_length=255)
    phone_number = models.CharField("Номер телефона", max_length=20)
    actual_address = models.TextField("Фактический адрес")
    registration_address = models.TextField("Адрес прописки")
    description = models.TextField("Описание ситуации / комментарий")
    incoming_letter = models.FileField("Входящее письмо", upload_to='letters/', blank=True, null=True)
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

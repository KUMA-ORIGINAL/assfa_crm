from django.db import models


class RequestType(models.Model):
    name = models.CharField("Название типа", max_length=100)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Тип заявки"
        verbose_name_plural = "Типы заявок"
        ordering = ['name']

    def __str__(self):
        return self.name

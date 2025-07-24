from django.db import models


class Batch(models.Model):
    class StatusChoices(models.TextChoices):
        acceptance = 'acceptance', 'Ожидает принятия'
        distribution = 'distribution', 'Ожидает распределения'
        good = 'good', 'Готова'

    number = models.IntegerField(unique=True, verbose_name="Номер партии")
    city = models.CharField(max_length=100, verbose_name="Город")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.acceptance,
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "Заявки"
        verbose_name_plural = "Заявки"
        ordering = ["-number"]

    def __str__(self):
        return f"{self.number} ({self.city})"


class SerialNumber(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='serial_numbers')
    serial = models.CharField(max_length=100, verbose_name="Серийный номер")
    model_bank = models.CharField(max_length=255, verbose_name="Модель банка")
    model = models.CharField(max_length=100, verbose_name='Модель', blank=True, null=True)
    brand = models.CharField(max_length=20, verbose_name='Производитель', blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True, verbose_name="Статус")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Местонахождение")

    class Meta:
        verbose_name = "Терминалы"
        verbose_name_plural = "Терминалы"

    def __str__(self):
        return self.serial

from django.contrib import admin
from .models import Batch, SerialNumber


# 👇 Inline класс для отображения SerialNumber прямо в админке партии
class SerialNumberInline(admin.TabularInline):  # или admin.StackedInline для более подробного вида
    model = SerialNumber
    extra = 1  # сколько пустых строк будет показано для добавления
    fields = ("serial", "model", "status", "location")  # какие поля показывать
    show_change_link = True  # ссылка на редактирование


# 👇 Админка для модели партии
@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("number", "city", "created_at")  # поля в списке
    search_fields = ("number", "city")  # поиск
    list_filter = ("city", "created_at")  # фильтры сбоку
    inlines = [SerialNumberInline]  # вставка SN внутрь


# 👇 Отдельная админка на случай, если хочешь управлять SN напрямую
@admin.register(SerialNumber)
class SerialNumberAdmin(admin.ModelAdmin):
    list_display = ("serial", "model", "status", "location", "batch")
    search_fields = ("serial", "model")
    list_filter = ("status", "location", "batch__city")

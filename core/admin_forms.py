# med_loupemed/core/admin_forms.py

from django import forms
from django.utils import timezone  # Для использования timezone.now().date()


class GenerateScheduleForm(forms.Form):
    # Поле для выбора начальной даты
    start_date = forms.DateField(
        label="Начальная дата",
        widget=forms.DateInput(attrs={"type": "date", "class": "vDateField"}),
        initial=timezone.now().date(),  # По умолчанию - сегодняшняя дата
        help_text="Выберите дату, с которой начнется генерация расписания.",
    )
    # Поле для выбора конечной даты
    end_date = forms.DateField(
        label="Конечная дата",
        widget=forms.DateInput(attrs={"type": "date", "class": "vDateField"}),
        initial=timezone.now().date()
        + timezone.timedelta(days=30),  # По умолчанию - через месяц
        help_text="Выберите дату, которой закончится генерация расписания (включительно).",
    )

    # Выбор врачей, для которых генерировать расписание (необязательно)
    # Если не выбрать никого, будет генерироваться для всех врачей с дефолтными настройками.
    doctors = forms.ModelMultipleChoiceField(
        queryset=None,  # Будет установлен в admin.py
        required=False,
        label="Выберите врачей (необязательно)",
        help_text="Оставьте пустым, чтобы сгенерировать для всех врачей с настроенным стандартным расписанием.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заполняем queryset для поля doctors
        from .models import (
            Doctor,
        )  # Импортируем Doctor здесь, чтобы избежать циклического импорта

        self.fields["doctors"].queryset = Doctor.objects.filter(
            is_active=True
        ).order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError(
                    "Конечная дата не может быть раньше начальной даты."
                )
            if end_date < timezone.now().date():
                raise forms.ValidationError(
                    "Нельзя генерировать расписание на прошедшие даты."
                )
        return cleaned_data

# med_loupemed/core/forms.py

from django import forms
from .models import Review, Doctor, DoctorSchedule, Appointment, Service, MedicalRecord, FAQItem


class ReviewForm(forms.ModelForm):

    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label="Выберите врача (необязательно)",
        label="Врач"
    )
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Review
        fields = ['full_name', 'email', 'rating', 'text', 'doctor']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш Email (необязательно)'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ваш отзыв...'}),
        }
        labels = {
            'full_name': 'Ваше имя',
            'email': 'Ваш Email',
            'text': 'Текст отзыва',
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Ваше имя")
    email = forms.EmailField(required=False, label="Ваш Email")
    phone_number = forms.CharField(max_length=20, required=False, label="Ваш телефон", help_text="Мы свяжемся с вами по телефону или email.") # Новое поле
    message = forms.CharField(widget=forms.Textarea, label="Ваше сообщение")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        if not email and not phone_number:
            raise forms.ValidationError(
                "Пожалуйста, укажите хотя бы свой Email или номер телефона для связи."
            )
        return cleaned_data


class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            'time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }


class DoctorScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = '__all__'
        widgets = {
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }


class UserAppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_active=True).order_by('name'),
        label="Врач",
        empty_label="Выберите врача"
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).order_by('name'),
        label="Услуга",
        empty_label="Выберите услугу"
    )
    date = forms.DateField(
        label="Дата приема",
        # type="text" нужен для Flatpickr, который сам превратит его в интерактивный календарь
        widget=forms.DateInput(attrs={'type': 'text', 'placeholder': 'Выберите дату', 'class': 'form-control datepicker-input'}),
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y']
    )
    time = forms.TimeField(
        label="Время приема",
        # Select будет динамически заполняться через AJAX
        widget=forms.Select(attrs={'class': 'form-control time-slots-select', 'disabled': 'disabled'}), # Изначально отключено
        required=False
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Дополнительные комментарии...'}),
        required=False,
        label="Комментарии"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'service', 'date', 'time', 'comments']

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('time') and self.is_bound:
            self.add_error('time', 'Пожалуйста, выберите доступное время приема.')
        return cleaned_data


class MedicalRecordUploadForm(forms.ModelForm):
    appointment = forms.ModelChoiceField(
        queryset=Appointment.objects.none(),
        label="Запись на прием",
        help_text="Выберите запись, к которой прикрепить результат."
    )

    class Meta:
        model = MedicalRecord
        fields = ['appointment', 'title', 'file', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название документа или анализа'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Дополнительные примечания к файлу (например, интерпретация результатов)'}),
        }
        labels = {
            'title': 'Название документа/анализа',
            'file': 'Файл (PDF, JPG, PNG и т.д.)',
            'notes': 'Примечания',
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        if doctor:
            existing_appointment_ids = MedicalRecord.objects.values_list('appointment_id', flat=True)
            self.fields['appointment'].queryset = Appointment.objects.filter(
                doctor=doctor,
                status__in=['completed', 'confirmed']
            ).exclude(id__in=existing_appointment_ids).order_by('-date', '-time')
        else:
            self.fields['appointment'].queryset = Appointment.objects.all().order_by('-date', '-time')


class UserQuestionForm(forms.ModelForm):
    class Meta:
        model = FAQItem
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Задайте свой вопрос...'}),
        }
        labels = {
            'question': 'Ваш вопрос',
        }

# med_loupemed/core/forms.py

from django import forms
from .models import Review, Doctor

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
    email = forms.EmailField(required=False, label="Ваш Email") # Сделал email необязательным, если телефон есть
    phone_number = forms.CharField(max_length=20, required=False, label="Ваш телефон", help_text="Мы свяжемся с вами по телефону или email.") # Новое поле
    message = forms.CharField(widget=forms.Textarea, label="Ваше сообщение")

    # Добавим кастомную валидацию, чтобы требовать хотя бы email или телефон
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        if not email and not phone_number:
            raise forms.ValidationError(
                "Пожалуйста, укажите хотя бы свой Email или номер телефона для связи."
            )
        return cleaned_data
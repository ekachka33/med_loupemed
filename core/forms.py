from django import forms
from .models import Review, Doctor

class ReviewForm(forms.ModelForm):
    # Переопределяем поле doctor, чтобы оно было необязательным для общего отзыва
    # и использовало ChoiceField для выбора врача из списка.
    # Это также пригодится для формы на doctor_detail.html
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_active=True).order_by('full_name'),
        required=False, # Сделать поле необязательным
        empty_label="Выберите врача (необязательно)", # Текст для пустого значения
        label="Врач"
    )
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput() # Будем использовать JS для красивого отображения звезд
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
            # 'doctor' уже задан выше
        }
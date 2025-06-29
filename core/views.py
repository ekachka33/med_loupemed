from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import AboutUsPage, ContactInfo, Doctor, Review, ServiceCategory, Service, ServicePriceItem
from .forms import ReviewForm, ContactForm
from django.conf import settings
from django.core.mail import send_mail
def home(request):
    """
    Представление для главной страницы.
    Отображает шаблон home.html.
    """
    about_us_page = AboutUsPage.objects.last()
    contact_form = ContactForm()
    context = {
        'about_us_page': about_us_page,
        'contact_form': contact_form,

    }

    return render(request, 'core/home.html', context)

def about_us_view(request):
    """Представление для страницы 'О клинике'."""
    about_us_page = AboutUsPage.objects.first()
    doctors = Doctor.objects.filter(is_active=True).order_by('name')
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')

    form = ReviewForm()
    contact_form = ContactForm()

    context = {
        'about_us_page': about_us_page,
        'doctors': doctors,
        'reviews': reviews,
        'form': form,
        'contact_form': contact_form,
    }
    return render(request, 'about.html', context)

def doctor_detail_view(request, pk):
    """Представление для детальной страницы врача."""
    doctor = get_object_or_404(Doctor, pk=pk)
    # Получаем только одобренные отзывы, связанные с этим врачом
    reviews = doctor.reviews.filter(is_approved=True).order_by('-created_at')
    contact_form = ContactForm()
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'contact_form': contact_form,
    }
    return render(request, 'doctor_detail.html', context)

@require_POST
def submit_review(request):
    """Представление для обработки отправки отзыва."""
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False
            review.save()
            return JsonResponse({'success': True, 'message': 'Спасибо за ваш отзыв! Он будет опубликован после модерации.'})
        else:
            # Если форма невалидна, возвращаем ошибки
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Недопустимый запрос.'}, status=400)


def service_list(request):
    categories = ServiceCategory.objects.all()
    # Получаем все активные услуги
    services = Service.objects.filter(is_active=True).order_by('name')

    # Логика для фильтрации по категории, если нужен
    category_slug = request.GET.get('category')
    if category_slug:
        services = services.filter(category__slug=category_slug)
        selected_category = get_object_or_404(ServiceCategory, slug=category_slug)
    else:
        selected_category = None
    contact_form = ContactForm()
    context = {
        'categories': categories,
        'services': services,
        'selected_category': selected_category,
        'contact_form': contact_form,
    }
    return render(request, 'services_list.html', context)

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    # Получаем пункты прайс-листа, связанные с этой услугой
    price_items = service.price_items.all().order_by('order')
    contact_form = ContactForm()

    context = {
        'service': service,
        'price_items': price_items,
        'contact_form': contact_form,
    }
    return render(request, 'service_detail.html', context)


def contact_page(request):
    contact_info = ContactInfo.objects.first()
    form = ContactForm() # Создаем экземпляр формы обратной связи

    context = {
        'contact_info': contact_info,
        'form': form,
    }
    return render(request, 'contact.html', context)



@require_POST
def submit_feedback(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        user_email = form.cleaned_data.get('email') # Email, который оставил пользователь
        phone_number = form.cleaned_data.get('phone_number', 'Не указан')
        message = form.cleaned_data['message']

        # 1. Отправка письма администратору
        admin_subject = f"Новое сообщение с сайта от {name}"
        admin_body = (
            f"Имя: {name}\n"
            f"Email: {user_email if user_email else 'Не указан'}\n"
            f"Телефон: {phone_number}\n\n"
            f"Сообщение:\n{message}"
        )
        try:
            send_mail(
                admin_subject,
                admin_body,
                settings.DEFAULT_FROM_EMAIL, # От кого (почта сайта из settings)
                [settings.CONTACT_FORM_RECIPIENT_EMAIL], # Кому (почта администратора из settings)
                fail_silently=False, # Если True, ошибки отправки будут игнорироваться
            )
        except Exception as e:
            print(f"Ошибка отправки email администратору: {e}") # Для дебага
            return JsonResponse({'success': False, 'message': 'Произошла ошибка при отправке сообщения администратору. Пожалуйста, попробуйте позже.'}, status=500)

        # 2. Отправка письма пользователю (если он указал email)
        if user_email and user_email != 'Не указан':
            user_subject = "Ваше сообщение успешно получено!"
            user_body = (
                f"Здравствуйте, {name}!\n\n"
                f"Благодарим вас за обращение. Мы получили ваше сообщение:\n"
                f"\"{message}\"\n\n"
                f"Мы свяжемся с вами в ближайшее время.\n\n"
                f"С уважением,\n"
                f"Медицинская Клиника LOUPMED"
            )
            try:
                send_mail(
                    user_subject,
                    user_body,
                    settings.DEFAULT_FROM_EMAIL, # От кого (почта сайта)
                    [user_email], # Кому (email пользователя)
                    fail_silently=False, # Ошибки отправки пользователю могут быть менее критичны
                )
            except Exception as e:
                print(f"Ошибка отправки email пользователю: {e}")
                pass # Не прерываем ответ, если ошибка только у пользователя

        return JsonResponse({'success': True, 'message': 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'})
    else:
        # Если форма невалидна, возвращаем ошибки валидации
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required # Этот декоратор требует, чтобы пользователь был авторизован
def profile_view(request):
    user = request.user
    is_doctor = False
    doctor_profile = None

    try:
        doctor_profile = Doctor.objects.get(user=user)
        is_doctor = True
    except Doctor.DoesNotExist:
        pass # Это обычный пользователь

    context = {
        'user': user,
        'is_doctor': is_doctor,
        'doctor_profile': doctor_profile,
        'title': 'Личный кабинет',
    }
    return render(request, 'core/profile.html', context)

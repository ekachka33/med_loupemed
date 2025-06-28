from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import AboutUsPage, ContactInfo, Doctor, Review, ServiceCategory, Service, ServicePriceItem
from .forms import ReviewForm
def home(request):
    """
    Представление для главной страницы.
    Отображает шаблон home.html.
    """
    about_us_page = AboutUsPage.objects.last()
    context = {
        'about_us_page': about_us_page,

    }

    return render(request, 'core/home.html', context)

def about_us_view(request):
    """Представление для страницы 'О клинике'."""
    about_us_page = AboutUsPage.objects.first()
    doctors = Doctor.objects.filter(is_active=True).order_by('full_name')
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')

    # Создаем пустую форму для отзыва (GET запрос)
    form = ReviewForm()

    context = {
        'about_us_page': about_us_page,
        'doctors': doctors,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'about.html', context)

def doctor_detail_view(request, pk): # pk - это первичный ключ врача
    """Представление для детальной страницы врача."""
    doctor = get_object_or_404(Doctor, pk=pk)
    # Получаем только одобренные отзывы, связанные с этим врачом
    reviews = doctor.reviews.filter(is_approved=True).order_by('-created_at')

    context = {
        'doctor': doctor,
        'reviews': reviews,
    }
    return render(request, 'doctor_detail.html', context)

@require_POST
def submit_review(request):
    """Представление для обработки отправки отзыва."""
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest': # Проверяем, что это AJAX запрос
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            # Поле is_approved по умолчанию False, так что модерация нужна
            review.is_approved = False # Убеждаемся, что отзыв не публикуется сразу
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

    context = {
        'categories': categories,
        'services': services,
        'selected_category': selected_category,
    }
    return render(request, 'services_list.html', context)

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    # Получаем пункты прайс-листа, связанные с этой услугой
    price_items = service.price_items.all().order_by('order')

    context = {
        'service': service,
        'price_items': price_items,
    }
    return render(request, 'service_detail.html', context)

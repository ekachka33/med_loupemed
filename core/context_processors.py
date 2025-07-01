from .models import ContactInfo


def contact_info(request):
    """
    Добавляет объект ContactInfo в контекст шаблона.
    Берет последнюю активную запись.
    """
    try:
        info = ContactInfo.objects.filter(is_active=True).latest('created_at')
    except ContactInfo.DoesNotExist:
        info = None
    return {'contact_info': info}
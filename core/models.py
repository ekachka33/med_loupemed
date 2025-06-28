from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class ContactRequest(models.Model):
    """
    Модель для хранения запросов обратной связи (как "Обратный звонок", так и "Задать вопрос").
    """
    full_name = models.CharField(max_length=255, verbose_name="Фамилия Имя Отчество")
    email = models.EmailField(verbose_name="Электронная почта", blank=True, null=True)
    phone_number = models.CharField(max_length=20, verbose_name="Контактный номер телефона", blank=True, null=True)
    message = models.TextField(verbose_name="Сообщение / Комментарий к звонку", blank=True, null=True)
    request_type = models.CharField(
        max_length=50,
        choices=[('question', 'Задать вопрос'), ('callback', 'Обратный звонок')],
        verbose_name="Тип запроса"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    class Meta:
        verbose_name = "Запрос обратной связи"
        verbose_name_plural = "Запросы обратной связи"
        ordering = ['-created_at']

    def __str__(self):
        return f"Запрос от {self.full_name} ({self.request_type}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AboutUsPage(models.Model):
    """
    Модель для хранения информации страницы "О компании".
    Предполагается, что будет только одна запись этой модели.
    """
    title = models.CharField(max_length=255, verbose_name="Заголовок страницы")
    content = models.TextField(verbose_name="Содержимое страницы")
    image = models.ImageField(upload_to='about_us/', blank=True, null=True, verbose_name="Изображение для страницы")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name = "Страница 'О компании'"
        verbose_name_plural = "Страница 'О компании'"

    def __str__(self):
        return self.title

class ContactInfo(models.Model):
    """
    Модель для хранения контактной информации компании.
    Предполагается, что будет только одна запись этой модели.
    """
    name = models.CharField(max_length=200, verbose_name="Название клиники", default="Медицинская Клиника") # Добавлено
    short_description = models.TextField(blank=True, verbose_name="Краткое описание/Миссия") # Добавлено

    address = models.CharField(max_length=255, verbose_name="Адрес")
    phone_number_main = models.CharField(max_length=20, verbose_name="Основной номер телефона")
    phone_number_alt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Дополнительный номер телефона")
    email_main = models.EmailField(verbose_name="Основной Email")
    email_alt = models.EmailField(blank=True, null=True, verbose_name="Дополнительный Email")
    work_hours = models.CharField(max_length=255, verbose_name="Часы работы", help_text="ПН-ПТ 9:00-18:00")
    map_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на карту (Google Maps/Yandex Maps)")
    facebook_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на Facebook")
    instagram_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на Instagram")
    is_active = models.BooleanField(default=True, verbose_name="Активная запись")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"
        ordering = ['-created_at']

    def __str__(self):
        # Используем название клиники, если оно есть, иначе дефолтное
        return self.name or "Контактная информация компании"


class Doctor(models.Model):
    """
    Модель для хранения информации о врачах.
    """
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    specialty = models.CharField(max_length=100, verbose_name="Специализация")
    bio = models.TextField(blank=True, verbose_name="Биография")
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True, verbose_name="Фотография")
    experience_years = models.IntegerField(default=0, verbose_name="Опыт работы (лет)")
    education = models.TextField(blank=True, verbose_name="Образование")
    is_active = models.BooleanField(default=True, verbose_name="Активный врач")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.specialty})"



class Review(models.Model):
    """
    Модель для хранения отзывов о клинике или врачах.
    """
    full_name = models.CharField(max_length=255, verbose_name="Имя клиента")
    email = models.EmailField(blank=True, null=True, verbose_name="Email (необязательно)")
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5,
        verbose_name="Оценка (от 1 до 5)"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name="Врач (если отзыв о конкретном враче)"
    )
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен (для публикации)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.full_name} на {self.rating} звезд (Врач: {self.doctor.full_name if self.doctor else 'Общий'})"


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, blank=True,
                            help_text="URL-псевдоним, генерируется автоматически из названия.")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения",
                                help_text="Чем меньше число, тем выше категория в списке.")

    class Meta:
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Добавляем механизм уникальности для slug, если имя не уникально
            original_slug = self.slug
            count = 1
            while ServiceCategory.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='services',
                                 verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    slug = models.SlugField(max_length=200, unique=True, blank=True,
                            help_text="URL-псевдоним, генерируется автоматически из названия.")
    short_description = models.TextField(verbose_name="Краткое описание (для списка)",
                                         help_text="Короткое описание услуги, до 200 символов.")
    full_description = models.TextField(verbose_name="Полное описание (для детальной страницы)")

    # Можно использовать DecimalField для цен, так как это точнее, чем FloatField
    # Можно оставить price, если цена всегда одна, или использовать min/max для диапазона
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     verbose_name="Базовая цена",
                                     help_text="Оставьте пустым, если цена варьируется (см. пункты прайс-листа).")

    is_active = models.BooleanField(default=True, verbose_name="Активна")
    image = models.ImageField(upload_to='service_images/', blank=True, null=True,
                              verbose_name="Изображение услуги")

    # Связь с моделью Doctor (предполагаем, что Doctor уже существует)
    doctors = models.ManyToManyField('Doctor', blank=True, related_name='services',
                                     verbose_name="Врачи, предоставляющие услугу")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            count = 1
            while Service.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServicePriceItem(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='price_items',
                                verbose_name="Услуга")
    item_name = models.CharField(max_length=200, verbose_name="Наименование пункта прайса")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    unit = models.CharField(max_length=50, blank=True, verbose_name="Единица измерения (например, 'за сеанс')")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Пункт прайс-листа услуги"
        verbose_name_plural = "Пункты прайс-листа услуг"
        ordering = ['order', 'item_name']
        unique_together = (
        'service', 'item_name')  # Чтобы в рамках одной услуги не было двух одинаковых названий пунктов

    def __str__(self):
        return f"{self.service.name} - {self.item_name}"
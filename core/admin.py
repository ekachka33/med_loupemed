from django.contrib import admin
from .models import ContactRequest, AboutUsPage, ContactInfo, Doctor, Review, ServiceCategory, Service, ServicePriceItem

# Регистрация модели ContactRequest
@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'request_type', 'created_at', 'is_processed')
    list_filter = ('request_type', 'is_processed', 'created_at')
    search_fields = ('full_name', 'email', 'phone_number', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)
    mark_as_processed.short_description = "Отметить выбранные запросы как обработанные"


# Регистрация модели AboutUsPage
@admin.register(AboutUsPage)
class AboutUsPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_updated')


# Регистрация модели ContactInfo
@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number_main', 'email_main', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'phone_number_main', 'email_main')
    fieldsets = (
        (None, {
            'fields': ('name', 'short_description', 'is_active')
        }),
        ('Контактные данные', {
            'fields': ('address', 'phone_number_main', 'phone_number_alt', 'email_main', 'email_alt', 'work_hours')
        }),
        ('Социальные сети и карта', {
            'fields': ('map_link', 'facebook_link', 'instagram_link')
        }),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialty', 'experience_years', 'is_active', 'user', 'updated_at')
    list_filter = ('specialty', 'is_active')
    search_fields = ('name', 'specialty', 'bio', 'user__username')
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {
            'fields': ('name', 'specialty', 'photo', 'is_active')
        }),
        ('Пользовательский аккаунт', { # <-- НОВАЯ ГРУППА ДЛЯ ПОЛЯ USER
            'fields': ('user',),
            'description': 'Привяжите профиль врача к аккаунту пользователя, если этот врач будет входить в систему.'
        }),
        ('Подробная информация', {
            'fields': ('bio', 'experience_years', 'education')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'doctor', 'rating', 'is_approved', 'created_at')
    list_filter = ('doctor', 'is_approved', 'rating')
    search_fields = ('full_name', 'text', 'name')
    readonly_fields = ('created_at',)
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Отклонить выбранные отзывы"


# Inline для ServicePriceItem, чтобы добавлять цены прямо на странице Service
class ServicePriceItemInline(admin.TabularInline):
    model = ServicePriceItem
    extra = 1 # Количество пустых форм для добавления новых пунктов
    fields = ('item_name', 'price', 'unit', 'order')

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Автоматическое заполнение slug
    search_fields = ('name', 'description')
    list_editable = ('order',) # Позволяет редактировать порядок прямо в списке

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'doctors') # Фильтрация по категории, активности и врачам
    search_fields = ('name', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('doctors',) # Удобный виджет для выбора нескольких врачей
    inlines = [ServicePriceItemInline] # Добавляем inline для пунктов прайс-листа
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'image', 'is_active')
        }),
        ('Описание', {
            'fields': ('short_description', 'full_description')
        }),
        ('Цены', {
            'fields': ('base_price',)
        }),
        ('Связи', {
            'fields': ('doctors',)
        }),
    )
# Register your models here.
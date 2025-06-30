from datetime import timedelta

from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django import forms
from .models import (
    ContactRequest, AboutUsPage, ContactInfo, Doctor, Review,
    ServiceCategory, Service, ServicePriceItem,
    Appointment, DoctorSchedule,
)

from .forms import AppointmentAdminForm, DoctorScheduleAdminForm
from .admin_forms import GenerateScheduleForm

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
        ('Пользовательский аккаунт', {
            'fields': ('user',),
            'description': 'Привяжите профиль врача к аккаунту пользователя, если этот врач будет входить в систему.'
        }),
        ('Подробная информация', {
            'fields': ('bio', 'experience_years', 'education')
        }),
        ('Стандартное расписание', {
            'fields': ('default_start_time', 'default_end_time', 'default_interval_minutes'),
            'description': 'Настройте часы работы по умолчанию для этого врача. '
                           'Будет использоваться для автоматической генерации расписания.'
        }),
    )



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'doctor', 'rating', 'text', 'is_approved', 'created_at')
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
    extra = 1
    fields = ('item_name', 'price', 'unit', 'order')

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_editable = ('order',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'doctors')
    search_fields = ('name', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('doctors',)
    inlines = [ServicePriceItemInline]
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


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentAdminForm
    list_display = ('user', 'doctor', 'service', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date', 'doctor', 'service')
    search_fields = ('user__username', 'doctor__name', 'service__name')
    raw_id_fields = ('user', 'doctor', 'service')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']



    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Отметить как подтвержденные"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Отметить как завершенные"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = "Отметить как отмененные"



@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    form = DoctorScheduleAdminForm  # Оставляем, если вы используете кастомную форму для редактирования записей расписания.
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'interval_minutes')  # Добавил interval_minutes
    list_filter = ('doctor', 'date')
    search_fields = ('doctor__name',)
    date_hierarchy = 'date'
    raw_id_fields = ('doctor',)

    # 1. Добавляем URL-путь для нашей страницы генерации
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('generate-schedule/', self.admin_site.admin_view(self.generate_schedule_view),
                 name='core_doctorschedule_generate_schedule'),
        ]
        return my_urls + urls

    # 2. Представление для обработки страницы генерации
    def generate_schedule_view(self, request):
        if request.method == 'POST':
            form = GenerateScheduleForm(request.POST)  # Используем нашу новую форму
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                selected_doctors = form.cleaned_data['doctors']

                if selected_doctors:
                    doctors_to_process = selected_doctors
                else:
                    doctors_to_process = Doctor.objects.filter(
                        is_active=True,
                        default_start_time__isnull=False,
                        default_end_time__isnull=False,
                        default_interval_minutes__gt=0
                    )

                generated_count = 0
                for doctor in doctors_to_process:
                    if not doctor.default_start_time or not doctor.default_end_time or doctor.default_interval_minutes <= 0:
                        if not selected_doctors:
                            continue
                        else:
                            messages.warning(request,
                                             f"Врач {doctor.name} не имеет настроенных стандартных часов работы. Расписание для него не сгенерировано.")
                            continue

                    current_date = start_date
                    while current_date <= end_date:
                        if not DoctorSchedule.objects.filter(doctor=doctor, date=current_date).exists():
                            try:
                                DoctorSchedule.objects.create(
                                    doctor=doctor,
                                    date=current_date,
                                    start_time=doctor.default_start_time,
                                    end_time=doctor.default_end_time,
                                    interval_minutes=doctor.default_interval_minutes
                                )
                                generated_count += 1
                            except Exception as e:
                                messages.error(request,
                                               f"Ошибка при генерации расписания для {doctor.name} на {current_date}: {e}")
                        current_date += timedelta(days=1)

                messages.success(request, f"Успешно сгенерировано {generated_count} записей расписания.")
                return redirect('admin:core_doctorschedule_changelist')
        else:
            form = GenerateScheduleForm()

        context = self.admin_site.each_context(request)
        context['form'] = form
        context['title'] = "Генерация расписания"
        return render(request, 'admin/generate_schedule.html', context)

    # 3. Добавляем ссылку на страницу генерации на странице списка DoctorSchedule
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['generate_schedule_url'] = reverse('admin:core_doctorschedule_generate_schedule')
        return super().changelist_view(request, extra_context=extra_context)

# Register your models here.
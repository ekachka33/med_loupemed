import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST

from .forms import (
    ContactForm,
    MedicalRecordUploadForm,
    ReviewForm,
    UserAppointmentForm,
    UserQuestionForm,
)
from .models import (
    AboutUsPage,
    Appointment,
    ContactInfo,
    ContactRequest,
    Doctor,
    DoctorSchedule,
    FAQItem,
    Review,
    Service,
    ServiceCategory,
)


def home(request):
    """
    Представление для главной страницы.
    Отображает шаблон home.html.
    """
    about_us_page = AboutUsPage.objects.last()
    contact_form = ContactForm()
    context = {
        "about_us_page": about_us_page,
        "contact_form": contact_form,
    }
    return render(request, "core/home.html", context)


def about_us_view(request):
    """Представление для страницы 'О клинике'."""
    about_us_page = AboutUsPage.objects.first()
    doctors = Doctor.objects.filter(is_active=True).order_by("name")
    reviews = Review.objects.filter(is_approved=True).order_by("-created_at")

    form = ReviewForm()
    contact_form = ContactForm()

    context = {
        "about_us_page": about_us_page,
        "doctors": doctors,
        "reviews": reviews,
        "form": form,
        "contact_form": contact_form,
    }
    return render(request, "about.html", context)


def doctor_detail_view(request, pk):
    """Представление для детальной страницы врача."""
    doctor = get_object_or_404(Doctor, pk=pk)
    # Получаем только одобренные отзывы, связанные с этим врачом
    reviews = doctor.reviews.filter(is_approved=True).order_by("-created_at")
    contact_form = ContactForm()
    context = {
        "doctor": doctor,
        "reviews": reviews,
        "contact_form": contact_form,
    }
    return render(request, "doctor_detail.html", context)


@require_POST
def submit_review(request):
    """Представление для обработки отправки отзыва."""
    if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False
            review.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "Спасибо за ваш отзыв! Он будет опубликован после модерации.",
                }
            )
        else:
            # Если форма невалидна, возвращаем ошибки
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return JsonResponse(
        {"success": False, "message": "Недопустимый запрос."}, status=400
    )


def service_list(request):
    categories = ServiceCategory.objects.all()
    services = Service.objects.filter(is_active=True).order_by("name")
    category_slug = request.GET.get("category")
    if category_slug:
        services = services.filter(category__slug=category_slug)
        selected_category = get_object_or_404(ServiceCategory, slug=category_slug)
    else:
        selected_category = None
    contact_form = ContactForm()
    context = {
        "categories": categories,
        "services": services,
        "selected_category": selected_category,
        "contact_form": contact_form,
    }
    return render(request, "services_list.html", context)


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    price_items = service.price_items.all().order_by("order")
    contact_form = ContactForm()

    context = {
        "service": service,
        "price_items": price_items,
        "contact_form": contact_form,
    }
    return render(request, "service_detail.html", context)


def contact_page(request):
    contact_info = ContactInfo.objects.first()
    form = ContactForm()

    context = {
        "contact_info": contact_info,
        "form": form,
    }
    return render(request, "contact.html", context)


@require_POST
def submit_feedback(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data["name"]
        user_email = form.cleaned_data.get("email")
        phone_number = form.cleaned_data.get("phone_number", "")
        message = form.cleaned_data["message"]

        request_type = "Сообщение с сайта"
        if phone_number:
            request_type = "Обратный звонок"

        try:
            ContactRequest.objects.create(
                full_name=name,
                email=user_email,
                phone_number=phone_number,
                message=message,
                request_type=request_type,
            )
        except Exception as e:
            print(f"Ошибка сохранения запроса обратной связи в БД: {e}")
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Произошла ошибка при сохранении вашего запроса. "
                        "Пожалуйста, попробуйте позже."
                    ),
                },
                status=500,
            )

        admin_subject = f"Новое сообщение с сайта от {name} (Тип: {request_type})"
        admin_body = (
            f"Имя: {name}\n"
            f"Email: {user_email if user_email else 'Не указан'}\n"
            f"Телефон: {phone_number if phone_number else 'Не указан'}\n\n"
            f"Сообщение:\n{message}"
        )
        try:
            send_mail(
                admin_subject,
                admin_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_FORM_RECIPIENT_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки email администратору: {e}")
            return JsonResponse(
                {
                    "success": True,
                    "message": (
                        "Ваш запрос успешно отправлен! "
                        "(Произошла ошибка при отправке уведомления на почту администратора)"
                    ),
                }
            )

        if user_email:
            user_subject = "Ваше сообщение успешно получено!"
            user_body = (
                f"Здравствуйте, {name}!\n\n"
                f"Благодарим вас за обращение. Мы получили ваше сообщение:\n"
                f'"{message}"\n\n'
                f"Мы свяжемся с вами в ближайшее время.\n\n"
                f"С уважением,\n"
                f"Медицинская Клиника LOUPMED"
            )
            try:
                send_mail(
                    user_subject,
                    user_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Ошибка отправки email пользователю: {e}")
                pass

        return JsonResponse(
            {
                "success": True,
                "message": (
                    "Ваше сообщение успешно отправлено! "
                    "Мы свяжемся с вами в ближайшее время."
                ),
            }
        )
    else:
        errors = form.errors.as_json()
        return JsonResponse({"success": False, "errors": errors}, status=400)


@login_required
def profile_view(request):
    user = request.user
    is_doctor = False
    doctor_profile = None

    try:
        doctor_profile = Doctor.objects.get(user=user)
        is_doctor = True
    except Doctor.DoesNotExist:
        pass

    context = {
        "user": user,
        "is_doctor": is_doctor,
        "doctor_profile": doctor_profile,
        "title": "Личный кабинет",
    }

    return render(request, "core/profile.html", context)


class MakeAppointmentView(LoginRequiredMixin, View):
    template_name = "core/make_appointment.html"
    login_url = "/accounts/login/"

    def get(self, request, *args, **kwargs):
        form = UserAppointmentForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.status = "pending"
            appointment.save()
            messages.success(
                request, "Ваша запись успешно создана! Ожидайте подтверждения."
            )
            return redirect("core:home")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
            return render(request, self.template_name, {"form": form})


class GetAvailableTimeSlotsView(View):
    def get(self, request, *args, **kwargs):
        doctor_id = request.GET.get("doctor_id")
        date_str = request.GET.get("date")
        service_id = request.GET.get("service_id")

        if not doctor_id or not date_str or not service_id:
            return JsonResponse(
                {"error": "Missing parameters (doctor_id, date, service_id needed)"},
                status=400,
            )

        try:
            doctor = get_object_or_404(Doctor, id=doctor_id)
            selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            service = get_object_or_404(Service, id=service_id)
            service_duration = service.duration_minutes
            if service_duration is None:
                service_duration = 30
        except Exception as e:
            return JsonResponse({"error": f"Invalid input: {e}"}, status=400)

        current_datetime = timezone.now()
        if selected_date < current_datetime.date():
            return JsonResponse(
                {"error": "Cannot book an appointment in the past"}, status=400
            )

        schedule = DoctorSchedule.objects.filter(
            doctor=doctor, date=selected_date
        ).first()

        available_slots = []

        if schedule:
            start_time_obj = schedule.start_time
            end_time_obj = schedule.end_time
            interval = schedule.interval_minutes

            if not (
                isinstance(start_time_obj, datetime.time)
                and isinstance(end_time_obj, datetime.time)
                and start_time_obj < end_time_obj
                and interval >= 5
            ):
                return JsonResponse(
                    {"error": "Invalid schedule configuration for doctor on this date"},
                    status=400,
                )

            booked_appointments = Appointment.objects.filter(
                doctor=doctor, date=selected_date, status__in=["pending", "confirmed"]
            ).select_related("service")

            booked_intervals = []
            for appt in booked_appointments:
                appt_service_duration = (
                    appt.service.duration_minutes
                    if appt.service and appt.service.duration_minutes is not None
                    else 30
                )
                start_dt = datetime.datetime.combine(selected_date, appt.time)
                end_dt = start_dt + datetime.timedelta(minutes=appt_service_duration)
                booked_intervals.append((start_dt, end_dt))

            current_slot_dt = datetime.datetime.combine(selected_date, start_time_obj)
            end_schedule_dt = datetime.datetime.combine(selected_date, end_time_obj)

            while (
                current_slot_dt + datetime.timedelta(minutes=service_duration)
                <= end_schedule_dt
            ):
                slot_end_dt = current_slot_dt + datetime.timedelta(
                    minutes=service_duration
                )
                is_booked = False

                for booked_start, booked_end in booked_intervals:
                    if current_slot_dt < booked_end and slot_end_dt > booked_start:
                        is_booked = True
                        break

                if (
                    selected_date == current_datetime.date()
                    and current_slot_dt < current_datetime
                ):
                    is_booked = True

                if not is_booked:
                    available_slots.append(current_slot_dt.strftime("%H:%M"))

                current_slot_dt += datetime.timedelta(minutes=interval)

        return JsonResponse({"available_slots": available_slots})


class DoctorScheduleView(LoginRequiredMixin, View):
    template_name = "core/doctor_schedule.html"
    login_url = "/accounts/login/"

    def get(self, request, *args, **kwargs):
        # Проверяем, что пользователь является доктором
        if not hasattr(request.user, "doctor_profile"):
            messages.error(
                request,
                "У вас нет доступа к расписанию врачей. Вы не привязаны к профилю доктора.",
            )
            return redirect("core:profile")

        doctor = request.user.doctor_profile
        today = timezone.now().date()

        today_appointments = Appointment.objects.filter(
            doctor=doctor, date=today, status__in=["pending", "confirmed"]
        ).order_by("time")

        context = {
            "doctor": doctor,
            "today_appointments": today_appointments,
            "title": f"Расписание и записи {doctor.name}",
        }
        return render(request, self.template_name, context)


def get_services_for_doctor(request):
    doctor_id = request.GET.get("doctor_id")
    services_data = []
    if doctor_id:
        try:
            doctor = get_object_or_404(Doctor, id=doctor_id)

            for service in doctor.services.filter(is_active=True).order_by("name"):
                services_data.append({"id": service.id, "name": service.name})
        except Exception:
            pass
    return JsonResponse(services_data, safe=False)


class UserAppointmentsView(LoginRequiredMixin, View):
    """
    Представление для отображения предстоящих и прошедших записей авторизованного пользователя.
    """

    template_name = "core/my_appointments.html"
    login_url = "/accounts/login/"

    def get(self, request, *args, **kwargs):
        user = request.user
        current_datetime = timezone.now()

        all_appointments = Appointment.objects.filter(user=user).order_by(
            "date", "time"
        )

        upcoming_appointments = []
        past_appointments = []

        for appt in all_appointments:
            naive_appointment_datetime = datetime.datetime.combine(appt.date, appt.time)
            appointment_datetime = timezone.make_aware(naive_appointment_datetime)

            if appointment_datetime >= current_datetime:
                upcoming_appointments.append(appt)
            else:
                past_appointments.append(appt)

        context = {
            "upcoming_appointments": upcoming_appointments,
            "past_appointments": past_appointments,
            "title": "Мои записи",
        }
        return render(request, self.template_name, context)


def is_doctor(user):
    return hasattr(user, "doctor_profile") and user.doctor_profile.is_active


@login_required
@user_passes_test(is_doctor)
def doctor_panel(request):
    doctor = request.user.doctor_profile
    all_appointments = Appointment.objects.filter(doctor=doctor).order_by(
        "-date", "-time"
    )

    if request.method == "POST":
        form = MedicalRecordUploadForm(request.POST, request.FILES, doctor=doctor)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.uploaded_by_doctor = request.user

            medical_record.save()
            messages.success(request, "Результат анализов успешно добавлен!")
            return redirect("core:doctor_panel")
        else:
            messages.error(
                request,
                "Ошибка при добавлении результата анализов. Проверьте введенные данные.",
            )
    else:
        form = MedicalRecordUploadForm(doctor=doctor)

    appointments_with_records = all_appointments.select_related("medical_record")

    context = {
        "title": "Панель врача",
        "doctor": doctor,
        "all_appointments": appointments_with_records,
        "form": form,
    }
    return render(request, "core/doctor_panel.html", context)


def faq_page(request):
    published_faq_items = FAQItem.objects.filter(is_published=True).order_by(
        "created_at"
    )
    form = UserQuestionForm()

    context = {
        "title": "Вопросы и Ответы",
        "faq_items": published_faq_items,
        "question_form": form,
    }
    return render(request, "core/faq.html", context)


@require_POST
def submit_question(request):
    form = UserQuestionForm(request.POST)
    if form.is_valid():
        faq_item = form.save(commit=False)
        faq_item.save()
        return JsonResponse(
            {
                "success": True,
                "message": (
                    "Ваш вопрос успешно отправлен! "
                    "Мы ответим на него в ближайшее время."
                ),
            }
        )
    else:
        errors = form.errors.as_json()
        return JsonResponse({"success": False, "errors": errors}, status=400)

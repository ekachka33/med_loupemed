# your_app/tests/test_forms.py
import os
from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# Импортируем формы
from core.forms import (
    AppointmentAdminForm,
    ContactForm,
    DoctorScheduleAdminForm,
    MedicalRecordUploadForm,
    ReviewForm,
    UserAppointmentForm,
    UserQuestionForm,
)

# Импортируем модели, которые будут использоваться
from core.models import Appointment, Doctor, DoctorSchedule, MedicalRecord, Service

User = get_user_model()


class ReviewFormTest(TestCase):

    def setUp(self):
        self.doctor = Doctor.objects.create(
            name="Др. Иван Петров", specialty="Терапевт", is_active=True
        )

    def test_review_form_valid_data_with_doctor(self):
        """
        Проверяет, что ReviewForm валидна с корректными данными, включая врача.
        """
        form_data = {
            "full_name": "Тестовое Имя",
            "email": "test@example.com",
            "rating": 4,
            "text": "Это отличный отзыв!",
            "doctor": self.doctor.id,
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        review = form.save()
        self.assertEqual(review.full_name, "Тестовое Имя")
        self.assertEqual(review.email, "test@example.com")
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.text, "Это отличный отзыв!")
        self.assertEqual(review.doctor, self.doctor)

    def test_review_form_valid_data_without_doctor(self):
        """
        Проверяет, что ReviewForm валидна с корректными данными без указания врача.
        """
        form_data = {
            "full_name": "Тестовое Имя Без Врача",
            "rating": 5,
            "text": "Это общий отзыв о клинике.",
            "email": "",
            "doctor": "",
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        review = form.save()
        self.assertEqual(review.full_name, "Тестовое Имя Без Врача")
        self.assertIsNone(review.email)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "Это общий отзыв о клинике.")
        self.assertIsNone(review.doctor)

    def test_review_form_missing_required_fields(self):
        """
        Проверяет, что ReviewForm невалидна при отсутствии обязательных полей.
        """
        form_data = {
            "email": "test@example.com",
            "rating": 3,
            "text": "Отзыв без имени.",
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)
        self.assertNotIn("text", form.errors)
        self.assertNotIn("rating", form.errors)

    def test_review_form_inactive_doctor_not_in_queryset(self):
        """
        Проверяет, что неактивные врачи не появляются в queryset поля doctor.
        """
        inactive_doctor = Doctor.objects.create(
            name="Др. Анна Смирнова", specialty="Хирург", is_active=False
        )
        form = ReviewForm()
        # Проверяем, что неактивного доктора нет в QuerySet поля 'doctor'
        self.assertNotIn(inactive_doctor, form.fields["doctor"].queryset)
        self.assertIn(self.doctor, form.fields["doctor"].queryset)


class ContactFormTest(TestCase):

    def test_contact_form_valid_data_with_email(self):
        """
        Проверяет, что ContactForm валидна с корректными данными (с email).
        """
        form_data = {
            "name": "Иван Иванов",
            "email": "ivan@example.com",
            "phone_number": "",  # Номер телефона может быть пустым
            "message": "Привет, это тестовое сообщение.",
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data["name"], "Иван Иванов")
        self.assertEqual(form.cleaned_data["email"], "ivan@example.com")
        self.assertEqual(form.cleaned_data["phone_number"], "")
        self.assertEqual(
            form.cleaned_data["message"], "Привет, это тестовое сообщение."
        )

    def test_contact_form_valid_data_with_phone(self):
        """
        Проверяет, что ContactForm валидна с корректными данными (с номером телефона).
        """
        form_data = {
            "name": "Мария Петрова",
            "email": "",  # Email может быть пустым
            "phone_number": "89001234567",
            "message": "Хочу записаться на прием.",
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data["name"], "Мария Петрова")
        self.assertEqual(form.cleaned_data["email"], "")
        self.assertEqual(form.cleaned_data["phone_number"], "89001234567")
        self.assertEqual(form.cleaned_data["message"], "Хочу записаться на прием.")

    def test_contact_form_valid_data_with_both_email_and_phone(self):
        """
        Проверяет, что ContactForm валидна с корректными данными (с email и номером телефона).
        """
        form_data = {
            "name": "Алексей Сидоров",
            "email": "alex@example.com",
            "phone_number": "89998887766",
            "message": "Просто проверяю связь.",
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_contact_form_missing_required_fields(self):
        """
        Проверяет, что ContactForm невалидна при отсутствии имени и сообщения.
        """
        form_data = {
            "email": "test@example.com",
            "phone_number": "123",
            "message": "Без имени",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)  # name обязательное

        form_data_no_message = {
            "name": "Тест",
            "email": "test@example.com",
            "phone_number": "123",
        }
        form = ContactForm(data=form_data_no_message)
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)  # message обязательное

    def test_contact_form_no_email_or_phone(self):
        """
        Проверяет, что ContactForm невалидна, если отсутствуют и email, и phone_number.
        """
        form_data = {
            "name": "Тест Без Контакта",
            "email": "",
            "phone_number": "",
            "message": "Привет.",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertIn(
            "Пожалуйста, укажите хотя бы свой Email или номер телефона для связи.",
            form.errors["__all__"][0],
        )

    def test_contact_form_invalid_email(self):
        """
        Проверяет, что ContactForm невалидна с некорректным форматом email.
        """
        form_data = {
            "name": "Тест Email",
            "email": "invalid-email",
            "phone_number": "12345",
            "message": "Сообщение.",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class AppointmentAdminFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="patient", password="password")
        self.doctor = Doctor.objects.create(
            name="Др. Смит", specialty="Окулист", is_active=True
        )
        self.service = Service.objects.create(
            name="Осмотр глаз", base_price=500, duration_minutes=30
        )

    def test_appointment_admin_form_valid_data(self):
        """
        Проверяет, что AppointmentAdminForm валидна с корректными данными.
        """
        form_data = {
            "user": self.user.id,
            "doctor": self.doctor.id,
            "service": self.service.id,
            "date": date.today().isoformat(),  # Используем ISO формат для даты
            "time": "10:00",  # Время в HH:MM
            "status": "pending",
            "comments": "Комментарии администратора",
            "diagnosis_results": "Предварительный диагноз",
        }
        form = AppointmentAdminForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        appointment = form.save()

        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.date, date.today())
        self.assertEqual(appointment.time, time(10, 0))
        self.assertEqual(appointment.status, "pending")
        self.assertEqual(appointment.comments, "Комментарии администратора")
        self.assertEqual(appointment.diagnosis_results, "Предварительный диагноз")

    def test_appointment_admin_form_missing_required_fields(self):
        """
        Проверяет, что AppointmentAdminForm невалидна при отсутствии обязательных полей.
        """
        form_data = {
            "doctor": self.doctor.id,
            "service": self.service.id,
            "date": date.today().isoformat(),
            "time": "10:00",
            "status": "pending",
            # Отсутствует 'user'
        }
        form = AppointmentAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("user", form.errors)


class DoctorScheduleAdminFormTest(TestCase):

    def setUp(self):
        self.doctor = Doctor.objects.create(
            name="Др. Джон Доу", specialty="Педиатр", is_active=True
        )

    def test_doctor_schedule_admin_form_valid_data(self):
        """
        Проверяет, что DoctorScheduleAdminForm валидна с корректными данными.
        """
        form_data = {
            "doctor": self.doctor.id,
            "date": date.today().isoformat(),
            "start_time": "09:00",
            "end_time": "17:00",
            "interval_minutes": 30,
        }
        form = DoctorScheduleAdminForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        schedule = form.save()

        self.assertEqual(schedule.doctor, self.doctor)
        self.assertEqual(schedule.date, date.today())
        self.assertEqual(schedule.start_time, time(9, 0))
        self.assertEqual(schedule.end_time, time(17, 0))
        self.assertEqual(schedule.interval_minutes, 30)

    def test_doctor_schedule_admin_form_missing_required_fields(self):
        """
        Проверяет, что DoctorScheduleAdminForm невалидна при отсутствии обязательных полей.
        """
        form_data = {
            "date": date.today().isoformat(),
            "start_time": "09:00",
            "end_time": "17:00",
            # Отсутствует 'doctor'
        }
        form = DoctorScheduleAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("doctor", form.errors)


class UserAppointmentFormTest(TestCase):

    def setUp(self):
        # Создаем тестовые данные
        self.user = User.objects.create_user(
            username="patient_user", password="password"
        )
        self.doctor1 = Doctor.objects.create(
            name="Др. Елена", specialty="Стоматолог", is_active=True
        )
        self.doctor2 = Doctor.objects.create(
            name="Др. Олег", specialty="Офтальмолог", is_active=False
        )
        self.service1 = Service.objects.create(
            name="Чистка зубов", base_price=1000, duration_minutes=60, is_active=True
        )
        self.service2 = Service.objects.create(
            name="Удаление зуба", base_price=2000, duration_minutes=45, is_active=False
        )

        # Добавляем услуги врачам, если нужно для queryset
        self.doctor1.services.add(self.service1)

        # Создаем расписание для доктора
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor1,
            date=date.today() + timedelta(days=7),  # Расписание на неделю вперед
            start_time=time(9, 0),
            end_time=time(17, 0),
            interval_minutes=30,
        )

    def test_user_appointment_form_initial_queryset(self):
        """
        Проверяет, что поля 'doctor' и 'service' формы содержат только активных врачей и услуги.
        """
        form = UserAppointmentForm()
        # Проверяем, что активный доктор в QuerySet
        self.assertIn(self.doctor1, form.fields["doctor"].queryset)
        # Проверяем, что неактивный доктор НЕ в QuerySet
        self.assertNotIn(self.doctor2, form.fields["doctor"].queryset)

        # Проверяем, что активная услуга в QuerySet
        self.assertIn(self.service1, form.fields["service"].queryset)
        # Проверяем, что неактивная услуга НЕ в QuerySet
        self.assertNotIn(self.service2, form.fields["service"].queryset)

    def test_user_appointment_form_valid_data(self):
        """
        Проверяет, что UserAppointmentForm валидна с корректными данными.
        """
        form_data = {
            "doctor": self.doctor1.id,
            "service": self.service1.id,
            "date": (
                date.today() + timedelta(days=7)
            ).isoformat(),  # Дата из расписания
            "time": "10:30",  # Время, которое попадает в расписание
            "comments": "Нужна консультация",
        }
        form = UserAppointmentForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Проверяем очищенные данные
        self.assertEqual(form.cleaned_data["doctor"], self.doctor1)
        self.assertEqual(form.cleaned_data["service"], self.service1)
        self.assertEqual(form.cleaned_data["date"], (date.today() + timedelta(days=7)))
        self.assertEqual(form.cleaned_data["time"], time(10, 30))
        self.assertEqual(form.cleaned_data["comments"], "Нужна консультация")

    def test_user_appointment_form_missing_required_fields(self):
        """
        Проверяет, что UserAppointmentForm невалидна при отсутствии обязательных полей.
        """
        form_data = {
            # 'doctor': self.doctor1.id, # Отсутствует
            "service": self.service1.id,
            "date": (date.today() + timedelta(days=7)).isoformat(),
            "time": "11:00",
            "comments": "Тест",
        }
        form = UserAppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("doctor", form.errors)

        form_data_no_date = {
            "doctor": self.doctor1.id,
            "service": self.service1.id,
            # 'date': ..., # Отсутствует
            "time": "11:00",
            "comments": "Тест",
        }
        form = UserAppointmentForm(data=form_data_no_date)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_user_appointment_form_no_time_selected(self):
        """
        Проверяет кастомную валидацию: форма должна быть невалидна, если time не выбрано.
        """
        form_data = {
            "doctor": self.doctor1.id,
            "service": self.service1.id,
            "date": (date.today() + timedelta(days=7)).isoformat(),
            "time": "",  # Время не выбрано
            "comments": "Проверка ошибки времени",
        }
        form = UserAppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("time", form.errors)
        self.assertIn(
            "Пожалуйста, выберите доступное время приема.", form.errors["time"]
        )

    def test_user_appointment_form_invalid_date_format(self):
        """
        Проверяет, что форма корректно обрабатывает невалидный формат даты.
        """
        form_data = {
            "doctor": self.doctor1.id,
            "service": self.service1.id,
            "date": "invalid-date",  # Некорректный формат
            "time": "10:00",
            "comments": "Тест",
        }
        form = UserAppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)


class MedicalRecordUploadFormTest(TestCase):

    def setUp(self):
        self.user_patient = User.objects.create_user(
            username="patient_for_record", password="password"
        )
        self.user_doctor_account = User.objects.create_user(
            username="doctor_uploader", password="password"
        )
        self.doctor = Doctor.objects.create(
            user=self.user_doctor_account,
            name="Др. Загрузкин",
            specialty="Лаборант",
            is_active=True,
        )
        self.service = Service.objects.create(
            name="Общий анализ крови", base_price=300, duration_minutes=15
        )

        # Создаем несколько записей на прием для тестирования QuerySet
        self.appointment1 = Appointment.objects.create(
            user=self.user_patient,
            doctor=self.doctor,
            service=self.service,
            date=date.today() - timedelta(days=5),  # Прошлая завершенная запись
            time=time(10, 0),
            status="completed",
        )
        self.appointment2 = Appointment.objects.create(
            user=self.user_patient,
            doctor=self.doctor,
            service=self.service,
            date=date.today()
            + timedelta(days=2),  # Предстоящая запись (статус confirmed)
            time=time(14, 0),
            status="confirmed",
        )
        self.appointment3 = Appointment.objects.create(
            user=self.user_patient,
            doctor=self.doctor,
            service=self.service,
            date=date.today() - timedelta(days=1),  # Прошлая, но еще не завершенная
            time=time(11, 0),
            status="pending",
        )

    def test_medical_record_upload_form_queryset_filtering(self):
        """
        Проверяет, что queryset для поля 'appointment' корректно фильтруется:
        - только записи для конкретного доктора
        - только со статусом 'completed' или 'confirmed'
        - исключаются записи, для которых уже есть MedicalRecord
        """
        MedicalRecord.objects.create(
            appointment=self.appointment1,
            title="Старый анализ",
            file=SimpleUploadedFile("test.txt", b"file_content"),
            uploaded_by_doctor=self.user_doctor_account,
        )

        form = MedicalRecordUploadForm(doctor=self.doctor)
        appointment_queryset = form.fields["appointment"].queryset

        self.assertNotIn(self.appointment1, appointment_queryset)

        self.assertIn(self.appointment2, appointment_queryset)

        self.assertNotIn(self.appointment3, appointment_queryset)

        if appointment_queryset.exists():
            self.assertEqual(appointment_queryset.first(), self.appointment2)

    def test_medical_record_upload_form_valid_data(self):
        """
        Проверяет, что MedicalRecordUploadForm валидна с корректными данными и файлом.
        """
        # Создаем простой тестовый файл
        test_file = SimpleUploadedFile(
            "test_document.pdf", b"This is a test PDF content."
        )

        form_data = {
            "appointment": self.appointment2.id,
            "title": "Результаты обследования",
            "notes": "Предварительные выводы врача.",
        }
        form_files = {"file": test_file}
        form = MedicalRecordUploadForm(
            data=form_data, files=form_files, doctor=self.doctor
        )

        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        medical_record = form.save(commit=False)
        medical_record.uploaded_by_doctor = self.user_doctor_account
        medical_record.save()

        self.assertIsNotNone(medical_record.pk)
        self.assertEqual(medical_record.appointment, self.appointment2)
        self.assertEqual(medical_record.title, "Результаты обследования")
        self.assertEqual(medical_record.notes, "Предварительные выводы врача.")
        self.assertTrue(os.path.exists(medical_record.file.path))
        self.assertEqual(
            os.path.basename(medical_record.file.name), "test_document.pdf"
        )

        # Очистка тестового файла
        medical_record.file.delete(save=False)


class UserQuestionFormTest(TestCase):

    def test_user_question_form_valid_data(self):
        """
        Проверяет, что UserQuestionForm валидна с корректными данными.
        """
        form_data = {
            "question": "Как долго длится прием у терапевта?",
        }
        form = UserQuestionForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        faq_item = form.save(commit=False)

        self.assertEqual(faq_item.question, "Как долго длится прием у терапевта?")
        self.assertIsNone(faq_item.answer)
        self.assertFalse(faq_item.is_published)

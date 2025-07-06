from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models import (
    AboutUsPage,
    Appointment,
    ContactInfo,
    ContactRequest,
    Doctor,
    DoctorSchedule,
    FAQItem,
    MedicalRecord,
    Review,
    Service,
    ServiceCategory,
    ServicePriceItem,
)

# Получаем модель пользователя Django
User = get_user_model()


class ContactRequestModelTest(TestCase):
    """
    Тесты для модели ContactRequest.
    Проверяют создание запроса обратной связи и его строковое представление.
    """

    def test_create_contact_request(self):
        """
        Проверяет, что объект ContactRequest может быть успешно создан
        с обязательными и необязательными полями.
        """
        # Создаем запрос типа 'question'
        question_request = ContactRequest.objects.create(
            full_name="Иванов Иван Иванович",
            email="ivanov@example.com",
            phone_number="+79001234567",
            message="У меня вопрос по услугам.",
            request_type="question",
        )
        self.assertEqual(question_request.full_name, "Иванов Иван Иванович")
        self.assertEqual(question_request.email, "ivanov@example.com")
        self.assertEqual(question_request.phone_number, "+79001234567")
        self.assertEqual(question_request.message, "У меня вопрос по услугам.")
        self.assertEqual(question_request.request_type, "question")
        self.assertFalse(question_request.is_processed)
        self.assertIsNotNone(question_request.created_at)

        # Создаем запрос типа 'callback' с минимальными данными
        callback_request = ContactRequest.objects.create(
            full_name="Петрова Анна Сергеевна",
            request_type="callback",
            phone_number="+79017654321",
        )
        self.assertEqual(callback_request.full_name, "Петрова Анна Сергеевна")
        self.assertIsNone(callback_request.email)  # Проверяем, что email null
        self.assertEqual(callback_request.phone_number, "+79017654321")
        self.assertIsNone(callback_request.message)  # Проверяем, что message null
        self.assertEqual(callback_request.request_type, "callback")
        self.assertFalse(callback_request.is_processed)

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта ContactRequest.
        """
        request = ContactRequest.objects.create(
            full_name="Сидоров Кирилл",
            request_type="question",
            message="Тестовое сообщение.",
        )
        # Убедимся, что формат времени соответствует ожидаемому
        expected_str = (
            f"Запрос от Сидоров Кирилл (question) - "
            f"{request.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        self.assertEqual(str(request), expected_str)

    def test_default_values(self):
        """
        Проверяет, что значения по умолчанию для полей устанавливаются правильно.
        """
        request = ContactRequest.objects.create(
            full_name="Тестовый Пользователь", request_type="callback"
        )
        self.assertFalse(request.is_processed)  # default=False

    def test_ordering(self):
        """
        Проверяет, что объекты ContactRequest сортируются по created_at в убывающем порядке.
        """
        # Создаем несколько запросов с разным временем
        now = timezone.now()
        request1 = ContactRequest.objects.create(
            full_name="Один",
            request_type="question",
            created_at=now - timedelta(days=2),
        )
        request2 = ContactRequest.objects.create(
            full_name="Два", request_type="question", created_at=now - timedelta(days=1)
        )
        request3 = ContactRequest.objects.create(
            full_name="Три", request_type="question", created_at=now
        )

        # Получаем объекты и проверяем порядок
        requests = ContactRequest.objects.all()
        self.assertEqual(list(requests), [request3, request2, request1])


class AboutUsPageModelTest(TestCase):
    """
    Тесты для модели AboutUsPage.
    Проверяют создание страницы "О компании" и ее строковое представление.
    """

    def test_create_about_us_page(self):
        """
        Проверяет, что объект AboutUsPage может быть успешно создан.
        """
        page = AboutUsPage.objects.create(
            title="О нашей клинике",
            content="Подробная информация о нашей миссии и истории.",
        )
        self.assertEqual(page.title, "О нашей клинике")
        self.assertEqual(page.content, "Подробная информация о нашей миссии и истории.")
        self.assertIsNotNone(page.last_updated)
        self.assertIsNone(page.image.name)

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта AboutUsPage.
        """
        page = AboutUsPage.objects.create(
            title="Наша история", content="Рассказ о становлении клиники."
        )
        self.assertEqual(str(page), "Наша история")

    def test_image_upload(self):
        """
        Проверяет возможность добавления изображения.
        Для реального тестирования загрузки файлов требуются дополнительные настройки.
        Здесь мы просто проверяем, что поле image существует.
        """
        page = AboutUsPage.objects.create(
            title="Тест с изображением", content="Контент."
        )
        self.assertIsNone(page.image.name)


class ContactInfoModelTest(TestCase):
    """
    Тесты для модели ContactInfo.
    Проверяют создание контактной информации и ее строковое представление.
    """

    def test_create_contact_info(self):
        """
        Проверяет, что объект ContactInfo может быть успешно создан
        со всеми обязательными и необязательными полями.
        """
        contact = ContactInfo.objects.create(
            name="Медицинский Центр Здоровье",
            short_description="Мы заботимся о вашем здоровье.",
            address="ул. Примерная, 10, г. Город",
            phone_number_main="+74951112233",
            email_main="info@zdorovie.ru",
            work_hours="ПН-ПТ 9:00-18:00, СБ 10:00-15:00",
            map_link="https://maps.google.com/?q=ул.+Примерная,+10",
            facebook_link="https://facebook.com/zdorovie",
            instagram_link="https://instagram.com/zdorovie",
        )
        self.assertEqual(contact.name, "Медицинский Центр Здоровье")
        self.assertEqual(contact.address, "ул. Примерная, 10, г. Город")
        self.assertEqual(contact.phone_number_main, "+74951112233")
        self.assertEqual(contact.email_main, "info@zdorovie.ru")
        self.assertEqual(contact.work_hours, "ПН-ПТ 9:00-18:00, СБ 10:00-15:00")
        self.assertTrue(contact.is_active)
        self.assertIsNotNone(contact.created_at)
        self.assertIsNotNone(contact.updated_at)

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта ContactInfo.
        """
        contact = ContactInfo.objects.create(
            name="Главный офис",
            address="ул. Центральная, 1",
            phone_number_main="+78005553535",
            email_main="main@office.com",
            work_hours="24/7",
        )
        self.assertEqual(str(contact), "Главный офис")

        contact_no_name = ContactInfo.objects.create(
            # Имя не указано, будет использовано значение по умолчанию "Медицинская Клиника"
            address="ул. Без Названия, 1",
            phone_number_main="+78001002030",
            email_main="noname@office.com",
            work_hours="ПН-ПТ 9:00-17:00",
        )
        # Ожидаем значение по умолчанию для name
        self.assertEqual(str(contact_no_name), "Медицинская Клиника")

    def test_default_values(self):
        """
        Проверяет, что значения по умолчанию для полей устанавливаются правильно.
        """
        contact = ContactInfo.objects.create(
            address="ул. По умолчанию, 1",
            phone_number_main="+79000000000",
            email_main="default@test.com",
            work_hours="По графику",
        )
        self.assertEqual(
            contact.name, "Медицинская Клиника"
        )  # default="Медицинская Клиника"
        self.assertTrue(contact.is_active)  # default=True

    def test_ordering(self):
        """
        Проверяет, что объекты ContactInfo сортируются по created_at в убывающем порядке.
        """
        now = timezone.now()
        contact1 = ContactInfo.objects.create(
            name="Старый",
            address="а",
            phone_number_main="1",
            email_main="a@a",
            work_hours="а",
            created_at=now - timedelta(days=2),
        )
        contact2 = ContactInfo.objects.create(
            name="Средний",
            address="б",
            phone_number_main="2",
            email_main="b@b",
            work_hours="б",
            created_at=now - timedelta(days=1),
        )
        contact3 = ContactInfo.objects.create(
            name="Новый",
            address="в",
            phone_number_main="3",
            email_main="c@c",
            work_hours="в",
            created_at=now,
        )

        contacts = ContactInfo.objects.all()
        self.assertEqual(list(contacts), [contact3, contact2, contact1])


class DoctorModelTest(TestCase):
    """
    Тесты для модели Doctor.
    Проверяют создание врача, его строковое представление и значения по умолчанию.
    """

    def setUp(self):
        """Создаем тестового пользователя для связи с доктором."""
        self.user = User.objects.create_user(
            username="test_doctor_user",
            email="doctor@example.com",
            password="password123",
        )

    def test_create_doctor(self):
        """
        Проверяет, что объект Doctor может быть успешно создан.
        """
        doctor = Doctor.objects.create(
            user=self.user,
            name="Др. Елена Смирнова",
            specialty="Терапевт",
            bio="Опытный терапевт с 15-летним стажем.",
            experience_years=15,
            education="МГУ им. Ломоносова",
        )
        self.assertEqual(doctor.name, "Др. Елена Смирнова")
        self.assertEqual(doctor.specialty, "Терапевт")
        self.assertEqual(doctor.user, self.user)
        self.assertTrue(doctor.is_active)
        self.assertEqual(doctor.experience_years, 15)
        self.assertEqual(
            doctor.default_interval_minutes, 30
        )  # Проверка дефолтного значения

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта Doctor.
        """
        doctor = Doctor.objects.create(name="Др. Петров Алексей", specialty="Хирург")
        self.assertEqual(str(doctor), "Др. Петров Алексей (Хирург)")

    def test_default_values(self):
        """
        Проверяет значения по умолчанию для полей Doctor.
        """
        doctor = Doctor.objects.create(name="Др. Иван Иванов", specialty="Педиатр")
        self.assertEqual(doctor.experience_years, 0)  # default=0
        self.assertEqual(doctor.default_interval_minutes, 30)  # default=30
        self.assertTrue(doctor.is_active)  # default=True
        self.assertIsNone(doctor.photo.name)  # photo is blank=True, null=True
        self.assertIsNone(doctor.default_start_time)
        self.assertIsNone(doctor.default_end_time)


class ReviewModelTest(TestCase):
    """
    Тесты для модели Review.
    Проверяют создание отзыва и его строковое представление.
    """

    def setUp(self):
        """Создаем тестового врача для связи с отзывом."""
        self.doctor = Doctor.objects.create(
            name="Др. Анна Иванова", specialty="Дерматолог"
        )

    def test_create_review(self):
        """
        Проверяет, что объект Review может быть успешно создан.
        """
        review = Review.objects.create(
            full_name="Мария С.",
            email="maria@example.com",
            rating=4,
            text="Отличный врач, очень внимательный.",
            doctor=self.doctor,
            is_approved=True,
        )
        self.assertEqual(review.full_name, "Мария С.")
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.text, "Отличный врач, очень внимательный.")
        self.assertEqual(review.doctor, self.doctor)
        self.assertTrue(review.is_approved)
        self.assertIsNotNone(review.created_at)

    def test_str_representation_with_doctor(self):
        """
        Проверяет строковое представление объекта Review с указанным врачом.
        """
        review = Review.objects.create(
            full_name="Алексей П.", rating=5, text="Все супер!", doctor=self.doctor
        )
        expected_str = f"Отзыв от Алексей П. на 5 звезд (Врач: {self.doctor.name})"
        self.assertEqual(str(review), expected_str)

    def test_str_representation_without_doctor(self):
        """
        Проверяет строковое представление объекта Review без указанного врача (общий отзыв).
        """
        review = Review.objects.create(
            full_name="Ольга К.", rating=3, text="Клиника хорошая."
        )
        expected_str = "Отзыв от Ольга К. на 3 звезд (Врач: Общий)"
        self.assertEqual(str(review), expected_str)

    def test_default_values(self):
        """
        Проверяет значения по умолчанию для полей Review.
        """
        review = Review.objects.create(full_name="Дмитрий", text="Хорошо.")
        self.assertEqual(review.rating, 5)  # default=5
        self.assertFalse(review.is_approved)  # default=False
        self.assertIsNone(review.doctor)  # blank=True, null=True


class ServiceCategoryModelTest(TestCase):
    """
    Тесты для модели ServiceCategory.
    Проверяют создание категории услуг.
    """

    def test_create_service_category(self):
        """
        Проверяет, что объект ServiceCategory может быть успешно создан.
        """
        category = ServiceCategory.objects.create(
            name="Стоматология", description="Услуги по уходу за зубами."
        )
        self.assertEqual(category.name, "Стоматология")
        self.assertEqual(category.slug, "")
        self.assertEqual(category.description, "Услуги по уходу за зубами.")
        self.assertEqual(category.order, 0)  # default=0

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта ServiceCategory.
        """
        category = ServiceCategory.objects.create(name="Педиатрия")
        self.assertEqual(str(category), "Педиатрия")

    def test_ordering(self):
        """
        Проверяет, что категории сортируются по полю 'order', затем по 'name'.
        """
        cat1 = ServiceCategory.objects.create(name="Кардиология", order=2)
        cat2 = ServiceCategory.objects.create(name="Педиатрия", order=1)
        cat3 = ServiceCategory.objects.create(name="Аллергология", order=1)

        categories = ServiceCategory.objects.all()
        # Ожидаемый порядок: cat3 (1, Аллергология), cat2 (1, Педиатрия), cat1 (2, Кардиология)
        self.assertEqual(list(categories), [cat3, cat2, cat1])


class ServiceModelTest(TestCase):
    """
    Тесты для модели Service.
    Проверяют создание услуги, генерацию slug и связи с другими моделями.
    """

    def setUp(self):
        """Создаем тестовую категорию и врача для связи с услугой."""
        self.category = ServiceCategory.objects.create(name="Общая медицина")
        self.doctor = Doctor.objects.create(name="Др. Смирнов", specialty="Терапевт")

    def test_create_service(self):
        """
        Проверяет, что объект Service может быть успешно создан.
        """
        service = Service.objects.create(
            category=self.category,
            name="Первичный осмотр",
            short_description="Консультация с терапевтом.",
            full_description="Полное обследование и анамнез.",
            base_price=1500.00,
            duration_minutes=45,
        )
        service.doctors.add(self.doctor)

        self.assertEqual(service.name, "Первичный осмотр")
        self.assertEqual(service.slug, "")
        self.assertEqual(service.category, self.category)
        self.assertEqual(service.base_price, 1500.00)
        self.assertEqual(service.duration_minutes, 45)
        self.assertTrue(service.is_active)
        self.assertIn(self.doctor, service.doctors.all())

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта Service.
        """
        service = Service.objects.create(
            name="Анализ крови",
            short_description="Общий анализ.",
            full_description="Полный анализ крови.",
        )
        self.assertEqual(str(service), "Анализ крови")

    def test_price_null_blank(self):
        """
        Проверяет, что поле base_price может быть пустым.
        """
        service = Service.objects.create(
            name="Комплексная диагностика",
            short_description="Комплекс.",
            full_description="Детальная диагностика.",
            base_price=None,  # intentionally left blank
        )
        self.assertIsNone(service.base_price)

    def test_doctors_m2m_relationship(self):
        """
        Проверяет связь Many-to-Many с Doctor.
        """
        service1 = Service.objects.create(
            name="Консультация",
            short_description="К.",
            full_description="Консультация.",
        )
        service2 = Service.objects.create(
            name="Операция", short_description="О.", full_description="Операция."
        )

        doctor1 = Doctor.objects.create(name="Др. Первый", specialty="Терапевт")
        doctor2 = Doctor.objects.create(name="Др. Второй", specialty="Хирург")

        service1.doctors.add(doctor1)
        service2.doctors.add(doctor1, doctor2)

        self.assertIn(doctor1, service1.doctors.all())
        self.assertNotIn(doctor2, service1.doctors.all())

        self.assertIn(doctor1, service2.doctors.all())
        self.assertIn(doctor2, service2.doctors.all())

        self.assertIn(service1, doctor1.services.all())
        self.assertIn(service2, doctor1.services.all())
        self.assertIn(service2, doctor2.services.all())
        self.assertNotIn(service1, doctor2.services.all())


class ServicePriceItemModelTest(TestCase):
    """
    Тесты для модели ServicePriceItem.
    Проверяют создание пункта прайс-листа и уникальность связки.
    """

    def setUp(self):
        """Создаем тестовую услугу для связи с пунктом прайс-листа."""
        self.service = Service.objects.create(
            name="Стоматологический осмотр",
            short_description="Осмотр.",
            full_description="Осмотр у стоматолога.",
        )

    def test_create_service_price_item(self):
        """
        Проверяет, что объект ServicePriceItem может быть успешно создан.
        """
        price_item = ServicePriceItem.objects.create(
            service=self.service,
            item_name="Первичная консультация",
            price=1200.50,
            unit="за сеанс",
        )
        self.assertEqual(price_item.service, self.service)
        self.assertEqual(price_item.item_name, "Первичная консультация")
        self.assertEqual(price_item.price, 1200.50)
        self.assertEqual(price_item.unit, "за сеанс")
        self.assertEqual(price_item.order, 0)  # default=0

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта ServicePriceItem.
        """
        price_item = ServicePriceItem.objects.create(
            service=self.service, item_name="Консультация", price=1000.00
        )
        self.assertEqual(str(price_item), f"{self.service.name} - Консультация")

    def test_unique_together_constraint(self):
        """
        Проверяет ограничение unique_together для service и item_name.
        """
        ServicePriceItem.objects.create(
            service=self.service, item_name="Вторичный прием", price=800.00
        )
        with self.assertRaises(Exception) as cm:  # Expecting IntegrityError or similar
            ServicePriceItem.objects.create(
                service=self.service,
                item_name="Вторичный прием",  # Same service and item_name
                price=900.00,
            )
        self.assertIn(
            "duplicate key value violates unique constraint", str(cm.exception)
        )

    def test_ordering(self):
        """
        Проверяет, что пункты прайс-листа сортируются по 'order', затем по 'item_name'.
        """
        item1 = ServicePriceItem.objects.create(
            service=self.service, item_name="B", price=100, order=2
        )
        item2 = ServicePriceItem.objects.create(
            service=self.service, item_name="A", price=200, order=1
        )
        item3 = ServicePriceItem.objects.create(
            service=self.service, item_name="C", price=300, order=1
        )

        items = ServicePriceItem.objects.filter(service=self.service)
        # Ожидаемый порядок: item2 (1, A), item3 (1, C), item1 (2, B)
        self.assertEqual(list(items), [item2, item3, item1])


class AppointmentModelTest(TestCase):
    """
    Тесты для модели Appointment.
    Проверяют создание записи на прием, строковое представление и вспомогательные методы.
    """

    def setUp(self):
        """Создаем тестового пользователя, врача и услугу для записей на прием."""
        self.user = User.objects.create_user(
            username="patient", email="patient@example.com", password="testpassword"
        )
        self.doctor = Doctor.objects.create(
            name="Др. Олег Иванов", specialty="Кардиолог"
        )
        self.service = Service.objects.create(
            name="Консультация кардиолога",
            short_description="Конс.",
            full_description="Полная консультация.",
        )

    def test_create_appointment(self):
        """
        Проверяет, что объект Appointment может быть успешно создан.
        """
        today = date.today()
        appointment_time = time(10, 0)
        appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            service=self.service,
            date=today,
            time=appointment_time,
            status="pending",
            comments="Есть боли в груди.",
        )
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.date, today)
        self.assertEqual(appointment.time, appointment_time)
        self.assertEqual(appointment.status, "pending")
        self.assertEqual(appointment.comments, "Есть боли в груди.")
        self.assertIsNotNone(appointment.created_at)
        self.assertIsNotNone(appointment.updated_at)

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта Appointment.
        """
        today = date.today()
        appointment_time = time(11, 30)
        appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            service=self.service,
            date=today,
            time=appointment_time,
        )
        # Ожидаем строковое представление времени с секундами
        expected_str = (
            f"Запись {self.user.username} к {self.doctor.name} на {today} "
            f"в {appointment_time.strftime('%H:%M:%S')}"
        )
        self.assertEqual(str(appointment), expected_str)

    def test_unique_together_constraint(self):
        """
        Проверяет ограничение unique_together для doctor, date, time.
        """
        test_date = date(2025, 7, 15)
        test_start = time(14, 0)
        Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            service=self.service,
            date=test_date,
            time=test_start,
        )
        with self.assertRaises(Exception) as cm:  # Expecting IntegrityError or similar
            Appointment.objects.create(
                user=self.user,
                doctor=self.doctor,
                service=self.service,
                date=test_date,
                time=test_start,  # Same doctor, date, time
            )
        self.assertIn(
            "duplicate key value violates unique constraint", str(cm.exception)
        )

    def test_is_past_appointment(self):
        """
        Проверяет метод is_past_appointment.
        """
        # ИСПРАВЛЕНИЕ: Вызываем функцию timezone.now()
        now = timezone.now()

        # Запись в прошлом (гарантированно)
        past_date = now.date() - timedelta(days=1)
        past_time = time(10, 0)
        past_appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            service=self.service,
            date=past_date,
            time=past_time,
        )
        self.assertTrue(past_appointment.is_past_appointment())
        # Запись в будущем (гарантированно)
        future_date = now.date() + timedelta(days=1)
        future_time = time(10, 0)
        future_appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            service=self.service,
            date=future_date,
            time=future_time,
        )
        self.assertFalse(future_appointment.is_past_appointment())

        # Запись в настоящем, время на 1 минуту в будущем
        # Используем timezone.localtime для работы с текущим временем в локальной таймзоне
        now_aware = timezone.localtime(now)  # Теперь now - это datetime объект
        future_time_today = (now_aware + timedelta(minutes=1)).time()
        current_appointment_future_today = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            service=self.service,
            date=now_aware.date(),
            time=future_time_today,
        )
        self.assertFalse(current_appointment_future_today.is_past_appointment())

        # Запись в настоящем, время на 1 минуту в прошлом
        past_time_today = (now_aware - timedelta(minutes=1)).time()
        current_appointment_past_today = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            service=self.service,
            date=now_aware.date(),
            time=past_time_today,
        )
        self.assertTrue(current_appointment_past_today.is_past_appointment())


class DoctorScheduleModelTest(TestCase):
    """
    Тесты для модели DoctorSchedule.
    Проверяют создание расписания врача и уникальность записи.
    """

    def setUp(self):
        """Создаем тестового врача для расписания."""
        self.doctor = Doctor.objects.create(
            name="Др. Ирина Коваль", specialty="Невролог"
        )

    def test_create_doctor_schedule(self):
        """
        Проверяет, что объект DoctorSchedule может быть успешно создан.
        """
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=date(2025, 7, 10),
            start_time=time(9, 0),
            end_time=time(17, 0),
            interval_minutes=45,
        )
        self.assertEqual(schedule.doctor, self.doctor)
        self.assertEqual(schedule.date, date(2025, 7, 10))
        self.assertEqual(schedule.start_time, time(9, 0))
        self.assertEqual(schedule.end_time, time(17, 0))
        self.assertEqual(schedule.interval_minutes, 45)

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта DoctorSchedule.
        """
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=date(2025, 7, 11),
            start_time=time(10, 0),
            end_time=time(18, 0),
        )
        # Ожидаем строковое представление времени с секундами
        expected_str = (
            f"Расписание {self.doctor.name} на {date(2025, 7, 11)}: 10:00:00-18:00:00"
        )
        self.assertEqual(str(schedule), expected_str)

    def test_unique_together_constraint(self):
        """
        Проверяет ограничение unique_together для doctor, date, start_time, end_time.
        """
        test_date = date(2025, 7, 15)
        test_start = time(9, 0)
        test_end = time(17, 0)
        DoctorSchedule.objects.create(
            doctor=self.doctor, date=test_date, start_time=test_start, end_time=test_end
        )
        with self.assertRaises(Exception) as cm:  # Expecting IntegrityError or similar
            DoctorSchedule.objects.create(
                doctor=self.doctor,
                date=test_date,
                start_time=test_start,
                end_time=test_end,  # Same doctor, date, start_time, end_time
            )
        self.assertIn(
            "duplicate key value violates unique constraint", str(cm.exception)
        )

    def test_default_interval_minutes(self):
        """
        Проверяет значение по умолчанию для interval_minutes.
        """
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=date(2025, 7, 12),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        self.assertEqual(schedule.interval_minutes, 30)  # default=30


class MedicalRecordModelTest(TestCase):
    """
    Тесты для модели MedicalRecord.
    Проверяют создание медицинской записи и ее связь с приемом.
    """

    def setUp(self):
        """
        Создаем тестового пользователя, врача, услугу и прием
        для связи с медицинской записью.
        """
        self.patient_user = User.objects.create_user(
            username="patient_record",
            email="patient_record@example.com",
            password="password123",
        )
        self.doctor_user = User.objects.create_user(
            username="doctor_uploader",
            email="doctor_uploader@example.com",
            password="password123",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user, name="Др. Евгений Прохоров", specialty="Лаборант"
        )
        self.service = Service.objects.create(
            name="Анализ крови",
            short_description="Кровь.",
            full_description="Полный анализ крови.",
        )
        self.appointment = Appointment.objects.create(
            user=self.patient_user,
            doctor=self.doctor,
            service=self.service,
            date=date(2025, 7, 1),
            time=time(9, 0),
            status="completed",
        )

    def test_create_medical_record(self):
        """
        Проверяет, что объект MedicalRecord может быть успешно создан.
        """
        record = MedicalRecord.objects.create(
            appointment=self.appointment,
            title="Результаты общего анализа крови",
            file="medical_records/blood_test_patient_record.pdf",  # Пример пути к файлу
            uploaded_by_doctor=self.doctor_user,
            notes="Все показатели в норме.",
        )
        self.assertEqual(record.appointment, self.appointment)
        self.assertEqual(record.title, "Результаты общего анализа крови")
        self.assertEqual(
            record.file.name, "medical_records/blood_test_patient_record.pdf"
        )
        self.assertEqual(record.uploaded_by_doctor, self.doctor_user)
        self.assertEqual(record.notes, "Все показатели в норме.")
        self.assertIsNotNone(record.uploaded_at)

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта MedicalRecord.
        """
        record = MedicalRecord.objects.create(
            appointment=self.appointment,
            title="Заключение УЗИ",
            file="medical_records/uzi_conclusion.pdf",
            uploaded_by_doctor=self.doctor_user,
        )
        expected_str = (
            f"Результат для {self.appointment.user.username} "
            f"({self.appointment.service.name} от {self.appointment.date})"
        )
        self.assertEqual(str(record), expected_str)

    def test_one_to_one_appointment_constraint(self):
        """
        Проверяет, что к одному приему можно привязать только одну медицинскую запись.
        """
        MedicalRecord.objects.create(
            appointment=self.appointment,
            title="Первая запись",
            file="medical_records/first.pdf",
            uploaded_by_doctor=self.doctor_user,
        )
        with self.assertRaises(Exception) as cm:  # Expecting IntegrityError or similar
            MedicalRecord.objects.create(
                appointment=self.appointment,  # Same appointment
                title="Вторая запись",
                file="medical_records/second.pdf",
                uploaded_by_doctor=self.doctor_user,
            )
        self.assertIn(
            "duplicate key value violates unique constraint", str(cm.exception)
        )


class FAQItemModelTest(TestCase):
    """
    Тесты для модели FAQItem.
    Проверяют создание элемента FAQ и его строковое представление.
    """

    def test_create_faq_item(self):
        """
        Проверяет, что объект FAQItem может быть успешно создан.
        """
        faq = FAQItem.objects.create(
            question="Как записаться на прием?",
            answer="Вы можете записаться через личный кабинет или по телефону.",
            is_published=True,
        )
        self.assertEqual(faq.question, "Как записаться на прием?")
        self.assertEqual(
            faq.answer, "Вы можете записаться через личный кабинет или по телефону."
        )
        self.assertTrue(faq.is_published)
        self.assertIsNotNone(faq.created_at)
        self.assertIsNotNone(faq.updated_at)

    def test_str_representation(self):
        """
        Проверяет строковое представление объекта FAQItem.
        """
        faq_short = FAQItem.objects.create(question="Вопрос", answer="Ответ")
        self.assertEqual(str(faq_short), "Вопрос")

        faq_long = FAQItem.objects.create(
            question="Очень длинный вопрос, который должен быть обрезан для строкового представления объекта.",
            answer="Ответ",
        )
        self.assertEqual(
            str(faq_long), "Очень длинный вопрос, который должен быть обрезан ..."
        )

    def test_default_values(self):
        """
        Проверяет значения по умолчанию для полей FAQItem.
        """
        faq = FAQItem.objects.create(question="Тестовый вопрос")
        self.assertIsNone(faq.answer)  # blank=True, null=True
        self.assertFalse(faq.is_published)  # default=False

    def test_ordering(self):
        """
        Проверяет, что объекты FAQItem сортируются по created_at в убывающем порядке.
        """
        now = timezone.now()
        faq1 = FAQItem.objects.create(
            question="1", answer="1", created_at=now - timedelta(days=2)
        )
        faq2 = FAQItem.objects.create(
            question="2", answer="2", created_at=now - timedelta(days=1)
        )
        faq3 = FAQItem.objects.create(question="3", answer="3", created_at=now)

        faqs = FAQItem.objects.all()
        self.assertEqual(list(faqs), [faq3, faq2, faq1])

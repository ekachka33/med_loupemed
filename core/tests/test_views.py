# core/tests/test_views.py
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch
import datetime

from core.models import (
    AboutUsPage, ContactInfo, ContactRequest, Doctor, Review, ServiceCategory,
    Service, DoctorSchedule, Appointment, MedicalRecord, FAQItem
)
from core.forms import (
    ContactForm, ReviewForm, UserAppointmentForm, MedicalRecordUploadForm,
    UserQuestionForm
)

User = get_user_model()


class BaseViewTest(TestCase):
    """
    Базовый класс для настройки общих данных для тестов представлений.
    """
    def setUp(self):
        self.client = Client()
        self.user_password = 'testpassword123'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=self.user_password
        )
        self.doctor_user = User.objects.create_user(
            username='doctoruser',
            email='doctor@example.com',
            password=self.user_password
        )

        # Создание базовых объектов для тестов
        self.category = ServiceCategory.objects.create(name='Тестовая Категория')
        self.service = Service.objects.create(
            name='Тестовая Услуга', category=self.category, duration_minutes=30, is_active=True
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user, name='Доктор Тест', specialty='Терапевт', is_active=True
        )
        self.doctor.services.add(self.service)

        self.about_us = AboutUsPage.objects.create(
            title='О нас', content='Тестовый контент о нас.'
        )
        self.contact_info = ContactInfo.objects.create(
            name='Тестовая Клиника',
            address='Тестовый адрес',
            phone_number_main='+79991234567',
            email_main='info@example.com',
            work_hours='ПН-ПТ 9:00-18:00'
        )
        self.review = Review.objects.create(
            full_name='Иван Петров', text='Отличный доктор!', is_approved=True, doctor=self.doctor
        )
        self.unapproved_review = Review.objects.create(
            full_name='Ольга Сидорова', text='Еще один отзыв.', is_approved=False, doctor=self.doctor
        )
        self.faq_item = FAQItem.objects.create(
            question='Тестовый вопрос?', answer='Тестовый ответ.', is_published=True
        )
        self.unpublished_faq_item = FAQItem.objects.create(
            question='Неопубликованный вопрос?', answer='Неопубликованный ответ.', is_published=False
        )


class HomeViewTest(BaseViewTest):
    def test_home_page_loads_correctly(self):
        """
        Проверяет, что главная страница загружается и возвращает статус 200.
        """
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_page_context(self):
        """
        Проверяет, что контекст главной страницы содержит AboutUsPage и ContactForm.
        """
        response = self.client.get(reverse('core:home'))
        self.assertIn('about_us_page', response.context)
        self.assertEqual(response.context['about_us_page'], self.about_us)
        self.assertIsInstance(response.context['contact_form'], ContactForm)


class AboutUsViewTest(BaseViewTest):
    def test_about_us_page_loads_correctly(self):
        """
        Проверяет, что страница 'О клинике' загружается и возвращает статус 200.
        """
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_about_us_page_context(self):
        """
        Проверяет, что контекст страницы 'О клинике' содержит нужные данные.
        """
        response = self.client.get(reverse('core:about'))
        self.assertIn('about_us_page', response.context)
        self.assertEqual(response.context['about_us_page'], self.about_us)

        self.assertIn('doctors', response.context)
        self.assertIn(self.doctor, response.context['doctors'])
        self.assertEqual(response.context['doctors'].count(), 1)

        self.assertIn('reviews', response.context)
        self.assertIn(self.review, response.context['reviews'])
        self.assertNotIn(self.unapproved_review, response.context['reviews'])
        self.assertEqual(response.context['reviews'].count(), 1)

        self.assertIsInstance(response.context['form'], ReviewForm)
        self.assertIsInstance(response.context['contact_form'], ContactForm)

    def test_about_us_page_inactive_doctor_not_shown(self):
        """
        Проверяет, что неактивные доктора не отображаются на странице 'О клинике'.
        """
        inactive_doctor = Doctor.objects.create(
            name='Неактивный Доктор', specialty='Хирург', is_active=False
        )
        response = self.client.get(reverse('core:about'))
        self.assertNotIn(inactive_doctor, response.context['doctors'])


class DoctorDetailViewTest(BaseViewTest):
    def test_doctor_detail_page_loads_correctly(self):
        """
        Проверяет, что детальная страница врача загружается и возвращает статус 200.
        """
        response = self.client.get(reverse('core:doctor_detail', args=[self.doctor.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctor_detail.html')

    def test_doctor_detail_page_404_for_non_existent_doctor(self):
        """
        Проверяет, что страница возвращает 404 для несуществующего врача.
        """
        response = self.client.get(reverse('core:doctor_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_doctor_detail_page_context(self):
        """
        Проверяет, что контекст детальной страницы врача содержит нужные данные.
        """
        response = self.client.get(reverse('core:doctor_detail', args=[self.doctor.pk]))

        self.assertIn('doctor', response.context)
        self.assertEqual(response.context['doctor'], self.doctor)

        self.assertIn('reviews', response.context)
        # Убедимся, что присутствуют только одобренные отзывы
        self.assertIn(self.review, response.context['reviews'])
        self.assertNotIn(self.unapproved_review, response.context['reviews'])
        self.assertEqual(response.context['reviews'].count(), 1)

        self.assertIsInstance(response.context['contact_form'], ContactForm)

    def test_doctor_detail_page_without_reviews(self):
        """
        Проверяет, что страница врача отображается корректно, если нет отзывов.
        """
        # Удаляем все отзывы, связанные с этим доктором
        Review.objects.filter(doctor=self.doctor).delete()
        response = self.client.get(reverse('core:doctor_detail', args=[self.doctor.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('reviews', response.context)
        self.assertEqual(response.context['reviews'].count(), 0)


class SubmitReviewViewTest(BaseViewTest):
    def test_submit_review_success_via_ajax_post(self):
        """
        Проверяет успешную отправку отзыва через AJAX POST запрос.
        """
        initial_review_count = Review.objects.count()

        data = {
            'full_name': 'Тестовый Отзыв',
            'email': 'test@example.com',
            'rating': 4,
            'text': 'Это отличный тестовый отзыв.',
            'doctor': self.doctor.pk,
        }

        # Делаем POST запрос с заголовком X-Requested-With для имитации AJAX
        response = self.client.post(
            reverse('core:submit_review'),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '{"success": true', status_code=200)  # Проверяем JSON-ответ
        self.assertEqual(Review.objects.count(), initial_review_count + 1)

        # Проверяем, что созданный отзыв не одобрен по умолчанию
        new_review = Review.objects.latest('created_at')
        self.assertEqual(new_review.full_name, 'Тестовый Отзыв')
        self.assertEqual(new_review.email, 'test@example.com')
        self.assertEqual(new_review.rating, 4)
        self.assertEqual(new_review.text, 'Это отличный тестовый отзыв.')
        self.assertEqual(new_review.doctor, self.doctor)
        self.assertFalse(new_review.is_approved)  # Должен быть False

    def test_submit_review_invalid_form_via_ajax_post(self):
        """
        Проверяет отправку невалидных данных отзыва через AJAX POST запрос.
        """
        initial_review_count = Review.objects.count()

        data = {
            'full_name': '',  # Пустое имя - невалидно
            'email': 'invalid-email',  # Невалидный email
            'rating': 0,  # Невалидный рейтинг
            'text': '',  # Пустой текст - невалидно
            'doctor': self.doctor.pk,
        }

        response = self.client.post(
            reverse('core:submit_review'),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 400)  # Ожидаем 400 Bad Request
        self.assertContains(response, '{"success": false', status_code=400)
        self.assertIn('errors', response.json())  # Убедимся, что есть поле 'errors' в JSON

        self.assertEqual(Review.objects.count(), initial_review_count)  # Отзыв не должен быть создан

    def test_submit_review_non_ajax_post(self):
        """
        Проверяет, что представление отклоняет обычный POST запрос (не AJAX).
        """
        initial_review_count = Review.objects.count()

        data = {
            'full_name': 'Обычный POST',
            'email': 'normal@example.com',
            'rating': 5,
            'text': 'Это обычный отзыв, не AJAX.',
        }

        response = self.client.post(reverse('core:submit_review'), data)

        self.assertEqual(response.status_code, 400)  # Ожидаем 400 Bad Request
        expected_json_response = {'success': False, 'message': 'Недопустимый запрос.'}
        self.assertJSONEqual(str(response.content, encoding='utf8'), expected_json_response)

        self.assertEqual(Review.objects.count(), initial_review_count)  # Отзыв не должен быть создан


class ContactPageTest(BaseViewTest):
    def test_contact_page_loads_correctly(self):
        """
        Проверяет, что страница контактов загружается и возвращает статус 200.
        """
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_contact_page_context(self):
        """
        Проверяет, что контекст страницы контактов содержит нужные данные.
        """
        response = self.client.get(reverse('core:contact'))
        self.assertIn('contact_info', response.context)
        self.assertEqual(response.context['contact_info'], self.contact_info)
        self.assertIsInstance(response.context['form'], ContactForm)


class SubmitFeedbackTest(BaseViewTest):
    @patch('core.views.send_mail')
    @patch('core.models.ContactRequest.objects.create')
    def test_submit_feedback_success_with_email(self, mock_create, mock_send_mail):
        """
        Проверяет успешную отправку формы обратной связи с email.
        """
        form_data = {
            'name': 'Тест Имя',
            'email': 'test@example.com',
            'message': 'Это тестовое сообщение.'
        }
        response = self.client.post(reverse('core:submit_feedback'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'success': True, 'message': 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'}
        )
        # Проверяем, что ContactRequest был создан
        mock_create.assert_called_once_with(
            full_name='Тест Имя',
            email='test@example.com',
            phone_number='',
            message='Это тестовое сообщение.',
            request_type='Сообщение с сайта'
        )
        # Проверяем, что send_mail был вызван дважды (администратору и пользователю)
        self.assertEqual(mock_send_mail.call_count, 2)

    @patch('core.views.send_mail')
    @patch('core.models.ContactRequest.objects.create')
    def test_submit_feedback_success_with_phone(self, mock_create, mock_send_mail):
        """
        Проверяет успешную отправку формы обратной связи с номером телефона (обратный звонок).
        """
        form_data = {
            'name': 'Тест Телефон',
            'phone_number': '+79991234567',
            'message': 'Прошу перезвонить мне.'
        }
        response = self.client.post(reverse('core:submit_feedback'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'success': True, 'message': 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'}
        )
        # Проверяем, что ContactRequest был создан
        mock_create.assert_called_once_with(
            full_name='Тест Телефон',
            email='', # Email будет пустым
            phone_number='+79991234567',
            message='Прошу перезвонить мне.',
            request_type='Обратный звонок'
        )
        self.assertEqual(mock_send_mail.call_count, 1)

    @patch('core.views.send_mail')
    def test_submit_feedback_invalid_form(self, mock_send_mail):
        """
        Проверяет, что невалидная форма обратной связи возвращает ошибку.
        """
        form_data = {
            'name': '',  # Невалидные данные
            'email': 'invalid-email',
            'message': ''
        }
        response = self.client.post(reverse('core:submit_feedback'), data=form_data)
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertFalse(json_response['success'])
        self.assertIn('name', json_response['errors'])
        self.assertIn('email', json_response['errors'])
        self.assertIn('message', json_response['errors'])
        # Убедимся, что send_mail не вызывался
        mock_send_mail.assert_not_called()

    @patch('core.views.send_mail')
    @patch('core.models.ContactRequest.objects.create', side_effect=Exception('DB Error'))
    def test_submit_feedback_db_error(self, mock_create, mock_send_mail):
        """
        Проверяет обработку ошибки при сохранении ContactRequest в БД.
        """
        form_data = {
            'name': 'Тест',
            'email': 'test@example.com',
            'message': 'Тест ошибки БД'
        }
        response = self.client.post(reverse('core:submit_feedback'), data=form_data)
        self.assertEqual(response.status_code, 500)
        json_response = response.json()
        self.assertFalse(json_response['success'])
        self.assertIn('Произошла ошибка при сохранении вашего запроса', json_response['message'])
        mock_send_mail.assert_not_called()


class FAQPageTest(BaseViewTest):
    def test_faq_page_loads_correctly(self):
        """
        Проверяет, что страница FAQ загружается и возвращает статус 200.
        """
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/faq.html')

    def test_faq_page_context(self):
        """
        Проверяет, что контекст страницы FAQ содержит нужные данные.
        """
        response = self.client.get(reverse('core:faq'))
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Вопросы и Ответы')
        self.assertIn('faq_items', response.context)
        self.assertIn(self.faq_item, response.context['faq_items'])  # Проверяем, что опубликованный FAQ есть

        # Создадим неопубликованный FAQ, чтобы убедиться, что он не отображается
        unpublished_faq = FAQItem.objects.create(
            question="Неопубликованный вопрос",
            answer="Неопубликованный ответ",
            is_published=False
        )
        response = self.client.get(reverse('core:faq'))  # Обновляем запрос
        self.assertNotIn(unpublished_faq, response.context['faq_items'])

        self.assertIsInstance(response.context['question_form'], UserQuestionForm)


class SubmitQuestionTest(BaseViewTest):
    def test_submit_question_success(self):
        """
        Проверяет успешную отправку вопроса пользователя через AJAX.
        """
        form_data = {
            'question': 'Это тестовый вопрос от пользователя.',
        }
        response = self.client.post(
            reverse('core:submit_question'),
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'success': True, 'message': 'Ваш вопрос успешно отправлен! Мы ответим на него в ближайшее время.'}
        )

        self.assertTrue(FAQItem.objects.filter(question='Это тестовый вопрос от пользователя.').exists())
        new_faq = FAQItem.objects.get(question='Это тестовый вопрос от пользователя.')
        self.assertFalse(new_faq.is_published)

    def test_submit_question_invalid_form(self):
        """
        Проверяет, что невалидная форма вопроса возвращает ошибку.
        """
        form_data = {
            'question': '',
        }
        response = self.client.post(
            reverse('core:submit_question'),
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertFalse(json_response['success'])
        self.assertIn('question', json_response['errors'])

    def test_submit_question_non_ajax_request(self):
        """
        Проверяет, что не-AJAX запрос на submit_question обрабатывается и возвращает 200,
        если данные валидны.
        """
        form_data = {
            'question': 'Обычный вопрос для не-AJAX теста.',
        }
        response = self.client.post(
            reverse('core:submit_question'),
            data=form_data,
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response['success'])
        self.assertIn('message', json_response)
        self.assertTrue(FAQItem.objects.filter(question='Обычный вопрос для не-AJAX теста.').exists())


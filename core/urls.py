from django.urls import path
from . import views
from .views import MakeAppointmentView, GetAvailableTimeSlotsView

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us_view, name='about'),
    path('doctor/<int:pk>/', views.doctor_detail_view, name='doctor_detail'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('services/', views.service_list, name='service_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('contact/', views.contact_page, name='contact'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('profile/', views.profile_view, name='profile'),
    path('make-appointment/', views.MakeAppointmentView.as_view(), name='make_appointment'),
    path('api/get-time-slots/', views.GetAvailableTimeSlotsView.as_view(), name='get_available_time_slots'),
    path('doctor/schedule/', views.DoctorScheduleView.as_view(), name='doctor_schedule'),
    path('get-services-for-doctor/', views.get_services_for_doctor, name='get_services_for_doctor'),

]



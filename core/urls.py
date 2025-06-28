from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us_view, name='about'),
    path('doctor/<int:pk>/', views.doctor_detail_view, name='doctor_detail'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('services/', views.service_list, name='service_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    # path('contact/', views.contact_view, name='contact'),
]

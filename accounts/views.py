from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from .forms import UserRegisterForm

# Простая функция для регистрации. Будет заменена на FormView или CreateView.
# Пока что просто перенаправляет на главную.
class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

# Функция для входа. Используем встроенную форму Django.
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('core:home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Функция для выхода. Используем встроенную функцию Django.
def logout_view(request):
    auth_logout(request)
    return redirect('core:home')



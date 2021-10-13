from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .forms import *


def index(request):
    context = {}
    return render(request, 'accounts/index.html', context)


@login_required(login_url='login')
def home(request):
    context = {}
    return render(request, 'accounts/home.html', context)


def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Konto użytkownika ' + user + ' zostało pomyślnie utworzone')
                return redirect('login')

        context = {'form': form}
        return render(request, 'accounts/register.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        context = {}

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.warning(request, "Nazwa użytkownika lub hasło są niepoprawne")
                return render(request, 'accounts/login.html', context)

        return render(request, 'accounts/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')

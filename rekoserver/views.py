from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from rekoserver.dbhandle import add_to_list
from rekoserver.forms import CreateUserForm
from rekoserver.models import Watched, Movies
from rekoserver.movieapi import m_api
from rekoserver.recommend import user_recommendations


def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return render(request, 'accounts/index.html')


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
            else:
                messages.warning(request, "Nie udało się założyć konta")
                return render(request, 'accounts/register.html')

        context = {'form': form}
        return render(request, 'accounts/register.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('login')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.warning(request, "Nazwa użytkownika lub hasło są niepoprawne")
                return render(request, 'accounts/login.html')

        return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    return render(request, 'accounts/home.html')


@login_required(login_url='login')
def search(request):
    context = {}

    if request.method == 'POST':
        if request.POST.get('name'):
            name = request.POST.get('name')
            movie_search = m_api.movie.search(name)
            if len(movie_search) > 0:
                context = {'found': movie_search, 'url': m_api.full_url, 'name': name}
            else:
                not_found = "Nie znaleziono danego filmu"
                context = {'msg': not_found}
        elif request.POST.get('m_id'):
            context = add_to_list(request)

    return render(request, 'accounts/search.html', context)


@login_required(login_url='login')
def watched(request):
    if request.method == 'POST':
        m_id = request.POST.get('m_id')
        entry = Watched.objects.get(user=request.user, m_id=m_id)
        entry.delete()

    movies_list = list(Movies.objects.filter(watched__user=request.user).order_by('title'))
    ratings = [r for r in [Watched.objects.filter(user=request.user, m_id=movies_list[it])[0].rating
                           for it in range(len(movies_list))]]

    watched_list = list(zip(movies_list, ratings))
    context = {'url': m_api.full_url, 'list': watched_list}

    return render(request, 'accounts/watched.html', context)


@login_required(login_url='login')
def recommend(request):
    result = user_recommendations(request.user)

    if not result.empty:
        recommendations = [m_api.movie.details(x) for x in result['id']]
        context = {'url': m_api.full_url, 'list': recommendations}
    else:
        context = {'list': None}

    if request.method == 'POST':
        context = add_to_list(request)
        return render(request, 'accounts/search.html', context)

    return render(request, 'accounts/recommend.html', context)

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView

from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('watched/', views.watched, name='watched'),
    path('recommend/', views.recommend, name='recommend'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.svg'))),

]

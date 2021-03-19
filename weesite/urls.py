from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('portfolio', views.portfolio_page, name='portfolio_page'),
    path('login', views.login_page, name='login_page'),
]
from django.urls import path
from .views import index, add_bank_req, login_aut, login_views, out, acceptance, acceptance_terminal, distribution

urlpatterns = [
    path('login/', login_views, name='login'),
    path('out/', out, name='out'),
    path('aut/', login_aut, name='aut'),
    path('home/', index, name='home'),
    path('add_bank_req/', add_bank_req, name='add_bank_req'),
    path('acceptance/', acceptance, name='acceptance'),
    path('acceptance_terminal/', acceptance_terminal, name='acceptance_terminal'),
    path('distribution/', distribution, name='distribution'),
]

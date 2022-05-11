from . import views
from django.urls import path

urlpatterns = [
    path('membership/',views.index,name='index'),
    path('', views.home, name='home'),
    path('auth/signup', views.SignUp.as_view(), name='signup'),
    path('auth/settings', views.settings, name='settings'),
    path('join', views.join, name='join'),
    path('checkout', views.checkout, name='checkout'),
    path('success', views.success, name='success'),
    path('cancel', views.cancel, name='cancel'),
    path('pause',views.pause_payments,name='pause'),
    path('resume', views.resumepayments, name='resume'),
    path('delete', views.delete, name='delete'),
    path('update', views.update, name='update'),


    path('updateaccounts', views.updateaccounts, name='updateaccounts'),

]

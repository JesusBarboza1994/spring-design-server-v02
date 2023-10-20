from django.urls import path
from . import views
#from ..api import simulate

urlpatterns = [
    path('', views.home, name='home'),
    path('clients/', views.clients),
    path('cars/<int:id>', views.cars),
    path('create-client/', views.create_client),
    path('create-spring/', views.create_spring),
    path('simulate-spring/', views.simulate_spring),
    path('login/', views.Login.as_view(), name='Login'),
    path('signup/',views.signup, name='signup'),
    path('prueba/', views.Prueba.as_view({'get': 'prueba'}), name='prueba'),
    path('refresh-token/', views.UserToken.as_view(), name='refresh_token'),
    path('logout/',views.Logout.as_view(), name='Logout') 

]
from django import views
from django.urls import path
from .views import  LoadMedicationView, RegisterDroneView

urlpatterns = [
    path('register/', RegisterDroneView.as_view(), name='register_drone'),
    path('load/<int:pk>/', LoadMedicationView.as_view(), name='load_medication'),

]



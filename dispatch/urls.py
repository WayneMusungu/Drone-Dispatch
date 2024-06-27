from django import views
from django.urls import path
from .views import  CheckDroneBatteryLevelView, CheckLoadedMedicationsView, LoadMedicationView, RegisterDroneView

urlpatterns = [
    path('drone/register/', RegisterDroneView.as_view(), name='register_drone'),
    path('drone/<int:id>/', LoadMedicationView.as_view(), name='load_medication'),
    path('drone/<int:id>/medications/', CheckLoadedMedicationsView.as_view(), name='loaded_medications'),
    # path('check-loaded/<int:pk>/', CheckLoadedMedicationsView.as_view(), name='check_loaded_medications'),
    # path('available-drones/', AvailableDronesForLoadingView.as_view(), name='available_drones_for_loading'),
    path('drone/<int:id>/battery/', CheckDroneBatteryLevelView.as_view(), name='check_drone_battery'),
    # path('change-to-loading/<int:pk>/', DroneChangeToLoadingView.as_view(), name='change-to-loading'),
]



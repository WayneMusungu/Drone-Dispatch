from django import views
from django.urls import path
from .views import  AvailableDronesForLoadingView, CheckDroneBatteryLevelView, CheckLoadedMedicationsView, LoadMedicationView, RegisterDroneView, DroneBatteryAuditListAPIView

urlpatterns = [
    path('drone/register/', RegisterDroneView.as_view(), name='register_drone'),
    path('drone/<int:id>/', LoadMedicationView.as_view(), name='load_medication'),
    path('drone/<int:id>/medications/', CheckLoadedMedicationsView.as_view(), name='loaded_medications'),
    path('drone/available-drones/', AvailableDronesForLoadingView.as_view(), name='available_drones_for_loading'),
    path('drone/<int:id>/battery/', CheckDroneBatteryLevelView.as_view(), name='check_drone_battery'),
    path('drone-audit/', DroneBatteryAuditListAPIView.as_view(), name='drone-battery-audit-list'),
]



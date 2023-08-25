from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('demo/', views.demo, name='demo'),
    path('start_recording/', views.start_recording, name='start_recording'),
    path('stop_recording/', views.stop_recording, name='stop_recording'),
    path('handle_uploaded_file/', views.handle_uploaded_file, name='handle_uploaded_file'),
    path('early_access/', views.early_access, name='early_access')
]

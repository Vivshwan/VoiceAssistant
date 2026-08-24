from django.urls import path
from . import views

app_name = 'shopping'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('api/voice-command/', views.voice_command, name='voice_command'),
    path('api/toggle-item/<int:item_id>/', views.toggle_item, name='toggle_item'),
    path('api/remove-item/<int:item_id>/', views.remove_item, name='remove_item'),
]
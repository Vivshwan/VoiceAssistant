from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Shopping List
    path('items/', views.ItemListCreateView.as_view(), name='item-list'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item-detail'),
    path('items/<int:item_id>/toggle/', views.ItemToggleView.as_view(), name='item-toggle'),
    path('items/clear/', views.ClearItemsView.as_view(), name='clear-items'),
    path('shopping-list/', views.ShoppingListView.as_view(), name='shopping-list'),

    # Voice Commands
    path('voice/', views.VoiceCommandView.as_view(), name='voice-command'),

    # Suggestions & History
    path('suggestions/', views.SuggestionsView.as_view(), name='suggestions'),
    path('history/', views.HistoryView.as_view(), name='history'),

    # Categories
    path('categories/', views.CategoriesView.as_view(), name='categories'),
]
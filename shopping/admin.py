from django.contrib import admin
from .models import ShoppingList, Item, ShoppingHistory, UserPreference

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__username']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'shopping_list', 'quantity', 'category', 'is_checked']
    list_filter = ['category', 'is_checked']
    search_fields = ['name', 'shopping_list__name']
    list_editable = ['quantity', 'is_checked']

@admin.register(ShoppingHistory)
class ShoppingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_name', 'category', 'purchased_at']
    list_filter = ['category', 'purchased_at']
    search_fields = ['item_name', 'user__username']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'budget', 'created_at']
    search_fields = ['user__username']
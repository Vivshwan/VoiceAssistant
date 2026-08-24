from rest_framework import serializers
from django.contrib.auth.models import User
from shopping.models import Item, ShoppingList, ShoppingHistory


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item model"""
    category_display = serializers.SerializerMethodField()
    unit_display = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'quantity', 'unit', 'unit_display',
            'category', 'category_display', 'notes', 'is_checked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_unit_display(self, obj):
        return obj.get_unit_display()


class ShoppingListSerializer(serializers.ModelSerializer):
    """Serializer for ShoppingList model"""
    items = ItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    checked_items = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingList
        fields = [
            'id', 'name', 'is_active', 'created_at', 'updated_at',
            'items', 'total_items', 'checked_items'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_items(self, obj):
        return obj.get_total_items()

    def get_checked_items(self, obj):
        return obj.get_checked_items()


class ShoppingHistorySerializer(serializers.ModelSerializer):
    """Serializer for ShoppingHistory model"""

    class Meta:
        model = ShoppingHistory
        fields = ['id', 'item_name', 'category', 'quantity', 'purchased_at']
        read_only_fields = ['purchased_at']


class VoiceCommandSerializer(serializers.Serializer):
    """Serializer for voice command requests"""
    text = serializers.CharField(max_length=500)
    intent = serializers.CharField(max_length=50, required=False, allow_blank=True)
    item = serializers.CharField(max_length=200, required=False, allow_blank=True)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    unit = serializers.CharField(max_length=50, required=False, allow_blank=True)
    category = serializers.CharField(max_length=50, required=False, allow_blank=True)
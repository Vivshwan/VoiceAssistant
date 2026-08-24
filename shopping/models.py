from django.db import models
from django.contrib.auth.models import User


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_lists')
    name = models.CharField(max_length=100, default='My Shopping List')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Item(models.Model):
    CATEGORY_CHOICES = [
        ('dairy', '🥛 Dairy'),
        ('produce', '🥬 Produce'),
        ('meat', '🥩 Meat'),
        ('bakery', '🍞 Bakery'),
        ('snacks', '🍿 Snacks'),
        ('beverages', '🥤 Beverages'),
        ('household', '🧹 Household'),
        ('personal', '🧴 Personal Care'),
        ('frozen', '❄️ Frozen'),
        ('other', '📦 Other'),
    ]

    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('pack', 'Pack'),
        ('bottle', 'Bottle'),
        ('can', 'Can'),
        ('box', 'Box'),
        ('bag', 'Bag'),
    ]

    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200, db_index=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    notes = models.TextField(blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        indexes = [models.Index(fields=['name', 'category'])]

    def __str__(self):
        return f"{self.quantity} {self.get_unit_display()} of {self.name}"

    def get_display_name(self):
        if self.unit:
            return f"{self.quantity} {self.get_unit_display()} {self.name}"
        return f"{self.quantity}x {self.name}"


class ShoppingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_history')
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    purchased_at = models.DateTimeField(auto_now_add=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    class Meta:
        ordering = ['-purchased_at']
        indexes = [models.Index(fields=['user', 'item_name'])]

    def __str__(self):
        return f"{self.user.username} bought {self.item_name}"
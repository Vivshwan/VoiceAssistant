from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ShoppingList(models.Model):
    """
    Main shopping list model
    Each user can have multiple lists (active/archived)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )
    name = models.CharField(max_length=100, default='My Shopping List')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def get_total_items(self):
        """Count total items in this list"""
        return self.items.count()

    def get_checked_items(self):
        """Count checked (purchased) items"""
        return self.items.filter(is_checked=True).count()

    def get_total_price(self):
        """Calculate total price of all items"""
        total = 0
        for item in self.items.filter(is_checked=False):
            if item.price:
                total += float(item.price) * float(item.quantity)
        return total


class Item(models.Model):
    """
    Individual item in a shopping list
    """
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
        ('cup', 'Cup'),
        ('tbsp', 'Tablespoon'),
        ('tsp', 'Teaspoon'),
    ]

    CURRENCY_CHOICES = [
        ('USD', '💵 USD'),
        ('EUR', '💶 EUR'),
        ('GBP', '💷 GBP'),
        ('INR', '₹ INR'),
    ]

    SEASON_CHOICES = [
        ('summer', '☀️ Summer'),
        ('winter', '❄️ Winter'),
        ('spring', '🌸 Spring'),
        ('fall', '🍂 Fall'),
        ('year_round', '🔄 Year Round'),
    ]

    # Basic fields
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=200, db_index=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    notes = models.TextField(blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ NEW: Price and currency for price range filtering
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price of the item"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        choices=CURRENCY_CHOICES
    )

    # ✅ NEW: Brand for brand filtering
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Brand name of the item"
    )

    # ✅ NEW: Seasonality for seasonal recommendations
    season = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=SEASON_CHOICES,
        help_text="Season when this item is best"
    )

    # ✅ NEW: Substitute information
    substitute_for = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='substitutes',
        help_text="This item is a substitute for"
    )

    # ✅ NEW: Dietary information for better suggestions
    dietary_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dietary information like vegan, gluten-free, etc."
    )

    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['name', 'category']),
            models.Index(fields=['price']),  # ✅ For price filtering
            models.Index(fields=['season']),  # ✅ For seasonal filtering
        ]

    def __str__(self):
        price_str = f" (${self.price})" if self.price else ""
        season_str = f" [{self.get_season_display()}]" if self.season else ""
        return f"{self.quantity} {self.get_unit_display()} of {self.name}{price_str}{season_str}"

    def get_display_name(self):
        """Return formatted item name with quantity"""
        if self.unit:
            return f"{self.quantity} {self.get_unit_display()} {self.name}"
        return f"{self.quantity}x {self.name}"

    def get_price_display(self):
        """Return formatted price"""
        if self.price:
            return f"{self.currency} {self.price:.2f}"
        return "N/A"

    def is_substitute(self):
        """Check if this item is a substitute"""
        return self.substitute_for is not None

    def get_substitute_for_name(self):
        """Get the name of the item this substitutes"""
        if self.substitute_for:
            return self.substitute_for.name
        return None

    def get_substitutes(self):
        """Get all substitutes for this item"""
        return self.substitutes.all()


class ShoppingHistory(models.Model):
    """
    Track purchased items for smart suggestions
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase_history'
    )
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    purchased_at = models.DateTimeField(auto_now_add=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    # ✅ NEW: Store price at time of purchase
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price at time of purchase"
    )
    currency = models.CharField(max_length=3, default='USD')

    # ✅ NEW: Store season when purchased
    season = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['-purchased_at']
        indexes = [
            models.Index(fields=['user', 'item_name']),
            models.Index(fields=['purchased_at']),
        ]

    def __str__(self):
        price_str = f" (${self.price})" if self.price else ""
        return f"{self.user.username} bought {self.item_name}{price_str}"


class UserPreference(models.Model):
    """
    Store user preferences for recommendations
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    preferred_categories = models.JSONField(default=list)
    dietary_restrictions = models.JSONField(default=list)
    favorite_brands = models.JSONField(default=list)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ NEW: Price range preference
    preferred_price_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum preferred price"
    )
    preferred_price_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum preferred price"
    )

    # ✅ NEW: Seasonal preferences
    preferred_seasons = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

    def get_price_range(self):
        """Get preferred price range as tuple"""
        if self.preferred_price_range_min and self.preferred_price_range_max:
            return (self.preferred_price_range_min, self.preferred_price_range_max)
        return None


class SeasonalItem(models.Model):
    """
    ✅ NEW: Model for managing seasonal items
    """
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=Item.CATEGORY_CHOICES)
    season = models.CharField(max_length=20, choices=Item.SEASON_CHOICES)
    reason = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['season', 'name']
        unique_together = ['name', 'season']

    def __str__(self):
        return f"{self.name} ({self.get_season_display()})"


class SubstituteItem(models.Model):
    """
    ✅ NEW: Model for managing substitutes
    """
    original_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='substitute_entries'
    )
    substitute_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='original_entries'
    )
    reason = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['original_item__name', 'substitute_item__name']
        unique_together = ['original_item', 'substitute_item']

    def __str__(self):
        return f"{self.original_item.name} → {self.substitute_item.name}"


class PriceAlert(models.Model):
    """
    ✅ NEW: Model for price alerts
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='price_alerts'
    )
    item_name = models.CharField(max_length=200)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.item_name} under {self.currency} {self.max_price}"
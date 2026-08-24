from django.core.management.base import BaseCommand
from voice_assistant.shopping.models import Item, ShoppingList
from voice_assistant.shopping.seasonal_data import get_seasonal_items, get_season
from voice_assistant.shopping.substitutes_data import get_substitutes


class Command(BaseCommand):
    help = 'Populate seasonal and substitute data for items'

    def handle(self, *args, **options):
        # Get all shopping lists
        lists = ShoppingList.objects.filter(is_active=True)

        count = 0
        for shopping_list in lists:
            # Add seasonal items if not present
            season = get_season()
            seasonal_items = get_seasonal_items(season)

            for item_data in seasonal_items[:3]:  # Add 3 seasonal items per list
                item_name = item_data['name']
                exists = shopping_list.items.filter(name__iexact=item_name).exists()

                if not exists:
                    Item.objects.create(
                        shopping_list=shopping_list,
                        name=item_name,
                        category=item_data['category'],
                        season=season,
                        quantity=1,
                        unit='pcs'
                    )
                    count += 1

            # Add substitute mappings
            items = shopping_list.items.all()
            for item in items[:5]:  # Process first 5 items
                substitutes = get_substitutes(item.name)
                if substitutes and not item.substitute_for:
                    # Add first substitute as an alternative
                    sub_data = substitutes[0]
                    substitute_item, created = Item.objects.get_or_create(
                        shopping_list=shopping_list,
                        name=sub_data['name'],
                        defaults={
                            'category': item.category,
                            'quantity': 1,
                            'unit': 'pcs',
                            'substitute_for': item
                        }
                    )
                    if created:
                        count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Added {count} seasonal and substitute items!'))
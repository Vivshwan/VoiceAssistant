from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.contrib.auth import login as auth_login
from .forms import UserRegistrationForm
from datetime import datetime
import json
import logging

from .models import (
    ShoppingList, Item, ShoppingHistory, UserPreference,
    SeasonalItem, SubstituteItem, PriceAlert
)
from .nlp_processor import NLPProcessor
from .seasonal_data import get_season, get_seasonal_items
from .substitutes_data import get_substitutes

logger = logging.getLogger(__name__)

# Initialize NLP processor
nlp_processor = NLPProcessor()


# ==================== MAIN VIEWS ====================

@login_required
def index(request):
    """Main page - displays shopping list with voice controls"""
    # Get or create active shopping list
    shopping_list, created = ShoppingList.objects.get_or_create(
        user=request.user,
        is_active=True,
        defaults={'name': 'My Shopping List'}
    )

    # Get all items for this list
    items = shopping_list.items.all()

    # Get smart suggestions
    suggestions = get_smart_suggestions(request.user)

    # Get seasonal items
    seasonal_items = get_seasonal_suggestions()

    # Get user preferences
    preferences, created = UserPreference.objects.get_or_create(user=request.user)

    context = {
        'shopping_list': shopping_list,
        'items': items,
        'total_items': items.count(),
        'checked_items': items.filter(is_checked=True).count(),
        'suggestions': suggestions,
        'seasonal_items': seasonal_items,
        'preferences': preferences,
        'total_price': shopping_list.get_total_price(),
    }

    return render(request, 'shopping/index.html', context)


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('shopping:index')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# ==================== VOICE COMMAND HANDLER ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def voice_command(request):
    """Handle voice commands from the frontend with all features"""
    try:
        data = json.loads(request.body)
        command_text = data.get('text', '')

        if not command_text:
            return JsonResponse({
                'success': False,
                'message': 'No command received'
            }, status=400)

        logger.info(f"Received voice command from {request.user.username}: {command_text}")

        # Process with NLP
        result = nlp_processor.process_command(command_text)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'message': f"Could not understand: {result['error']}"
            }, status=400)

        intent = result.get('intent', 'unknown')

        # Handle different intents
        if intent == 'add':
            return handle_add_command(request, result)
        elif intent == 'remove':
            return handle_remove_command(request, result)
        elif intent == 'search':
            return handle_search_command(request, result)
        elif intent == 'clear':
            return handle_clear_command(request, result)
        elif intent == 'seasonal':
            return handle_seasonal_command(request, result)
        elif intent == 'substitute':
            return handle_substitute_command(request, result)
        elif intent == 'price_alert':
            return handle_price_alert_command(request, result)
        elif intent == 'help':
            return JsonResponse({
                'success': True,
                'message': "You can say: 'Add milk', 'Remove bread', 'Search apples', 'Find items under $5', 'What's in season?', or 'What can substitute milk?'"
            })
        else:
            return JsonResponse({
                'success': False,
                'message': "Command not recognized. Try: 'Add milk', 'Remove bread', 'Search apples', or 'Find items under $5'"
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


# ==================== COMMAND HANDLERS ====================

def handle_add_command(request, result):
    """Handle add item command with price and brand support"""
    item_name = result.get('item')
    quantity = result.get('quantity', 1)
    unit = result.get('unit', 'pcs')
    category = result.get('category', 'other')
    price = result.get('price')
    brand = result.get('brand')

    if not item_name:
        return JsonResponse({
            'success': False,
            'message': "What would you like to add?"
        }, status=400)

    # Get or create active shopping list
    shopping_list, _ = ShoppingList.objects.get_or_create(
        user=request.user,
        is_active=True
    )

    # Check if item already exists
    existing_item = shopping_list.items.filter(
        name__iexact=item_name,
        is_checked=False
    ).first()

    if existing_item:
        # Update quantity instead of creating duplicate
        existing_item.quantity += quantity
        if price:
            existing_item.price = price
        if brand:
            existing_item.brand = brand
        existing_item.save()
        message = f"Updated {item_name}: now {existing_item.quantity} {existing_item.get_unit_display()}"
        if existing_item.price:
            message += f" at ${existing_item.price}"
    else:
        # Create new item
        new_item = Item.objects.create(
            shopping_list=shopping_list,
            name=item_name,
            quantity=quantity,
            unit=unit,
            category=category,
            price=price,
            brand=brand
        )
        message = f"Added {quantity} {new_item.get_unit_display()} of {item_name}"
        if new_item.price:
            message += f" at ${new_item.price}"

    return JsonResponse({
        'success': True,
        'message': message,
        'action': 'add',
        'item': {
            'name': item_name,
            'quantity': str(quantity),
            'unit': unit,
            'category': category,
            'price': str(price) if price else None,
            'brand': brand
        }
    })


def handle_remove_command(request, result):
    """Handle remove item command"""
    item_name = result.get('item')
    quantity = result.get('quantity', 1)

    if not item_name:
        return JsonResponse({
            'success': False,
            'message': "What would you like to remove?"
        }, status=400)

    # Get active list
    shopping_list = get_object_or_404(
        ShoppingList,
        user=request.user,
        is_active=True
    )

    # Find item by normalized name
    found_items = []
    for item in shopping_list.items.filter(is_checked=False):
        if normalize_item_name(item.name) == normalize_item_name(item_name):
            found_items.append(item)

    if not found_items:
        return JsonResponse({
            'success': False,
            'message': f"Couldn't find {item_name} in your list"
        }, status=404)

    item = found_items[0]

    # If quantity specified and item has enough, reduce quantity
    if quantity and item.quantity > quantity:
        item.quantity -= quantity
        item.save()
        return JsonResponse({
            'success': True,
            'message': f"Removed {quantity} {item.get_unit_display()} of {item_name}. Remaining: {item.quantity}"
        })
    else:
        # Remove the entire item
        item.delete()
        return JsonResponse({
            'success': True,
            'message': f"Removed {item_name} from your list"
        })


def handle_search_command(request, result):
    """Handle search command with price range and brand filtering - SQLite compatible"""
    query = result.get('item')
    price_range = result.get('price_range')
    brand = result.get('brand')

    if not query and not price_range and not brand:
        return JsonResponse({
            'success': False,
            'message': "What would you like to search for?"
        }, status=400)

    results = []

    # Get active shopping list
    shopping_list = get_object_or_404(
        ShoppingList,
        user=request.user,
        is_active=True
    )

    # Build query
    items_query = shopping_list.items.all()

    # Filter by name
    if query:
        items_query = items_query.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query)
        )

    # Filter by price range
    if price_range:
        try:
            max_price = float(price_range.replace('$', '').strip())
            items_query = items_query.filter(
                price__lte=max_price,
                price__isnull=False
            )
        except:
            pass

    # Filter by brand
    if brand:
        items_query = items_query.filter(brand__icontains=brand)

    list_items = items_query[:10]

    for item in list_items:
        results.append({
            'name': item.name,
            'category': item.category,
            'quantity': str(item.quantity),
            'unit': item.get_unit_display(),
            'price': str(item.price) if item.price else None,
            'brand': item.brand if item.brand else None,
            'source': 'current'
        })

    # Search in history (SQLite compatible - no DISTINCT ON)
    if query:
        history_items = ShoppingHistory.objects.filter(
            user=request.user,
            item_name__icontains=query
        ).order_by('-purchased_at')[:30]

        # Deduplicate using Python
        seen_names = set()
        for item in history_items:
            if item.item_name not in seen_names:
                seen_names.add(item.item_name)
                results.append({
                    'name': item.item_name,
                    'category': item.category,
                    'source': 'history',
                    'price': str(item.price) if item.price else None
                })

    if results:
        return JsonResponse({
            'success': True,
            'message': f"Found {len(results)} items",
            'results': results
        })
    else:
        return JsonResponse({
            'success': False,
            'message': f"No items found matching your criteria"
        }, status=404)


def handle_clear_command(request, result):
    """Handle clear all items command"""
    shopping_list = get_object_or_404(
        ShoppingList,
        user=request.user,
        is_active=True
    )

    count = shopping_list.items.filter(is_checked=False).count()
    shopping_list.items.filter(is_checked=False).delete()

    return JsonResponse({
        'success': True,
        'message': f"Cleared {count} items from your list",
        'action': 'clear'
    })


def handle_seasonal_command(request, result):
    """Handle seasonal recommendations command"""
    season = get_season()
    seasonal_items = get_seasonal_items(season)

    if seasonal_items:
        items = []
        for item in seasonal_items[:5]:
            items.append({
                'name': item['name'],
                'category': item['category'],
                'reason': item['reason']
            })

        return JsonResponse({
            'success': True,
            'message': f"🌱 {season.capitalize()} seasonal items:",
            'items': items,
            'season': season
        })
    else:
        return JsonResponse({
            'success': False,
            'message': f"No seasonal items found for {season}"
        }, status=404)


def handle_substitute_command(request, result):
    """Handle substitute recommendation command"""
    item_name = result.get('item')

    if not item_name:
        return JsonResponse({
            'success': False,
            'message': "What item would you like substitutes for?"
        }, status=400)

    substitutes = get_substitutes(item_name)

    if substitutes:
        sub_list = []
        for sub in substitutes[:5]:
            sub_list.append({
                'name': sub['name'],
                'reason': sub['reason']
            })

        return JsonResponse({
            'success': True,
            'message': f"Substitutes for {item_name}:",
            'substitutes': sub_list,
            'original': item_name
        })
    else:
        return JsonResponse({
            'success': False,
            'message': f"No substitutes found for {item_name}"
        }, status=404)


def handle_price_alert_command(request, result):
    """Handle price alert command"""
    item_name = result.get('item')
    price_range = result.get('price_range')

    if not item_name or not price_range:
        return JsonResponse({
            'success': False,
            'message': "Please specify an item and max price. Example: 'Alert me when milk is under $3'"
        }, status=400)

    try:
        max_price = float(price_range.replace('$', '').strip())

        # Create price alert
        alert, created = PriceAlert.objects.get_or_create(
            user=request.user,
            item_name=item_name,
            defaults={'max_price': max_price}
        )

        if not created:
            alert.max_price = max_price
            alert.is_active = True
            alert.save()

        return JsonResponse({
            'success': True,
            'message': f"✅ Price alert set for {item_name} under ${max_price}"
        })
    except:
        return JsonResponse({
            'success': False,
            'message': "Invalid price format. Example: 'Alert me when milk is under $3'"
        }, status=400)


# ==================== SMART SUGGESTIONS ====================

def get_smart_suggestions(user):
    """Generate smart suggestions based on history, seasons, and substitutes"""
    suggestions = []

    # 1. Get frequently bought items from user's history
    frequent_items = ShoppingHistory.objects.filter(
        user=user
    ).values('item_name', 'category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    for item in frequent_items:
        suggestions.append({
            'name': item['item_name'],
            'category': item['category'],
            'reason': f'Bought {item["count"]} times'
        })

    # 2. Get seasonal items if user has history
    if suggestions:
        seasonal_items = get_seasonal_suggestions()
        for item in seasonal_items[:3]:
            if not any(s['name'].lower() == item['name'].lower() for s in suggestions):
                suggestions.append(item)

    # 3. Get substitute suggestions
    if suggestions:
        top_item = suggestions[0]['name']
        substitutes = get_substitutes(top_item)
        for sub in substitutes[:2]:
            suggestions.append({
                'name': sub['name'],
                'category': 'substitute',
                'reason': f"💡 Alternative to {top_item}: {sub['reason']}"
            })

    # 4. If no history, show popular seasonal items
    if not suggestions:
        seasonal_items = get_seasonal_suggestions()
        for item in seasonal_items[:5]:
            suggestions.append({
                'name': item['name'],
                'category': item['category'],
                'reason': f"🌱 {item['reason']}"
            })

    return suggestions[:10]


def get_seasonal_suggestions():
    """Get seasonal item recommendations"""
    current_season = get_season()
    seasonal_items = get_seasonal_items(current_season)

    suggestions = []
    for item in seasonal_items[:5]:
        suggestions.append({
            'name': item['name'],
            'category': item['category'],
            'reason': f"{item['reason']} 🍂",
            'season': current_season
        })

    return suggestions


# ==================== NORMALIZATION HELPERS ====================

def normalize_item_name(name: str) -> str:
    """Normalize item name for comparison"""
    if not name:
        return ""

    name = name.lower().strip()

    # Remove plural 's'
    if name.endswith('ies') and len(name) > 3:
        name = name[:-3] + 'y'
    elif name.endswith('ves') and len(name) > 3:
        name = name[:-3] + 'f'
    elif name.endswith('ses') and len(name) > 3:
        name = name[:-2]
    elif name.endswith('xes') and len(name) > 3:
        name = name[:-2]
    elif name.endswith('zes') and len(name) > 3:
        name = name[:-2]
    elif name.endswith('ches') and len(name) > 3:
        name = name[:-2]
    elif name.endswith('shes') and len(name) > 3:
        name = name[:-2]
    elif name.endswith('es') and len(name) > 3:
        name = name[:-2]
    elif name.endswith('s') and len(name) > 3:
        name = name[:-1]

    # Special cases
    special_cases = {
        'potatoes': 'potato',
        'tomatoes': 'tomato',
        'mangoes': 'mango',
        'children': 'child',
        'women': 'woman',
        'men': 'man',
        'teeth': 'tooth',
        'feet': 'foot',
        'mice': 'mouse',
        'geese': 'goose',
    }

    if name in special_cases:
        name = special_cases[name]

    return name


# ==================== ITEM MANAGEMENT ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def toggle_item(request, item_id):
    """Toggle item checked status"""
    try:
        item = get_object_or_404(Item, id=item_id, shopping_list__user=request.user)
        item.is_checked = not item.is_checked
        item.save()

        # Save to history when checked
        if item.is_checked:
            ShoppingHistory.objects.create(
                user=request.user,
                item_name=item.name,
                category=item.category,
                quantity=item.quantity,
                price=item.price,
                season=item.season
            )

        return JsonResponse({
            'success': True,
            'message': f"{'Checked' if item.is_checked else 'Unchecked'} {item.name}",
            'is_checked': item.is_checked
        })
    except Item.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Item not found'
        }, status=404)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def remove_item(request, item_id):
    """Remove an item from the shopping list"""
    try:
        item = get_object_or_404(Item, id=item_id, shopping_list__user=request.user)
        item_name = item.name
        item.delete()
        return JsonResponse({
            'success': True,
            'message': f'Removed {item_name} from your list'
        })
    except Item.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Item not found'
        }, status=404)


@login_required
def get_price_alerts(request):
    """Get active price alerts for user"""
    alerts = PriceAlert.objects.filter(user=request.user, is_active=True)
    data = []
    for alert in alerts:
        data.append({
            'item_name': alert.item_name,
            'max_price': float(alert.max_price),
            'currency': alert.currency
        })
    return JsonResponse({
        'success': True,
        'alerts': data
    })


@login_required
def delete_price_alert(request, alert_id):
    """Delete a price alert"""
    try:
        alert = get_object_or_404(PriceAlert, id=alert_id, user=request.user)
        alert.is_active = False
        alert.save()
        return JsonResponse({
            'success': True,
            'message': 'Price alert deleted'
        })
    except PriceAlert.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Alert not found'
        }, status=404)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
import json
import logging

from .models import ShoppingList, Item, ShoppingHistory
from .nlp_processor import NLPProcessor
from .forms import UserRegistrationForm

logger = logging.getLogger(__name__)
nlp_processor = NLPProcessor()


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('shopping:index')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def index(request):
    shopping_list, created = ShoppingList.objects.get_or_create(
        user=request.user,
        is_active=True,
        defaults={'name': 'My Shopping List'}
    )
    items = shopping_list.items.all()
    suggestions = get_smart_suggestions(request.user)

    context = {
        'shopping_list': shopping_list,
        'items': items,
        'total_items': items.count(),
        'checked_items': items.filter(is_checked=True).count(),
        'suggestions': suggestions,
    }
    return render(request, 'shopping/index.html', context)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def voice_command(request):
    try:
        data = json.loads(request.body)
        command_text = data.get('text', '')
        if not command_text:
            return JsonResponse({'success': False, 'message': 'No command received'}, status=400)

        result = nlp_processor.process_command(command_text)
        if 'error' in result:
            return JsonResponse({'success': False, 'message': f"Could not understand: {result['error']}"}, status=400)

        intent = result.get('intent', 'unknown')

        if intent == 'add':
            return handle_add_command(request, result)
        elif intent == 'remove':
            return handle_remove_command(request, result)
        elif intent == 'search':
            return handle_search_command(request, result)
        elif intent == 'clear':
            return handle_clear_command(request, result)
        elif intent == 'help':
            return JsonResponse(
                {'success': True, 'message': "Say: 'Add milk', 'Remove bread', 'Search apples', or 'Clear list'"})
        else:
            return JsonResponse({'success': False,
                                 'message': "Command not recognized. Try: 'Add milk', 'Remove bread', or 'Search apples'"},
                                status=400)
    except Exception as e:
        logger.error(f"Error: {e}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


def handle_add_command(request, result):
    item_name = result.get('item')
    quantity = result.get('quantity', 1)
    unit = result.get('unit', 'pcs')
    category = result.get('category', 'other')

    if not item_name:
        return JsonResponse({'success': False, 'message': "What would you like to add?"}, status=400)

    shopping_list, _ = ShoppingList.objects.get_or_create(user=request.user, is_active=True)
    existing_item = shopping_list.items.filter(name__iexact=item_name, is_checked=False).first()

    if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
        message = f"Updated {item_name}: now {existing_item.quantity} {existing_item.get_unit_display()}"
    else:
        new_item = Item.objects.create(
            shopping_list=shopping_list,
            name=item_name,
            quantity=quantity,
            unit=unit,
            category=category
        )
        message = f"Added {quantity} {new_item.get_unit_display()} of {item_name}"

    return JsonResponse({'success': True, 'message': message, 'action': 'add'})


def handle_remove_command(request, result):
    item_name = result.get('item')
    if not item_name:
        return JsonResponse({'success': False, 'message': "What would you like to remove?"}, status=400)

    shopping_list = get_object_or_404(ShoppingList, user=request.user, is_active=True)
    try:
        item = shopping_list.items.get(name__iexact=item_name, is_checked=False)
        item.delete()
        return JsonResponse({'success': True, 'message': f"Removed {item_name} from your list", 'action': 'remove'})
    except Item.DoesNotExist:
        return JsonResponse({'success': False, 'message': f"Couldn't find {item_name} in your list"}, status=404)


def handle_search_command(request, result):
    query = result.get('item')
    if not query:
        return JsonResponse({'success': False, 'message': "What would you like to search for?"}, status=400)

    results = []
    shopping_list = get_object_or_404(ShoppingList, user=request.user, is_active=True)
    list_items = shopping_list.items.filter(Q(name__icontains=query) | Q(category__icontains=query))[:10]

    for item in list_items:
        results.append({
            'name': item.name,
            'category': item.category,
            'quantity': str(item.quantity),
            'unit': item.get_unit_display(),
            'source': 'current'
        })

    if results:
        return JsonResponse({'success': True, 'message': f"Found {len(results)} items", 'results': results})
    else:
        return JsonResponse({'success': False, 'message': f"No items found matching '{query}'"}, status=404)


def handle_clear_command(request, result):
    shopping_list = get_object_or_404(ShoppingList, user=request.user, is_active=True)
    count = shopping_list.items.filter(is_checked=False).count()
    shopping_list.items.filter(is_checked=False).delete()
    return JsonResponse({'success': True, 'message': f"Cleared {count} items from your list", 'action': 'clear'})


def get_smart_suggestions(user):
    suggestions = []
    frequent_items = ShoppingHistory.objects.filter(user=user).values('item_name', 'category').annotate(
        count=Count('id')).order_by('-count')[:5]
    for item in frequent_items:
        suggestions.append(
            {'name': item['item_name'], 'category': item['category'], 'reason': f'Bought {item["count"]} times'})
    return suggestions


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def toggle_item(request, item_id):
    try:
        item = get_object_or_404(Item, id=item_id, shopping_list__user=request.user)
        item.is_checked = not item.is_checked
        item.save()
        if item.is_checked:
            ShoppingHistory.objects.create(
                user=request.user,
                item_name=item.name,
                category=item.category,
                quantity=item.quantity
            )
        return JsonResponse({'success': True, 'message': f"{'Checked' if item.is_checked else 'Unchecked'} {item.name}",
                             'is_checked': item.is_checked})
    except Item.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def remove_item(request, item_id):
    try:
        item = get_object_or_404(Item, id=item_id, shopping_list__user=request.user)
        item_name = item.name
        item.delete()
        return JsonResponse({'success': True, 'message': f'Removed {item_name} from your list'})
    except Item.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)
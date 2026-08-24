from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Count
from shopping.models import Item, ShoppingList, ShoppingHistory
from shopping.nlp_processor import NLPProcessor
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    ItemSerializer,
    ShoppingListSerializer,
    ShoppingHistorySerializer,
    VoiceCommandSerializer
)
import logging

logger = logging.getLogger(__name__)
nlp_processor = NLPProcessor()


# ==================== AUTHENTICATION VIEWS ====================

class RegisterView(generics.CreateAPIView):
    """User registration API"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'message': 'User created successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login API"""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class LogoutView(APIView):
    """User logout API"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ==================== SHOPPING LIST VIEWS ====================

class ShoppingListView(generics.ListAPIView):
    """Get current shopping list"""
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user, is_active=True)


class ItemListCreateView(generics.ListCreateAPIView):
    """List all items and create new item"""
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shopping_list = ShoppingList.objects.get(user=self.request.user, is_active=True)
        return shopping_list.items.all()

    def perform_create(self, serializer):
        shopping_list = ShoppingList.objects.get(user=self.request.user, is_active=True)
        serializer.save(shopping_list=shopping_list)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific item"""
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shopping_list = ShoppingList.objects.get(user=self.request.user, is_active=True)
        return shopping_list.items.all()


class ItemToggleView(APIView):
    """Toggle item checked status"""
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            shopping_list = ShoppingList.objects.get(user=request.user, is_active=True)
            item = shopping_list.items.get(id=item_id)
            item.is_checked = not item.is_checked
            item.save()

            if item.is_checked:
                ShoppingHistory.objects.create(
                    user=request.user,
                    item_name=item.name,
                    category=item.category,
                    quantity=item.quantity
                )

            return Response({
                'success': True,
                'message': f"{'Checked' if item.is_checked else 'Unchecked'} {item.name}",
                'item': ItemSerializer(item).data
            })
        except Item.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Item not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ClearItemsView(APIView):
    """Clear all unchecked items"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        shopping_list = ShoppingList.objects.get(user=request.user, is_active=True)
        count = shopping_list.items.filter(is_checked=False).count()
        shopping_list.items.filter(is_checked=False).delete()
        return Response({
            'success': True,
            'message': f'Cleared {count} items from your list'
        })


# ==================== VOICE COMMAND VIEW ====================

class VoiceCommandView(APIView):
    """Process voice command via API"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VoiceCommandSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        command_text = serializer.validated_data.get('text')

        # Process with NLP
        result = nlp_processor.process_command(command_text)

        if 'error' in result:
            return Response({
                'success': False,
                'message': f"Could not understand: {result['error']}"
            }, status=status.HTTP_400_BAD_REQUEST)

        intent = result.get('intent', 'unknown')

        if intent == 'add':
            return self.handle_add(request, result)
        elif intent == 'remove':
            return self.handle_remove(request, result)
        elif intent == 'search':
            return self.handle_search(request, result)
        elif intent == 'clear':
            return self.handle_clear(request)
        elif intent == 'help':
            return Response({
                'success': True,
                'message': 'Available commands: Add, Remove, Search, Clear, Help'
            })
        else:
            return Response({
                'success': False,
                'message': "Command not recognized"
            }, status=status.HTTP_400_BAD_REQUEST)

    def handle_add(self, request, result):
        item_name = result.get('item')
        quantity = result.get('quantity', 1)
        unit = result.get('unit', 'pcs')
        category = result.get('category', 'other')

        if not item_name:
            return Response({
                'success': False,
                'message': "What would you like to add?"
            }, status=status.HTTP_400_BAD_REQUEST)

        shopping_list, _ = ShoppingList.objects.get_or_create(
            user=request.user,
            is_active=True
        )

        existing_item = shopping_list.items.filter(
            name__iexact=item_name,
            is_checked=False
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            message = f"Updated {item_name}: now {existing_item.quantity} {existing_item.get_unit_display()}"
            item_data = ItemSerializer(existing_item).data
        else:
            new_item = Item.objects.create(
                shopping_list=shopping_list,
                name=item_name,
                quantity=quantity,
                unit=unit,
                category=category
            )
            message = f"Added {quantity} {new_item.get_unit_display()} of {item_name}"
            item_data = ItemSerializer(new_item).data

        return Response({
            'success': True,
            'message': message,
            'action': 'add',
            'item': item_data
        })

    def handle_remove(self, request, result):
        item_name = result.get('item')

        if not item_name:
            return Response({
                'success': False,
                'message': "What would you like to remove?"
            }, status=status.HTTP_400_BAD_REQUEST)

        shopping_list = ShoppingList.objects.get(user=request.user, is_active=True)

        try:
            item = shopping_list.items.get(
                name__iexact=item_name,
                is_checked=False
            )
            item.delete()
            return Response({
                'success': True,
                'message': f"Removed {item_name} from your list",
                'action': 'remove'
            })
        except Item.DoesNotExist:
            return Response({
                'success': False,
                'message': f"Couldn't find {item_name} in your list"
            }, status=status.HTTP_404_NOT_FOUND)

    def handle_search(self, request, result):
        query = result.get('item')

        if not query:
            return Response({
                'success': False,
                'message': "What would you like to search for?"
            }, status=status.HTTP_400_BAD_REQUEST)

        results = []
        history_items = ShoppingHistory.objects.filter(
            user=request.user,
            item_name__icontains=query
        ).distinct('item_name')[:10]

        for item in history_items:
            results.append({
                'name': item.item_name,
                'category': item.category,
                'source': 'history'
            })

        shopping_list = ShoppingList.objects.get(user=request.user, is_active=True)
        list_items = shopping_list.items.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )[:5]

        for item in list_items:
            results.append({
                'name': item.name,
                'category': item.category,
                'quantity': str(item.quantity),
                'unit': item.get_unit_display(),
                'source': 'current'
            })

        return Response({
            'success': True,
            'message': f"Found {len(results)} items",
            'results': results
        })

    def handle_clear(self, request):
        shopping_list = ShoppingList.objects.get(user=request.user, is_active=True)
        count = shopping_list.items.filter(is_checked=False).count()
        shopping_list.items.filter(is_checked=False).delete()
        return Response({
            'success': True,
            'message': f"Cleared {count} items from your list",
            'action': 'clear'
        })


# ==================== SUGGESTIONS VIEW ====================

class SuggestionsView(generics.ListAPIView):
    """Get smart suggestions"""
    serializer_class = ShoppingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingHistory.objects.filter(user=self.request.user).order_by('-purchased_at')[:10]

    def list(self, request, *args, **kwargs):
        suggestions = []
        frequent_items = ShoppingHistory.objects.filter(
            user=request.user
        ).values('item_name', 'category').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        for item in frequent_items:
            suggestions.append({
                'name': item['item_name'],
                'category': item['category'],
                'reason': f'Bought {item["count"]} times'
            })

        return Response({
            'success': True,
            'suggestions': suggestions
        })


# ==================== HISTORY VIEW ====================

class HistoryView(generics.ListAPIView):
    """Get shopping history"""
    serializer_class = ShoppingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingHistory.objects.filter(user=self.request.user).order_by('-purchased_at')[:50]

    def delete(self, request):
        ShoppingHistory.objects.filter(user=request.user).delete()
        return Response({
            'success': True,
            'message': 'Shopping history cleared'
        })


# ==================== CATEGORIES VIEW ====================

class CategoriesView(APIView):
    """Get all categories with item counts"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shopping_list = ShoppingList.objects.get(user=request.user, is_active=True)
        categories = {}

        for item in shopping_list.items.all():
            category = item.get_category_display()
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        return Response({
            'success': True,
            'categories': categories
        })
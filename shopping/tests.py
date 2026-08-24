from django.test import TestCase
from django.contrib.auth.models import User
from .models import ShoppingList, Item
from .nlp_processor import NLPProcessor


class ShoppingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.shopping_list = ShoppingList.objects.create(user=self.user, name='Test List')

    def test_create_item(self):
        item = Item.objects.create(
            shopping_list=self.shopping_list,
            name='Milk',
            quantity=2,
            unit='l'
        )
        self.assertEqual(item.name, 'Milk')
        self.assertEqual(item.quantity, 2)


class NLPProcessorTest(TestCase):
    def setUp(self):
        self.processor = NLPProcessor()

    def test_add_command(self):
        result = self.processor.process_command('Add milk')
        self.assertEqual(result['intent'], 'add')
        self.assertEqual(result['item'], 'milk')

    def test_quantity_extraction(self):
        result = self.processor.process_command('Add 2 bottles of water')
        self.assertEqual(result['intent'], 'add')
        self.assertEqual(result['item'], 'water')
        self.assertEqual(result['quantity'], 2)
        self.assertEqual(result['unit'], 'bottle')
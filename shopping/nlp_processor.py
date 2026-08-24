import re
import logging
from typing import Dict, Any, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class NLPProcessor:
    def __init__(self):
        self.intent_patterns = {
            'add': r'\b(add|get|buy|need|want|grab|purchase|i want|i need)\b',
            'remove': r'\b(remove|delete|erase|take out|get rid of)\b',
            'search': r'\b(find|search|look for|show me|where is)\b',
            'clear': r'\b(clear|empty|delete all|remove all|reset)\b',
            'help': r'\b(help|what can i say|how to use)\b',
        }

        self.unit_mappings = {
            'kg': 'kg', 'kilogram': 'kg', 'kilo': 'kg',
            'g': 'g', 'gram': 'g',
            'l': 'l', 'liter': 'l', 'litre': 'l',
            'ml': 'ml', 'milliliter': 'ml',
            'pcs': 'pcs', 'piece': 'pcs', 'pieces': 'pcs',
            'pack': 'pack', 'packet': 'pack',
            'bottle': 'bottle', 'bottles': 'bottle',
            'can': 'can', 'cans': 'can',
            'box': 'box', 'boxes': 'box',
            'bag': 'bag', 'bags': 'bag',
        }

        self.category_keywords = {
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream'],
            'produce': ['apple', 'banana', 'orange', 'tomato', 'potato', 'onion', 'carrot', 'lettuce'],
            'meat': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'steak'],
            'bakery': ['bread', 'bun', 'bagel', 'croissant', 'cake', 'cookie'],
            'snacks': ['chip', 'cracker', 'cookie', 'candy', 'chocolate', 'nut'],
            'beverages': ['water', 'juice', 'soda', 'coffee', 'tea', 'drink'],
            'household': ['paper', 'towel', 'soap', 'shampoo', 'cleaner'],
            'personal': ['toothpaste', 'shampoo', 'soap', 'deodorant'],
            'frozen': ['frozen', 'pizza', 'ice cream', 'fries'],
        }

        self.word_numbers = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
            'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'dozen': 12,
        }

        self.filler_words = {'um', 'uh', 'like', 'you know', 'actually', 'basically', 'so', 'well'}

    def process_command(self, text: str) -> Dict[str, Any]:
        if not text:
            return {'error': 'Empty command'}

        text = text.strip()
        cleaned_text = self.clean_text(text)
        intent = self.extract_intent(cleaned_text)
        entities = self.extract_entities(cleaned_text)

        if entities.get('item'):
            entities['category'] = self.categorize_item(entities['item'])

        return {
            'original_text': text,
            'intent': intent,
            'item': entities.get('item'),
            'quantity': entities.get('quantity', Decimal('1')),
            'unit': entities.get('unit', 'pcs'),
            'category': entities.get('category', 'other'),
        }

    def clean_text(self, text: str) -> str:
        cleaned = text.lower()
        for filler in self.filler_words:
            cleaned = cleaned.replace(filler, '')
        return ' '.join(cleaned.split())

    def extract_intent(self, text: str) -> str:
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return intent
        return 'unknown'

    def extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {'item': None, 'quantity': Decimal('1'), 'unit': 'pcs'}

        quantity, unit = self.extract_quantity(text)
        if quantity:
            entities['quantity'] = quantity
        if unit:
            entities['unit'] = unit

        item_text = text
        for intent, pattern in self.intent_patterns.items():
            item_text = re.sub(pattern, '', item_text, flags=re.IGNORECASE)
        item_text = re.sub(r'\d+\.?\d*\s*(kg|g|l|ml|pcs|pack|bottle|can|box|bag)', '', item_text, flags=re.IGNORECASE)
        item_text = ' '.join(item_text.split()).strip()

        if item_text:
            entities['item'] = item_text

        return entities

    def extract_quantity(self, text: str) -> Tuple:
        # Check for word numbers (six, ten, etc.)
        words = text.lower().split()
        for i, word in enumerate(words):
            if word in self.word_numbers:
                num = self.word_numbers[word]
                unit = 'pcs'
                if i + 1 < len(words) and words[i + 1] in self.unit_mappings:
                    unit = self.unit_mappings[words[i + 1]]
                return Decimal(str(num)), unit

        # Check for digit numbers
        pattern = r'(\d+\.?\d*)\s*([a-z]+)?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                quantity = Decimal(match[0])
                unit = 'pcs'
                if len(match) > 1 and match[1] and match[1].lower() in self.unit_mappings:
                    unit = self.unit_mappings[match[1].lower()]
                return quantity, unit
            except:
                continue

        return None, None

    def categorize_item(self, item_name: str) -> str:
        if not item_name:
            return 'other'
        item_name = item_name.lower()
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in item_name:
                    return category
        return 'other'
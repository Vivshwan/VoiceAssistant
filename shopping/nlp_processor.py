"""
Natural Language Processing for voice commands
Smart: Auto-correction, intent detection, entity extraction, price extraction
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from spellchecker import SpellChecker
from textblob import TextBlob
import difflib

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        """Initialize NLP models and patterns"""

        # Spell checker
        self.spell = SpellChecker()

        # Smart: Dynamic word learning
        self.learned_words = set()

        # Common shopping items (dynamically grows)
        self.common_items = {
            'milk', 'bread', 'eggs', 'butter', 'cheese', 'yogurt',
            'apple', 'banana', 'orange', 'grapes', 'strawberry', 'blueberry',
            'chicken', 'fish', 'meat', 'beef', 'pork', 'lamb', 'turkey',
            'rice', 'pasta', 'noodles', 'sauce', 'oil', 'vinegar',
            'water', 'juice', 'soda', 'coffee', 'tea', 'smoothie',
            'soap', 'shampoo', 'toothpaste', 'towel', 'paper', 'detergent',
            'tomato', 'onion', 'garlic', 'ginger', 'potato', 'cucumber',
            'lettuce', 'spinach', 'carrot', 'broccoli', 'pepper', 'mushroom',
            'pizza', 'burger', 'sandwich', 'salad', 'soup', 'sushi',
            'cake', 'cookie', 'chocolate', 'candy', 'ice cream',
            'bread', 'bun', 'bagel', 'croissant', 'muffin', 'donut',
            'cheese', 'yogurt', 'butter', 'cream', 'curd', 'paneer',
            'shampoo', 'conditioner', 'soap', 'lotion', 'deodorant',
            'oranges', 'apples', 'bananas', 'grapes', 'strawberries',
            'egg', 'eggs', 'milk'
        }

        # Intent patterns (with new seasonal and substitute intents)
        self.intent_patterns = {
            'add': r'\b(add|get|buy|need|want|grab|purchase|please add|i want|i need|can i get|i would like|put|place|i\'ll take|give me|i love|i like|take|would like|could i have|may i have|need some|want some|bring|fetch|pick up|get me|i want to buy|i need to buy)\b',
            'remove': r'\b(remove|delete|erase|take out|get rid of|no need|forget|discard|cancel|don\'t need|take off|drop|delete item|take away|subtract|reduce|minus|less|take|remove item|remove from list)\b',
            'search': r'\b(find|search|look for|show me|where is|find me|locate|get me|looking for|find item|search for|show)\b',
            'clear': r'\b(clear|empty|delete all|remove all|reset|clear list|empty list|remove everything|wipe|remove all items|delete everything)\b',
            'help': r'\b(help|what can i say|how to use|commands|instructions|what do i do|how does this work|guide|help me)\b',
            'seasonal': r'\b(seasonal|in season|season|what\'s in season|current season|what\'s seasonal)\b',
            'substitute': r'\b(substitute|alternative|replacement|instead of|swap|replace|option|alternative for|can i use|what can i use)\b',
            'price_alert': r'\b(alert|notify|tell me when|price drop|under|less than|below)\s*\$?(\d+\.?\d*)\s*for\s*([a-z]+)',
        }

        # Unit mappings
        self.unit_mappings = {
            'kilo': 'kg', 'kilogram': 'kg', 'kg': 'kg',
            'gram': 'g', 'g': 'g',
            'liter': 'l', 'litre': 'l', 'l': 'l',
            'milliliter': 'ml', 'millilitre': 'ml', 'ml': 'ml',
            'ounce': 'oz', 'oz': 'oz',
            'pound': 'lb', 'lbs': 'lb', 'lb': 'lb',
            'piece': 'pcs', 'pieces': 'pcs', 'pcs': 'pcs',
            'pack': 'pack', 'packet': 'pack',
            'bottle': 'bottle', 'bottles': 'bottle',
            'can': 'can', 'cans': 'can',
            'box': 'box', 'boxes': 'box',
            'bag': 'bag', 'bags': 'bag',
            'cup': 'cup', 'cups': 'cup',
            'tbsp': 'tbsp', 'tablespoon': 'tbsp',
            'tsp': 'tsp', 'teaspoon': 'tsp',
            'dozen': 'pcs', 'dozens': 'pcs'
        }

        # Category keywords
        self.category_keywords = {
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream', 'yoghurt', 'curd', 'paneer'],
            'produce': ['apple', 'banana', 'orange', 'lettuce', 'tomato', 'potato', 'onion',
                       'carrot', 'broccoli', 'spinach', 'fruit', 'vegetable', 'salad', 'cucumber',
                       'pepper', 'mushroom', 'avocado', 'lemon', 'lime', 'garlic', 'ginger',
                       'strawberry', 'blueberry', 'grape'],
            'meat': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'steak', 'meat', 'lamb', 'turkey'],
            'bakery': ['bread', 'bun', 'bagel', 'croissant', 'cake', 'cookie', 'pastry', 'muffin', 'donut'],
            'snacks': ['chip', 'cracker', 'cookie', 'candy', 'chocolate', 'nut', 'snack', 'popcorn', 'pretzel'],
            'beverages': ['water', 'soda', 'juice', 'coffee', 'tea', 'drink', 'smoothie', 'milk shake', 'energy drink'],
            'household': ['paper', 'towel', 'soap', 'shampoo', 'cleaner', 'detergent', 'toilet', 'tissue', 'trash bag'],
            'personal': ['toothpaste', 'shampoo', 'soap', 'deodorant', 'lotion', 'razor', 'shaving cream', 'conditioner'],
            'frozen': ['frozen', 'pizza', 'ice cream', 'fries', 'nugget', 'waffle', 'pancake'],
        }

        # Word to number mapping
        self.word_numbers = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
            'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000,
            'dozen': 12, 'half': 0.5, 'quarter': 0.25
        }

        # Confidence threshold
        self.confidence_threshold = 0.6

        # Filler words
        self.filler_words = {'um', 'uh', 'like', 'you know', 'actually', 'basically', 'so', 'well',
                            'please', 'thank you', 'thanks', 'sorry', 'excuse me', 'ah', 'oh',
                            'hmm', 'erm', 'er', 'uhh', 'umm'}

        # Protected words that should never be auto-corrected
        self.protected_words = set()
        for intent, words in self.intent_patterns.items():
            # Extract words from patterns (remove regex special chars)
            for word in words.split('|'):
                cleaned = re.sub(r'[^a-zA-Z\s]', '', word)
                if cleaned:
                    self.protected_words.add(cleaned.lower())

    # ==================== AUTO-CORRECTION ====================

    def smart_correct(self, text: str) -> Dict[str, Any]:
        """Smart auto-correction that understands context"""
        if not text:
            return {'original': text, 'corrected': text, 'confidence': 1.0, 'changes': [], 'was_corrected': False}

        words = text.split()
        corrected_words = []
        changes = []

        for word in words:
            original_word = word
            word_lower = word.lower()

            # Skip auto-correction for protected words
            if word_lower in self.protected_words:
                corrected_words.append(word)
                continue

            # Skip short words
            if len(word) <= 2:
                corrected_words.append(word)
                continue

            # Skip words with numbers
            if any(char.isdigit() for char in word):
                corrected_words.append(word)
                continue

            # Skip email-like patterns
            if '@' in word or '.' in word:
                corrected_words.append(word)
                continue

            # Find best match from known words
            best_match = self.find_best_match(word)

            if best_match and best_match.lower() in self.protected_words:
                corrected_words.append(word)
                continue

            if best_match and best_match != word:
                confidence = self.calculate_confidence(word, best_match)
                if confidence > self.confidence_threshold:
                    corrected_words.append(best_match)
                    changes.append({
                        'original': original_word,
                        'corrected': best_match,
                        'confidence': confidence
                    })
                    logger.info(f"Smart corrected: '{word}' → '{best_match}' (confidence: {confidence:.2f})")
                    continue

            # Use TextBlob for contextual correction
            try:
                blob = TextBlob(word)
                corrected = str(blob.correct())

                if corrected.lower() in self.protected_words:
                    corrected_words.append(word)
                    continue

                if corrected != word and len(corrected) > 1:
                    if self.is_meaningful_word(corrected):
                        corrected_words.append(corrected)
                        changes.append({
                            'original': original_word,
                            'corrected': corrected,
                            'confidence': 0.7
                        })
                        logger.info(f"Context corrected: '{word}' → '{corrected}'")
                        continue
            except:
                pass

            corrected_words.append(word)

        corrected_text = ' '.join(corrected_words)

        return {
            'original': text,
            'corrected': corrected_text,
            'changes': changes,
            'was_corrected': text != corrected_text,
            'confidence': self.calculate_overall_confidence(changes) if changes else 1.0
        }

    def find_best_match(self, word: str) -> Optional[str]:
        """Find the best matching word from known words"""
        word_lower = word.lower()

        if word_lower in self.common_items:
            return word

        all_known = self.common_items.union(self.learned_words)
        matches = difflib.get_close_matches(word_lower, list(all_known), n=3, cutoff=0.6)

        if matches:
            return matches[0]

        # Check for plural/singular variations
        if word_lower.endswith('s') and word_lower[:-1] in all_known:
            return word_lower[:-1]
        if word_lower.endswith('es') and word_lower[:-2] in all_known:
            return word_lower[:-2]
        if word_lower.endswith('ies') and word_lower[:-3] + 'y' in all_known:
            return word_lower[:-3] + 'y'

        return None

    def calculate_confidence(self, original: str, corrected: str) -> float:
        """Calculate confidence score for a correction"""
        if not original or not corrected:
            return 0.0

        original = original.lower()
        corrected = corrected.lower()

        if original == corrected:
            return 1.0

        if len(original) == len(corrected):
            diff = sum(1 for a, b in zip(original, corrected) if a != b)
            if diff == 0:
                return 1.0
            elif diff == 1:
                return 0.9
            elif diff <= 2:
                return 0.75
            elif diff <= 3:
                return 0.6

        len_diff = abs(len(original) - len(corrected))
        if len_diff <= 1:
            return 0.8
        elif len_diff <= 2:
            return 0.6
        elif len_diff <= 3:
            return 0.4

        if corrected in self.common_items:
            return 0.8

        return 0.5

    def is_meaningful_word(self, word: str) -> bool:
        """Check if a word is meaningful"""
        if len(word) <= 2:
            return False

        if any(char in 'aeiouAEIOU' for char in word):
            return True

        if word.lower() in self.common_items:
            return True

        return False

    def calculate_overall_confidence(self, changes: list) -> float:
        """Calculate overall confidence of all corrections"""
        if not changes:
            return 1.0

        total = sum(change.get('confidence', 0.5) for change in changes)
        return total / len(changes)

    # ==================== WORD TO NUMBER CONVERSION ====================

    def word_to_number(self, word: str) -> Optional[float]:
        """Convert word numbers (six, ten, etc.) to digits"""
        word = word.lower().strip()
        return self.word_numbers.get(word)

    def extract_quantity(self, text: str) -> Tuple[Optional[Decimal], Optional[str]]:
        """Extract quantity and unit from text"""
        text_lower = text.lower()
        words = text_lower.split()

        # Try to find number words
        for i, word in enumerate(words):
            if word in self.word_numbers:
                num_value = self.word_numbers[word]
                if num_value > 0:
                    unit = 'pcs'
                    if i + 1 < len(words):
                        next_word = words[i + 1]
                        if next_word in self.unit_mappings:
                            unit = self.unit_mappings[next_word]
                        elif next_word == 'of' and i + 2 < len(words):
                            next_next = words[i + 2]
                            if next_next in self.unit_mappings:
                                unit = self.unit_mappings[next_next]
                        elif next_word in self.common_items:
                            pass
                    return Decimal(str(num_value)), unit

        # Check for compound numbers
        for i, word in enumerate(words):
            if word in self.word_numbers:
                num_value = self.word_numbers[word]
                if i + 1 < len(words) and words[i + 1] in self.word_numbers:
                    next_num = self.word_numbers[words[i + 1]]
                    if num_value in [20, 30, 40, 50, 60, 70, 80, 90]:
                        total = num_value + next_num
                        return Decimal(str(total)), 'pcs'

        # Try to find digit numbers
        pattern = r'(\d+\.?\d*)\s*([a-z]+)?'
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:
            try:
                quantity_str = match[0]
                unit_str = match[1] if len(match) > 1 else None
                quantity = Decimal(quantity_str)
                unit = 'pcs'
                if unit_str:
                    unit_lower = unit_str.lower()
                    if unit_lower in self.unit_mappings:
                        unit = self.unit_mappings[unit_lower]
                    elif unit_lower in ['of', 'for', 'with', 'and']:
                        continue
                return quantity, unit
            except:
                continue

        return None, None

    # ==================== PRICE EXTRACTION ====================

    def extract_price(self, text: str) -> Optional[Decimal]:
        """Extract price from text (e.g., '$5', 'under $5', '5 dollars')"""
        price_patterns = [
            r'\$?(\d+\.?\d*)\s*(dollars?)?',
            r'under\s*\$?(\d+\.?\d*)',
            r'less than\s*\$?(\d+\.?\d*)',
            r'below\s*\$?(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(dollars?)?\s*(or less|max|maximum)',
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Find the group with the number
                for group in match.groups():
                    if group and re.match(r'^\d+\.?\d*$', str(group)):
                        try:
                            return Decimal(group)
                        except:
                            pass
        return None

    def extract_brand(self, text: str) -> Optional[str]:
        """Extract brand from text"""
        brand_patterns = [
            r'\b(brand|from)\s+([a-z\s]+?)(\s+or|$|\s+and)',
            r'\b(organic|whole foods|store brand|generic)\s+([a-z]+)?',
            r'\b(brand)\s+([a-z]+)',
        ]

        for pattern in brand_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Try to find the brand name in groups
                for group in match.groups():
                    if group and len(group) > 2 and not group.isdigit():
                        # Clean the brand name
                        brand = re.sub(r'\s(or|and|with|for)$', '', group.strip())
                        if len(brand) > 1:
                            return brand
        return None

    # ==================== ITEM EXTRACTION ====================

    def extract_main_item(self, text: str) -> str:
        """Extract the main item from text using smart algorithms"""
        cleaned = text.lower()

        # Remove action words with regex
        action_patterns = [
            r'\bremove\b', r'\bdelete\b', r'\berase\b', r'\btake out\b',
            r'\bget rid of\b', r'\bdrop\b', r'\badd\b', r'\bget\b',
            r'\bbuy\b', r'\bneed\b', r'\bwant\b', r'\bgrab\b', r'\bpurchase\b',
            r'\bplease\b', r'\bcan i\b', r'\bi want\b', r'\bi need\b',
            r'\bget me\b', r'\bgive me\b', r'\bput\b', r'\bplace\b',
            r'\bclear\b', r'\bempty\b', r'\bdelete all\b', r'\bremove all\b',
            r'\bfind\b', r'\bsearch\b', r'\blook for\b', r'\bshow me\b',
            r'\bseasonal\b', r'\bin season\b',
            r'\bsubstitute\b', r'\balternative\b', r'\breplacement\b',
        ]

        for pattern in action_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Remove filler words
        for filler in self.filler_words:
            cleaned = cleaned.replace(filler, '')

        # Remove common words
        common_words = ['the', 'a', 'an', 'some', 'any', 'this', 'that', 'these', 'those',
                       'to', 'for', 'with', 'without', 'from', 'by', 'of', 'on', 'at', 'in']
        for word in common_words:
            cleaned = cleaned.replace(f' {word} ', ' ')

        # Remove price mentions
        cleaned = re.sub(r'\$?\d+\.?\d*\s*(dollars?)?', '', cleaned)

        # Clean up
        cleaned = ' '.join(cleaned.split())

        # Extract all potential items
        words = cleaned.split()
        potential_items = []

        for word in words:
            # Skip numbers
            if word.replace('.', '').isdigit():
                continue
            # Skip units
            if word in self.unit_mappings:
                continue
            # Skip if it's a number word
            if word in self.word_numbers:
                continue
            # Check if meaningful
            if self.is_meaningful_word(word):
                potential_items.append(word)

        if potential_items:
            potential_items.sort(key=len, reverse=True)
            return potential_items[0]

        return cleaned

    # ==================== INTENT DETECTION ====================

    def understand_intent(self, text: str) -> str:
        """Understand intent using context and smart analysis"""
        text_lower = text.lower()

        # Check for seasonal intent
        seasonal_keywords = ['seasonal', 'in season', 'season', 'what\'s in season', 'current season']
        if any(keyword in text_lower for keyword in seasonal_keywords):
            return 'seasonal'

        # Check for substitute intent
        substitute_keywords = ['substitute', 'alternative', 'replacement', 'instead of', 'swap', 'replace']
        if any(keyword in text_lower for keyword in substitute_keywords):
            return 'substitute'

        # Check for price alert intent
        if 'alert' in text_lower or 'notify' in text_lower:
            if re.search(r'under\s*\$?\d+', text_lower) or re.search(r'less than\s*\$?\d+', text_lower):
                return 'price_alert'

        # Check for clear words
        if 'clear' in text_lower.split():
            return 'clear'

        # Check for clear phrases
        clear_phrases = ['clear the list', 'empty list', 'delete all', 'remove all',
                         'remove everything', 'delete everything', 'wipe', 'clear list']
        if any(phrase in text_lower for phrase in clear_phrases):
            return 'clear'

        # Check for removal words
        remove_keywords = ['remove', 'delete', 'erase', 'take out', 'get rid of',
                          'take off', 'drop', 'no need', 'forget', 'discard',
                          'cancel', "don't need", 'subtract', 'reduce', 'minus', 'less']
        if any(word in text_lower for word in remove_keywords):
            return 'remove'

        # Check for search words
        search_keywords = ['find', 'search', 'look for', 'show me', 'where is',
                          'find me', 'locate', 'get me', 'looking for']
        if any(word in text_lower for word in search_keywords) or '?' in text:
            return 'search'

        # Check for help words
        help_keywords = ['help', 'how to', 'commands', 'instructions', 'what can i say']
        if any(word in text_lower for word in help_keywords):
            return 'help'

        # Check if it's just a single word (probably add if it's an item)
        if len(text_lower.split()) <= 3:
            for word in text_lower.split():
                if word in self.common_items:
                    return 'add'

        # Check for action words
        for intent, words in self.intent_patterns.items():
            if intent in ['seasonal', 'substitute', 'price_alert']:
                continue
            pattern = self.intent_patterns[intent]
            if re.search(pattern, text_lower, re.IGNORECASE):
                return intent

        return 'add'

    # ==================== CATEGORIZATION ====================

    def categorize_item(self, item_name: str) -> str:
        """Categorize item based on name"""
        if not item_name:
            return 'other'

        item_name = item_name.lower()

        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in item_name:
                    return category

        return 'other'

    # ==================== NORMALIZATION ====================

    def normalize_item(self, item_name: str) -> str:
        """Normalize item name to singular form"""
        if not item_name:
            return ""

        item_name = item_name.lower().strip()

        plural_rules = [
            (r'ies$', 'y'),
            (r'ves$', 'f'),
            (r'([sxz])es$', r'\1'),
            (r'([^aeiou])ies$', r'\1y'),
            (r's$', ''),
        ]

        for pattern, replacement in plural_rules:
            if re.search(pattern, item_name):
                item_name = re.sub(pattern, replacement, item_name)
                break

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

        if item_name in special_cases:
            item_name = special_cases[item_name]

        return item_name

    # ==================== MAIN PROCESSING ====================

    def process_command(self, text: str) -> Dict[str, Any]:
        """Main processing pipeline with all smart features"""
        if not text:
            return {'error': 'Empty command'}

        text = text.strip()
        logger.info(f"Processing command: {text}")

        try:
            # Detect intent from original text
            raw_intent = self.understand_intent(text)
            logger.info(f"Raw intent from original: {raw_intent}")

            # Smart auto-correction
            correction_result = self.smart_correct(text)
            corrected_text = correction_result['corrected']

            logger.info(f"Smart corrected: '{text}' → '{corrected_text}'")

            # Use raw intent or re-detect from corrected
            intent = raw_intent
            if intent == 'add':
                intent = self.understand_intent(corrected_text)
            logger.info(f"Final intent: {intent}")

            # Extract main item
            item = self.extract_main_item(corrected_text)

            if not item or len(item) <= 2:
                item = self.extract_main_item(text)

            if not item or len(item) <= 2:
                words = corrected_text.split()
                for word in words:
                    if self.is_meaningful_word(word) and len(word) > 2:
                        if self.word_to_number(word) is None:
                            item = word
                            break

            # Learn new words
            if item and len(item) > 2:
                self.learned_words.add(item.lower())
                self.common_items.add(item.lower())
                normalized = self.normalize_item(item)
                if normalized and normalized != item.lower():
                    self.learned_words.add(normalized)
                    self.common_items.add(normalized)

            # Extract quantity
            quantity, unit = self.extract_quantity(corrected_text)
            if not quantity:
                quantity, unit = self.extract_quantity(text)
            if not quantity:
                words = text.lower().split()
                for word in words:
                    num = self.word_to_number(word)
                    if num is not None and num > 0:
                        quantity = Decimal(str(num))
                        unit = 'pcs'
                        break

            if not quantity:
                quantity = Decimal('1')
            if not unit:
                unit = 'pcs'

            # ✅ NEW: Extract price and brand
            price = self.extract_price(corrected_text)
            if not price:
                price = self.extract_price(text)

            brand = self.extract_brand(corrected_text)
            if not brand:
                brand = self.extract_brand(text)

            # Extract price range (for search)
            price_range = None
            if price:
                # If price was extracted, it might be a price range
                price_range = f"${price}"

            # Categorize item
            category = 'other'
            if item:
                category = self.categorize_item(item)

            result = {
                'original_text': text,
                'corrected_text': corrected_text,
                'was_corrected': correction_result['was_corrected'],
                'corrections': correction_result['changes'],
                'confidence': correction_result['confidence'],
                'intent': intent,
                'item': item,
                'normalized_item': self.normalize_item(item) if item else '',
                'quantity': quantity,
                'unit': unit,
                'category': category,
                'price': price,
                'brand': brand,
                'price_range': price_range,
                'cleaned_text': corrected_text
            }

            logger.info(f"Processed result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return {
                'error': str(e),
                'original_text': text,
                'intent': 'unknown'
            }

    # ==================== HELPER METHODS ====================

    def clean_text(self, text: str) -> str:
        """Clean text by removing extra spaces and filler words"""
        cleaned = text.lower()
        for filler in self.filler_words:
            cleaned = cleaned.replace(filler, '')
        return ' '.join(cleaned.split())

    def extract_intent(self, text: str) -> str:
        """Extract intent using patterns"""
        text_lower = text.lower()
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return intent
        return 'unknown'

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {
            'item': None,
            'quantity': Decimal('1'),
            'unit': 'pcs',
            'price_range': None,
            'brand': None,
            'price': None,
        }

        # Extract quantity
        quantity, unit = self.extract_quantity(text)
        if quantity:
            entities['quantity'] = quantity
        if unit:
            entities['unit'] = unit

        # Extract price
        price = self.extract_price(text)
        if price:
            entities['price'] = price
            entities['price_range'] = f"${price}"

        # Extract brand
        brand = self.extract_brand(text)
        if brand:
            entities['brand'] = brand

        # Extract item
        item = self.extract_main_item(text)
        if item:
            entities['item'] = item

        return entities

    def auto_correct_sentence(self, text: str) -> str:
        """Auto-correct an entire sentence using TextBlob"""
        try:
            blob = TextBlob(text)
            return str(blob.correct())
        except:
            return text
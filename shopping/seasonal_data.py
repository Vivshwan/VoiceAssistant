"""
Seasonal recommendations data
"""

SEASONAL_ITEMS = {
    'summer': [
        {'name': 'Watermelon', 'category': 'produce', 'reason': 'Perfect for hot days'},
        {'name': 'Strawberries', 'category': 'produce', 'reason': 'In season now'},
        {'name': 'Ice Cream', 'category': 'frozen', 'reason': 'Great summer treat'},
        {'name': 'Lemonade', 'category': 'beverages', 'reason': 'Refreshing summer drink'},
        {'name': 'Cucumber', 'category': 'produce', 'reason': 'Hydrating summer vegetable'},
        {'name': 'Tomato', 'category': 'produce', 'reason': 'Summer ripe tomatoes'},
        {'name': 'Corn', 'category': 'produce', 'reason': 'Summer sweet corn'},
        {'name': 'Bell Peppers', 'category': 'produce', 'reason': 'Colorful summer peppers'},
        {'name': 'Zucchini', 'category': 'produce', 'reason': 'Summer squash'},
        {'name': 'Peaches', 'category': 'produce', 'reason': 'Juicy summer fruit'},
        {'name': 'Plums', 'category': 'produce', 'reason': 'Sweet summer fruit'},
        {'name': 'Grilling Items', 'category': 'meat', 'reason': 'BBQ season!'},
    ],
    'winter': [
        {'name': 'Oranges', 'category': 'produce', 'reason': 'Winter citrus'},
        {'name': 'Pomegranate', 'category': 'produce', 'reason': 'Winter superfood'},
        {'name': 'Sweet Potatoes', 'category': 'produce', 'reason': 'Winter comfort food'},
        {'name': 'Soup Ingredients', 'category': 'other', 'reason': 'Warm winter meals'},
        {'name': 'Hot Chocolate', 'category': 'beverages', 'reason': 'Cozy winter drink'},
        {'name': 'Cinnamon', 'category': 'other', 'reason': 'Warm winter spice'},
        {'name': 'Kale', 'category': 'produce', 'reason': 'Winter greens'},
        {'name': 'Brussels Sprouts', 'category': 'produce', 'reason': 'Winter vegetable'},
        {'name': 'Ginger', 'category': 'other', 'reason': 'Warm winter spice'},
        {'name': 'Apples', 'category': 'produce', 'reason': 'Winter storage fruit'},
        {'name': 'Pears', 'category': 'produce', 'reason': 'Winter fruit'},
        {'name': 'Hearty Stew Meat', 'category': 'meat', 'reason': 'Winter comfort food'},
    ],
    'spring': [
        {'name': 'Asparagus', 'category': 'produce', 'reason': 'Spring vegetable'},
        {'name': 'Strawberries', 'category': 'produce', 'reason': 'Spring berry season'},
        {'name': 'Artichokes', 'category': 'produce', 'reason': 'Spring vegetable'},
        {'name': 'Peas', 'category': 'produce', 'reason': 'Fresh spring peas'},
        {'name': 'Radishes', 'category': 'produce', 'reason': 'Spring radishes'},
        {'name': 'Lettuce', 'category': 'produce', 'reason': 'Spring greens'},
        {'name': 'Spinach', 'category': 'produce', 'reason': 'Spring spinach'},
        {'name': 'Rhubarb', 'category': 'produce', 'reason': 'Spring fruit'},
        {'name': 'Spring Onions', 'category': 'produce', 'reason': 'Spring vegetables'},
        {'name': 'Mushrooms', 'category': 'produce', 'reason': 'Spring morels'},
    ],
    'fall': [
        {'name': 'Pumpkin', 'category': 'produce', 'reason': 'Fall favorite'},
        {'name': 'Apples', 'category': 'produce', 'reason': 'Fall harvest'},
        {'name': 'Pears', 'category': 'produce', 'reason': 'Fall fruit'},
        {'name': 'Cranberries', 'category': 'produce', 'reason': 'Fall berry'},
        {'name': 'Butternut Squash', 'category': 'produce', 'reason': 'Fall squash'},
        {'name': 'Sweet Potatoes', 'category': 'produce', 'reason': 'Fall comfort food'},
        {'name': 'Brussels Sprouts', 'category': 'produce', 'reason': 'Fall vegetable'},
        {'name': 'Cauliflower', 'category': 'produce', 'reason': 'Fall vegetable'},
        {'name': 'Pomegranate', 'category': 'produce', 'reason': 'Fall fruit'},
        {'name': 'Cinnamon', 'category': 'other', 'reason': 'Fall spice'},
        {'name': 'Nutmeg', 'category': 'other', 'reason': 'Fall spice'},
        {'name': 'Apple Cider', 'category': 'beverages', 'reason': 'Fall drink'},
    ],
    'year_round': [
        {'name': 'Milk', 'category': 'dairy', 'reason': 'Essential staple'},
        {'name': 'Bread', 'category': 'bakery', 'reason': 'Essential staple'},
        {'name': 'Eggs', 'category': 'dairy', 'reason': 'Essential staple'},
        {'name': 'Butter', 'category': 'dairy', 'reason': 'Essential staple'},
        {'name': 'Rice', 'category': 'other', 'reason': 'Essential staple'},
        {'name': 'Pasta', 'category': 'other', 'reason': 'Essential staple'},
        {'name': 'Olive Oil', 'category': 'other', 'reason': 'Essential staple'},
        {'name': 'Salt', 'category': 'other', 'reason': 'Essential staple'},
        {'name': 'Pepper', 'category': 'other', 'reason': 'Essential staple'},
        {'name': 'Sugar', 'category': 'other', 'reason': 'Essential staple'},
        {'name': 'Coffee', 'category': 'beverages', 'reason': 'Daily essential'},
        {'name': 'Tea', 'category': 'beverages', 'reason': 'Daily essential'},
    ]
}


def get_season():
    """Get current season based on month"""
    import datetime
    month = datetime.datetime.now().month

    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    else:  # 9, 10, 11
        return 'fall'


def get_seasonal_items(season=None):
    """Get items for a specific season or current season"""
    if not season:
        season = get_season()
    return SEASONAL_ITEMS.get(season, [])
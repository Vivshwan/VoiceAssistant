"""
Product substitutes database
"""

SUBSTITUTES = {
    'milk': [
        {'name': 'Almond Milk', 'reason': 'Dairy-free alternative'},
        {'name': 'Soy Milk', 'reason': 'Plant-based alternative'},
        {'name': 'Oat Milk', 'reason': 'Popular plant-based milk'},
        {'name': 'Coconut Milk', 'reason': 'Creamy alternative'},
        {'name': 'Lactose-Free Milk', 'reason': 'For lactose intolerance'},
    ],
    'butter': [
        {'name': 'Margarine', 'reason': 'Plant-based alternative'},
        {'name': 'Coconut Oil', 'reason': 'Vegan baking alternative'},
        {'name': 'Olive Oil', 'reason': 'Healthy alternative'},
        {'name': 'Avocado', 'reason': 'Healthy fat alternative'},
        {'name': 'Greek Yogurt', 'reason': 'Low-fat baking alternative'},
    ],
    'sugar': [
        {'name': 'Honey', 'reason': 'Natural sweetener'},
        {'name': 'Maple Syrup', 'reason': 'Natural sweetener'},
        {'name': 'Stevia', 'reason': 'Zero-calorie alternative'},
        {'name': 'Agave Nectar', 'reason': 'Plant-based sweetener'},
        {'name': 'Coconut Sugar', 'reason': 'Low glycemic alternative'},
    ],
    'eggs': [
        {'name': 'Flax Eggs', 'reason': 'Vegan baking alternative'},
        {'name': 'Chia Eggs', 'reason': 'Vegan baking alternative'},
        {'name': 'Applesauce', 'reason': 'Baking binder alternative'},
        {'name': 'Mashed Banana', 'reason': 'Baking binder alternative'},
        {'name': 'Tofu', 'reason': 'Scrambled egg alternative'},
    ],
    'bread': [
        {'name': 'Gluten-Free Bread', 'reason': 'For gluten sensitivity'},
        {'name': 'Whole Wheat Bread', 'reason': 'Healthier alternative'},
        {'name': 'Rye Bread', 'reason': 'Flavorful alternative'},
        {'name': 'Sourdough', 'reason': 'Digestive friendly'},
        {'name': 'Corn Tortillas', 'reason': 'Gluten-free alternative'},
    ],
    'pasta': [
        {'name': 'Zucchini Noodles', 'reason': 'Low-carb alternative'},
        {'name': 'Brown Rice Pasta', 'reason': 'Gluten-free alternative'},
        {'name': 'Chickpea Pasta', 'reason': 'High-protein alternative'},
        {'name': 'Quinoa Pasta', 'reason': 'Gluten-free, high-protein'},
        {'name': 'Spaghetti Squash', 'reason': 'Low-carb alternative'},
    ],
    'rice': [
        {'name': 'Brown Rice', 'reason': 'Whole grain alternative'},
        {'name': 'Quinoa', 'reason': 'High-protein grain'},
        {'name': 'Cauliflower Rice', 'reason': 'Low-carb alternative'},
        {'name': 'Wild Rice', 'reason': 'Nutty flavor alternative'},
        {'name': 'Couscous', 'reason': 'Quick-cooking alternative'},
    ],
    'flour': [
        {'name': 'Almond Flour', 'reason': 'Low-carb, high-protein'},
        {'name': 'Coconut Flour', 'reason': 'High-fiber alternative'},
        {'name': 'Oat Flour', 'reason': 'Gluten-free alternative'},
        {'name': 'Rice Flour', 'reason': 'Gluten-free alternative'},
        {'name': 'Whole Wheat Flour', 'reason': 'Healthier alternative'},
    ],
    'oil': [
        {'name': 'Olive Oil', 'reason': 'Heart-healthy alternative'},
        {'name': 'Coconut Oil', 'reason': 'High-heat cooking'},
        {'name': 'Avocado Oil', 'reason': 'High-heat, healthy fat'},
        {'name': 'Canola Oil', 'reason': 'Neutral flavor'},
        {'name': 'Sunflower Oil', 'reason': 'High-heat alternative'},
    ],
    'chicken': [
        {'name': 'Tofu', 'reason': 'Plant-based protein'},
        {'name': 'Tempeh', 'reason': 'Fermented plant protein'},
        {'name': 'Seitan', 'reason': 'Wheat-based protein'},
        {'name': 'Turkey', 'reason': 'Leaner meat'},
        {'name': 'Mushrooms', 'reason': 'Umami-rich alternative'},
    ],
    'beef': [
        {'name': 'Ground Turkey', 'reason': 'Leaner meat'},
        {'name': 'Lamb', 'reason': 'Flavorful alternative'},
        {'name': 'Portobello Mushrooms', 'reason': 'Vegetarian alternative'},
        {'name': 'Lentils', 'reason': 'Plant-based protein'},
        {'name': 'Jackfruit', 'reason': 'Pulled meat texture alternative'},
    ],
    'fish': [
        {'name': 'Tofu', 'reason': 'Plant-based alternative'},
        {'name': 'Seaweed', 'reason': 'Ocean flavor alternative'},
        {'name': 'Seitan', 'reason': 'High-protein alternative'},
        {'name': 'Salmon', 'reason': 'Alternative fish option'},
        {'name': 'Tuna', 'reason': 'Alternative fish option'},
    ],
    'cream': [
        {'name': 'Coconut Cream', 'reason': 'Dairy-free alternative'},
        {'name': 'Cashew Cream', 'reason': 'Plant-based alternative'},
        {'name': 'Half and Half', 'reason': 'Lighter alternative'},
        {'name': 'Greek Yogurt', 'reason': 'Lower-fat alternative'},
        {'name': 'Oat Milk', 'reason': 'Plant-based alternative'},
    ],
    'cheese': [
        {'name': 'Nutritional Yeast', 'reason': 'Cheese flavor, vegan'},
        {'name': 'Vegan Cheese', 'reason': 'Plant-based alternative'},
        {'name': 'Low-Fat Cheese', 'reason': 'Lower-fat alternative'},
        {'name': 'Cottage Cheese', 'reason': 'Lower-fat alternative'},
        {'name': 'Feta Cheese', 'reason': 'Alternative cheese option'},
    ],
}


def get_substitutes(item_name):
    """Get substitutes for a specific item"""
    item_name = item_name.lower()

    # Check for exact match
    if item_name in SUBSTITUTES:
        return SUBSTITUTES[item_name]

    # Check for partial match
    for key, substitutes in SUBSTITUTES.items():
        if key in item_name or item_name in key:
            return substitutes

    return []


def get_all_substitute_items():
    """Get all items that have substitutes"""
    return list(SUBSTITUTES.keys())
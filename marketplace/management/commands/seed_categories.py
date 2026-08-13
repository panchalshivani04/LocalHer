from django.core.management.base import BaseCommand
from marketplace.models import Category

DEFAULT_CATEGORIES = [
    {
        'name': 'Food & Pickles',
        'icon_class': 'fa-jar',
        'description': 'Homemade pickles, papads, spices, and traditional recipes.'
    },
    {
        'name': 'Tailoring & Embroidery',
        'icon_class': 'fa-scissors',
        'description': 'Blouse stitching, kurti altering, custom embroidery, and dress designing.'
    },
    {
        'name': 'Baking & Desserts',
        'icon_class': 'fa-cake-candles',
        'description': 'Fresh home-baked cakes, cookies, chocolates, and pastries.'
    },
    {
        'name': 'Tiffin & Home Meals',
        'icon_class': 'fa-utensils',
        'description': 'Daily home-cooked meal boxes, breakfast, and lunch services.'
    },
    {
        'name': 'Beauty & Mehendi',
        'icon_class': 'fa-wand-magic-sparkles',
        'description': 'Bridal mehendi, hair styling, skin care, and party makeup.'
    },
    {
        'name': 'Handmade Crafts & Decor',
        'icon_class': 'fa-paint-brush',
        'description': 'Crochet items, home decor, wall art, and festive decorations.'
    },
    {
        'name': 'Jewellery & Accessories',
        'icon_class': 'fa-gem',
        'description': 'Handcrafted beads, terracotta jewellery, hair accessories, and bags.'
    },
    {
        'name': 'Tuition & Coaching',
        'icon_class': 'fa-graduation-cap',
        'description': 'School subject tutoring, music, art, and language classes.'
    },
]

class Command(BaseCommand):
    help = 'Seeds initial business categories for LocalHer'

    def handle(self, *args, **options):
        count = 0
        for cat_data in DEFAULT_CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon_class': cat_data['icon_class'],
                    'description': cat_data['description']
                }
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} categories.'))

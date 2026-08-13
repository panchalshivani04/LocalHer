from django.core.management.base import BaseCommand
from accounts.models import User, SellerProfile
from marketplace.models import Category, Product


class Command(BaseCommand):
    help = 'Seeds sample sellers and products into LocalHer'

    def handle(self, *args, **options):
        # Create Seller 1: Priya (Multi-category: Food & Pickles + Tailoring)
        user_priya, created = User.objects.get_or_create(
            username='priya',
            defaults={
                'email': 'priya@example.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'phone_number': '9876543210',
                'city': 'Ahmedabad',
                'area': 'Navrangpura',
                'pincode': '380009',
                'is_seller': True
            }
        )
        if created:
            user_priya.set_password('priya123')
            user_priya.save()

        seller_priya, _ = SellerProfile.objects.get_or_create(
            user=user_priya,
            defaults={
                'business_name': "Priya's Homemade & Stitching Studio",
                'bio': 'Homemade authentic Gujarati pickles, papad, and professional blouse stitching services.',
                'whatsapp_number': '9876543210',
                'city': 'Ahmedabad',
                'area': 'Navrangpura',
                'pincode': '380009',
                'is_verified': True
            }
        )

        # Create Seller 2: Ananya (Baking & Crafts)
        user_ananya, created = User.objects.get_or_create(
            username='ananya',
            defaults={
                'email': 'ananya@example.com',
                'first_name': 'Ananya',
                'last_name': 'Patel',
                'phone_number': '9123456789',
                'city': 'Ahmedabad',
                'area': 'Bodakdev',
                'pincode': '380054',
                'is_seller': True
            }
        )
        if created:
            user_ananya.set_password('ananya123')
            user_ananya.save()

        seller_ananya, _ = SellerProfile.objects.get_or_create(
            user=user_ananya,
            defaults={
                'business_name': 'Ananya Bakehouse & Crochet',
                'bio': 'Fresh eggless cakes, custom brownies, and handmade crochet accessories.',
                'whatsapp_number': '9123456789',
                'city': 'Ahmedabad',
                'area': 'Bodakdev',
                'pincode': '380054',
                'is_verified': True
            }
        )

        # Categories
        cat_food = Category.objects.filter(name__icontains='Food').first()
        cat_tailor = Category.objects.filter(name__icontains='Tailoring').first()
        cat_bake = Category.objects.filter(name__icontains='Baking').first()
        cat_craft = Category.objects.filter(name__icontains='Crafts').first()

        # Demo Products for Priya
        if cat_food:
            Product.objects.get_or_create(
                seller=seller_priya,
                title='Traditional Spicy Mango Pickle (500g)',
                defaults={
                    'category': cat_food,
                    'description': 'Sun-dried raw mangoes pickled with authentic spices and pure mustard oil. No artificial preservatives.',
                    'price': 250.00,
                    'price_unit': 'per jar',
                    'product_type': 'PRODUCT',
                    'city': seller_priya.city,
                    'area': seller_priya.area,
                    'pincode': seller_priya.pincode,
                }
            )
            Product.objects.get_or_create(
                seller=seller_priya,
                title='Authentic Lemon Chili Pickle (250g)',
                defaults={
                    'category': cat_food,
                    'description': 'Juicy lemons cured naturally with green chilies and rock salt.',
                    'price': 180.00,
                    'price_unit': 'per jar',
                    'product_type': 'PRODUCT',
                    'city': seller_priya.city,
                    'area': seller_priya.area,
                    'pincode': seller_priya.pincode,
                }
            )

        if cat_tailor:
            Product.objects.get_or_create(
                seller=seller_priya,
                title='Custom Designer Blouse Stitching',
                defaults={
                    'category': cat_tailor,
                    'description': 'Perfect fit blouse stitching with neck patterns, piping, and dori. Turnaround time: 3 days.',
                    'price': 650.00,
                    'price_unit': 'per piece',
                    'product_type': 'SERVICE',
                    'city': seller_priya.city,
                    'area': seller_priya.area,
                    'pincode': seller_priya.pincode,
                }
            )
            Product.objects.get_or_create(
                seller=seller_priya,
                title='Designer Kurti Alteration & Stitching',
                defaults={
                    'category': cat_tailor,
                    'description': 'Full suit & kurti tailoring with custom sleeve and neck designs.',
                    'price': 450.00,
                    'price_unit': 'per suit',
                    'product_type': 'SERVICE',
                    'city': seller_priya.city,
                    'area': seller_priya.area,
                    'pincode': seller_priya.pincode,
                }
            )

        # Demo Products for Ananya
        if cat_bake:
            Product.objects.get_or_create(
                seller=seller_ananya,
                title='Fresh Chocolate Fudge Birthday Cake (1kg)',
                defaults={
                    'category': cat_bake,
                    'description': '100% eggless rich chocolate fudge cake customized with name and birthday message.',
                    'price': 850.00,
                    'price_unit': 'per kg',
                    'product_type': 'PRODUCT',
                    'city': seller_ananya.city,
                    'area': seller_ananya.area,
                    'pincode': seller_ananya.pincode,
                }
            )

        if cat_craft:
            Product.objects.get_or_create(
                seller=seller_ananya,
                title='Handmade Crochet Tote Bag',
                defaults={
                    'category': cat_craft,
                    'description': 'Durable cotton yarn handcrafted tote bag in pastel aesthetic colors.',
                    'price': 499.00,
                    'price_unit': 'per bag',
                    'product_type': 'PRODUCT',
                    'city': seller_ananya.city,
                    'area': seller_ananya.area,
                    'pincode': seller_ananya.pincode,
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded sample sellers and products.'))

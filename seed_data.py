import os
import shutil
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calicutstar_project.settings')
django.setup()

from django.utils.text import slugify
from restaurant.models import Category, MenuItem, SpecialItem, ComboOffer, GalleryItem, Review

def seed_database():
    print("Starting database seeding...")

    # Define paths for media copy
    static_images_dir = os.path.join('static', 'images')
    media_dir = 'media'
    
    os.makedirs(os.path.join(media_dir, 'menu_items'), exist_ok=True)
    os.makedirs(os.path.join(media_dir, 'specials'), exist_ok=True)
    os.makedirs(os.path.join(media_dir, 'combos'), exist_ok=True)
    os.makedirs(os.path.join(media_dir, 'gallery'), exist_ok=True)

    # 1. Clear existing data
    print("Clearing old data...")
    Category.objects.all().delete()
    MenuItem.objects.all().delete()
    SpecialItem.objects.all().delete()
    ComboOffer.objects.all().delete()
    GalleryItem.objects.all().delete()
    Review.objects.all().delete()

    # Helper function to copy images
    def copy_media_asset(src_filename, dest_subfolder, dest_filename):
        src_path = os.path.join(static_images_dir, src_filename)
        dest_path = os.path.join(media_dir, dest_subfolder, dest_filename)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            return f"{dest_subfolder}/{dest_filename}"
        return None

    # Copy files for seeding
    biriyani_media_path = copy_media_asset('hero_biriyani.png', 'menu_items', 'biriyani.png')
    porotta_media_path = copy_media_asset('hero_porotta.png', 'menu_items', 'porotta.png')
    fish_media_path = copy_media_asset('hero_fish.png', 'menu_items', 'fish.png')
    spices_media_path = copy_media_asset('about_main.png', 'menu_items', 'spices.png')

    special_fish_path = copy_media_asset('hero_fish.png', 'specials', 'special_fish.png')
    special_mutton_path = copy_media_asset('about_main.png', 'specials', 'special_mutton.png')
    special_beef_path = copy_media_asset('hero_porotta.png', 'specials', 'special_beef.png')
    special_chicken_path = copy_media_asset('hero_biriyani.png', 'specials', 'special_chicken.png')

    combo1_path = copy_media_asset('hero_porotta.png', 'combos', 'combo_porotta.png')
    combo2_path = copy_media_asset('hero_biriyani.png', 'combos', 'combo_biriyani.png')

    gallery_interior_path = copy_media_asset('about_main.png', 'gallery', 'gallery_interior.png')
    gallery_food_path = copy_media_asset('hero_biriyani.png', 'gallery', 'gallery_food.png')
    gallery_dining_path = copy_media_asset('hero_porotta.png', 'gallery', 'gallery_dining.png')
    gallery_signature_path = copy_media_asset('hero_fish.png', 'gallery', 'gallery_signature.png')

    # 2. Seed Categories
    print("Seeding Categories...")
    categories_data = [
        {"name": "Breakfast", "icon": "bi-egg-fried", "order": 1},
        {"name": "Meals", "icon": "bi-egg", "order": 2},
        {"name": "Biriyani", "icon": "bi-fire", "order": 3},
        {"name": "Fish Dishes", "icon": "bi-water", "order": 4},
        {"name": "Chicken Dishes", "icon": "bi-award", "order": 5},
        {"name": "Beef Dishes", "icon": "bi-shield-check", "order": 6},
        {"name": "Mutton Dishes", "icon": "bi-bookmark-star", "order": 7},
        {"name": "Snacks", "icon": "bi-cookie", "order": 8},
        {"name": "Juices & Beverages", "icon": "bi-cup-straw", "order": 9},
    ]

    categories = {}
    for cat in categories_data:
        c = Category.objects.create(
            name=cat["name"],
            slug=slugify(cat["name"]),
            icon=cat["icon"],
            order_index=cat["order"]
        )
        categories[cat["name"]] = c

    # 3. Seed Menu Items
    print("Seeding Menu Items...")
    menu_items_data = [
        # Breakfast
        {"name": "Soft Appam with Egg Roast", "category": "Breakfast", "price": 12.00, "desc": "Two soft-centered lacy rice hoppers served with Kerala style spicy egg roast gravy.", "image": porotta_media_path, "veg": False, "spicy": True},
        {"name": "Puttu with Kadala Curry", "category": "Breakfast", "price": 10.00, "desc": "Steamed ground rice and coconut cylinders served with authentic spicy black chickpea curry.", "image": spices_media_path, "veg": True, "spicy": True},
        {"name": "Neyyappam & Tea Combo", "category": "Breakfast", "price": 8.00, "desc": "Traditional sweet fried rice fritter served with hot cardamom Sulaimani tea.", "image": None, "veg": True, "spicy": False},
        
        # Meals
        {"name": "Authentic Kerala Veg Meals", "category": "Meals", "price": 15.00, "desc": "Traditional brown rice served with Sambar, Avial, Thoran, Kalan, Pickle, Pappadam, and Payasam on a banana leaf.", "image": spices_media_path, "veg": True, "spicy": False},
        {"name": "Calicut Star Fish Meals", "category": "Meals", "price": 20.00, "desc": "Our signature Veg Meals supplemented with rich traditional Malabar red fish curry gravy.", "image": fish_media_path, "veg": False, "spicy": True},

        # Biriyani
        {"name": "Malabar Chicken Biriyani", "category": "Biriyani", "price": 18.00, "desc": "Fragrant Kaima rice cooked with choice chicken pieces, rich spices, and pure ghee. Authentic Calicut taste.", "image": biriyani_media_path, "veg": False, "spicy": True},
        {"name": "Malabar Mutton Biriyani", "category": "Biriyani", "price": 25.00, "desc": "Aromatic, slow-cooked Kaima rice layered with tender mutton chunks in a secret spice blend.", "image": biriyani_media_path, "veg": False, "spicy": True},
        {"name": "Malabar Beef Biriyani", "category": "Biriyani", "price": 20.00, "desc": "Traditional layered rice preparation showcasing tender beef pieces marinated in authentic Malabar spices.", "image": biriyani_media_path, "veg": False, "spicy": True},

        # Fish Dishes
        {"name": "Red Chatti Fish Curry", "category": "Fish Dishes", "price": 18.00, "desc": "Traditional kingfish curry cooked in spicy tamarind sauce in a clay pot.", "image": fish_media_path, "veg": False, "spicy": True},
        {"name": "King Fish Fry", "category": "Fish Dishes", "price": 15.00, "desc": "Fresh fish marinated in rustic homemade chilly-garlic paste and shallow fried in coconut oil.", "image": fish_media_path, "veg": False, "spicy": True},
        {"name": "Malabar Fish Mango Curry", "category": "Fish Dishes", "price": 22.00, "desc": "Mildly spiced, creamy coconut-based curry cooked with raw green mango slices and fish.", "image": fish_media_path, "veg": False, "spicy": False},

        # Chicken Dishes
        {"name": "Malabar Chicken Kadai", "category": "Chicken Dishes", "price": 16.00, "desc": "Spicy chicken stir-fry cooked with bell peppers, tomatoes, and freshly ground kadai spices.", "image": None, "veg": False, "spicy": True},
        {"name": "Chilly Chicken Dry", "category": "Chicken Dishes", "price": 15.00, "desc": "Indo-Chinese style crispy chicken stir-fried with green chilies, onions, and bell peppers.", "image": None, "veg": False, "spicy": True},
        {"name": "Kerala Chicken Stew", "category": "Chicken Dishes", "price": 18.00, "desc": "Tender chicken pieces simmered in mild coconut milk gravy with potatoes and carrots.", "image": biriyani_media_path, "veg": False, "spicy": False},
        {"name": "Chicken Kondattam", "category": "Chicken Dishes", "price": 20.00, "desc": "Crispy fried boneless chicken tossed in a spicy, tangy sun-dried condiment sauce.", "image": biriyani_media_path, "veg": False, "spicy": True},

        # Beef Dishes
        {"name": "Beef Kondattam", "category": "Beef Dishes", "price": 22.00, "desc": "Spicy, crunchy beef bites tossed with roasted red chillies, garlic, and vinegar sauces.", "image": porotta_media_path, "veg": False, "spicy": True},
        {"name": "Traditional Beef Dry Fry", "category": "Beef Dishes", "price": 18.00, "desc": "Authentic Kerala Beef Ularthiyathu slow-roasted with coconut bites, coriander, and black pepper.", "image": porotta_media_path, "veg": False, "spicy": True},
        {"name": "Spicy Beef Chilly", "category": "Beef Dishes", "price": 18.00, "desc": "Sliced beef wok-tossed with green chilies, red onions, ginger, and green bell peppers.", "image": porotta_media_path, "veg": False, "spicy": True},

        # Mutton Dishes
        {"name": "Malabar Mutton Kuruma", "category": "Mutton Dishes", "price": 24.00, "desc": "Rich, creamy mutton curry prepared with cashews, coconut paste, and mild aromatic spices.", "image": None, "veg": False, "spicy": False},
        {"name": "Mutton Stew", "category": "Mutton Dishes", "price": 22.00, "desc": "Homely style mutton chunks simmered in spiced coconut milk with onions and green chilies.", "image": spices_media_path, "veg": False, "spicy": False},
        {"name": "Mutton Masala Roast", "category": "Mutton Dishes", "price": 26.00, "desc": "Thick semi-gravy mutton roast cooked with sliced onions, tomatoes, ginger, and roasted spices.", "image": None, "veg": False, "spicy": True},

        # Snacks
        {"name": "Sweet Unnakaya", "category": "Snacks", "price": 5.00, "desc": "Malabar classic: boiled ripe plantain mashed, stuffed with sweetened coconut & raisins, and deep-fried.", "image": None, "veg": True, "spicy": False},
        {"name": "Pazham Pori (Banana Fritters)", "category": "Snacks", "price": 4.00, "desc": "Crispy gold fritters made from ripe Kerala bananas. Perfect evening tea companion.", "image": None, "veg": True, "spicy": False},
        {"name": "Kerala Samosa (Beef/Chicken)", "category": "Snacks", "price": 3.00, "desc": "Triangle pastry sheets filled with spiced minced meat, onions, and curry leaves.", "image": None, "veg": False, "spicy": True},

        # Juices & Beverages
        {"name": "Sulaimani Cardamom Tea", "category": "Juices & Beverages", "price": 2.00, "desc": "Traditional black tea brewed with cardamom and mint, finished with a dash of lime juice.", "image": None, "veg": True, "spicy": False},
        {"name": "Malabar Special Shake", "category": "Juices & Beverages", "price": 10.00, "desc": "Signature rich shake blended with dried fruits, nuts, dates, and fresh ice cream.", "image": None, "veg": True, "spicy": False},
        {"name": "Mint Lime Cooler", "category": "Juices & Beverages", "price": 5.00, "desc": "Refreshing fresh lime juice blended with fresh mint leaves and sugar syrup.", "image": None, "veg": True, "spicy": False},
    ]

    for item in menu_items_data:
        MenuItem.objects.create(
            name=item["name"],
            category=categories[item["category"]],
            description=item["desc"],
            price=item["price"],
            image=item["image"],
            is_available=True,
            is_vegetarian=item["veg"],
            is_spicy=item["spicy"],
            order_index=0
        )

    # 4. Seed Today's Specials
    print("Seeding Today's Specials...")
    specials_data = [
        # Fish Specials
        {"name": "Clay Pot Fish Curry", "desc": "Fresh Kingfish simmered in cocum-sour spicy red gravy. Tastes best with boiled tapioca (Kappa).", "price": 20.00, "image": special_fish_path, "group": "Fish Specials"},
        {"name": "Fish Mango Curry", "desc": "Traditional Calicut fish dish in a light gravy of ground coconut, ginger, raw mango, and fresh curry leaves.", "price": 22.00, "image": special_fish_path, "group": "Fish Specials"},
        
        # Mutton Specials
        {"name": "Mutton Stew", "desc": "Rich, comforting stew with tender mutton pieces cooked in fresh first-press coconut milk with potatoes.", "price": 24.00, "image": special_mutton_path, "group": "Mutton Specials"},
        {"name": "Mutton Kuruma", "desc": "Classic Malabar style mutton curry with cashew paste, cardamom, and fresh coriander spices.", "price": 25.00, "image": special_mutton_path, "group": "Mutton Specials"},
        
        # Beef Specials
        {"name": "Beef Kondattam", "desc": "Thin strips of beef deep fried and tossed with dry chillies, ginger, vinegar, and onions. Extra spicy.", "price": 22.00, "image": special_beef_path, "group": "Beef Specials"},
        {"name": "Beef Dry Fry (Ularthiyathu)", "desc": "Slow-roasted beef tossed with crispy coconut slices, garam masala, and roasted curry leaves. Our bestseller.", "price": 18.00, "image": special_beef_path, "group": "Beef Specials"},
        
        # Chicken Specials
        {"name": "Chicken Stew", "desc": "Tender chicken simmered gently in coconut milk with green chilies, ginger, and spices. Pairs best with Appam.", "price": 18.00, "image": special_chicken_path, "group": "Chicken Specials"},
        {"name": "Chicken Kondattam", "desc": "Spicy, deep-fried chicken cubes coated in a dark, sticky, caramelized chilly-condiment glaze.", "price": 20.00, "image": special_chicken_path, "group": "Chicken Specials"},
    ]

    for spec in specials_data:
        SpecialItem.objects.create(
            name=spec["name"],
            description=spec["desc"],
            price=spec["price"],
            image=spec["image"],
            is_available=True,
            category_group=spec["group"]
        )

    # 5. Seed Combo Offers
    print("Seeding Combo Offers...")
    combos_data = [
        {"title": "Porotta + Beef Curry + Tea", "desc": "Three pieces of flaky hot porottas, served with traditional slow-cooked beef roast and a piping hot cup of Sulaimani tea.", "orig": 24.00, "spec": 18.00, "image": combo1_path},
        {"title": "Malabar Chicken Biriyani + Lime", "desc": "Our signature chicken biriyani made with authentic Kaima rice, served with Mint Lime cooler, raitha, pickle, and dates.", "orig": 28.00, "spec": 22.00, "image": combo2_path},
        {"title": "Appam + Chicken Stew + Sulaimani", "desc": "Three soft-centered lacy rice appams, served with aromatic chicken stew simmered in coconut milk and sweet cardamom tea.", "orig": 22.00, "spec": 16.00, "image": combo2_path},
    ]

    for comb in combos_data:
        ComboOffer.objects.create(
            title=comb["title"],
            description=comb["desc"],
            original_price=comb["orig"],
            special_price=comb["spec"],
            image=comb["image"],
            is_available=True
        )

    # 6. Seed Gallery Items
    print("Seeding Gallery Items...")
    gallery_data = [
        {"title": "Traditional Dining Ambience", "cat": "Interior", "desc": "Traditional Kerala inspired wood carvings and family layouts in Riyadh.", "image": gallery_interior_path},
        {"title": "Spiced Preparation Counter", "cat": "Interior", "desc": "Traditional clay pots and fresh spices used in our kitchen.", "image": gallery_interior_path},
        {"title": "Aromatic Malabar Biriyani", "cat": "Food", "desc": "Ghee rice layered with authentic spices and chicken.", "image": gallery_food_path},
        {"title": "Layered Porotta Service", "cat": "Food", "desc": "Flaky, layered porottas fresh off the griddle.", "image": gallery_dining_path},
        {"title": "Guest Lunch Service", "cat": "Dining", "desc": "Families experiencing authentic banana leaf dining.", "image": gallery_dining_path},
        {"title": "Signture Red Fish Curry", "cat": "Signature", "desc": "Our authentic red chatti fish curry, slow-simmered.", "image": gallery_signature_path},
    ]

    for gal in gallery_data:
        GalleryItem.objects.create(
            title=gal["title"],
            category=gal["cat"],
            caption=gal["desc"],
            image=gal["image"]
        )

    # 7. Seed Reviews
    print("Seeding Guest Reviews...")
    reviews_data = [
        {"name": "Rashid Al-Qahtani", "rating": 5, "text": "Calicut Star brings the absolute best Kerala food in Riyadh. The flaky porotta and beef dry fry are legendary. Highly recommended for families!"},
        {"name": "John Mathew", "rating": 5, "text": "Being from Kerala, I am very picky about my biriyani. The Malabar Chicken Biriyani at Calicut Star matches the authentic taste of Calicut town. Extremely satisfied."},
        {"name": "Siddharth Verma", "rating": 4, "text": "Very delicious food with authentic taste and highly friendly service. The pricing is very reasonable and portions are generous. The cardamom tea was a perfect end to the meal."},
        {"name": "Amina Ibrahim", "rating": 5, "text": "Clean, authentic, and cozy. The family dining area is very comfortable. We ordered the Chicken Stew with Appam, and it was outstandingly soft and fresh."},
    ]

    for rev in reviews_data:
        Review.objects.create(
            customer_name=rev["name"],
            rating=rev["rating"],
            review_text=rev["text"],
            is_approved=True
        )

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()

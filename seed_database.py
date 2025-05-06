"""
Seed script for populating the database with test users and artifacts.
Run with: python manage.py shell < seed_database.py
"""

import os
import sys
import random
import datetime
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
import requests
from io import BytesIO

# Setup Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monolith.settings')
django.setup()

# Import models
from artifacts.models import Artifact, Category, Tag, UserPreference
from users.models import Friendship

User = get_user_model()

# Categories for analog items
CATEGORIES = [
    {"name": "Vinyl Records", "description": "Analog audio recordings on vinyl discs"},
    {"name": "Film Cameras", "description": "Analog photographic equipment using film"},
    {"name": "Typewriters", "description": "Mechanical or electronic devices for writing"},
    {"name": "Cassette Tapes", "description": "Magnetic tape audio storage format"},
    {"name": "Board Games", "description": "Physical games played on a board with pieces"},
    {"name": "Trading Cards", "description": "Collectible printed cards in sets"},
    {"name": "VHS Tapes", "description": "Video Home System magnetic tape format"},
    {"name": "Vintage Books", "description": "Classic and collectible physical books"},
    {"name": "Mechanical Watches", "description": "Timepieces with mechanical movements"},
    {"name": "Vintage Radios", "description": "Antique audio reception devices"}
]

# Tags for artifacts
TAGS = [
    "vintage", "collectible", "rare", "mint-condition", "used", 
    "limited-edition", "retro", "classic", "antique", "authentic",
    "handmade", "original", "unique", "nostalgic", "functional"
]

# Test users data
TEST_USERS = [
    {"username": "vintage_collector", "email": "vintage@example.com", "bio": "Passionate about all things vintage and retro."},
    {"username": "analog_enthusiast", "email": "analog@example.com", "bio": "Loving the pre-digital era artifacts."},
    {"username": "retro_trader", "email": "retro@example.com", "bio": "Trading retro items is my passion."},
    {"username": "vinyl_junkie", "email": "vinyl@example.com", "bio": "Can't get enough of those vinyl records!"},
    {"username": "film_photographer", "email": "film@example.com", "bio": "Only shoot on film, digital is cheating."},
    {"username": "typewriter_poet", "email": "typewriter@example.com", "bio": "Writing poetry on my collection of typewriters."},
    {"username": "cassette_dj", "email": "cassette@example.com", "bio": "Making mixtapes since the 80s."},
    {"username": "board_game_guru", "email": "boardgames@example.com", "bio": "I have over 500 board games in my collection."},
    {"username": "card_collector", "email": "cards@example.com", "bio": "Trading cards are more than just a hobby."},
    {"username": "mechanical_timekeeper", "email": "watches@example.com", "bio": "Fascinated by the artistry of mechanical watches."}
]

# Sample artifact data for each category
ARTIFACTS_BY_CATEGORY = {
    "Vinyl Records": [
        {"title": "The Beatles - Abbey Road Original Pressing", "description": "Original 1969 pressing in excellent condition. A true collector's item."},
        {"title": "Pink Floyd - Dark Side of the Moon", "description": "Rare first pressing with original posters and stickers included."},
        {"title": "Elvis Presley - Elvis Presley (debut album)", "description": "1956 debut album, some wear on sleeve but vinyl in great condition."},
        {"title": "Michael Jackson - Thriller", "description": "The best-selling album of all time, 1982 pressing with original inserts."},
        {"title": "Queen - A Night at the Opera", "description": "Features Bohemian Rhapsody, original UK pressing from 1975."}
    ],
    "Film Cameras": [
        {"title": "Leica M3 Rangefinder", "description": "Classic 35mm rangefinder camera from the 1950s, fully operational."},
        {"title": "Polaroid SX-70 Land Camera", "description": "Iconic folding SX-70 instant camera from the 1970s."},
        {"title": "Hasselblad 500C/M Medium Format", "description": "Professional medium format camera used by NASA during Apollo missions."},
        {"title": "Nikon F3 35mm SLR", "description": "Professional SLR camera from the 1980s, comes with 50mm lens."},
        {"title": "Rolleiflex 2.8F TLR", "description": "Classic twin lens reflex camera known for exceptional build quality."}
    ],
    "Typewriters": [
        {"title": "IBM Selectric II", "description": "Iconic electric typewriter with the revolutionary 'golf ball' type element."},
        {"title": "Olivetti Valentine", "description": "Designed by Ettore Sottsass, this red portable typewriter is a design icon."},
        {"title": "Royal Quiet De Luxe", "description": "Portable manual typewriter from the 1940s, used by many famous authors."},
        {"title": "Hermes 3000", "description": "Swiss-made precision typewriter known for smooth typing action."},
        {"title": "Smith-Corona Sterling", "description": "Classic portable typewriter in mint condition with original case."}
    ],
    "Cassette Tapes": [
        {"title": "TDK SA-90 High Bias Cassettes (5-pack)", "description": "Unopened pack of high-quality recording cassettes."},
        {"title": "Maxell XLII-90 Cassettes", "description": "Premium blank cassettes for audiophiles, sealed."},
        {"title": "Led Zeppelin IV Original Cassette", "description": "First release cassette version of the legendary album."},
        {"title": "Sony Walkman WM-10", "description": "Ultra-compact cassette player, fully working condition."},
        {"title": "BASF Chrome Extra II 90", "description": "German-made chrome cassettes with excellent frequency response."}
    ],
    "Board Games": [
        {"title": "Original Monopoly Set (1935)", "description": "Early edition Monopoly set with wooden houses."},
        {"title": "Vintage Scrabble (1948)", "description": "Early Scrabble edition in wooden box with wooden tiles."},
        {"title": "Risk (1959 First Edition)", "description": "Original version of the strategy board game."},
        {"title": "Clue/Cluedo First Edition", "description": "1949 first edition of the classic murder mystery game."},
        {"title": "Chess Set - Hand Carved Wooden Pieces", "description": "Vintage chess set with beautifully hand-carved pieces."}
    ],
    "Trading Cards": [
        {"title": "1952 Topps Mickey Mantle", "description": "Rare baseball card of Yankees legend Mickey Mantle."},
        {"title": "Magic: The Gathering Alpha Black Lotus", "description": "The most valuable Magic card ever printed, near-mint condition."},
        {"title": "Pokemon Base Set 1st Edition Charizard", "description": "Holographic Charizard from the original Pokemon set."},
        {"title": "1986 Fleer Michael Jordan Rookie Card", "description": "Iconic basketball card in protective case."},
        {"title": "Star Wars Complete Card Set (1977)", "description": "Original Star Wars trading cards, complete set with rare chase cards."}
    ],
    "VHS Tapes": [
        {"title": "Star Wars Original Trilogy Box Set", "description": "Original release before the special editions, excellent condition."},
        {"title": "E.T. The Extra-Terrestrial (First VHS Release)", "description": "Original home video release of Spielberg's classic."},
        {"title": "Disney's Black Diamond Collection", "description": "Rare collection of Disney classics in the valuable Black Diamond editions."},
        {"title": "Ghostbusters (1984) Original VHS", "description": "First release VHS of the supernatural comedy."},
        {"title": "Back to the Future Trilogy", "description": "Complete box set of the time travel adventures."}
    ],
    "Vintage Books": [
        {"title": "To Kill a Mockingbird First Edition", "description": "1960 first printing of Harper Lee's masterpiece."},
        {"title": "The Great Gatsby (First Edition, 1925)", "description": "Rare first printing with original dust jacket."},
        {"title": "Moby Dick 1851 First Edition", "description": "First American edition of Melville's epic novel."},
        {"title": "The Hobbit (1937)", "description": "First edition of Tolkien's adventure with original maps."},
        {"title": "Pride and Prejudice (1813 Triple-Decker)", "description": "Original three-volume edition of Austen's beloved novel."}
    ],
    "Mechanical Watches": [
        {"title": "Omega Speedmaster Professional", "description": "The 'Moonwatch' worn by Apollo astronauts, 1960s vintage."},
        {"title": "Rolex Submariner 5513", "description": "Vintage dive watch from the 1960s, no date model."},
        {"title": "Patek Philippe Calatrava", "description": "Elegant dress watch with manual winding movement."},
        {"title": "Jaeger-LeCoultre Reverso", "description": "Art Deco design with unique reversible case."},
        {"title": "Heuer Carrera 2447", "description": "Vintage chronograph from the golden age of motorsport."}
    ],
    "Vintage Radios": [
        {"title": "Zenith Trans-Oceanic", "description": "Legendary portable tube radio that could receive worldwide broadcasts."},
        {"title": "Philco Cathedral Radio", "description": "Iconic wooden cabinet radio from the 1930s."},
        {"title": "Bakelite Emerson Radio", "description": "Art Deco Bakelite table radio, fully restored and working."},
        {"title": "Grundig Majestic", "description": "German-made tube radio with exceptional sound quality."},
        {"title": "RCA Victor Radio Phonograph", "description": "Combination radio and record player in wooden console."}
    ]
}

# Generic stock photo URLs by category for placeholder images
STOCK_PHOTOS_BY_CATEGORY = {
    "Vinyl Records": [
        "https://source.unsplash.com/random/800x600/?vinyl",
        "https://source.unsplash.com/random/800x600/?record",
        "https://source.unsplash.com/random/800x600/?turntable",
        "https://source.unsplash.com/random/800x600/?album",
        "https://source.unsplash.com/random/800x600/?vinyl+record"
    ],
    "Film Cameras": [
        "https://source.unsplash.com/random/800x600/?film+camera",
        "https://source.unsplash.com/random/800x600/?vintage+camera",
        "https://source.unsplash.com/random/800x600/?analog+camera",
        "https://source.unsplash.com/random/800x600/?leica",
        "https://source.unsplash.com/random/800x600/?hasselblad"
    ],
    "Typewriters": [
        "https://source.unsplash.com/random/800x600/?typewriter",
        "https://source.unsplash.com/random/800x600/?vintage+typewriter",
        "https://source.unsplash.com/random/800x600/?manual+typewriter",
        "https://source.unsplash.com/random/800x600/?typing+machine",
        "https://source.unsplash.com/random/800x600/?retro+typewriter"
    ],
    "Cassette Tapes": [
        "https://source.unsplash.com/random/800x600/?cassette",
        "https://source.unsplash.com/random/800x600/?tape",
        "https://source.unsplash.com/random/800x600/?walkman",
        "https://source.unsplash.com/random/800x600/?mixtape",
        "https://source.unsplash.com/random/800x600/?cassette+tape"
    ],
    "Board Games": [
        "https://source.unsplash.com/random/800x600/?board+game",
        "https://source.unsplash.com/random/800x600/?monopoly",
        "https://source.unsplash.com/random/800x600/?chess",
        "https://source.unsplash.com/random/800x600/?scrabble",
        "https://source.unsplash.com/random/800x600/?vintage+game"
    ],
    "Trading Cards": [
        "https://source.unsplash.com/random/800x600/?trading+cards",
        "https://source.unsplash.com/random/800x600/?baseball+card",
        "https://source.unsplash.com/random/800x600/?pokemon+card",
        "https://source.unsplash.com/random/800x600/?collectible+card",
        "https://source.unsplash.com/random/800x600/?card+collection"
    ],
    "VHS Tapes": [
        "https://source.unsplash.com/random/800x600/?vhs",
        "https://source.unsplash.com/random/800x600/?videotape",
        "https://source.unsplash.com/random/800x600/?vhs+tape",
        "https://source.unsplash.com/random/800x600/?video+cassette",
        "https://source.unsplash.com/random/800x600/?vcr"
    ],
    "Vintage Books": [
        "https://source.unsplash.com/random/800x600/?vintage+book",
        "https://source.unsplash.com/random/800x600/?old+book",
        "https://source.unsplash.com/random/800x600/?antique+book",
        "https://source.unsplash.com/random/800x600/?first+edition",
        "https://source.unsplash.com/random/800x600/?rare+book"
    ],
    "Mechanical Watches": [
        "https://source.unsplash.com/random/800x600/?mechanical+watch",
        "https://source.unsplash.com/random/800x600/?vintage+watch",
        "https://source.unsplash.com/random/800x600/?omega+watch",
        "https://source.unsplash.com/random/800x600/?rolex",
        "https://source.unsplash.com/random/800x600/?pocket+watch"
    ],
    "Vintage Radios": [
        "https://source.unsplash.com/random/800x600/?vintage+radio",
        "https://source.unsplash.com/random/800x600/?antique+radio",
        "https://source.unsplash.com/random/800x600/?tube+radio",
        "https://source.unsplash.com/random/800x600/?old+radio",
        "https://source.unsplash.com/random/800x600/?retro+radio"
    ]
}

def download_image(url):
    """Download an image from URL and return as ContentFile"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return ContentFile(response.content)
        else:
            print(f"Failed to download image: {url}, status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image {url}: {str(e)}")
        return None

@transaction.atomic
def seed_database():
    """Seed the database with test data"""
    print("Seeding database...")
    
    # Create categories
    categories = {}
    for category_data in CATEGORIES:
        category, created = Category.objects.get_or_create(
            name=category_data["name"],
            defaults={"description": category_data["description"]}
        )
        categories[category_data["name"]] = category
        print(f"Category {'created' if created else 'exists'}: {category.name}")
    
    # Create tags
    tags = {}
    for tag_name in TAGS:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags[tag_name] = tag
        print(f"Tag {'created' if created else 'exists'}: {tag.name}")
    
    # Create test users
    users = []
    print("Creating test users...")
    for user_data in TEST_USERS:
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={
                "email": user_data["email"],
                "bio": user_data["bio"],
                "is_active": True
            }
        )
        
        if created:
            user.set_password("testpass123")
            user.save()
            print(f"Created user: {user.username}")
        else:
            print(f"User exists: {user.username}")
            
        # Create user preferences
        prefs, _ = UserPreference.objects.get_or_create(user=user)
        users.append(user)
    
    # Create some friendships between users
    print("Creating friendships...")
    for i, user in enumerate(users):
        # Each user follows 3-5 other users
        follow_count = random.randint(3, 5)
        other_users = users.copy()
        other_users.remove(user)
        users_to_follow = random.sample(other_users, min(follow_count, len(other_users)))
        
        for user_to_follow in users_to_follow:
            friendship, created = Friendship.objects.get_or_create(
                sender=user,
                receiver=user_to_follow,
                defaults={"status": "accepted"}
            )
            if created:
                print(f"{user.username} is now following {user_to_follow.username}")
    
    # Create artifacts
    print("Creating artifacts...")
    for category_name, artifacts_data in ARTIFACTS_BY_CATEGORY.items():
        category = categories[category_name]
        photo_urls = STOCK_PHOTOS_BY_CATEGORY[category_name]
        
        for i, artifact_data in enumerate(artifacts_data):
            # Assign to a random user
            user = random.choice(users)
            
            # Get a random photo URL for this category
            photo_url = random.choice(photo_urls)
            
            # Create the artifact
            artifact, created = Artifact.objects.get_or_create(
                title=artifact_data["title"],
                defaults={
                    "user": user,
                    "description": artifact_data["description"],
                    "category": category,
                    "popularity_score": random.randint(0, 100)
                }
            )
            
            if created:
                print(f"Created artifact: {artifact.title}")
                
                # Download and attach image
                image_content = download_image(photo_url)
                if image_content:
                    image_name = f"{category_name.lower().replace(' ', '_')}_{i}.jpg"
                    artifact.image.save(image_name, image_content, save=True)
                    
                    # Thumbnail is auto-generated in the model's save method
                    artifact.save()
                
                # Add random tags
                tag_count = random.randint(2, 5)
                random_tags = random.sample(list(tags.values()), tag_count)
                artifact.tags.add(*random_tags)
            else:
                print(f"Artifact exists: {artifact.title}")
    
    print("Database seeding complete!")

if __name__ == "__main__":
    seed_database() 
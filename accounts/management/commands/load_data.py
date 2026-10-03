"""
python manage.py load_data
Loads all sample data: locations, users (tourists, owners, guides), vehicles, hotels, rooms, guides, emergency contacts.
Default password for all test accounts: Test@1234
"""
import os
import shutil
from decimal import Decimal
import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings

class Command(BaseCommand):
    help = 'Load sample data for SmartTourist'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('*** Loading sample data with AI & proper name-related images...'))
        
        self.stdout.write('--- Cleaning database...')
        from vehicles.models import Vehicle, VehicleImage, VehicleBooking, VehicleReview
        from hotels.models import Hotel, HotelRoom, HotelBooking, HotelReview
        from guides.models import TourGuide, GuideBooking, GuideReview
        from ai_assistant.models import TripPlan, EmergencyContact, ChatbotQuery
        from accounts.models import User, TouristLocation, UserFavorite
        
        VehicleReview.objects.all().delete()
        VehicleBooking.objects.all().delete()
        VehicleImage.objects.all().delete()
        Vehicle.objects.all().delete()
        
        HotelReview.objects.all().delete()
        HotelBooking.objects.all().delete()
        HotelRoom.objects.all().delete()
        Hotel.objects.all().delete()
        
        GuideReview.objects.all().delete()
        GuideBooking.objects.all().delete()
        TourGuide.objects.all().delete()
        
        EmergencyContact.objects.all().delete()
        TripPlan.objects.all().delete()
        ChatbotQuery.objects.all().delete()
        UserFavorite.objects.all().delete()
        
        User.objects.exclude(role='admin').delete()
        TouristLocation.objects.all().delete()
        
        self.stdout.write('--- Copying generated AI and standard images to media folder...')
        self._copy_generated_images()

        self._locations()
        self._users()
        self._vehicles()
        self._hotels()
        self._guides()
        self._emergency()
        self._generate_credentials_file()
        
        self.stdout.write(self.style.SUCCESS('\n*** Sample data and real images loaded successfully! Login credentials written to login_credentials.txt'))

    def _copy_generated_images(self):
        # Path to the artifact directories where the generated images are stored
        artifact_dirs = [
            r"C:\Users\vishw\.gemini\antigravity-ide\brain\39f7683f-e5dd-4005-aba2-4a2066d58dfa",
            r"C:\Users\vishw\.gemini\antigravity-ide\brain\a68210ce-71e9-4763-a2e9-55e56fa8d57a",
            r"C:\Users\vishw\AppData\Local\Google\Chrome\User Data\Default"
        ]
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        
        # Map each destination image to a list of potential source filenames (ordered by preference)
        image_map = {
            'vehicles/thumbnails/bike.png': ['vehicle_bike_1783234089164.png'],
            'vehicles/thumbnails/scooter.png': ['vehicle_scooter_1783234109924.png'],
            'vehicles/thumbnails/car.png': ['vehicle_car_1783234134511.png'],
            'vehicles/thumbnails/suv.png': ['vehicle_suv_1783234195535.png'],
            'vehicles/thumbnails/bus.png': ['vehicle_bus_1783234227868.png'],
            'vehicles/thumbnails/cycle.png': ['vehicle_cycle_1783234248263.png'],
            'hotels/thumbnails/luxury.png': ['hotel_luxury_1783234267442.png'],
            'hotels/thumbnails/resort.png': ['hotel_resort_1783234288677.png'],
            'hotels/thumbnails/heritage.png': ['hotel_heritage_1783234304438.png'],
            'hotels/thumbnails/standard.png': ['hotel_standard_1783234322445.png'],
            'hotels/thumbnails/budget.png': ['hotel_budget_1783234341115.png'],
            'hotels/rooms/single.png': ['hotel_standard_1783234322445.png'],
            'hotels/rooms/double.png': ['hotel_standard_1783234322445.png'],
            'hotels/rooms/suite.png': ['hotel_luxury_1783234267442.png'],
            'guides/guide_male.png': ['guide_male_1783234358981.png'],
            'guides/guide_female.png': ['guide_female_1783234375904.png'],
            'guides/guide_male_old.png': ['guide_male_old_1783234393068.png'],
            'guides/guide_female_indian.png': ['guide_female_indian_1783234411597.png'],
            'locations/mysore.png': ['location_mysore_1783234428360.png'],
            'locations/coorg.png': ['location_coorg_1783234446320.png'],
            'locations/goa.png': ['goa_beach_1786334006713.png', 'location_coorg_1783234446320.png'],
            'locations/ooty.png': ['ooty_tea_gardens_1786334032059.png', 'location_coorg_1783234446320.png'],
            'locations/manali.png': ['manali_mountains_1786334058555.png', 'location_coorg_1783234446320.png'],
            'locations/kerala.png': ['kerala_backwaters_1786334081310.png', 'location_mysore_1783234428360.png']
        }
        
        for rel_path, filenames in image_map.items():
            copied = False
            for artifact_dir in artifact_dirs:
                for filename in filenames:
                    src = os.path.join(artifact_dir, filename)
                    if os.path.exists(src):
                        dst = os.path.join(media_dir, rel_path)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                        copied = True
                        break
                if copied:
                    break
            if not copied:
                self.stdout.write(self.style.WARNING(f"  Warning: Source image for {rel_path} not found in any artifact directory."))

    def _locations(self):
        from accounts.models import TouristLocation
        locs = [
            ('Mysore',  'mysore',  'Karnataka',        'City of Palaces — grand architecture, silk sarees and the vibrant Dasara festival.',          'October to February'),
            ('Coorg',   'coorg',   'Karnataka',        'Scotland of India — lush coffee plantations, misty hills and stunning waterfalls.',           'October to May'),
            ('Goa',     'goa',     'Goa',              "India's beach paradise — golden sands, Portuguese heritage and fresh seafood.",               'November to March'),
            ('Ooty',    'ooty',    'Tamil Nadu',       'Queen of Hill Stations — scenic toy train, botanical gardens and cool weather.',               'October to June'),
            ('Manali',  'manali',  'Himachal Pradesh', 'Gateway to the Himalayas — snow peaks, adventure sports and the scenic Beas River valley.',   'March to June & Sep–Nov'),
            ('Kerala',  'kerala',  'Kerala',           "God's Own Country — serene backwaters, lush hill stations, beaches and Ayurveda retreats.",   'September to March'),
        ]
        for name, slug, state, desc, season in locs:
            img_path = f"locations/{slug}.png"
            TouristLocation.objects.create(name=name, slug=slug, state=state,
                                           description=desc, best_season=season, image=img_path, is_active=True)
        self.stdout.write(f'  -> {len(locs)} locations')

    def _users(self):
        from accounts.models import User
        
        # Ensure Admin is present and has the correct password
        if not User.objects.filter(email='admin@smart.in').exists():
            u = User(email='admin@smart.in', username='admin', first_name='Admin', last_name='User', role='admin', is_staff=True, is_superuser=True, is_active=True, is_verified=True)
            u.set_password('Test@1234')
            u.save()
        else:
            u = User.objects.get(email='admin@smart.in')
            u.set_password('Test@1234')
            u.save()
            
        # Create 5 Tourist accounts
        for i in range(1, 6):
            email = f'tourist{i}@smart.in'
            if not User.objects.filter(email=email).exists():
                u = User(email=email, username=f'tourist{i}', first_name=f'Tourist', last_name=str(i), role='tourist', is_active=True, is_verified=True)
                u.set_password('Test@1234')
                u.save()
                
        # Create 10 Vehicle Owner accounts
        for i in range(1, 11):
            email = f'vowner{i}@smart.in'
            if not User.objects.filter(email=email).exists():
                u = User(email=email, username=f'vowner{i}', first_name=f'Vehicle', last_name=f'Owner {i}', role='vehicle_owner', is_active=True, is_verified=True)
                u.set_password('Test@1234')
                u.save()
                
        # Create 10 Hotel Owner accounts
        for i in range(1, 11):
            email = f'howner{i}@smart.in'
            if not User.objects.filter(email=email).exists():
                u = User(email=email, username=f'howner{i}', first_name=f'Hotel', last_name=f'Owner {i}', role='hotel_owner', is_active=True, is_verified=True)
                u.set_password('Test@1234')
                u.save()

        # Create 30 Tour Guide accounts (One-to-One profile is created in _guides method)
        for i in range(1, 31):
            email = f'guide{i}@smart.in'
            if not User.objects.filter(email=email).exists():
                u = User(email=email, username=f'guide{i}', first_name=f'Guide', last_name=str(i), role='guide', is_active=True, is_verified=True)
                u.set_password('Test@1234')
                u.save()

        self.stdout.write('  -> User accounts created (Tourists, Vehicle Owners, Hotel Owners, Guides)')

    def _vehicles(self):
        from accounts.models import User, TouristLocation
        from vehicles.models import Vehicle
        
        owners = list(User.objects.filter(role='vehicle_owner'))
        locs = list(TouristLocation.objects.all())
        
        vehicle_data = [
            # Mysore (5)
            ("Royal Enfield Classic 350", "bike", "Royal Enfield", "Classic 350", 2022, "KA-09-EF-1234", "petrol", "manual", 2, 80, 800, 2000, "Helmet, Tool Kit, First Aid", "Classic retro cruiser, perfect for Mysore city tours."),
            ("Honda Activa 6G", "scooter", "Honda", "Activa 6G", 2023, "KA-09-GH-5678", "petrol", "automatic", 2, 50, 400, 1000, "Helmet, Mobile Holder", "Reliable and easy to ride scooter for daily commuting."),
            ("Maruti Swift Dzire", "car", "Maruti", "Swift Dzire", 2022, "KA-09-JK-9012", "petrol", "manual", 5, 150, 1500, 3000, "AC, Music System, GPS, Airbags", "Comfortable sedan with great mileage for family trips."),
            ("Toyota Innova Crysta", "suv", "Toyota", "Innova Crysta", 2021, "KA-09-LM-3456", "diesel", "automatic", 7, 250, 2500, 5000, "AC, Infotainment, GPS, Carrier", "Spacious and luxurious SUV, best for group travel."),
            ("Hero Lectro C8", "cycle", "Hero", "Lectro C8", 2023, "KA-09-NP-7890", "electric", "manual", 1, 20, 200, 500, "Helmet, Lock", "Electric cycle for eco-friendly city exploration."),
            
            # Coorg (5)
            ("Mahindra Thar 4x4", "suv", "Mahindra", "Thar", 2022, "KA-12-AB-9876", "diesel", "manual", 4, 300, 3000, 6000, "4WD, Convertible Roof, AC, GPS", "Rugged 4x4 off-roader, ideal for Coorg's hilly terrain."),
            ("TVS Jupiter 125", "scooter", "TVS", "Jupiter 125", 2023, "KA-12-CD-5432", "petrol", "automatic", 2, 45, 450, 1000, "Helmet, Under-seat Charger", "Spacious scooter with large boot space."),
            ("Hyundai Creta", "suv", "Hyundai", "Creta", 2022, "KA-12-EF-3210", "petrol", "automatic", 5, 200, 2000, 4000, "Sunroof, AC, GPS, Ventilated Seats", "Premium SUV for a smooth ride through coffee estates."),
            ("Royal Enfield Himalayan", "bike", "Royal Enfield", "Himalayan", 2021, "KA-12-GH-7777", "petrol", "manual", 2, 120, 1200, 3000, "Helmet, Saddle Stays, USB Charger", "Adventure tourer built for rough mountain roads."),
            ("Decathlon Rockrider ST100", "cycle", "Decathlon", "Rockrider", 2022, "KA-12-JK-8888", "petrol", "manual", 1, 15, 150, 500, "Helmet, Water Bottle Holder", "Sturdy mountain bicycle for estate trails."),
            
            # Goa (5)
            ("Thar Open Top", "suv", "Mahindra", "Thar Open", 2022, "GA-03-XY-1010", "petrol", "manual", 4, 350, 3500, 5000, "Open Top, Custom Alloys, AC, Bluetooth", "Open jeep for the ultimate Goa beach vibe."),
            ("Vespa VXL 150", "scooter", "Vespa", "VXL 150", 2023, "GA-03-ZA-2020", "petrol", "automatic", 2, 80, 700, 1500, "Retro Helmet, Chrome Mirrors", "Stylish Italian scooter, perfect for beach hopping."),
            ("Suzuki Access 125", "scooter", "Suzuki", "Access 125", 2023, "GA-03-BC-3030", "petrol", "automatic", 2, 50, 450, 1000, "Helmet, Mobile Charger", "Comfortable and classic scooter for sightseeing."),
            ("Honda City", "car", "Honda", "City", 2021, "GA-03-DE-4040", "petrol", "automatic", 5, 180, 1800, 3500, "Leather Seats, AC, Sunroof, GPS", "Elegant sedan for premium travel around Goa."),
            ("KTM Duke 250", "bike", "KTM", "Duke 250", 2022, "GA-03-FG-5050", "petrol", "manual", 2, 130, 1300, 3000, "Helmet, Riding Gloves", "Sporty naked street bike for quick rides."),
            
            # Ooty (5)
            ("Maruti Ertiga", "bus", "Maruti", "Ertiga", 2022, "TN-43-AA-1122", "petrol", "manual", 7, 220, 2200, 4000, "AC, Music System, Rear Camera", "Affordable 7-seater MUV, perfect for families visiting Ooty."),
            ("Ather 450X Gen 3", "scooter", "Ather", "450X", 2023, "TN-43-BB-3344", "electric", "automatic", 2, 70, 600, 2000, "Smart Helmet, Touchscreen GPS", "High-performance electric scooter with hill-assist."),
            ("Yamaha FZ-S V3", "bike", "Yamaha", "FZ-S", 2022, "TN-43-CC-5566", "petrol", "manual", 2, 90, 900, 2000, "Helmet, Tank Bag", "Comfortable street bike with great handling on curves."),
            ("Tata Nexon EV", "suv", "Tata", "Nexon EV", 2023, "TN-43-DD-7788", "electric", "automatic", 5, 250, 2500, 5000, "Silent Cabin, AC, Sunroof, GPS", "Eco-friendly SUV with long range, perfect for hill roads."),
            ("Montra Madrock", "cycle", "Montra", "Madrock", 2022, "TN-43-EE-9900", "petrol", "manual", 1, 20, 180, 500, "Helmet, Lock", "Cross-country bicycle for riding around Ooty Lake."),
            
            # Manali (5)
            ("Toyota Fortuner 4x4", "suv", "Toyota", "Fortuner", 2021, "HP-01-MM-0001", "diesel", "automatic", 7, 450, 4500, 10000, "4WD, Bull Bar, AC, Infotainment, GPS", "Premium 4WD SUV to conquer snow and rough terrains."),
            ("Royal Enfield Himalayan Scram 411", "bike", "Royal Enfield", "Scram 411", 2023, "HP-01-NN-0002", "petrol", "manual", 2, 140, 1400, 3000, "Helmet, Panniers, GPS Mount", "Purpose-built scrambler for Himalayan trails."),
            ("Maruti Alto K10", "car", "Maruti", "Alto K10", 2023, "HP-01-PP-0003", "petrol", "manual", 5, 100, 900, 2000, "Heater, Music System", "Compact car, very easy to drive and park in narrow hill streets."),
            ("Ola S1 Air", "scooter", "Ola", "S1 Air", 2023, "HP-01-QQ-0004", "electric", "automatic", 2, 60, 500, 1500, "Helmet, Smart App Control", "Sleek and smart electric scooter for short trips."),
            ("Firefox Target 21S", "cycle", "Firefox", "Target", 2022, "HP-01-RR-0005", "petrol", "manual", 1, 25, 220, 500, "Helmet, Safety lights", "21-speed gear cycle for hilly road cycling."),
            
            # Kerala (5)
            ("Force Traveller 12 Str", "bus", "Force", "Traveller", 2021, "KL-07-XX-9090", "diesel", "manual", 12, 400, 4000, 8000, "AC, Carrier, LED Screen, Mic System", "Spacious 12-seater tourer, best for big families and tour groups."),
            ("Honda CB350 H'ness", "bike", "Honda", "CB350", 2022, "KL-07-YY-8080", "petrol", "manual", 2, 100, 1000, 2500, "Helmet, Crash Guard", "Smooth retro cruiser for coastal highway riding."),
            ("TVS iQube S", "scooter", "TVS", "iQube S", 2023, "KL-07-ZZ-7070", "electric", "automatic", 2, 60, 550, 1500, "Helmet, Connected Screen", "Silent electric scooter for exploring peaceful villages."),
            ("Maruti Baleno", "car", "Maruti", "Baleno", 2022, "KL-07-AA-6060", "petrol", "manual", 5, 140, 1400, 3000, "AC, Infotainment, Rear Sensors", "Premium hatchback with a spacious cabin and smooth engine."),
            ("Tata Safari", "suv", "Tata", "Safari", 2022, "KL-07-BB-5050", "diesel", "automatic", 7, 300, 3000, 6000, "Panoramic Sunroof, AC, JBL Audio, GPS", "Luxurious 3-row SUV for family road trips.")
        ]
        
        for i, (name, vtype, brand, model, year, reg, fuel, trans, seats, pph, ppd, dep, features, desc) in enumerate(vehicle_data):
            loc = locs[i // 5]  # 5 vehicles per location
            owner = owners[i % len(owners)]  # distribute across owners
            img_path = f"vehicles/thumbnails/{vtype}.png"
            Vehicle.objects.create(
                owner=owner, name=name, vehicle_type=vtype, brand=brand, model=model,
                year=year, registration_number=reg, fuel_type=fuel, transmission=trans,
                seating_capacity=seats, price_per_hour=Decimal(str(pph)), price_per_day=Decimal(str(ppd)),
                security_deposit=Decimal(str(dep)), features=features, location=loc,
                pickup_address=f'Near {loc.name} Airport/Railway Station, {loc.name}',
                description=desc, is_available=True, is_approved=True, is_featured=(i % 6 == 0),
                avg_rating=Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                total_bookings=random.randint(5, 50), thumbnail=img_path
            )
        self.stdout.write(f'  -> {len(vehicle_data)} vehicles loaded')

    def _hotels(self):
        from accounts.models import User, TouristLocation
        from hotels.models import Hotel, HotelRoom
        
        owners = list(User.objects.filter(role='hotel_owner'))
        locs = list(TouristLocation.objects.all())
        
        hotel_data = [
            # Mysore (5)
            ("Mysore Palace View Hotel", "heritage", 5, "Mysore", "Karnataka", "Experience royal grandeur with direct views of the iconic Mysore Palace.", "WiFi, Pool, Spa, Restaurant, Valet Parking, Gym", "0821-2444111", "palaceview@mysorehotels.in"),
            ("Royal Orchid Metropole", "heritage", 4, "Mysore", "Karnataka", "A historic heritage hotel built by the Maharaja of Mysore, featuring vintage decor.", "WiFi, Pool, Bar, Restaurant, Garden, Heritage Tour", "0821-2520655", "metropole@royalorchid.in"),
            ("Hotel Kings Kourt", "standard", 3, "Mysore", "Karnataka", "Comfortable, modern, and affordable accommodation near the Mysore railway station.", "WiFi, Restaurant, Parking, Room Service, AC", "0821-2421481", "bookings@kingskourt.in"),
            ("Windflower Resort & Spa", "resort", 4, "Mysore", "Karnataka", "Lush green wellness resort at the foothills of Chamundi Hills offering peaceful spa retreats.", "WiFi, Pool, Spa, Bonfire, Restaurant, Indoor Games", "0821-2521521", "mysore@windflowerresorts.com"),
            ("Roamer's Nest Hostel", "budget", 2, "Mysore", "Karnataka", "A cozy, vibrant backpacker hostel for budget travellers and solo adventurers.", "WiFi, Shared Kitchen, Lounge, Bicycle Rental, Laundry", "0821-4009999", "roamersnest@hostels.in"),
            
            # Coorg (5)
            ("Coorg Cliffs Resort", "resort", 4, "Madikeri", "Karnataka", "Perched on a cliff, offering panoramic views of the Western Ghats and mist-covered hills.", "WiFi, Infinity Pool, Bonfire, Restaurant, Plantation Walk", "08272-200111", "info@coorgcliffs.com"),
            ("The Tamara Coorg", "luxury", 5, "Yevakapadi", "Karnataka", "An ultra-luxury eco-resort nestled deep inside coffee plantations with wooden cottages.", "WiFi, Heated Pool, Spa, Fine Dining, Lounge, Coffee Tasting", "08272-238000", "reservations@thetamara.com"),
            ("Madikeri Heritage Home", "boutique", 3, "Madikeri", "Karnataka", "A traditional Kodava homestay experience with home-cooked local delicacies.", "WiFi, Home-cooked Meals, Parking, Garden, Local Guides", "08272-225225", "heritagehome@coorgstays.in"),
            ("Club Mahindra Madikeri", "resort", 4, "Madikeri", "Karnataka", "Sprawling family resort with adventure activities, spa, and multiple dining options.", "WiFi, Two Pools, Gym, Kids Zone, Bonfire, Restaurant", "08272-221122", "madikeri@clubmahindra.com"),
            ("Hill View Budget Stay", "budget", 2, "Madikeri", "Karnataka", "Affordable and clean rooms overlooking Madikeri town, ideal for short visits.", "WiFi, Hot Water, Parking, Room Service", "08272-229988", "hillview@budgetcoorg.in"),
            
            # Goa (5)
            ("Taj Exotica Resort & Spa", "luxury", 5, "Benaulim", "Goa", "Mediterranean-style luxury resort spread across 56 acres along the white sands of South Goa.", "WiFi, Private Beach Access, Golf Course, Spa, Multiple Pools", "0832-6683333", "exotica.goa@tajhotels.com"),
            ("Cidade de Goa", "deluxe", 4, "Dona Paula", "Goa", "Beachfront deluxe resort exhibiting beautiful Portuguese-Goan architecture and vibrant vibes.", "WiFi, Beachfront, Pool, Bar, Watersports, Restaurant", "0832-2454545", "cidade@ihcltata.com"),
            ("Calangute Beach Resort", "resort", 4, "Calangute", "Goa", "Modern beachfront resort in the heart of Calangute, steps away from shacks and nightlife.", "WiFi, Pool, Beach Bar, Restaurant, Sea Views", "0832-2277777", "calangute@beachresorts.in"),
            ("Panaji Heritage Inn", "heritage", 3, "Fontainhas", "Goa", "A charming boutique heritage hotel situated in the Latin Quarter of Fontainhas.", "WiFi, Cafe, Heritage Walk, AC, Library", "0832-2228888", "fontainhas@heritagegoa.in"),
            ("Backpacker's Goa", "budget", 2, "Anjuna", "Goa", "Funky beachside backpackers hostel with social spaces, live music, and pub crawls.", "WiFi, Dorms, Cafe, Bar, Bike Rental, Social Lounge", "0832-2273030", "anjuna@backpackersgoa.in"),
            
            # Ooty (5)
            ("Savoy Hotel Ooty", "heritage", 5, "Ooty", "Tamil Nadu", "Stately colonial-era heritage hotel built in 1829, featuring heritage rooms and fireplaces.", "WiFi, Fireplace, Spa, Billiards, Restaurant, Tea Lounge", "0423-2225500", "savoy.ooty@tajhotels.com"),
            ("Sterling Ooty Fern Hill", "resort", 4, "Ooty", "Tamil Nadu", "Resort overlooking the beautiful Ooty valley and terraced farming slopes.", "WiFi, Restaurant, Spa, Bonfire, Indoor Games, Kids Activity Area", "0423-2441000", "fernhill@sterlingholidays.com"),
            ("Lakeview Hotel Ooty", "standard", 3, "Ooty", "Tamil Nadu", "Sprawling complex of individual cottages set across 8 acres, close to the Ooty Lake.", "WiFi, Individual Cottages, Fireplace, Horse Riding, Restaurant", "0423-2443580", "lakeview@ootyhotels.in"),
            ("Monarch Hotel", "deluxe", 4, "Ooty", "Tamil Nadu", "Perched high on a hill, offering luxury rooms with indoor pool and stunning mountain vistas.", "WiFi, Indoor Pool, Bar, Restaurant, Gym, Disco", "0423-2444418", "monarch@hotelmonarch.in"),
            ("Pine View Budget Cottages", "budget", 2, "Ooty", "Tamil Nadu", "Cozy, simple budget wooden cottages situated near the pine forests, quiet and peaceful.", "WiFi, Hot Water, Bonfire setup, Parking", "0423-2440099", "pineview@budgetooty.in"),
            
            # Manali (5)
            ("Solang Valley Resort", "resort", 4, "Solang Valley", "Himachal Pradesh", "Premium adventure resort situated on the banks of Beas River in Solang, close to ski slopes.", "WiFi, Riverside Lawn, Gym, Bonfire, Adventure Sports, Bar", "01902-256101", "solang@valleyresorts.com"),
            ("Span Resort & Spa", "luxury", 5, "Manali-Kullu Highway", "Himachal Pradesh", "Legendary luxury riverside resort offering breathtaking views of snow peaks and pine forests.", "WiFi, Riverfront, Spa, Pool, Helipad, Fine Dining", "01902-240101", "span@spanresorts.com"),
            ("Snow Valley Resorts", "deluxe", 4, "Log Huts Area", "Manali", "Elegant resort surrounded by apple orchards, offering luxury rooms and a revolving restaurant.", "WiFi, Apple Orchard Garden, Revolving Cafe, Gym, Kids Area", "01902-253228", "manali@snowvalleyresorts.com"),
            ("Himalayan Heritage Guest House", "heritage", 3, "Old Manali", "Himachal Pradesh", "Traditional wooden and stone Himachali house offering a quiet cultural stay.", "WiFi, Mountain View, Cafe, Library, Local Tours", "01902-250080", "heritage@oldmanali.in"),
            ("Old Manali Hostel", "budget", 2, "Old Manali", "Himachal Pradesh", "Vibrant backpacker hostel popular with international travellers, close to cafes and trails.", "WiFi, Shared Lounge, Rooftop Cafe, Bonfire, Board Games", "01902-259999", "oldmanali@hostels.in"),
            
            # Kerala (5)
            ("Kumarakom Lake Resort", "resort", 5, "Kumarakom", "Kerala", "Award-winning luxury resort situated on the banks of Lake Vembanad, featuring heritage villas.", "WiFi, Backwater Infinity Pool, Ayurveda Spa, Houseboat Cruises, Fine Dining", "0481-2524900", "kumarakom@lakeresorts.in"),
            ("Brunton Boatyard", "heritage", 5, "Fort Kochi", "Kerala", "Built on the site of a historic boatyard, recreating the 19th-century Dutch-Portuguese lifestyle.", "WiFi, Swimming Pool, Seafront Dining, Sunset Cruises, Ayurveda Centre", "0484-2215461", "brunton@cghearth.com"),
            ("Munnar Tea Hills Resort", "resort", 4, "Munnar", "Kerala", "Boutique resort featuring individual villas scattered across lush green tea garden slopes.", "WiFi, Spa, Valley View Balconies, Restaurant, Trekking Guides", "0486-5232822", "munnar@teahills.com"),
            ("Alleppey Houseboat Retreat", "boutique", 4, "Alleppey", "Kerala", "Traditional luxury houseboats providing overnight cruises along the scenic backwaters.", "WiFi, All Meals Included, Sun Deck, Fishing setup, AC Rooms", "0477-2243333", "houseboats@keralaretreat.in"),
            ("Fort Kochi Budget Inn", "budget", 2, "Fort Kochi", "Kerala", "Clean and simple budget lodging near the Chinese Fishing Nets and historic churches.", "WiFi, Air Conditioning, Bicycle Rental, Travel Desk", "0484-2210099", "fortkochi@budgetinn.in")
        ]
        
        for i, (name, cat, stars, city, state, desc, amenities, phone, email) in enumerate(hotel_data):
            loc = locs[i // 5]
            owner = owners[i % len(owners)]
            
            slug = slugify(name)
            base, n = slug, 1
            while Hotel.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"; n += 1
            
            # Determine mapped hotel image
            himg = cat if cat in ['luxury', 'resort', 'heritage', 'budget'] else 'standard'
            img_path = f"hotels/thumbnails/{himg}.png"
            
            hotel = Hotel.objects.create(
                owner=owner, name=name, slug=slug, category=cat,
                star_rating=stars, city=city, state=state,
                description=desc, amenities=amenities, phone=phone,
                email=email, address=f'{city} Center, {state}', location=loc,
                is_approved=True, is_featured=(i % 6 == 0),
                avg_rating=Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                total_bookings=random.randint(10, 100), thumbnail=img_path
            )
            
            # Rooms setup: adjust price per night based on hotel category and star rating
            price_multiplier = {5: 3.5, 4: 2.2, 3: 1.2, 2: 0.6}.get(stars, 1.0)
            
            rooms_to_create = [
                ('single', '101', 1, price_multiplier * 1200, 'AC, WiFi, TV, Geyser, Single Bed'),
                ('double', '202', 2, price_multiplier * 2200, 'AC, WiFi, TV, Geyser, Queen Bed, Coffee Maker'),
                ('suite',  '303', 4, price_multiplier * 5000, 'AC, WiFi, TV, Geyser, King Bed, Living Area, Bathtub, Balcony')
            ]
            
            for rtype, rnum, cap, rprice, ramenities in rooms_to_create:
                room_img = f"hotels/rooms/{rtype}.png"
                HotelRoom.objects.create(
                    hotel=hotel, room_type=rtype, room_number=rnum,
                    capacity=cap, price_per_night=Decimal(str(round(rprice, 2))),
                    amenities=ramenities, has_ac=True, has_wifi=True, is_available=True,
                    thumbnail=room_img
                )
                
        self.stdout.write(f'  -> {len(hotel_data)} hotels with {len(hotel_data)*3} rooms loaded')

    def _guides(self):
        from accounts.models import User, TouristLocation
        from guides.models import TourGuide
        
        guide_users = list(User.objects.filter(role='guide').order_by('id'))
        locs = list(TouristLocation.objects.all())
        
        guide_data = [
            # Mysore (5)
            ("Ramesh Kumar", "historical", 8, "English, Hindi, Kannada", "Expert heritage guide specializing in Mysore Palace, Hoysala architecture, and Srirangapatna history.", 150, 1200),
            ("Suresh Gowda", "general", 5, "Kannada, English", "Friendly local guide who knows all the sightseeing spots, shopping hubs, and local transport options in Mysore.", 80, 700),
            ("Vikram Singh", "photography", 6, "English, Hindi, Punjabi", "Professional photographer and guide who knows the best spots and timings for shooting the palace and surrounding landscapes.", 200, 1500),
            ("Priya Sharma", "cultural", 7, "English, Hindi, Sanskrit", "Specializes in the cultural heritage of Mysore, including local festivals (Dasara), yoga, and traditional crafts.", 120, 1000),
            ("Ashwin Dev", "historical", 10, "English, Kannada, Tamil", "Senior historian guide with publications on the Wodeyar dynasty and regional temples.", 220, 1800),
            
            # Coorg (5)
            ("Rohan K", "nature", 5, "English, Kannada, Kodava", "Coffee plantation tour specialist, trek leader, and bird watching enthusiast in Coorg.", 100, 900),
            ("Kavya M", "nature", 4, "English, Kannada, Malayalam", "Passionate environmentalist and nature walk guide. Enjoys showing the flora and fauna of the Western Ghats.", 110, 1000),
            ("Somanna P", "adventure", 6, "Kannada, Kodava, English", "Trekking expert for Tadiandamol, Brahmagiri, and white-water rafting coordinator in Coorg.", 150, 1300),
            ("Bopanna C", "cultural", 9, "English, Kodava, Hindi", "Specialist in Kodava culture, martial arts history, traditional weddings, and ancestral home visits.", 130, 1100),
            ("Muthappa B", "general", 3, "Kannada, Kodava", "Local resident who guides visitors through popular spots like Abbey Falls, Raja Seat, and Golden Temple.", 70, 600),
            
            # Goa (5)
            ("John Fernandes", "nature", 6, "English, Konkani, Portuguese", "Expert on spice plantation tours, backwater bird-watching, and quiet non-touristy beaches in Goa.", 140, 1200),
            ("Maria D'Souza", "cultural", 8, "English, Konkani, Hindi", "Specializes in old Goan churches, Portuguese history, Indo-Portuguese architecture, and heritage walks.", 150, 1300),
            ("Rohit Naik", "food", 5, "English, Hindi, Konkani", "Food blogger and culinary guide offering spice farm tours, seafood crawls, and traditional feni-tasting experiences.", 160, 1400),
            ("Sunita R", "photography", 4, "English, Hindi, Marathi", "Guides tourists to scenic sunset points, colorful lanes of Fontainhas, and remote fort ruins for photography.", 120, 1100),
            ("David Pinto", "adventure", 7, "English, Konkani", "Scuba diving instructor and trekking guide for Dudhsagar water falls and adventure water sports.", 200, 1800),
            
            # Ooty (5)
            ("Mani K", "historical", 7, "English, Tamil, Badaga", "Guides visitors through Ooty's colonial history, stone house, toy train, and botanical gardens.", 110, 1000),
            ("Rajan S", "nature", 9, "English, Tamil, Malayalam", "Expert on Nilgiri Biosphere, forest trekking, tea garden walks, and local wildlife spotting.", 130, 1200),
            ("Shanthi M", "cultural", 6, "Tamil, English, Kannada", "Specializes in Toda tribal culture, handicrafts, local tea factory tours, and botanical flora.", 100, 900),
            ("Karthik R", "adventure", 5, "English, Tamil, Hindi", "Trekking guide for Doddabetta peak, Pykara falls hiking, and camping coordinator.", 120, 1100),
            ("Lakshmi N", "general", 4, "Tamil, Kannada", "Local guide for quick Ooty sightseeing, shopping for chocolates/essential oils, and boat rides.", 80, 700),
            
            # Manali (5)
            ("Tenzin N", "adventure", 8, "English, Hindi, Tibetan", "Certified mountaineer leading treks to Beas Kund, Hampta Pass, and paragliding coordinator in Solang.", 180, 1600),
            ("Ram Lal", "nature", 10, "Hindi, English", "Specialist in Himalayan flora, apple orchard tours, and day hikes to local waterfalls and hot springs.", 140, 1200),
            ("Shyam Singh", "historical", 6, "Hindi, English", "Guides visitors through Hadimba Temple history, Vashisht temple, and Castle Naggar historical walk.", 100, 900),
            ("Anita Devi", "cultural", 5, "Hindi, English", "Tours around local villages (Malana/Vashisht), detailing Himachali traditions, weaving, and local food.", 110, 1000),
            ("Bobby Sharma", "photography", 4, "Hindi, English", "Landscape photography specialist for snow valleys, Solang, and Rohtang Pass views.", 150, 1300),
            
            # Kerala (5)
            ("Harish Pillai", "nature", 7, "English, Malayalam, Tamil", "Specializes in Alleppey backwater ecology, bird sanctuary tours, and canal canoeing guides.", 120, 1100),
            ("Rajesh Nair", "cultural", 9, "English, Malayalam, Hindi", "Guides tourists through Fort Kochi's Jewish Synagogue, Dutch Palace, and Kathakali dance shows.", 130, 1200),
            ("Anjali V", "food", 5, "English, Malayalam", "Culinary tour guide offering tours of Kochi spice markets and home-cooking classes for traditional sadhya meals.", 150, 1300),
            ("Sajeev K", "general", 6, "English, Malayalam", "Houseboat cruise guide and local coordinator for village tourism and coconut picking demonstrations.", 100, 900),
            ("Unni Krishnan", "adventure", 8, "English, Malayalam, Tamil", "Trekking guide for Munnar hills, Anamudi trekking, and bamboo rafting coordinator.", 160, 1500)
        ]
        
        # Guide image mapping rotation
        g_images = [
            'guides/guide_male.png',
            'guides/guide_female.png',
            'guides/guide_male_old.png',
            'guides/guide_female_indian.png'
        ]
        
        for i, (name, expertise, exp, langs, bio, pph, ppd) in enumerate(guide_data):
            u = guide_users[i]
            # Rename guide user's actual first and last name to match the guide profile name
            name_parts = name.split(" ")
            u.first_name = name_parts[0]
            u.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            u.save()
            
            img_path = g_images[i % len(g_images)]
            g = TourGuide.objects.create(
                user=u, years_experience=exp, expertise=expertise,
                languages=langs, price_per_hour=Decimal(str(pph)), price_per_day=Decimal(str(ppd)),
                bio=bio, is_available=True, is_approved=True, is_featured=(i % 6 == 0),
                avg_rating=Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                total_tours=random.randint(10, 120), profile_image=img_path
            )
            loc = locs[i // 5]
            g.locations.add(loc)
            
        self.stdout.write(f'  -> {len(guide_data)} guides loaded')

    def _emergency(self):
        from accounts.models import TouristLocation
        from ai_assistant.models import EmergencyContact
        locs = list(TouristLocation.objects.all())
        contacts = [
            (0,'Mysore Police Control Room','0821-2420800','police'),
            (0,'Columbia Asia Hospital Mysore','0821-3989999','hospital'),
            (0,'Karnataka Tourist Helpline','1800-425-4425','tourist_helpline'),
            (1,'Madikeri District Hospital','08272-222444','hospital'),
            (1,'Coorg Police Helpline','08272-228333','police'),
            (2,'Goa Police','0832-2423000','police'),
            (2,'Goa Medical College','0832-2458727','hospital'),
            (2,'Goa Tourist Helpline','1800-111-363','tourist_helpline'),
            (3,'Ooty General Hospital','0423-2442212','hospital'),
            (3,'Ooty Police Station','0423-2444000','police'),
            (4,'Manali Police Station','01902-252340','police'),
            (4,'Zonal Hospital Manali','01902-252341','hospital'),
            (5,'Kerala Tourist Helpline','1800-425-4747','tourist_helpline'),
            (5,'Ernakulam General Hospital','0484-2361251','hospital')
        ]
        for idx, name, phone, ctype in contacts:
            if idx < len(locs):
                EmergencyContact.objects.create(location=locs[idx], name=name, phone=phone, type=ctype)
        self.stdout.write(f'  -> {len(contacts)} emergency contacts loaded')

    def _generate_credentials_file(self):
        filepath = os.path.join(settings.BASE_DIR, 'login_credentials.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# SmartTourist User Accounts & Login Credentials\n\n")
            f.write("This file is automatically generated by `python manage.py load_data` for reference.\n")
            f.write("All test accounts share the same default password: **Test@1234**\n\n")
            
            f.write("## 🔑 Admin Account\n\n")
            f.write("| Email | Username | Password | Role |\n")
            f.write("|---|---|---|---|\n")
            f.write("| `admin@smart.in` | `admin` | `Test@1234` | Admin |\n\n")
            
            f.write("## 🔑 Tourist Accounts\n\n")
            f.write("| Email | Username | Password | Role |\n")
            f.write("|---|---|---|---|\n")
            for i in range(1, 6):
                f.write(f"| `tourist{i}@smart.in` | `tourist{i}` | `Test@1234` | Tourist |\n")
            f.write("\n")
            
            f.write("## 🔑 Vehicle Owner Accounts\n\n")
            f.write("| Email | Username | Password | Role |\n")
            f.write("|---|---|---|---|\n")
            for i in range(1, 11):
                f.write(f"| `vowner{i}@smart.in` | `vowner{i}` | `Test@1234` | Vehicle Owner |\n")
            f.write("\n")
            
            f.write("## 🔑 Hotel Owner Accounts\n\n")
            f.write("| Email | Username | Password | Role |\n")
            f.write("|---|---|---|---|\n")
            for i in range(1, 11):
                f.write(f"| `howner{i}@smart.in` | `howner{i}` | `Test@1234` | Hotel Owner |\n")
            f.write("\n")
            
            f.write("## 🔑 Tour Guide Accounts\n\n")
            f.write("| Email | Username | Password | Role | Assigned Name | Destination |\n")
            f.write("|---|---|---|---|---|---|\n")
            
            destinations = ["Mysore", "Coorg", "Goa", "Ooty", "Manali", "Kerala"]
            guide_names = [
                "Ramesh Kumar", "Suresh Gowda", "Vikram Singh", "Priya Sharma", "Ashwin Dev",
                "Rohan K", "Kavya M", "Somanna P", "Bopanna C", "Muthappa B",
                "John Fernandes", "Maria D'Souza", "Rohit Naik", "Sunita R", "David Pinto",
                "Mani K", "Rajan S", "Shanthi M", "Karthik R", "Lakshmi N",
                "Tenzin N", "Ram Lal", "Shyam Singh", "Anita Devi", "Bobby Sharma",
                "Harish Pillai", "Rajesh Nair", "Anjali V", "Sajeev K", "Unni Krishnan"
            ]
            for i in range(1, 31):
                dest = destinations[(i - 1) // 5]
                name = guide_names[i - 1]
                f.write(f"| `guide{i}@smart.in` | `guide{i}` | `Test@1234` | Tour Guide | {name} | {dest} |\n")
            f.write("\n")

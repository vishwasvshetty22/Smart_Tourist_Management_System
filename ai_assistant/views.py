import json, uuid, requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import ChatbotQuery, TripPlan, EmergencyContact
from accounts.models import TouristLocation


# ── Rule-based destination data ───────────────────────────────────────────────
DEST_DATA = {
    'Mysore': {
        'places': ['Mysore Palace','Chamundi Hills','Brindavan Gardens','Mysore Zoo','Devaraja Market','St Philomena Church'],
        'food':   ['Mysore Masala Dosa','Mysore Pak','Obbattu','Curd Rice'],
        'hotels': [{'name':'Lalitha Mahal Palace Hotel','type':'luxury','price_per_night':8000,'rating':4.5},
                   {'name':'Royal Orchid Metropole','type':'deluxe','price_per_night':4500,'rating':4.2},
                   {'name':'Hotel Mayura Hoysala','type':'budget','price_per_night':1200,'rating':3.8}],
        'best_time': 'October to February',
    },
    'Coorg': {
        'places': ["Abbey Falls","Raja's Seat","Namdroling Monastery","Iruppu Falls","Talakaveri","Dubare Elephant Camp"],
        'food':   ['Pandi Curry','Kadambuttu','Bamboo Shoot Curry','Nool Puttu'],
        'hotels': [{'name':'Evolve Back Coorg','type':'resort','price_per_night':12000,'rating':4.8},
                   {'name':'Honey Valley Estate','type':'boutique','price_per_night':3500,'rating':4.4},
                   {'name':'Hotel Capitol','type':'budget','price_per_night':1500,'rating':3.6}],
        'best_time': 'October to May',
    },
    'Goa': {
        'places': ['Baga Beach','Old Goa Churches','Fort Aguada','Dudhsagar Falls','Anjuna Market','Palolem Beach'],
        'food':   ['Fish Curry Rice','Prawn Balchão','Bebinca','Xacuti'],
        'hotels': [{'name':'Taj Fort Aguada','type':'luxury','price_per_night':15000,'rating':4.7},
                   {'name':'Park Hyatt Goa','type':'deluxe','price_per_night':9000,'rating':4.5},
                   {'name':'Zostel Goa','type':'budget','price_per_night':800,'rating':4.0}],
        'best_time': 'November to March',
    },
    'Ooty': {
        'places': ['Botanical Gardens','Ooty Lake','Doddabetta Peak','Nilgiri Mountain Railway','Tea Museum','Pine Forest'],
        'food':   ['Varkey','Home-made Chocolates','Ooty Eucalyptus Tea'],
        'hotels': [{'name':'Savoy Hotel','type':'heritage','price_per_night':6000,'rating':4.4},
                   {'name':'Sterling Ooty','type':'deluxe','price_per_night':4000,'rating':4.2},
                   {'name':'YWCA Ooty','type':'budget','price_per_night':1000,'rating':3.5}],
        'best_time': 'October to June',
    },
    'Manali': {
        'places': ['Rohtang Pass','Solang Valley','Hadimba Temple','Old Manali','Vashisht Hot Springs','River Beas'],
        'food':   ['Sidu','Aktori','Babru','Patande','Khatta'],
        'hotels': [{'name':'Span Resort & Spa','type':'resort','price_per_night':7000,'rating':4.5},
                   {'name':'Hotel Himalayan Heights','type':'standard','price_per_night':2500,'rating':4.0},
                   {'name':'Snow View Guest House','type':'budget','price_per_night':800,'rating':3.7}],
        'best_time': 'March to June & Sep–Nov',
    },
    'Kerala': {
        'places': ['Alleppey Backwaters','Munnar Tea Gardens','Periyar Wildlife','Kovalam Beach','Padmanabhaswamy Temple','Fort Kochi'],
        'food':   ['Kerala Sadhya','Fish Molee','Puttu & Kadala','Appam','Karimeen Pollichathu'],
        'hotels': [{'name':'Kumarakom Lake Resort','type':'resort','price_per_night':18000,'rating':4.9},
                   {'name':'Coconut Lagoon','type':'heritage','price_per_night':10000,'rating':4.7},
                   {'name':'Hotel Sea View','type':'budget','price_per_night':1200,'rating':3.9}],
        'best_time': 'September to March',
    },
}

CHATBOT_RULES = [
    (['hello','hi','hey','helo'],  "👋 Hi! I'm TravelBot. I can help you with vehicles, hotels, guides, trip planning, and more. What can I do for you?"),
    (['vehicle','bike','car','scooter','rent'], "🚗 We offer bikes (₹400–900/day), scooters (₹300–500/day), cars (₹1,200–2,500/day), and SUVs (₹2,000–3,500/day). Visit /vehicles/ to browse!"),
    (['hotel','room','stay','accommodation'], "🏨 Hotels from ₹800/night (budget) to ₹18,000/night (luxury resort). Visit /hotels/ to search by destination!"),
    (['guide','tour guide','local guide'], "🧭 Certified multilingual guides from ₹300/hour or ₹1,500/day. Visit /guides/ to browse profiles!"),
    (['trip','plan','itinerary','ai plan'], "🤖 Use our AI Trip Planner at /ai/trip-planner/ — enter your budget, days & destination to get a full itinerary instantly!"),
    (['goa'], "🌊 Goa: Best Nov–Mar. Must visit Baga Beach, Fort Aguada, Old Goa Churches. Try Fish Curry Rice & Bebinca!"),
    (['mysore'], "🏯 Mysore: Best Oct–Feb. Visit Mysore Palace (stunning during Dasara!), Chamundi Hills, Brindavan Gardens. Famous for Mysore Pak!"),
    (['coorg'], "☕ Coorg: Best Oct–May. Visit Abbey Falls, coffee estates, Raja's Seat. Stay in a plantation homestay!"),
    (['ooty'], "🌸 Ooty: Best Oct–Jun. Take the Nilgiri Mountain Railway, visit Botanical Gardens. Try homemade chocolates!"),
    (['manali'], "❄️ Manali: Best Mar–Jun & Sep–Nov. Visit Rohtang Pass, Solang Valley, Hadimba Temple. Carry warm clothes!"),
    (['kerala'], "🌴 Kerala: Best Sep–Mar. Houseboat in Alleppey, tea gardens in Munnar, Ayurveda retreats. Try Kerala Sadhya!"),
    (['book','booking','how to'], "📅 Booking is easy: 1) Select destination 2) Choose vehicle/hotel/guide 3) Pick dates 4) Pay 5) Get confirmed!"),
    (['cancel','cancellation'], "❌ Cancel any pending/confirmed booking from 'My Bookings' in your dashboard before the service date."),
    (['pay','payment','cost','price'], "💳 We support UPI, Cards, Net Banking. All prices in INR. Payment is simulated in this demo version."),
    (['emergency','sos','help'], "🆘 Emergency numbers: Police: 100 | Ambulance: 108 | Fire: 101 | Tourist Helpline: 1800-111-363"),
    (['weather'], "🌤️ Check live weather on the home page! We show temperature, humidity and wind speed for all 6 destinations."),
    (['thank','thanks','great','awesome'], "😊 You're welcome! Happy travels! Feel free to ask anything else. ✈️"),
]


def _rule_based_response(message):
    msg = message.lower()
    for keywords, response in CHATBOT_RULES:
        if any(k in msg for k in keywords):
            return response
    return ("🤔 I'm not sure about that. I can help with:\n"
            "• Vehicle rentals 🚗\n• Hotel bookings 🏨\n• Tour guides 🧭\n"
            "• Trip planning 🗺️\n• Destinations (Goa, Mysore, Coorg…)\n"
            "• Booking & cancellation help\n\nWhat would you like to know?")


def _generate_plan(location, budget, num_days, num_people, preferences):
    data = DEST_DATA.get(location.name, {
        'places': ['City Centre','Local Market','Heritage Site','Nature Park','Cultural Museum'],
        'food':   ['Local Cuisine','Street Food'],
        'hotels': [{'name':'Grand Hotel','type':'standard','price_per_night':3000,'rating':4.0},
                   {'name':'Budget Inn','type':'budget','price_per_night':1000,'rating':3.5}],
        'best_time': 'October to March',
    })
    places = data['places']
    itinerary = {}
    for d in range(1, num_days + 1):
        ps = places[((d-1)*2) % len(places): ((d-1)*2+3) % len(places) + 1] or places[:3]
        itinerary[f"Day {d}"] = {
            'morning':   f"Visit {ps[0]}. Arrive early for best experience and photography.",
            'afternoon': f"Explore {ps[1] if len(ps)>1 else ps[0]}. Enjoy local lunch — try {', '.join(data['food'][:2])}.",
            'evening':   f"Relax at {ps[2] if len(ps)>2 else ps[0]}. Explore local shops and street food.",
            'tip':       f"Day {d} tip: Carry water, sunscreen, and comfortable footwear.",
        }
    ppd = budget / num_days / num_people
    hotel_cost = 1500 if ppd < 2000 else (4000 if ppd < 7000 else 10000)
    vehicles = [
        {'type':'car','name':'Sedan / Hatchback','price_per_day':1500,'seats':4,'note':'Best for families'},
        {'type':'bike','name':'Royal Enfield / Bullet','price_per_day':800,'seats':2,'note':'Adventure rides'},
        {'type':'scooter','name':'Honda Activa','price_per_day':400,'seats':2,'note':'Budget city rides'},
    ]
    cost = {
        'accommodation': round(hotel_cost * num_days),
        'food':          round(min(ppd * 0.25, 600) * num_days * num_people),
        'transport':     round(min(ppd * 0.20, 500) * num_days),
        'activities':    round(budget * 0.12),
        'misc':          round(budget * 0.08),
        'total_estimated': round(budget * 0.93),
    }
    return {
        'itinerary': itinerary,
        'hotels': data['hotels'],
        'vehicles': vehicles,
        'cost_breakdown': cost,
        'must_visit': places[:5],
        'food': data['food'],
        'best_time': data['best_time'],
        'tips': [
            f"Best time to visit {location.name}: {data['best_time']}",
            "Always carry a government-issued photo ID.",
            "Book hotels/vehicles in advance during peak season.",
            "Respect local customs and dress modestly at religious sites.",
            f"Must-try food: {', '.join(data['food'][:3])}",
        ],
        'location_name': location.name,
    }


def trip_planner(request):
    locations = TouristLocation.objects.filter(is_active=True)
    saved_plans = []
    if request.user.is_authenticated:
        saved_plans = TripPlan.objects.filter(user=request.user)[:5]

    if request.method == 'POST' and request.user.is_authenticated:
        location_id = request.POST.get('location')
        budget      = float(request.POST.get('budget', 10000))
        num_days    = int(request.POST.get('num_days', 3))
        num_people  = int(request.POST.get('num_people', 1))
        prefs       = request.POST.getlist('preferences')
        try:
            location = TouristLocation.objects.get(id=location_id)
            plan = _generate_plan(location, budget, num_days, num_people, prefs)

            trip = TripPlan.objects.create(
                user=request.user, location=location,
                budget=budget, num_days=num_days, num_people=num_people,
                preferences=', '.join(prefs),
                itinerary=plan['itinerary'],
                hotel_suggestions=plan['hotels'],
                vehicle_suggestions=plan['vehicles'],
                cost_breakdown=plan['cost_breakdown'],
                tips=plan['tips'],
                title=f"{num_days}-Day Trip to {location.name}",
            )
            return render(request, 'ai_assistant/trip_result.html', {
                'plan': plan, 'trip': trip, 'location': location
            })
        except Exception as e:
            from django.contrib import messages as msg
            msg.error(request, f'Could not generate plan: {e}')

    return render(request, 'ai_assistant/trip_planner.html', {
        'locations': locations, 'saved_plans': saved_plans
    })


@login_required
def my_trip_plans(request):
    plans = TripPlan.objects.filter(user=request.user)
    return render(request, 'ai_assistant/my_plans.html', {'plans': plans})


@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data       = json.loads(request.body)
        user_msg   = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        if not user_msg:
            return JsonResponse({'error': 'empty'}, status=400)

        # Try OpenAI
        if getattr(settings, 'OPENAI_API_KEY', ''):
            try:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
                recent = list(ChatbotQuery.objects.filter(session_id=session_id).order_by('-timestamp')[:5])
                history = []
                for q in reversed(recent):
                    history += [{"role":"user","content":q.user_message},
                                {"role":"assistant","content":q.bot_response}]
                history.append({"role":"user","content":user_msg})
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role":"system","content":"You are TravelBot, a helpful assistant for SmartTourist. Help with vehicle rentals, hotel bookings, tour guides, and Indian tourism. Be friendly and concise."},
                              *history],
                    max_tokens=400,
                )
                bot_resp = resp.choices[0].message.content
            except Exception:
                bot_resp = _rule_based_response(user_msg)
        else:
            bot_resp = _rule_based_response(user_msg)

        ChatbotQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=session_id,
            user_message=user_msg, bot_response=bot_resp,
        )
        return JsonResponse({'response': bot_resp, 'session_id': session_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def weather_api(request):
    location = request.GET.get('location', 'Mysore')
    key = getattr(settings, 'WEATHER_API_KEY', '')
    if key:
        try:
            url  = f"https://api.openweathermap.org/data/2.5/weather?q={location},IN&appid={key}&units=metric"
            resp = requests.get(url, timeout=5).json()
            return JsonResponse({
                'temperature': resp['main']['temp'],
                'feels_like':  resp['main']['feels_like'],
                'humidity':    resp['main']['humidity'],
                'description': resp['weather'][0]['description'].title(),
                'icon':        resp['weather'][0]['icon'],
                'wind_speed':  resp['wind']['speed'],
            })
        except Exception:
            pass
    import random
    desc = random.choice(['Partly Cloudy','Sunny','Clear Sky','Light Breeze','Overcast'])
    return JsonResponse({
        'temperature': random.randint(20, 32),
        'feels_like':  random.randint(19, 34),
        'humidity':    random.randint(50, 85),
        'description': desc,
        'icon':        '02d',
        'wind_speed':  random.randint(5, 20),
    })


def emergency_contacts(request, location_id):
    contacts = EmergencyContact.objects.filter(location_id=location_id, is_active=True)
    return JsonResponse({'contacts': [
        {'name':c.name,'phone':c.phone,'type':c.type,'address':c.address} for c in contacts
    ]})

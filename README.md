<<<<<<< HEAD
# AI-Based Smart Tourist Travel & Rental Management Platform

**SmartTourist** — Full-stack Django web app with SQLite, AI chatbot, trip planner, vehicle rental, hotel booking & tour guide hiring.

---

##  Quick Start (5 Steps)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations accounts vehicles hotels guides bookings payments ai_assistant notifications admin_dashboard
python manage.py migrate

# 4. Load sample data
python manage.py load_data

# 5. Start server
python manage.py runserver
```

Open → **http://127.0.0.1:8000**

---

## 🔑 Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@smart.in | Test@1234 |

All other users (tourists, vehicle owners, hotel owners, guides) must register themselves via the Register page.

## 🛡️ Admin Panel Access

**URL:** http://127.0.0.1:8000/admin-panel/

Login with **admin@smart.in** / **Test@1234** — the admin panel lets you:
- ✅ Approve / reject vehicles, hotels, and guides
- 👥 Manage users (block/unblock, view roles)
- 📊 View all bookings across the platform
- 💰 Monitor payments and revenue stats
- 🔔 Send notifications to users

> Django's built-in admin (for database-level access) is at `/django-admin/`  
> Create a superuser with: `python manage.py createsuperuser`

## 📧 Email (Forgot Password)

The forgot-password feature is configured to send emails via Gmail SMTP from **vishwasshetty2580@gmail.com**.

**Setup steps:**
1. Enable 2-Step Verification on your Google account
2. Go to: Google Account → Security → App Passwords
3. Generate an App Password (select "Mail" + "Windows Computer")
4. Open `smart_tourist/settings.py` and replace `YOUR_GMAIL_APP_PASSWORD` with the generated password

```python
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'   # your 16-char App Password
```

---

## Project Structure

```
smart_tourist_sqlite/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← auto-created after migrate
├── README.md
│
├── smart_tourist/          ← Django config
│   ├── settings.py         ← SQLite config here
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/               ← Custom User, Auth, Locations
├── vehicles/               ← Vehicle listings & bookings
├── hotels/                 ← Hotel & room management
├── guides/                 ← Tour guide management
├── bookings/               ← Shared booking utilities
├── payments/               ← Payment simulation
├── ai_assistant/           ← AI Trip Planner + TravelBot
├── notifications/          ← System notifications
├── admin_dashboard/        ← Analytics & admin panel
│
├── static/
│   ├── css/main.css        ← Main stylesheet
│   └── js/main.js          ← Main JavaScript
│
└── templates/
    ├── base.html            ← Master layout
    ├── home.html
    ├── accounts/
    ├── vehicles/
    ├── hotels/
    ├── guides/
    ├── ai_assistant/
    ├── admin/
    └── payments/
```

---

## ✨ Features

### Tourist
- Register/Login with role selection
- Browse & filter vehicles, hotels, guides
- Real-time availability checking (AJAX)
- Book vehicles (hourly/daily), hotels, guides
- Simulated payment with transaction ID
- Cancel bookings, view booking history
- AI Trip Planner (budget + days → full itinerary)
- TravelBot AI Chatbot on every page
- Live weather widget
- SOS Emergency button (Police/Ambulance/Fire)
- Save favorites, write reviews

### Vehicle Owner
- List vehicles with images & pricing
- Accept/reject booking requests
- Earnings dashboard

### Hotel Owner
- Add hotels with multiple room types
- Manage reservations

### Tour Guide
- Create profile with expertise & languages
- Accept tour bookings

### Admin
- Analytics dashboard (Chart.js)
- Approve/reject listings (vehicles, hotels, guides)
- Block/unblock users
- View all bookings

---

## 🔌 Optional API Keys

Edit `smart_tourist/settings.py`:

```python
# AI Trip Planner & Chatbot (works without — uses rule-based fallback)
OPENAI_API_KEY = 'sk-...'

# Live Weather Widget (works without — uses mock data)
WEATHER_API_KEY = 'your_openweathermap_key'

# Email (currently prints to console — no setup needed for dev)
# Change EMAIL_BACKEND to smtp for real emails
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Django 4.2 |
| Database | SQLite (built-in, zero config) |
| Frontend | HTML5, Bootstrap 5.3, JavaScript ES6 |
| Charts | Chart.js |
| Icons | Font Awesome 6.5 |
| AI | OpenAI GPT-3.5 + rule-based fallback |
| Weather | OpenWeatherMap API + mock fallback |

---

## 🗺 Key URLs

| URL | Page |
|-----|------|
| `/` | Home |
| `/accounts/register/` | Register |
| `/accounts/login/` | Login |
| `/dashboard/` | Role dashboard |
| `/vehicles/` | Vehicle listings |
| `/hotels/` | Hotel listings |
| `/guides/` | Guide listings |
| `/ai/trip-planner/` | AI Trip Planner |
| `/admin-panel/` | Admin dashboard |
| `/django-admin/` | Django admin |

---

## 📝 Notes

- Database: SQLite — **no MySQL setup needed**. File `db.sqlite3` is created automatically.
- Email: Prints to console in dev mode. Change `EMAIL_BACKEND` in settings for real SMTP.
- Images: Stored in `media/` folder locally.
- All APIs have built-in fallbacks — platform works fully without any API keys.

---

*MCA Final Year Project 2024-25 | SmartTourist Platform*
=======
# Smart_Tourist_Management_System
 Full-stack Django web app with SQLite, AI chatbot, trip planner, vehicle rental, hotel booking &amp; tour guide hiring.
>>>>>>> 044cbc65a2214c6c131544aeed17f01130df6a15

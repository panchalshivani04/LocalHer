# LocalHer 🌸

**LocalHer** is a modern, community-focused Django web application designed to empower local women entrepreneurs by connecting them directly with neighborhood buyers for authentic homemade products, customized goods, and local services.

---

## 🌟 About the Project

In many communities, local women entrepreneurs—such as home bakers, pickle makers, tailors, artisans, and tutors—produce high-quality homemade items and offer essential services. However, they often lack an organized digital platform to showcase their storefronts to nearby customers.

**LocalHer** solves this problem by providing a neighborhood digital marketplace where:
- **Customers** can discover nearby homemade products and services, save favorites, place orders, write reviews, and communicate safely with sellers.
- **Women Entrepreneurs (Sellers)** can register storefronts, create product/service listings, track customer order requests, manage listings, and receive verified badges.
- **Community Safety & Privacy** are prioritized through built-in user blocking, incident reporting, and platform-wide moderation tools.

---

## 🎯 Problem Statement

Small, home-based businesses run by women often rely on informal word-of-mouth or social messaging groups. This creates key challenges:
1. **Limited Local Discoverability**: Nearby residents are often unaware of home businesses operating in their immediate neighborhood.
2. **Lack of Organized Catalogs**: Products and pricing are hard to browse systematically.
3. **Safety & Privacy Concerns**: Sharing personal contact numbers publicly can lead to unwanted harassment or unmonitored communication.

**LocalHer** provides a dedicated, structured marketplace platform with category search, structured storefronts, transparent order lifecycles, and built-in chat moderation to foster safe community commerce.

---

## 💡 Project Objective

- **Promote Local Women Entrepreneurs**: Increase online visibility for home businesses.
- **Streamline Product & Service Discovery**: Enable search and filtering by category, product type, city, area, and business name.
- **Enable Safe In-App Communication**: Provide built-in messaging with photo sharing and privacy controls so users do not need to share phone numbers publicly.
- **Facilitate Order Workflow**: Provide a sequential order request lifecycle (`PENDING` → `ACCEPTED` → `FULFILLED` / `CANCELLED`) with automatic chat notifications.
- **Maintain Platform Moderation**: Empower administrators with custom tools to review safety reports, verify businesses, and block abusive accounts.

---

## ✨ Key Features

### 👤 Customer Features
- **User Authentication**: Secure registration and login with session management.
- **Marketplace Browsing**: Filter listings by category (e.g., *Food & Pickles*, *Tailoring & Embroidery*, *Baking & Desserts*) and listing type (*Physical Product* vs. *Local Service*).
- **Search**: Search listings by keyword, business name, or location.
- **Cart & Order Placement**: Add items to cart and place orders with custom instructions.
- **Sequential Order Tracker**: Monitor order status in real time (`PENDING`, `ACCEPTED`, `FULFILLED`, `CANCELLED`).
- **Favorites**: Save favorite products for quick access.
- **Product Reviews & Ratings**: Submit 1 to 5 star ratings and written feedback for purchased items.

### 🏪 Seller & Storefront Features
- **Seller Registration**: Register a custom business profile with a bio, location details, area pincode, cover image, and WhatsApp contact.
- **Product & Service Management**: Add, edit, or delete listings with title, slug, price unit, description, category, and multiple image attachments.
- **Storefront Page**: Unique public business profile URL displaying all active listings.
- **Seller Order Management**: View incoming customer order requests, update order status sequentially, and notify customers automatically.
- **Verification Badge**: Receive an admin-verified trust badge (`Verified ✅`).

### 💬 In-App Messaging & Safety Controls
- **Real-Time Customer-Seller Chat**: Messaging thread per customer-seller pairing with unread badge counters.
- **Image Sharing**: Send photo attachments (e.g., reference designs, custom stitching samples, product photos) directly inside chat threads.
- **Automated Order System Logs**: Inline chat notifications automatically generated on order placement, acceptance, completion, or cancellation.
- **User Blocking**: Instantly block specific users from contacting you.
- **Incident Reporting**: Submit safety reports for review by platform administrators.

### 🛡️ Custom Admin Command Center (`/localher-admin/`)
- **Automatic Superuser Redirection**: Superuser logins automatically land on the custom admin dashboard.
- **Real-Time Statistics**: Monitor total customers, registered sellers, active listings, customer reviews, pending reports, and blocked accounts.
- **Customer Management**: Search, inspect, suspend, block, or restore customer accounts.
- **Seller & Business Directory**: Inspect registered storefronts, verify businesses, or manage access.
- **Product & Review Moderation**: Moderate listings and delete inappropriate reviews.
- **Safety Reports Queue**: Review incident reports with actions to *Mark Under Review*, *Dismiss*, *Suspend User*, or *Block User Permanently*.
- **Blocked Users Directory**: Manage platform-wide login-disabled accounts.
- **Standard Django Admin Backup**: Full preservation of standard `/admin/` portal for advanced database management.

---

## 👥 User Roles

| Role | Access & Capabilities |
| :--- | :--- |
| **Customer** | Browse marketplace, search products/services, add to cart, place orders, chat with sellers, save favorites, leave reviews, block/report users. |
| **Seller** | Everything a customer can do, plus: create business profile, manage product/service listings, view incoming orders, update order status, receive verification badge. |
| **Superuser / Admin** | Access Custom Admin Dashboard (`/localher-admin/`) and standard Django Admin (`/admin/`), view database analytics, verify sellers, moderate reviews/products, review safety reports, suspend or permanently block user logins. |

---

## 💬 Communication & Safety

LocalHer features a dedicated in-app messaging system connecting buyers and sellers without exposing personal phone numbers publicly.

```
Customer ──( In-App Chat )── Seller
   │                               │
   ├─────── Block User ────────────┤ (Prevents direct contact between users)
   │                               │
   └─────── Report User ───────────┴─► Admin Moderation Queue ─► Platform Ban
```

### Privacy & Data Storage
- **Database Persistence**: Messages and media attachments are stored securely in the database (`chat_message` table) and associated strictly with authorized customer-seller conversations.
- **Strict Authorization**: Conversations are private and restricted to the participating customer, seller, and platform administrators investigating safety reports.
- **Unsend Capability**: Users can unsend their own chat messages.

### Safety Terminology
- **BLOCK (Peer-to-Peer)**: Prevents a specific user from sending messages or initiating new conversations with the person who blocked them.
- **REPORT**: Submits an incident report to the platform administration queue for investigation.
- **ADMIN ACTION (Platform-Wide)**: Administrators can review reports and set `user.is_active = False`, immediately logging out the offender and blocking them from logging into LocalHer.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.14, Django 5.2 / 6.1
- **Database**: 
  - **PostgreSQL** (Production / Render deployment via `psycopg2-binary` & `dj-database-url`)
  - **SQLite3** (`db.sqlite3` fallback for local offline development)
- **Frontend & Styling**: HTML5, Vanilla CSS (`static/css/main.css`), Bootstrap 5, FontAwesome 6
- **Typography**: Google Fonts (*Plus Jakarta Sans* & *Inter*)
- **Environment Management**: `python-dotenv`

---

## 🏗️ Project Architecture

```
                      ┌───────────────────────────┐
                      │    Web Browser Client     │
                      └─────────────┬─────────────┘
                                    │ HTTP / REST
                                    ▼
                      ┌───────────────────────────┐
                      │    Django WSGI Server     │
                      └─────────────┬─────────────┘
                                    │
    ┌──────────────┬────────────────┼────────────────┬──────────────┐
    ▼              ▼                ▼                ▼              ▼
┌─────────┐  ┌────────────┐  ┌─────────────┐  ┌────────────┐  ┌───────────┐
│ accounts│  │marketplace │  │   orders    │  │    chat    │  │   admin   │
└────┬────┘  └─────┬──────┘  └──────┬──────┘  └─────┬──────┘  └─────┬─────┘
     │             │                │               │             │
     └─────────────┴────────────────┼───────────────┴─────────────┘
                                    │ ORM
                                    ▼
                      ┌───────────────────────────┐
                      │  PostgreSQL / SQLite DB   │
                      └───────────────────────────┘
```

---

## 📁 Project Structure

```
LocalHer/
├── accounts/               # User authentication, profiles & registration
│   ├── models.py           # User & SellerProfile models
│   ├── views.py            # Login, registration, profile views
│   └── urls.py
├── marketplace/            # Category & Product discovery catalog
│   ├── models.py           # Category, Product, ProductImage & Review models
│   ├── views.py            # Marketplace, catalog, search, product detail
│   └── urls.py
├── orders/                 # Cart & Order processing pipeline
│   ├── models.py           # Order, OrderItem, CartItem, Favorite models
│   ├── views.py            # Checkout, customer orders, order cancel
│   └── urls.py
├── dashboard/              # Seller Dashboard management
│   ├── views.py            # Seller order management, listing management
│   └── urls.py
├── chat/                   # In-app real-time messaging & moderation
│   ├── models.py           # Conversation, Message, UserBlock, Report models
│   ├── views.py            # Chat threads, unsend message, report/block endpoints
│   └── urls.py
├── admin_dashboard/        # Custom LocalHer Admin Command Center
│   ├── decorators.py       # @superuser_required protection
│   ├── views.py            # Dashboard stats, moderation queue, user management
│   └── urls.py
├── localher/               # Django core settings & root URL routing
│   ├── settings.py         # Database settings, dj-database-url, dotenv
│   └── urls.py
├── static/                 # CSS stylesheets, JavaScript & static assets
│   └── css/main.css
├── templates/              # HTML Django templates
│   ├── accounts/
│   ├── admin_dashboard/
│   ├── chat/
│   ├── dashboard/
│   ├── marketplace/
│   ├── orders/
│   └── base.html
├── media/                  # User uploads (product photos, profile pictures)
├── .env.example            # Environment variables configuration template
├── .gitignore              # Git ignore configuration
├── manage.py               # Django CLI management script
└── requirements.txt        # Python package dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ installed
- Git installed

### 2. Clone the Repository
```bash
git clone https://github.com/panchalshivani04/LocalHer.git
cd LocalHer
```

### 3. Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Configuration
Copy `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```
*(Optionally set `DATABASE_URL=postgres://...` in `.env` if connecting to local PostgreSQL. If omitted, Django defaults to local `db.sqlite3`.)*

### 6. Apply Database Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver 8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser!

---

## 🌐 Deploying to Render

1. Push your repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com/) and connect your repository.
3. Create a **PostgreSQL Instance** on Render.
4. Add the following **Environment Variables** in Render Web Service settings:
   - `DATABASE_URL`: *(Automatically filled by Render when linking PostgreSQL)*
   - `SECRET_KEY`: `your-secure-production-secret-key`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
5. Render Build & Start Commands:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py init_superuser`
   - **Start Command**: `gunicorn localher.wsgi:application`

---

# Restaurant Menu System - Backend API

This is the Django REST API backend for the Restaurant Menu System.

## Features

- **Categories Management**: CRUD operations for food categories
- **Menu Items**: Complete menu item management with multilingual support
- **Promotions**: Special offers and promotional items
- **Reviews**: Customer review system with approval workflow
- **Orders**: Order management system for restaurant operations
- **Search**: Advanced search functionality for menu items
- **Multilingual Support**: English, Uzbek, and Russian language support

## API Endpoints

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}/` - Get category details

### Menu Items
- `GET /api/menu-items/` - List all menu items
- `GET /api/menu-items/{id}/` - Get menu item details
- `GET /api/categories/{id}/menu-items/` - Get menu items by category

### Promotions
- `GET /api/promotions/` - List active promotions
- `GET /api/promotions/{id}/` - Get promotion details

### Reviews
- `GET /api/reviews/` - List approved reviews
- `POST /api/reviews/` - Create new review (requires approval)

### Orders
- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Get order details
- `PATCH /api/orders/{id}/status/` - Update order status

### Search & Stats
- `GET /api/search/?q={query}` - Search menu items
- `GET /api/stats/` - Get menu statistics

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip or pipenv

### Installation

1. **Clone the repository and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate with sample data (optional)**
   ```bash
   python manage.py populate_data
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` to manage:
- Categories
- Menu Items
- Promotions
- Reviews
- Orders

## API Documentation

The API uses Django REST Framework and provides:
- JSON responses
- Pagination (20 items per page)
- Filtering and searching
- CORS support for frontend integration

## Database

The project uses SQLite by default for development. For production, configure PostgreSQL or MySQL in settings.py.

## File Structure

```
backend/
├── restaurant_api/          # Django project settings
├── menu/                   # Main app
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # Data serializers
│   ├── urls.py            # URL routing
│   └── management/        # Custom management commands
├── media/                 # Uploaded files
├── staticfiles/           # Static files
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Development

### Adding New Features

1. Create models in `menu/models.py`
2. Create serializers in `menu/serializers.py`
3. Create views in `menu/views.py`
4. Add URLs in `menu/urls.py`
5. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Testing

```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper database
3. Set up static file serving
4. Configure CORS for your domain
5. Use environment variables for sensitive data

## Support

For questions or issues, please check the Django REST Framework documentation or create an issue in the repository.

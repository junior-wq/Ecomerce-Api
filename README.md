# E-Commerce API

A RESTful backend for an e-commerce application built with **Django** and **Django REST Framework**. Handles products, users, carts, orders, and payment processing with Stripe. Designed to be consumed by a separate frontend.

## Features

- User authentication (login/register)
- Product catalog with stock management
- Cart and order management
- Payment integration with Stripe
- RESTful endpoints for all resources
- Role-based access control for admin operations

## Getting Started

### Prerequisites

- Python 3.9+
- Stripe account for testing payments

### Installation

1. Clone the repository:

```bash
git clone https://github.com/junior-wq/ecommerce-api.git
cd ecommerce-api
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Set up environment variables in a .env file at the project root:
```   
STRIPE_API_KEY=sk_test_XXXXXXXXXXXXXXXXX
DOMAIN= Your domain
```
5. Apply migrations:
```
python manage.py migrate
```

6. Run the development server:
```
python manage.py runserver
```



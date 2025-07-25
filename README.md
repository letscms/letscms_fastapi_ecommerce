# E-commerce FastAPI Application

A full-featured e-commerce API built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

### Core Functionality
- **User Management**: Registration, authentication, profile management
- **Product Catalog**: Categories, products, inventory management
- **Shopping Cart**: Add/remove items, quantity management
- **Order Management**: Order creation, status tracking, order history
- **Reviews & Ratings**: Product reviews and ratings system
- **Address Management**: Multiple shipping addresses per user
- **Payment Processing**: Stripe integration for payments
- **Admin Dashboard**: Analytics, order management, inventory control

### Security Features
- JWT-based authentication
- Role-based access control (User/Admin)
- Password hashing with bcrypt
- Input validation with Pydantic

### API Features
- RESTful API design
- Comprehensive API documentation (Swagger/OpenAPI)
- CORS support
- Error handling and validation
- Pagination support

## Project Structure

```
fastapi_app/
├── app/
│   ├── controllers/          # Business logic
│   │   ├── user_controller.py
│   │   ├── product_controller.py
│   │   ├── cart_controller.py
│   │   ├── order_controller.py
│   │   ├── category_controller.py
│   │   ├── address_controller.py
│   │   └── review_controller.py
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── address.py
│   │   └── review.py
│   ├── routes/              # API endpoints
│   │   ├── user_routes.py
│   │   ├── product_routes.py
│   │   ├── cart_routes.py
│   │   ├── order_routes.py
│   │   ├── category_routes.py
│   │   ├── address_routes.py
│   │   ├── review_routes.py
│   │   ├── payment_routes.py
│   │   └── admin_routes.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user_schema.py
│   │   ├── product_schema.py
│   │   ├── cart_schema.py
│   │   ├── order_schema.py
│   │   ├── category_schema.py
│   │   ├── address_schema.py
│   │   └── review_schema.py
│   ├── utils/               # Utility functions
│   │   ├── auth_dependency.py
│   │   ├── jwt_handler.py
│   │   └── payment_service.py
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   └── main.py              # FastAPI app
├── requirements.txt         # Dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (optional, for caching)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv fastapi_venv
   source fastapi_venv/bin/activate  # On Windows: fastapi_venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE ecommerce_db;
   CREATE USER ecommerce_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login
- `GET /api/users/me` - Get current user info

### Products
- `GET /api/products/` - List products
- `GET /api/products/{id}` - Get product by ID
- `GET /api/products/search` - Search products
- `POST /api/products/` - Create product (Admin)
- `PUT /api/products/{id}` - Update product (Admin)
- `DELETE /api/products/{id}` - Delete product (Admin)

### Categories
- `GET /api/categories/` - List categories
- `GET /api/categories/{id}` - Get category by ID
- `POST /api/categories/` - Create category (Admin)
- `PUT /api/categories/{id}` - Update category (Admin)
- `DELETE /api/categories/{id}` - Delete category (Admin)

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add` - Add item to cart
- `PUT /api/cart/items/{id}` - Update cart item
- `DELETE /api/cart/items/{id}` - Remove item from cart
- `DELETE /api/cart/clear` - Clear cart

### Orders
- `GET /api/orders/` - Get user's orders
- `GET /api/orders/{id}` - Get order by ID
- `POST /api/orders/` - Create order
- `POST /api/orders/{id}/cancel` - Cancel order
- `GET /api/orders/admin` - Get all orders (Admin)
- `PUT /api/orders/{id}` - Update order (Admin)

### Addresses
- `GET /api/addresses/` - Get user's addresses
- `POST /api/addresses/` - Create address
- `PUT /api/addresses/{id}` - Update address
- `DELETE /api/addresses/{id}` - Delete address

### Reviews
- `GET /api/reviews/` - Get reviews
- `POST /api/reviews/` - Create review
- `PUT /api/reviews/{id}` - Update review
- `DELETE /api/reviews/{id}` - Delete review

### Payments
- `POST /api/payments/create-payment-intent` - Create payment intent
- `POST /api/payments/confirm-payment` - Confirm payment
- `POST /api/payments/refund` - Process refund (Admin)

### Admin
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/recent-orders` - Recent orders
- `GET /api/admin/top-products` - Top selling products
- `GET /api/admin/low-stock-products` - Low stock alerts
- `GET /api/admin/revenue-chart` - Revenue analytics

## Database Schema

### Users
- ID, username, email, password
- First name, last name, phone
- Admin status, active status
- Timestamps

### Products
- ID, name, description, price
- SKU, stock quantity, image URL
- Category relationship
- Active status, timestamps

### Categories
- ID, name, description
- Image URL, active status
- Timestamps

### Orders
- ID, user relationship, total amount
- Status, shipping/billing addresses
- Payment method, tracking number
- Timestamps

### Order Items
- Order and product relationships
- Quantity, price at time of order

### Cart Items
- User and product relationships
- Quantity, timestamps

### Addresses
- User relationship, address fields
- Default address flag

### Reviews
- User and product relationships
- Rating (1-5), comment
- Timestamps

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Error Handling

The API returns consistent error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Environment Variables

Required environment variables (see `.env.example`):

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `STRIPE_SECRET_KEY` - Stripe secret key for payments
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, Please Connect Over Whatsapp: +919717478599.
We provide Software development Services for the Webapplications and Mobile applications as well

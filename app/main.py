from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    user_routes, category_routes, product_routes, cart_routes, 
    order_routes, address_routes, review_routes, payment_routes, admin_routes
)
from app.database import engine, Base
from app.models import user, category, product, address, cart, order, review
import sys

app = FastAPI(
    title="E-commerce API",
    description="A comprehensive e-commerce API built with FastAPI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables
Base.metadata.create_all(bind=engine)

print("PYTHONPATH:", sys.path)

# Include routers
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
app.include_router(category_routes.router, prefix="/api/categories", tags=["Categories"])
app.include_router(product_routes.router, prefix="/api/products", tags=["Products"])
app.include_router(cart_routes.router, prefix="/api/cart", tags=["Cart"])
app.include_router(order_routes.router, prefix="/api/orders", tags=["Orders"])
app.include_router(address_routes.router, prefix="/api/addresses", tags=["Addresses"])
app.include_router(review_routes.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(payment_routes.router, prefix="/api/payments", tags=["Payments"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to E-commerce API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api")
def api_info():
    return {
        "title": "E-commerce API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/api/users",
            "categories": "/api/categories",
            "products": "/api/products",
            "cart": "/api/cart",
            "orders": "/api/orders",
            "addresses": "/api/addresses",
            "reviews": "/api/reviews",
            "payments": "/api/payments",
            "admin": "/api/admin",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }
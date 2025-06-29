import os
import django
import random
from decimal import Decimal
from datetime import datetime

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

# Clear existing data (optional)
Customer.objects.all().delete()
Product.objects.all().delete()
Order.objects.all().delete()

# Create sample customers
customers = [
    Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
    Customer(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
    Customer(name="Carol Davis", email="carol@example.com"),
]

Customer.objects.bulk_create(customers)
print(f"✅ Created {Customer.objects.count()} customers")

# Create sample products
products = [
    Product(name="Laptop", price=Decimal("999.99"), stock=10),
    Product(name="Smartphone", price=Decimal("599.49"), stock=25),
    Product(name="Headphones", price=Decimal("89.99"), stock=50),
]

Product.objects.bulk_create(products)
print(f"✅ Created {Product.objects.count()} products")

# Create an order for Alice with 2 products
customer = Customer.objects.get(email="alice@example.com")
selected_products = list(Product.objects.all()[:2])
total = sum(p.price for p in selected_products)

order = Order.objects.create(
    customer=customer,
    total_amount=total,
    order_date=datetime.now()
)
order.products.set(selected_products)

print(f"✅ Created 1 order for {customer.name} with total amount {total}")

print("🎉 Database seeding complete!")

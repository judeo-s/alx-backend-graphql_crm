import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from decimal import Decimal
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.db import transaction
from django.utils import timezone
from graphql import GraphQLError
import re

class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# ===> GraphQL Types <===
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    products = graphene.List(ProductType)
    total_amount = graphene.Decimal()

    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

    def resolve_products(self, info):
        return self.products.all()

    def resolve_total_price(self, info):
        return self.total_amount

# ===> Helper Validation <===
def is_valid_phone(phone):
    return bool(re.match(r'^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$', phone))

# ===> Mutations <===
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        name = input.name
        email = input.email
        phone = input.phone

        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists.")

        if phone and not is_valid_phone(phone):
            raise GraphQLError("Invalid phone format.")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created = []
        errors = []

        for item in input:
            try:
                name = item.name
                email = item.email
                phone = item.phone

                if not name or not email:
                    raise ValueError("Name and Email are required")
                if Customer.objects.filter(email=email).exists():
                    raise ValueError(f"Email {email} already exists")
                if phone and not is_valid_phone(phone):
                    raise ValueError(f"Invalid phone: {phone}")

                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                created.append(customer)
            except Exception as e:
                errors.append(str(e))
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)
    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        name = input.name
        price = Decimal(str(input.price))
        stock = input.stock or 0

        if price <= 0:
            raise GraphQLError("Price must be positive")
        if stock < 0:
            raise GraphQLError("Stock can't be negative")
        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)
    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        customer_id = input.customer_id
        product_ids = input.product_ids
        order_date = input.order_date

        if not product_ids:
            raise GraphQLError("Atleast one product must be selected")
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")

        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise GraphQLError("One or more products are invalid.")

        total_amount = sum([p.price for p in products])
        order = Order(customer=customer, total_amount=total_amount, order_date=order_date or timezone.now())
        order.save()
        order.products.set(products)

        return CreateOrder(order=order)

# ===> Root Query and Mutation <===
class Query(graphene.ObjectType):
    customer = graphene.relay.Node.Field(CustomerType)
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)

    product = graphene.relay.Node.Field(ProductType)
    all_products = DjangoFilterConnectionField(ProductType)

    order = graphene.relay.Node.Field(OrderType)
    all_orders = DjangoFilterConnectionField(OrderType)

    # def resolve_all_customers(root, info):
    #     return Customer.objects.all()

    # def resolve_all_products(root, info):
    #     return Product.objects.all()

    # def resolve_all_orders(root, info):
    #     return Order.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

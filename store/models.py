from django.db import models
from users.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    price = models.IntegerField()
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrderManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}

        if not post_data.get('total_price'):
            errors['total_price'] = "Total price is required."

        return errors


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    def __str__(self):
        return f"Order #{self.id} - {self.user.first_name}"


class OrderItemManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}

        quantity = post_data.get('quantity')
        if not quantity or not quantity.isdigit() or int(quantity) < 1:
            errors['quantity'] = "Quantity must be a positive number."

        return errors


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField()
    subtotal_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderItemManager()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"
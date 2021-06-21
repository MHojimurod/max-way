from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    combo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "category"


class Product(models.Model):
    title = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    price = models.IntegerField(blank=False, null=False, default=0)
    image = models.ImageField(upload_to='image/', blank=False, null=False)
    category = models.ForeignKey(Category, blank=False, null=True, on_delete=models.SET_NULL)
    foods = models.ManyToManyField('self', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "product"


class Order(models.Model):
    products = models.JSONField(blank=False, null=False)
    status = models.IntegerField(blank=False, null=False, default=1)
    total_price = models.IntegerField(blank=False, null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order"


class User(models.Model):
    first_name = models.CharField(max_length=128, blank=False, null=False)
    last_name = models.CharField(max_length=128, blank=False, null=False)
    phone = models.CharField(max_length=100, blank=False, null=False)
    price_type = models.PositiveIntegerField(blank=False, null=False, default=0)
    order = models.ForeignKey(Order, blank=False, null=True, on_delete=models.SET_NULL)
    address = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "user"

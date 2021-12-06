from decimal import Decimal
from django.db.models import fields
from django.db import transaction
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from core.models import User
from store.models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, Review

class CustomerSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    user_id = serializers.IntegerField(read_only=True)
    # user = serializers.PrimaryKeyRelatedField(queryset= User.objects.all())
    class Meta:
        model = Customer
        fields = ["id","user_id","phone","birth_date","membership"]

class CollectionSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    class Meta:
        model = Collection
        fields = ["id","title","products_count"]
    products_count=serializers.IntegerField(read_only=True)
    # products_count = serializers.SerializerMethodField(method_name="calc_products_count")
    # def calc_products_count(self,collection:Collection):
    #     return collection.product_set.count()
# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6,decimal_places= 2,source="unit_price")
#     price_with_tax = serializers.SerializerMethodField(method_name="calc_tax")
#     collection_id = serializers.IntegerField()
#     # collection = serializers.PrimaryKeyRelatedField(queryset= Collection.objects.all()) #不明白为什么需要queryset
#     # collection = serializers.StringRelatedField()
#     # collection = CollectionSerializer()
#     collection = serializers.HyperlinkedRelatedField(queryset =Collection.objects.all(),view_name = "collection-detail")
#     def calc_tax(self,product:Product):
#         return product.unit_price*Decimal(1.1)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=["id","title","unit_price","description","slug","inventory","price_with_tax","collection","collection_id"] #对于外键还真的构造了外键id字段
    # collection = serializers.HyperlinkedRelatedField(queryset =Collection.objects.all(),view_name = "collection-detail")
    # price = serializers.DecimalField(max_digits=6,decimal_places= 2,source="unit_price")
    price_with_tax = serializers.SerializerMethodField(method_name="calc_tax")
    def calc_tax(self,product:Product):
        return product.unit_price*Decimal(1.1)
    def validate(self, attrs):
        return super().validate(attrs)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields=['id','date','name','description']
    def create(self, validated_data):
        product_id = self.context['product_pk']
        return Review.objects.create(product_id=product_id,**validated_data)


class CartItemProductSerializer(serializers.ModelSerializer):
        class Meta:
            model=Product
            fields=["id","title","unit_price","description","slug"] #对于外键还真的构造了外键id字段
        
    
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields = ["id","product","quantity","total_price"]
    product = CartItemProductSerializer()
    total_price=serializers.SerializerMethodField()
    def get_total_price(self,cartItem:CartItem):
        return cartItem.product.unit_price * cartItem.quantity
class CartItemPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields = ["quantity"]
    
class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields = ["id","product","quantity"]

    def save(self, **kwargs):
        return super().save(**kwargs)

    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        try:
            cartItem=CartItem.objects.get(cart_id=cart_id,product_id=validated_data['product'].id)
            cartItem.quantity+=validated_data['quantity']
            cartItem.save()
            return cartItem
        except CartItem.DoesNotExist:
            return CartItem.objects.create(cart_id=cart_id,**validated_data)

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields = ["id","created_at","items","total_price"]
    id=serializers.UUIDField(read_only=True)
    items=CartItemSerializer(many=True,read_only=True)
    total_price=serializers.SerializerMethodField()
    def get_total_price(self,cart:Cart):
        return sum(cartItem.product.unit_price * cartItem.quantity for cartItem in cart.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields = ["id","product","quantity","unit_price"]
    product=ProductSerializer()
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields = ["id","placed_at","customer","payment_status","items"]
        # read_only_fields=["items"]
    
    items=OrderItemSerializer(many=True)
class OrderPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields = ["payment_status"]
        # read_only_fields=["items"]
    

class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    def validate_cart_id(self,cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No cart with the given ID was found")
        elif CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("No cart items")
        return cart_id
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id=self.validated_data['cart_id']
            (customer,_) = Customer.objects.get_or_create(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cartItems = CartItem.objects.filter(cart_id=cart_id)
            orderItems = [OrderItem(order=order,product=cartItem.product,quantity=cartItem.quantity,unit_price=cartItem.product.unit_price) for cartItem in cartItems]
            OrderItem.objects.bulk_create(orderItems)
            Cart.objects.get(pk=cart_id).delete()
            return order

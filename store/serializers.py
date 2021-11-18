from decimal import Decimal
from django.db.models import fields
from rest_framework import serializers

from store.models import Collection, Product, Review
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

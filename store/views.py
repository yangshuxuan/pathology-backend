from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView


from .models import Collection, Product

from .serializers import CollectionSerializer, ProductSerializer
# Create your views here.
class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    def get_serializer_context(self):
        return {'request':self.request}


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all() #为什么需要这个呢
    serializer_class = ProductSerializer
    
    def delete(self,request,pk):
        product = get_object_or_404(Product,pk=pk)
        if product.orderitems.count() > 0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    

class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(products_count=Count("products")) #为什么需要这个呢
    serialize_class = CollectionSerializer

    def delete(self,request,pk):
        collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")),pk=pk)
        if collection.products_count > 0:
            return Response({"error":"can't delete it"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

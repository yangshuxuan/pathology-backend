from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from store.filters import ProductFilter

from .models import Collection, OrderItem, Product, Review

from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilter
    
    def get_serializer_context(self):
        return {'request':self.request}
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id = kwargs["pk"]).count()> 0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)




class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id = kwargs["pk"]).count()> 0:
            return Response({"error":"can't delete it"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        get_object_or_404(Product,pk=self.kwargs["product_pk"])
        return Review.objects.filter(product_id=self.kwargs["product_pk"])
        
    def get_serializer_context(self):
        return {"product_pk":self.kwargs["product_pk"]}
        
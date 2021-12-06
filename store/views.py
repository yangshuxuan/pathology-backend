from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework import pagination
from rest_framework.decorators import action, permission_classes
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from django.db.models import Count, F, Value
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from store.filters import ProductFilter
from store.pagination import DefaultPagination
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated

from store.permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission

from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, Review
from .serializers import CartItemCreateSerializer, CartItemPatchSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CustomerSerializer, OrderCreateSerializer, OrderPatchSerializer, OrderSerializer, ProductSerializer, ReviewSerializer



class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(CreateModelMixin,ListModelMixin,RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin,GenericViewSet):
    http_method_names =['get','post','patch','delete']
    # serializer_class = CartItemCreateSerializer
    # serializer_class = CartItemSerializer
    def get_queryset(self):
        get_object_or_404(Cart,pk=self.kwargs["cart_pk"])
        return CartItem.objects.select_related('product').annotate(total_price=F('product__unit_price')*F('quantity')).filter(cart_id=self.kwargs["cart_pk"])
    def get_serializer_class(self):
        if self.request.method=="POST":
            return CartItemCreateSerializer
        elif self.request.method=="PATCH":
            return CartItemPatchSerializer
        else:
            return CartItemSerializer
 
    def get_serializer_context(self):
        return {"cart_pk":self.kwargs["cart_pk"]}



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilter
    search_fields =['title','description','collection__title']
    ordering_fields = ['unit_price']
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_context(self):
        return {'request':self.request}
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id = kwargs["pk"]).count()> 0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)




class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
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
        
# class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes=[IsAdminUser]
    # permission_classes=[DjangoModelPermissions]
    # permission_classes = [FullDjangoModelPermissions]
    # permission_classes=[DjangoModelPermissionsOrAnonReadOnly]
    # permission_classes=[IsAuthenticated]
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    @action(detail=True,permission_classes=[ViewCustomerHistoryPermission])
    def history(self,request,pk):
        return Response(f"ok {pk}")


    @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    def me(self,request):
        (customer,created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
# class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
class OrderViewSet(ModelViewSet):
    http_method_names=["get","patch","delete","head","options"]
    # serializer_class = OrderSerializer
    # queryset = Order.objects.all()
    # permission_classes=[IsAdminUser]
    # permission_classes=[IsAuthenticated]
    # def get_permissions(self):
    #     if self.request.method in ['PUT','DELETE','PATCH']:
    #         return [IsAdminUser()]
    #     return [IsAuthenticated()]
        
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data = request.data,context={"user_id":self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    def get_serializer_class(self):
        if self.request.method=="POST":
            return OrderCreateSerializer
        elif self.request.method == 'PATCH':
            return OrderPatchSerializer
        return OrderSerializer
    def get_serializer_context(self):
        return {"user_id":self.request.user.id}




    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only("id").get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)
    
    @action(detail=False,permission_classes=[])
    def history(self,request):
        data = {
            "Image": {
                "xmlns": "http://schemas.microsoft.com/deepzoom/2009",
                "Url": "http://127.0.0.1:9001/media/mydz_files/",
                "Overlap": "0",
                "TileSize": "254",
                "Format": "jpeg",
                "Size": {
                "Height": "74973",
                "Width": "78888",
                },
            }
            }
        return Response(data)

from django.http import JsonResponse
from .serializers import productSerializer, OrderSerializer, ProductInfoSerializer, OrderCreateSerializer, UserSerializer
from .models import Product, Order, User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from api.filters import ProductFilter, InStockFilterBackend, OrderFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework import viewsets
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.throttling import ScopedRateThrottle
from api.tasks import send_order_confirmation_mail


class ProductListCreateAPIView(generics.ListCreateAPIView):
    throttle_scope = 'products'
    throttle_classes = [ScopedRateThrottle]
    queryset = Product.objects.order_by('pk')
    serializer_class = productSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = None
    # pagination_class.page_query_param = 'pagenum'
    # pagination_class.page_size_query_param = 'size'
    # pagination_class.max_page_size = 4
    
    
    @method_decorator(cache_page(60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()
    
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
            
        
        return super().get_permissions()


#  Not using this
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serailizer = productSerializer(products, many=True)
    
    return Response({
        'data': serailizer.data
    })


#  Not using this
class ProductCreateAPIView(generics.CreateAPIView):
    model = Product
    serializer_class = productSerializer
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request, *args, **kwargs)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = productSerializer
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        
        if self.request.method in  ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
            
        
        return super().get_permissions()
    
#  Not using this 
@api_view(['GET'])
def product_details(request, pk):
    products = get_object_or_404(Product, pk=pk)
    serailizer = productSerializer(products)
    
    return Response(serailizer.data)


class OrderViewSet(viewsets.ModelViewSet):
    throttle_scope = 'orders'
    throttle_classes = [ScopedRateThrottle]
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes =  [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    
    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(60 * 15, key_prefix='order_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    
    def perform_create(self,serializer):
        order =  serializer.save(user=self.request.user)
        send_order_confirmation_mail.delay(order.order_id, self.request.user.email)
        
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update': # Can also use Post method to check
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    
    
    # @action(detail=False, methods=['get'], url_path='user-orders', permission_classes=[IsAuthenticated])
    # def user_orders(self,request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data)
        

#  Not using this
class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    
 
#  Not using this   
class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
    
    
    
#  Not using this
@api_view(['GET'])
def order_list(request):
    orders = Order.objects.prefetch_related('items__product').all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


class ProductInfoAPIView(APIView):
    
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products' : products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        
        return Response(serializer.data)
        


# Not using this
@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products' : products,
        'count': len(products),
        'max_price': products.aggregate(max_price=Max('price'))['max_price']
    })  
    return Response(serializer.data)
    


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None
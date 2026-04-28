from django.http import JsonResponse
from .serializers import productSerializer, OrderSerializer, ProductInfoSerializer
from .models import Product, Order
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = productSerializer
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
            
        
        return super().get_permissions()

# @api_view(['GET'])
# def product_list(request):
#     products = Product.objects.all()
#     serailizer = productSerializer(products, many=True)
    
#     return Response({
#         'data': serailizer.data
#     })

# class ProductCreateAPIView(generics.CreateAPIView):
#     model = Product
#     serializer_class = productSerializer
    
#     def create(self, request, *args, **kwargs):
#         print(request.data)
#         return super().create(request, *args, **kwargs)


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = productSerializer
    
    
# @api_view(['GET'])
# def product_details(request, pk):
#     products = get_object_or_404(Product, pk=pk)
#     serailizer = productSerializer(products)
    
#     return Response(serailizer.data)


class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    
    
class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
    
    
    
    
# @api_view(['GET'])
# def order_list(request):
#     orders = Order.objects.prefetch_related('items__product').all()
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)


class ProductInfoAPIView(APIView):
    
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products' : products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        
        return Response(serializer.data)
        

# @api_view(['GET'])
# def product_info(request):
#     products = Product.objects.all()
#     serializer = ProductInfoSerializer({
#         'products' : products,
#         'count': len(products),
#         'max_price': products.aggregate(max_price=Max('price'))['max_price']
#     })  
#     return Response(serializer.data)
    

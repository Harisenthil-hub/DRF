from django.http import JsonResponse
from .serializers import productSerializer, OrderSerializer, ProductInfoSerializer
from .models import Product, Order
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models import Max

@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serailizer = productSerializer(products, many=True)
    
    return Response({
        'data': serailizer.data
    })

@api_view(['GET'])
def product_details(request, pk):
    products = get_object_or_404(Product, pk=pk)
    serailizer = productSerializer(products)
    
    return Response(serailizer.data)
    
    
@api_view(['GET'])
def order_list(request):
    orders = Order.objects.prefetch_related('items__product').all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products' : products,
        'count': len(products),
        'max_price': products.aggregate(max_price=Max('price'))['max_price']
    })
    
    return Response(serializer.data)
    

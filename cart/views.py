from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
    
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    
    return render(request, 'cart/detail.html', {'cart': cart})

@require_POST
def cart_update(request, product_id):
    """Update cart quantity via AJAX"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        quantity = data.get('quantity', 1)
        
        # Validate quantity
        if quantity < 1:
            quantity = 1
        if quantity > product.stock:
            quantity = product.stock
        
        # Update cart
        cart.add(product=product, quantity=quantity, override_quantity=True)
        
        # Calculate new totals
        item_total = float(product.price) * quantity
        cart_total = float(cart.get_total_price())
        cart_count = len(cart)
        
        return JsonResponse({
            'success': True,
            'item_total': item_total,
            'cart_total': cart_total,
            'cart_count': cart_count,
            'message': 'Cart updated successfully'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests

@login_required
def order_create(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('shop:product_list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Save order
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'pending'
            order.paid = False
            order.total_amount = cart.get_total_price()
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Clear the cart
            cart.clear()
            
            # Initialize Paystack payment
            url = 'https://api.paystack.co/transaction/initialize'
            headers = {
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'email': order.email,
                'amount': int(order.total_amount * 100),  # Convert to pesewas/kobo
                'reference': f'ORDER-{order.id}-{order.user.id}-{order.created_at.strftime("%Y%m%d%H%M%S")}',
                'callback_url': request.build_absolute_uri(reverse('payment:callback')),
                'metadata': {
                    'order_id': order.id,
                    'user_id': order.user.id,
                    'user_email': order.email,
                    'full_name': order.full_name
                }
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                response_data = response.json()
                
                if response_data['status']:
                    # Redirect directly to Paystack payment page
                    return redirect(response_data['data']['authorization_url'])
                else:
                    messages.error(request, f'Payment initialization failed: {response_data.get("message", "Unknown error")}')
                    return redirect('cart:cart_detail')
                    
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Payment service error: {str(e)}')
                return redirect('cart:cart_detail')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                return redirect('cart:cart_detail')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order/create.html', {
        'cart': cart,
        'form': form
    })

@login_required
def order_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order/completed.html', {'order': order})
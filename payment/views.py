from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
import requests
from orders.models import Order
from django.conf import settings

def payment_callback(request):
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'No payment reference found.')
        return redirect('shop:product_list')
    
    # Verify payment with Paystack
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        
        if response_data['status'] and response_data['data']['status'] == 'success':
            # Get order from metadata
            metadata = response_data['data']['metadata']
            order_id = metadata.get('order_id')
            
            if order_id:
                order = Order.objects.get(id=order_id)
                # Mark order as paid
                order.paid = True
                order.payment_ref = reference
                order.status = 'processing'
                order.save()
                
                messages.success(request, 'Payment successful! Your order has been placed.')
                return redirect('orders:order_completed', order_id=order.id)
            else:
                messages.error(request, 'Order not found in payment metadata.')
                return redirect('shop:product_list')
        else:
            messages.error(request, f'Payment verification failed: {response_data.get("message", "Unknown error")}')
            return redirect('shop:product_list')
            
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('shop:product_list')
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Payment verification error: {str(e)}')
        return redirect('shop:product_list')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
        return redirect('shop:product_list')
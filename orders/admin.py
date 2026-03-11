from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'phone', 'total_amount', 'status', 'paid', 'created_at']
    list_filter = ['status', 'paid', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'address']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'full_name', 'email', 'phone', 'address')
        }),
        ('Order Information', {
            'fields': ('status', 'paid', 'total_amount', 'payment_ref', 'payment_method')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity']
    list_filter = ['order']
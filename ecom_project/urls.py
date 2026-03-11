from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Makay Luxury Administration"
admin.site.site_title = "Makay Luxury Admin"
admin.site.index_title = "Welcome to Makay Luxury Dashboard"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls')),  # Move cart BEFORE shop
    path('orders/', include('orders.urls')),
    path('payment/', include('payment.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('shop.urls')),  # Shop should be last
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from .models import Catagory, Product, Cart, Favourite, Order, OrderItem
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from shop.models import Cart, Product, Order
from .models import Cart, Catagory, Favourite, Order, Product
from django.contrib.auth.models import User 

admin.site.register(Catagory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Favourite)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'address', 'total_price', 'status', 'list_items', 'payment_mode', 'created_at']
    list_filter = ['payment_mode', 'created_at']
    search_fields = ['user__username', 'full_name', 'phone', 'email']
    inlines = [OrderItemInline]

    def list_items(self, obj):
        return ", ".join([item.product.name for item in obj.order_items.all()])
    list_items.short_description = 'Ordered Items'

admin.site.register(Order, OrderAdmin)


def custom_admin_index(request):
    context = admin.site.each_context(request)
    context['carts_count'] = Cart.objects.count()
    context['categories_count'] = Catagory.objects.count()
    context['favourites_count'] = Favourite.objects.count()
    context['orders_count'] = Order.objects.count()
    context['products_count'] = Product.objects.count()
    context['users_count'] = User.objects.count()
   
    return render(request, 'admin/custom_index.html', context)

admin.site.index = custom_admin_index


from django.contrib import admin

# Register your models here.

from .models import Size, Product,CartItem,Order,OrderItem

admin.site.register(Size)
admin.site.register(Product)
admin.site.register(CartItem)
# admin.site.register(Order)
admin.site.register(OrderItem)
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # kitne empty forms add karna hai by default





class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'status', 'created_at')
    list_editable = ('status',)  # list page pe status edit karne ke liye
    list_filter = ('status',)    # filter ke liye


admin.site.register(Order, OrderAdmin)


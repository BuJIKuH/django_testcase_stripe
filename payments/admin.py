from django.contrib import admin
from .models import Item, OrderItem, Order, Discount


class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'promocode', 'percent_off', 'active', 'visible', ]
    exclude = ['stripe_id']


class ItemAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, ]


admin.site.register(Discount, DiscountAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)

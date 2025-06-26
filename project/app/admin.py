from django.contrib import admin
from .models import Manufacturer, Category, Product, Cart, CartItem

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "country")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category")
    list_filter = ("category", "manufacturer")
    search_fields = ("name",)

    readonly_fields = ("preview",)
    def preview(self, obj):
        return f'<img src="{obj.photo.url}" width="100">' if obj.photo else "Нет фото"
    preview.allow_tags = True    

class CartItemsInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("sum",)
    
    def sum(self, obj):
        return obj.item_price()
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "total")
    inlines = [CartItemsInline]
    
    def total(self, obj):
        return obj.total_price()    
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "sum")
    
    def sum(self, obj):
        return obj.item_price()    
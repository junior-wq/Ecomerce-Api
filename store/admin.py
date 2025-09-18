# from django.contrib import admin
from .models import Product, ProductImages,Cart,CartItem

# class ProductImageInline(admin.TabularInline):
#     model = ProductImages
#     extra = 0  # Número de imagens extras ao adicionar um produto

# class ProductAdmin(admin.ModelAdmin):
#     inlines = [ProductImageInline]

# admin.site.register(Product, ProductAdmin)



from django.contrib import admin
from .models import ProductImages

# class ProductImagesAdmin(admin.ModelAdmin):
#     def save_model(self, request, obj, form, change):
#         # Passa o request para o save do modelo
#         obj.save(request=request)

admin.site.register([ProductImages, Product,Cart,CartItem])

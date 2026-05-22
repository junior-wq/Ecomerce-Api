from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, ProductImages,Order,OrderItem,Cart,CartItem,WhatsAppStats,Category

admin.site.site_header = "🛍️ Luxus - Admin Panel"
admin.site.site_title = "Luxus Admin"
admin.site.index_title = "Welcome to Luxus Administration"



@admin.register(WhatsAppStats)
class WhatsAppStatsAdmin(admin.ModelAdmin):
    readonly_fields = ('product_name', 'clicks')
    list_display = ('product_name', 'clicks')
    ordering = ('-clicks',)



# Inline para ProductImages
class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    min_num = 1
    max_num = 5
    verbose_name = "Imagem do Produto"
    verbose_name_plural = "Imagens do Produto"

# Form para validações no admin
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.pk:
            try:
                self.instance.clean()
            except ValidationError as e:
                raise ValidationError(e)
        return cleaned_data

# ✅ ADMIN DO PRODUCT - REGISTRADO CORRETAMENTE
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ("display_first_image", "name", "price", "discount", "discounted_price", "display_stock")
    list_filter = ("discount", "stock")
    search_fields = ("name", "description")
    list_per_page = 20
    ordering = ['name']  # Ordenação padrão por nome
    
    # ✅ Torna estes campos clicáveis para ordenação
    sortable_by = ['name', 'price', 'discount', 'stock']
    
    inlines = [ProductImagesInline]
    
    def display_first_image(self, obj):
        """Exibe a primeira imagem do produto"""
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                first_image.image.url
            )
        return "🖼️"
    
    display_first_image.short_description = "Imagem"
    
    def display_stock(self, obj):
        """Mostra stock com cor vermelha se for menor que 10"""
        if obj.stock < 10:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                obj.stock
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">{}</span>',
            obj.stock
        )
    
    display_stock.short_description = "Stock"
    
    # ✅ Torna discounted_price ordenável
    def discounted_price(self, obj):
        return f"€{obj.discounted_price:.2f}"
    discounted_price.admin_order_field = 'price'  # Ordena pelo preço original
    discounted_price.short_description = "Preço c/ Desconto"
    
    def save_related(self, request, form, formsets, change):
        """Valida após salvar as imagens"""
        super().save_related(request, form, formsets, change)
        if form.instance.images.count() < 1:
            raise ValidationError("O produto deve ter pelo menos 1 imagem.")



admin.site.register([Order,OrderItem])
admin.site.register([Cart,CartItem])
admin.site.register([Category])
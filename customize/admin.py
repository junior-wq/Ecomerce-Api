from django.contrib import admin
from .models import (
    Logo,
    Banner,
    About,
    FooterColumn,
    FooterListItem
)




admin.site.register(Logo)

admin.site.register(Banner)
admin.site.register(About)
# admin.site.register(FooterColumn)
# admin.site.register(FooterListItem)



class FooterColumInline(admin.TabularInline):
    model =FooterListItem
    extra = 1
    min_num = 1
    max_num = 5
    verbose_name = "Link"
    # verbose_name_plural = "Links das Colunas"


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    # list_display=[]
    inlines = [FooterColumInline]





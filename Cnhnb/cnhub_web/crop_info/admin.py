from django.contrib import admin
from crop_info import models
# Register your models here.


@admin.register(models.CategoryOne)
class CategoryOneAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(models.CategoryTwo)
class CategoryTwoAdmin(admin.ModelAdmin):
    list_display = ['category_one', 'name']


@admin.register(models.CategoryThree)
class CategoryThreeAdmin(admin.ModelAdmin):
    list_display = ['get_categoryone', 'category_tow', 'name']


@admin.register(models.Commodity)
class Commodity(admin.ModelAdmin):
    list_display = ['get_categoryone', 'get_categorytwo', 'get_categorythree', 'name', 'price', 'start_wholesale', 'get_specification']


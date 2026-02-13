from django.contrib import admin
from django.utils.html import format_html

from .models import (
    ServiceCategory,
    Service,
    ServiceAdditionalFeature,
    ServiceHour,
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name", "subtitle", "is_active", "icon_preview", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("category_name", "subtitle")
    ordering = ("-id",)

    def icon_preview(self, obj):
        if obj.category_icon_upload:
            return format_html(
                '<img src="{}" style="height:35px;width:35px;object-fit:cover;border-radius:6px;" />',
                obj.category_icon_upload.url
            )
        return "-"
    icon_preview.short_description = "Icon"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category_name",
        "man_price",
        "offer_price",
        "discount",
        "is_active",
        "image_preview",
        "created_at",
    )
    list_filter = ("is_active", "created_at", "category_id")
    search_fields = ("name", "description", "category_id__category_name")
    ordering = ("-id",)
    autocomplete_fields = ("category_id",)

    def category_name(self, obj):
        return obj.category_id.category_name
    category_name.short_description = "Category"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:35px;width:55px;object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Image"


@admin.register(ServiceAdditionalFeature)
class ServiceAdditionalFeatureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "additional_features_title",
        "service_name",
        "additional_features_price",
        "estimate_time",
        "estimate_time_unit",
        "image_preview",
        "created_at",
    )
    list_filter = ("estimate_time_unit", "created_at", "service_id")
    search_fields = ("additional_features_title", "subtitle", "service_id__name")
    ordering = ("-id",)
    autocomplete_fields = ("service_id",)

    def service_name(self, obj):
        return obj.service_id.name
    service_name.short_description = "Service"

    def image_preview(self, obj):
        if obj.additional_features_image:
            return format_html(
                '<img src="{}" style="height:35px;width:55px;object-fit:cover;border-radius:6px;" />',
                obj.additional_features_image.url
            )
        return "-"
    image_preview.short_description = "Image"


@admin.register(ServiceHour)
class ServiceHourAdmin(admin.ModelAdmin):
    list_display = ("id", "service_name", "day_of_week", "from_time", "to_time", "is_closed", "created_at")
    list_filter = ("day_of_week", "is_closed", "created_at", "service_id")
    search_fields = ("service_id__name",)
    ordering = ("service_id", "day_of_week")
    autocomplete_fields = ("service_id",)

    def service_name(self, obj):
        return obj.service_id.name
    service_name.short_description = "Service"

from django.db import models


class ServiceCategory(models.Model):
    category_icon_upload = models.ImageField(upload_to="category/icons/",null=True,blank=True)
    category_name = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_category"

    def __str__(self):
        return self.category_name


class Service(models.Model):
    category_id = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="services")

    name = models.CharField(max_length=160)
    description = models.TextField(null=True, blank=True)

    man_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    image = models.ImageField(upload_to="services/images/", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service"

    def __str__(self):
        return self.name


class ServiceAdditionalFeature(models.Model):
    service_id = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="additional_features")

    additional_features_title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    additional_features_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_features_image = models.ImageField(upload_to="services/additional_features/", null=True, blank=True)
    estimate_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimate_time_unit = models.CharField(max_length=20, default="hour")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_additional_features"

    def __str__(self):
        return self.additional_features_title


class ServiceHour(models.Model):
    service_id = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="hours")

    day_of_week = models.IntegerField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "service_hours"

    def __str__(self):
        return f"{self.service_id.name} - {self.day_of_week}"

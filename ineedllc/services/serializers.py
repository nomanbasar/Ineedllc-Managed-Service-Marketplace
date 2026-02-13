from rest_framework import serializers
from .models import ServiceCategory, Service, ServiceHour, ServiceAdditionalFeature


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = [
            "id",
            "category_icon_upload",
            "category_name",
            "subtitle",
            "is_active",
            "created_at",
            "updated_at",
        ]



class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "category_id",
            "name",
            "description",
            "man_price",
            "offer_price",
            "discount",
            "image",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ServiceHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceHour
        fields = ["id", "service_id", "day_of_week", "from_time", "to_time", "is_closed", "created_at"]

    def validate(self, attrs):
        # is_closed না পাঠালে default False ধরে নাও
        is_closed = attrs.get("is_closed", False)

        # closed হলে time না দিলেও চলবে
        if is_closed:
            attrs["from_time"] = attrs.get("from_time") or "00:00:00"
            attrs["to_time"] = attrs.get("to_time") or "00:00:00"
            return attrs

        # open হলে from/to required
        if not attrs.get("from_time") or not attrs.get("to_time"):
            raise serializers.ValidationError("from_time and to_time are required when is_closed=false")

        if attrs["from_time"] >= attrs["to_time"]:
            raise serializers.ValidationError("from_time must be earlier than to_time")

        return attrs


# ---------- Bulk (Figma Sat-Fri) ----------
class ServiceHourItemSerializer(serializers.Serializer):
    day_of_week = serializers.IntegerField(min_value=0, max_value=6)
    is_closed = serializers.BooleanField(required=False, default=False)
    from_time = serializers.TimeField(required=False, allow_null=True)
    to_time = serializers.TimeField(required=False, allow_null=True)

    def validate(self, attrs):
        is_closed = attrs.get("is_closed", False)

        if is_closed:
            attrs["from_time"] = attrs.get("from_time") or "00:00:00"
            attrs["to_time"] = attrs.get("to_time") or "00:00:00"
            return attrs

        if not attrs.get("from_time") or not attrs.get("to_time"):
            raise serializers.ValidationError("from_time and to_time are required when is_closed=false")

        if attrs["from_time"] >= attrs["to_time"]:
            raise serializers.ValidationError("from_time must be earlier than to_time")

        return attrs


class ServiceHourBulkSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    hours = ServiceHourItemSerializer(many=True)

    def validate_hours(self, value):
        days = [x["day_of_week"] for x in value]
        if len(days) != len(set(days)):
            raise serializers.ValidationError("Duplicate day_of_week found in hours array")
        return value
    
    
class ServiceAdditionalFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAdditionalFeature
        fields = [
            "id",
            "service_id",
            "additional_features_title",
            "subtitle",
            "additional_features_price",
            "additional_features_image",
            "estimate_time",
            "estimate_time_unit",
            "created_at",
            "updated_at",
        ]

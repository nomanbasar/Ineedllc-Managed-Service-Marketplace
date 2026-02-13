from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .permissions import IsAdminUserRole
from .models import ServiceCategory, Service, ServiceHour, ServiceAdditionalFeature
from .pagination import paginate_queryset
from .serializers import (
    ServiceCategorySerializer,
    ServiceSerializer,
    ServiceHourSerializer,
    ServiceAdditionalFeatureSerializer,
    ServiceHourBulkSerializer
)


# PUBLIC APIs (frontend)

class PublicCategoryList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = ServiceCategory.objects.filter(is_active=True).order_by("category_name")
        return Response({"success": True, "message": "category_list", "data": ServiceCategorySerializer(qs, many=True).data})


class PublicServiceList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Service.objects.filter(is_active=True).select_related("category_id").order_by("-created_at")

        category_id = request.query_params.get("category_id")
        search = request.query_params.get("search")

        if category_id:
            qs = qs.filter(category_id_id=category_id)
        if search:
            qs = qs.filter(name__icontains=search)

        return Response({"success": True, "message": "service_list", "data": ServiceSerializer(qs, many=True).data})


# ADMIN APIs (create/update)

class AdminCategoryListCreate(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        qs = ServiceCategory.objects.all().order_by("-created_at")

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(category_name__icontains=search)

        page_qs, meta = paginate_queryset(qs, request)

        return Response(
            {
                "success": True,
                "message": "admin_category_list",
                "meta": meta,
                "data": ServiceCategorySerializer(page_qs, many=True).data,
            }
        )

    def post(self, request):
        s = ServiceCategorySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({"success": True, "message": "category_created", "data": ServiceCategorySerializer(obj).data}, status=status.HTTP_201_CREATED)


class AdminCategoryDetail(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def put(self, request, category_id):
        obj = ServiceCategory.objects.get(id=category_id)
        s = ServiceCategorySerializer(obj, data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({"success": True, "message": "category_updated", "data": ServiceCategorySerializer(obj).data})

    def delete(self, request, category_id):
        obj = ServiceCategory.objects.get(id=category_id)
        obj.delete()
        return Response({"success": True, "message": "category_deleted"})


class AdminServiceListCreate(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        qs = Service.objects.all().select_related("category_id").order_by("-created_at")

        category_id = request.query_params.get("category_id")
        search = request.query_params.get("search")

        if category_id:
            qs = qs.filter(category_id_id=category_id)

        if search:
            qs = qs.filter(name__icontains=search)

        page_qs, meta = paginate_queryset(qs, request)

        return Response(
            {
                "success": True,
                "message": "admin_service_list",
                "meta": meta,
                "data": ServiceSerializer(page_qs, many=True).data,
            }
        )
   

    def post(self, request):
        s = ServiceSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({"success": True, "message": "service_created", "data": ServiceSerializer(obj).data}, status=status.HTTP_201_CREATED)


class AdminServiceDetail(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def put(self, request, service_id):
        obj = Service.objects.get(id=service_id)
        s = ServiceSerializer(obj, data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response({"success": True, "message": "service_updated", "data": ServiceSerializer(obj).data})

    def delete(self, request, service_id):
        obj = Service.objects.get(id=service_id)
        obj.delete()
        return Response({"success": True, "message": "service_deleted"})


class AdminServiceHourCreate(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request):
        """
        POST /api/services/admin/service-hours/
        body: {service_id, day_of_week, from_time, to_time, is_closed(optional)}
        same service+day -> update, else create (no duplicate)
        """
        s = ServiceHourSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        service_id = s.validated_data["service_id"].id
        day = s.validated_data["day_of_week"]

        obj, created = ServiceHour.objects.update_or_create(
            service_id_id=service_id,
            day_of_week=day,
            defaults={
                "from_time": s.validated_data["from_time"],
                "to_time": s.validated_data["to_time"],
                "is_closed": s.validated_data.get("is_closed", False),
            }
        )

        return Response({
            "success": True,
            "message": "service_hour_saved",
            "data": ServiceHourSerializer(obj).data,
            "meta": {"created": created}
        }, status=status.HTTP_200_OK)


class AdminServiceHourBulkUpsert(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request):
        s = ServiceHourBulkSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        service_id = s.validated_data["service_id"]
        hours = s.validated_data["hours"]

        Service.objects.get(id=service_id)

        days = [h["day_of_week"] for h in hours]

        with transaction.atomic():
            # overwrite behavior
            ServiceHour.objects.filter(
                service_id_id=service_id,
                day_of_week__in=days
            ).delete()

            objs = []
            for h in hours:
                objs.append(ServiceHour(
                    service_id_id=service_id,
                    day_of_week=h["day_of_week"],
                    from_time=h.get("from_time") or "00:00:00",
                    to_time=h.get("to_time") or "00:00:00",
                    is_closed=h.get("is_closed", False),
                ))

            ServiceHour.objects.bulk_create(objs)

        # 🔥 return same structure as request (frontend friendly)
        return Response({
            "success": True,
            "message": "service_hours_saved",
            "data": {
                "service_id": service_id,
                "hours": hours
            }
        }, status=status.HTTP_200_OK)

class AdminServiceHourList(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        """
        GET /api/services/admin/service-hours/list/?service_id=1
        """
        service_id = request.query_params.get("service_id")
        if not service_id:
            return Response({"success": False, "message": "service_id is required"}, status=400)

        qs = ServiceHour.objects.filter(service_id_id=service_id).order_by("day_of_week")
        return Response({
            "success": True,
            "message": "service_hours_list",
            "data": ServiceHourSerializer(qs, many=True).data
        })


class AdminAdditionalFeatureCreate(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request):
        # ✅ supports multipart/form-data (image upload)
        s = ServiceAdditionalFeatureSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save()

        return Response({
            "success": True,
            "message": "additional_feature_created",
            "data": ServiceAdditionalFeatureSerializer(obj).data
        }, status=status.HTTP_201_CREATED)


class AdminAdditionalFeatureList(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        service_id = request.query_params.get("service_id")
        qs = ServiceAdditionalFeature.objects.all().order_by("-created_at")

        if service_id:
            qs = qs.filter(service_id_id=service_id)

        return Response({
            "success": True,
            "message": "additional_feature_list",
            "data": ServiceAdditionalFeatureSerializer(qs, many=True).data
        })

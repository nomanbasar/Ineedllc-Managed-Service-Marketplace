from django.urls import path
from .views import (
    PublicCategoryList,
    PublicServiceList,

    AdminCategoryListCreate,
    AdminCategoryDetail,
    AdminServiceListCreate,
    AdminServiceDetail,
    AdminServiceHourCreate,
    AdminAdditionalFeatureCreate,
    AdminAdditionalFeatureList,

    AdminServiceHourBulkUpsert,
    AdminServiceHourList,
)

urlpatterns = [
    # public
    path("categories/", PublicCategoryList.as_view()),
    path("", PublicServiceList.as_view()),

    # admin
    path("admin/categories/", AdminCategoryListCreate.as_view()),
    path("admin/categories/<int:category_id>/", AdminCategoryDetail.as_view()),

    path("admin/services/", AdminServiceListCreate.as_view()),
    path("admin/services/<int:service_id>/", AdminServiceDetail.as_view()),

    path("admin/service-hours/", AdminServiceHourCreate.as_view()),
    path("admin/service-hours/bulk/", AdminServiceHourBulkUpsert.as_view()),
    path("admin/service-hours/list/", AdminServiceHourList.as_view()),

    path("admin/additional-features/", AdminAdditionalFeatureCreate.as_view()),
    path("admin/additional-features/list/", AdminAdditionalFeatureList.as_view()),
]

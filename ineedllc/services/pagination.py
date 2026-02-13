from math import ceil
from rest_framework.exceptions import ValidationError


def paginate_queryset(qs, request, default_limit=10, max_limit=100):
    """
    Query params:
      ?page=1&limit=10

    Returns:
      (paginated_qs, meta)
    """
    page = request.query_params.get("page", 1)
    limit = request.query_params.get("limit", default_limit)

    try:
        page = int(page)
        limit = int(limit)
    except (TypeError, ValueError):
        raise ValidationError({"success": False, "message": "Invalid page/limit. Must be integers."})

    if page < 1:
        page = 1
    if limit < 1:
        limit = default_limit
    if limit > max_limit:
        limit = max_limit

    total = qs.count()
    total_page = ceil(total / limit) if total > 0 else 1

    start = (page - 1) * limit
    end = start + limit
    paginated_qs = qs[start:end]

    meta = {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPage": total_page,
    }
    return paginated_qs, meta

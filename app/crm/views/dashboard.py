import json
from datetime import timedelta

from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models.functions import TruncDay
from django.db.models import Count, Sum

from crm.models import Request

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

def dashboard_callback(request, context):
    today = now().date()
    week_ago = today - timedelta(days=6)

    # Заявки по дням
    qs = (
        Request.objects.filter(created_at__date__gte=week_ago)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    performance_data = {item["day"].strftime("%Y-%m-%d"): item["count"] for item in qs}
    labels = [(week_ago + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    counts = [performance_data.get(date, 0) for date in labels]

    # Выплаты по дням
    amount_qs = (
        Request.objects.filter(created_at__date__gte=week_ago)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(total=Sum("requested_amount"))
        .order_by("day")
    )
    amount_data = {item["day"].strftime("%Y-%m-%d"): float(item["total"] or 0) for item in amount_qs}
    amounts = [amount_data.get(date, 0) for date in labels]

    context.update({
        "performance": [
            {
                "title": _("Количество заявок за неделю"),
                "metric": sum(counts),
                "chart": json.dumps({
                    "labels": [WEEKDAYS[(week_ago + timedelta(days=i)).weekday()] for i in range(7)],
                    "datasets": [
                        {
                            "data": counts,
                            "borderColor": "var(--color-primary-700)",
                        }
                    ],
                }),
            },
            {
                "title": _("Запрошено средств за неделю"),
                "metric": f"{sum(amounts):,.2f}",
                "chart": json.dumps({
                    "labels": [WEEKDAYS[(week_ago + timedelta(days=i)).weekday()] for i in range(7)],
                    "datasets": [
                        {
                            "data": amounts,
                            "borderColor": "var(--color-primary-300)",
                        }
                    ],
                }),
            },
        ]
    })

    return context

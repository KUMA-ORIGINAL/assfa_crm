import copy
import json
from collections import defaultdict
from datetime import timedelta

from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import TruncDay
from django.db.models import Count, Sum

from config.settings import REQUEST_STATUSES
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

    chart_options = {
        "responsive": True,
        "maintainAspectRatio": False,
        "scales": {
            "y": {
                "beginAtZero": True,
                "ticks": {
                    "stepSize": 1,
                },
            },
        },
        "plugins": {
            "legend": {
                "display": False
            },
            "tooltip": {
                "enabled": True
            }
        },
    }

    chart_options_2 = copy.deepcopy(chart_options)
    chart_options_2["scales"]["y"]['ticks'] = {}

    STATUS_CATEGORIES = {
        'new': 'У специалиста',
        'approved_by_specialist': 'У директора',
        'rejected_by_specialist': 'Отклонено',
        'approved_by_director': 'У бухгалтера',
        'rejected_by_director': 'Отклонено',
        'sent_to_chairman': 'У председателя',
        'approved_by_chairman': 'У бухгалтера',
        'rejected_by_chairman': 'Отклонено',
        'awaiting_payment': 'У бухгалтера',
        'paid': 'Выплачено',
    }
    status_counts = (
        Request.objects
        .values('status')
        .annotate(count=Count('id'))
    )
    status_dict = {item['status']: item['count'] for item in status_counts}
    category_counts = defaultdict(int)
    for status, count in status_dict.items():
        category = STATUS_CATEGORIES.get(status)
        if category:
            category_counts[category] += count
    CATEGORY_ORDER = [
        'У специалиста',
        'У директора',
        'У председателя',
        'У бухгалтера',
        'Отклонено',
        'Выплачено',
    ]
    status_data = [
        {
            "title": category,
            "count": category_counts.get(category, 0)
        }
        for category in CATEGORY_ORDER
    ]

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
                "options": json.dumps(chart_options),
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
                "options": json.dumps(chart_options_2),
            },
        ],
        "status_data": status_data,
    })

    return context

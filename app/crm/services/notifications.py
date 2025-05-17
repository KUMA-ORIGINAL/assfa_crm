from django.contrib.auth import get_user_model
from tg_bot.utils import send_telegram_message

User = get_user_model()


def notify_status_change(role: str, request_obj, new_status: str):
    """
    Отправляет уведомление всем пользователям с заданной ролью.
    """
    users = User.objects.filter(role=role).exclude(tg_chat_id__isnull=True).exclude(tg_chat_id__exact="")
    new_status = new_status.replace('_', ' ').title()

    message = (
        f"📄 <b>Новая заявка на одобрение</b>\n"
        f"<b>ID:</b> {request_obj.id}\n"
        f"<b>ФИО или название учреждения:</b> {request_obj.full_name_or_org}\n"
        f"<b>Новый статус:</b> {new_status}"
    )

    for user in users:
        send_telegram_message(
            chat_id=user.tg_chat_id,
            message=message,
            button_text="Перейти на страницу",
            button_url=f"https://as-safa.operator.kg/admin/crm/request/{request_obj.id}/change/"
        )

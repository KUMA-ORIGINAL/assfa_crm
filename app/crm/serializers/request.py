from rest_framework import serializers
from crm.models import Request


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            "id",
            "subject_type",
            "full_name_or_org",
            "phone_number",
            "actual_address",
            "registration_address",
            "description",
            "incoming_letter",
            'requisites',
            "requested_amount",
            "approved_amount_director",
            "approved_amount_chairman",
            "request_type",
            "status",
            "created_at",
            "updated_at",
            "attachments",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "approved_amount_director", "approved_amount_chairman", "status"]

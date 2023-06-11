import traceback

from base.util import Util
from dateutil import tz
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import pagination, serializers
from rest_framework.response import Response
from rest_framework.views import exception_handler


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response({"totalRecords": self.page.paginator.count, "data": data})


class APIResponse(Response):
    def __init__(self, data="", code=1, message=""):
        super().__init__({"code": code, "data": data, "message": message})


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    response = exception_handler(exc, context)
    # res = Util.create_from_exception(exc)
    print(context, "context")

    if response is None:
        Util.create_exception_log(exc, context["view"], traceback=traceback.format_exc())
        return APIResponse(code=0, message=str(exc))

    # Now add the HTTP status code to the response.
    response.data["status_code"] = response.status_code
    response.data["code"] = 0
    response.data["message"] = "Error occurred"

    return response


class FilePath(serializers.FileField):
    def to_representation(self, instance):
        request = self.context.get("request")
        instance = str(instance)
        img_src = Util.get_resource_url("profile", instance) if instance else ""
        if img_src:
            return request.build_absolute_uri(img_src.strip())
        return None


class LocalDateTime(serializers.DateTimeField):
    def to_representation(self, instance):
        current_time_zone = timezone.get_current_timezone_name()
        from_zone = tz.gettz("UTC")
        to_zone = tz.gettz(current_time_zone)
        utctime = instance.replace(tzinfo=from_zone)
        new_time = utctime.astimezone(to_zone)
        return new_time.strftime("%d/%m/%Y %H:%M:%S")


class BulkListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [self.child.create(attrs) for attrs in validated_data]
        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)
        return result

    def update(self, instances, validated_data):
        instance_hash = {index: instance for index, instance in enumerate(instances)}

        result = [self.child.update(instance_hash[index], attrs) for index, attrs in enumerate(validated_data)]

        writable_fields = [x for x in self.child.Meta.fields if x not in self.child.Meta.read_only_fields]

        try:
            self.child.Meta.model.objects.bulk_update(result, writable_fields)
        except IntegrityError as e:
            raise ValidationError(e)

        return result


class ModelObjectidField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data

from accounts.models import Group, UserProfile
from customer.models import Country, Customer
from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Concat
from finance_api.rest_config import APIResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

from base.choices import base_choices
from base.serializers import LookupsSerializer

from .models import CodeTable


@api_view(["GET"])
@parser_classes([JSONParser])
def lookups(request, model):
    response = []
    if model == "users":
        response = []
        query = Q()
        query.add(Q(user__is_active=True), query.connector)
        user_profiles = UserProfile.objects.filter().values("user__first_name", "user__username", "user__last_name", "user_id").order_by("user__first_name")
        for user_profile in user_profiles:
            response.append({"display_value": user_profile["user__first_name"] + " " + user_profile["user__last_name"], "key_value": user_profile["user_id"]})

        serializer = LookupsSerializer(response, many=True)
        return APIResponse(serializer.data)

    if model == "roles":
        user_roles = Group.objects.filter().order_by("name")[:10]
        response = []
        for user_role in user_roles:
            response.append({"display_value": user_role.name, "key_value": user_role.id})
            serializer = LookupsSerializer(response, many=True)
            response = serializer.data
        return APIResponse(response)

    if model == "hand_company":
        customer_name = (
            Customer.objects.filter(is_root__isnull=False)
            .annotate(hand_name=Concat("name", Value(" - "), "short_name", output_field=CharField()))
            .values("id", "hand_name")
            .order_by("name")
        )
        response = []
        for customer in customer_name:
            response.append({"display_value": customer["hand_name"], "key_value": customer["id"]})
            serializer = LookupsSerializer(response, many=True)
            response = serializer.data
        return APIResponse(response)

    if model == "country":
        country_name = Country.objects.filter().order_by("name")
        response = []
        for country in country_name:
            response.append({"display_value": country.name, "key_value": country.id})
            serializer = LookupsSerializer(response, many=True)
            response = serializer.data
        return APIResponse(response)

    if model == "status":
        secondary_status = CodeTable.objects.filter(code__in=["AAA", "DUE", "LEXIS2", "LEXIS3", "PAYMENTPLAN", "TOINCASSO", "Trivion"]).values("id", "desc").order_by("id")
        response = []
        for status in secondary_status:
            response.append({"display_value": status["desc"], "key_value": status["id"]})
            serializer = LookupsSerializer(response, many=True)
            response = serializer.data
        return APIResponse(response)

    if model == "change_status":
        change_status = (
            CodeTable.objects.filter(code__in=["Euler", "INVCLOSED", "INVCOMMERCIAL", "INVPENDING", "INVPROFORMA", "PRE-PAID", "PROFORMADELETED"])
            .values("id", "desc")
            .order_by("id")
        )
        response = []
        for status in change_status:
            response.append({"display_value": status["desc"], "key_value": status["id"]})
            serializer = LookupsSerializer(response, many=True)
            response = serializer.data
        return APIResponse(response)


@api_view(["GET"])
@parser_classes([JSONParser])
def choice_lookups(request, choice):
    choices = dict(base_choices(choice))
    response = []
    for key, val in choices.items():
        response.append({"display_value": val, "key_value": key})
    return APIResponse(response)

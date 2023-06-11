import django
import django_filters
from django.contrib.auth.models import Group
from django_filters.filters import OrderingFilter

from accounts.models import UserProfile


class UserFilter(django_filters.FilterSet):

    first_name = django_filters.CharFilter(field_name='user__first_name', lookup_expr='istartswith')
    last_name = django_filters.CharFilter(field_name='user__last_name', lookup_expr='istartswith')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='istartswith')
    usergroup = django_filters.CharFilter(field_name='user__usergroup__group__name', lookup_expr='istartswith')

    ordering = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('user__first_name', 'first_name'),
            ('user__last_name', 'last_name'),
            ('user__username', 'username'),
            ('user__usergroup__group__name', 'usergroup'),
        ),
    )

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'username', 'usergroup']
class RoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name",lookup_expr='istartswith')
    ordering = OrderingFilter(
        fields=(
            ("id","id"),
            ("name","name"),
),
)
    class Meta:
        model = Group
        fields = ["name"]

class UserRoleFilter(django_filters.FilterSet):
    display_value = django_filters.CharFilter(field_name="name",lookup_expr='istartswith')
    ordering = OrderingFilter(
        fields=(
            ("id","id"),
            ("name","display_value"),),)
    class Meta:
        model = Group
        fields = ["name"]

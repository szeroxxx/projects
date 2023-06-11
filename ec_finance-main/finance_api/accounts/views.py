from itertools import chain
import json
from base.util import Util
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.postgres.aggregates.general import ArrayAgg
from finance_api.rest_config import APIResponse, CustomPagination
from rest_framework import generics, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from accounts.filter import RoleFilter, UserFilter, UserRoleFilter
from accounts.models import ContentPermission, Group, GroupPermission, MainMenu, PagePermission, UserGroup, UserProfile
from accounts.serializers import RolePermissionSerializer, UserListSerializer, UserProfileSerializer, UserRoleSerializer, UpdateUserSerializer, UserSerializer


class GetMenus(APIView):
    def get(self, request):
        user_id = request.GET.get("user_id")
        global perms_ids
        perms_ids = Util.get_cache("menu_perm_ids")
        if perms_ids is None:
            user = User.objects.get(id=user_id)
            perms = Util.get_permitted_menu(user_id, user.is_superuser)
            Util.set_cache("menu_perm_ids", perms, 86400)
            perms_ids = perms
        menu_list = Util.get_cache("menus")
        if menu_list is None:
            menus = MainMenu.objects.filter(parent_id=None, is_active=True).values("id", "name", "menu_code", "icon").order_by("sequence")
            menu_list = []
            for menu in menus:
                menu_dict = {
                    "id": menu["id"],
                    "name": menu["name"],
                    "code": menu["menu_code"],
                    "ico": menu["icon"],
                }
                sub_menu = for_sub_menus(menu["id"])

                menu_dict["menu"] = sub_menu
                menu_list.append(menu_dict)
            Util.set_cache("menus", menu_list, 86400)

        menu_lists = check_menu_permissions(menu_list, perms_ids)
        return APIResponse(menu_lists)


def for_sub_menus(menu_id):
    sub_menu_list = []
    sub_menus = MainMenu.objects.filter(parent_id_id=menu_id, is_active=True).values("id", "name", "menu_code", "url", "icon").order_by("sequence")
    for sub_menu in sub_menus:
        sub_menu_dict = {
            "id": sub_menu["id"],
            "name": sub_menu["name"],
            "code": sub_menu["menu_code"],
            "ico": sub_menu["icon"],
        }
        sub_sub_menu = for_sub_menus(sub_menu["id"])
        if sub_menu["url"]:
            sub_menu_dict["url"] = sub_menu["url"]
        sub_menu_dict["menu"] = sub_sub_menu
        sub_menu_list.append(sub_menu_dict)
    return sub_menu_list


def check_menu_permissions(menus, perms_ids):
    final_list = []
    for mn in menus:
        if mn["id"] in perms_ids:
            perms_ids.remove(mn["id"])
            if len(mn["menu"]) > 0:
                sub_menu = func(mn["menu"])
                mn["menu"] = sub_menu
                final_list.append(mn)
    return final_list


def func(sub_menus):
    sub_final = []
    for s_menus in sub_menus:
        if s_menus["id"] in perms_ids:
            perms_ids.remove(s_menus["id"])
            nest_sub_menu = func(s_menus["menu"])
            s_menus["menu"] = nest_sub_menu
            sub_final.append(s_menus)
    return sub_final


class UserView(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def get_user(self, request):
        user_id = request.data.get("user_id")
        user_role_obj = UserGroup.objects.filter(user_id=user_id).values_list("group_id", flat=True).distinct()
        role_ids = [x for x in user_role_obj]
        user = User.objects.filter(id=user_id).values("first_name", "last_name", "email", "is_active").first()
        user["role_ids"] = role_ids
        serializer = UserSerializer(user)
        return APIResponse(serializer.data)

    @action(detail=False, methods=["post"])
    def create_user(self, request):
        email = request.data.get("email")
        user_role_ids = request.data.get("role_ids")
        role_ids = []
        if user_role_ids:
            role_ids = [int(x) for x in user_role_ids.split(",")]
        if email is None:
            return APIResponse(code=0, message="Please Enter Username.")
        if User.objects.filter(email__iexact=email).count() > 0:
            return APIResponse(code=0, message="Email already exists.")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(username=email)
            UserProfile.objects.create(user_id=serializer.data["id"], display_row=10)
            user_group = [UserGroup(user_id=serializer.data["id"], group_id=group_id) for group_id in role_ids]
            UserGroup.objects.bulk_create(user_group)
            return APIResponse(serializer.data)
        msg = serializer.errors
        if "password" in serializer.errors:
            msg = json.dumps(msg["password"])
            msg = json.loads(msg)
            msg = msg[0]
        return APIResponse(code=0, message=msg)

    @action(detail=False, methods=["post"])
    def update_user(self, request):
        user_id = request.data.get("user_id")
        role_ids = request.data.get("role_ids")
        user = User.objects.get(id=user_id)
        serializer = UpdateUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            exist_role_ids = UserGroup.objects.filter(user_id=user_id).values_list("group_id", flat=True).distinct()
            if role_ids:
                role_ids = [int(x) for x in role_ids.split(",")]
                user_group = [UserGroup(user=user, group_id=role_id) for role_id in role_ids if role_id not in exist_role_ids]
                delete_role_ids = [x for x in exist_role_ids if x not in role_ids]
                if len(delete_role_ids) > 0:
                    UserGroup.objects.filter(user_id=user_id, group_id__in=delete_role_ids).delete()
                UserGroup.objects.bulk_create(user_group)
            return APIResponse(serializer.data)
        return APIResponse(serializer.errors)

    @action(detail=False, methods=["post"])
    def get_profile(self, request):
        user_id = request.data.get("user_id")
        if user_id != "undefined":
            user = (
                UserProfile.objects.filter(user_id=user_id)
                .values("user_id", "user__first_name", "user__last_name", "user__email", "profile_image", "theme", "display_row", "default_page")
                .first()
            )
            serializer = UserProfileSerializer(user, context={"request": request})
            return APIResponse(serializer.data)
        return APIResponse(code=0, message="something wrong")

    @action(detail=False, methods=["post"])
    def save_profile(self, request):
        user_id = request.data.get("user_id")
        if user_id != "undefined":
            user_profile = UserProfile.objects.get(user_id=user_id)
            userprofile_serializer = UserProfileSerializer(user_profile, data=request.data, context={"request": request})
            if userprofile_serializer.is_valid():
                userprofile_serializer.save()
                return APIResponse(userprofile_serializer.data)
        return APIResponse(userprofile_serializer.errors)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        user_id = request.data.get("user_id")
        user = User.objects.get(id=user_id)
        if not user.check_password(request.data.get("old_password")):
            return APIResponse(code=0, message="Current password is wrong")
        user.set_password(request.data.get("new_password"))
        user.save()
        return APIResponse(code=1, message="Password Changed successfully.")


class UserListView(generics.ListAPIView):
    queryset = (
        UserProfile.objects.select_related("user")
        .prefetch_related("user__usergroup_set")
        .filter(is_active=True)
        .values("user_id", "user__first_name", "user__last_name", "user__username")
        .annotate(usergroup=ArrayAgg("user__usergroup__group__name"))
    )
    serializer_class = UserListSerializer
    pagination_class = CustomPagination
    filterset_class = UserFilter


class UserRole(generics.ListAPIView):
    queryset = Group.objects.values("id", "name")
    serializer_class = UserRoleSerializer
    filterset_class = UserRoleFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(serializer.data)


class RoleListView(generics.ListAPIView):
    queryset = Group.objects.values("id", "name")
    serializer_class = RolePermissionSerializer
    pagination_class = CustomPagination
    filterset_class = RoleFilter


class UserRoleView(viewsets.ViewSet):
    @action(detail=False, methods=["get"])
    def get_role(self, request):
        role_id = request.GET.get("role_id")
        role_id = role_id if role_id != "undefined" else None
        list_data = []
        perms = []
        group = Group.objects.filter(id=role_id).values("id", "name").first()
        content_permissions = ContentPermission.objects.values("content_group").order_by("sequence")
        for content_permission in content_permissions:
            index = next((index for index, item in enumerate(list_data) if item["content_group"] == content_permission["content_group"]), None)
            if index is None:
                content_name = self.add_perm_list(content_permission["content_group"], [])
                list_data.append({"content_group": content_permission["content_group"], "content_name": content_name})

        avail_perms = PagePermission.objects.filter(content__isnull=False).values("id", "content_id", "menu_id", "act_name", "act_code")
        if role_id is not None:
            for lists in list_data:
                for permission in lists["content_name"]:
                    applied_perms = GroupPermission.objects.filter(page_permission__content__id=permission["id"], group_id=group["id"]).values_list("page_permission_id", flat=True)
                    perms = list(chain(perms, applied_perms))
        return APIResponse({"permissions": avail_perms, "applied_perms": perms, "lists": list_data, "group": group})

    def add_perm_list(self, content_group, list_data):
        content_groups = ContentPermission.objects.filter(content_group=content_group).values("id", "content_name").order_by("sequence")
        for content_group in content_groups:
            list_data.append({"id": content_group["id"], "content_name": content_group["content_name"]})
        return list_data

    @action(detail=False, methods=["post"])
    def create_and_update_role(self, request):
        user_id = int(request.data.get("user_id"))
        role_id = request.data.get("role_id", None)
        permission_ids = request.data.get("role_perm", None)
        user = User.objects.get(id=user_id)
        if Util.has_perm("can_add_update_role", user) is False:
            return APIResponse(code=0, message="You do not have permission to perform this action")
        if role_id is None:
            serializer = RolePermissionSerializer(data=request.data)
        else:
            group = Group.objects.get(id=int(role_id))
            serializer = RolePermissionSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            group_id = int(serializer.data["id"])
            if permission_ids is not None and len(permission_ids) > 0:
                permissions = []
                new_permissions = [int(x) for x in permission_ids.split(",")]
                role_permissions = GroupPermission.objects.filter(group_id=group_id, page_permission_id__isnull=False).values_list("page_permission_id", flat=True).distinct()
                for perm in new_permissions:
                    if perm not in role_permissions:
                        permissions.append(GroupPermission(group_id=group_id, page_permission_id=perm, created_by_id=user_id))
                GroupPermission.objects.bulk_create(permissions)
                perms_to_del = []
                for perm in role_permissions:
                    if perm not in new_permissions:
                        perms_to_del.append(perm)
                if len(perms_to_del) > 0:
                    GroupPermission.objects.filter(page_permission_id__in=perms_to_del, group_id=group_id).delete()
            Util.clear_cache("menu_perm_ids")
            return APIResponse(serializer.data)
        msg = serializer.errors
        if "name" in serializer.errors:
            msg = "User role name already exist."
        return APIResponse(code=0, message=msg)

    @action(detail=False, methods=["post"])
    def delete_role(self, request):
        role_ids = request.data["ids"]
        if not role_ids:
            return APIResponse(code=0, message="No records selected")
        ids = [int(x) for x in role_ids.split(",")]
        assigned_roles = ""
        roles = UserGroup.objects.filter(group_id__in=ids).values("group__name")

        for role in roles:
            assigned_roles = assigned_roles + role["group__name"] + ", "

        if assigned_roles != "":
            return APIResponse(code=0, message="'Role " " + {} + " " is assigned to some users. Action cannot be performed. ".format(assigned_roles[:-2]))

        GroupPermission.objects.filter(group_id__in=ids).delete()
        Group.objects.filter(id__in=ids).delete()
        return APIResponse(code=0, message="Data deleted")


class AuthUser(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.filter(username=username).values("id", "is_active").first()
        user_is = authenticate(username=username, password=password)
        if user is None or user_is is None:
            return APIResponse(code=0, message="User does not exist in Finance App.")

        if user["is_active"] is False or user_is is None:
            return APIResponse(code=0, message="User is not Active.")

        user_info = (
            UserProfile.objects.filter(user__username=username)
            .values("user_id", "user__first_name", "user__last_name", "theme", "display_row", "default_page", "profile_image")
            .first()
        )
        img_src = Util.get_resource_url("profile", user_info["profile_image"]) if user_info["profile_image"] else ""
        user_info["profile_image"] = request.build_absolute_uri(img_src.strip())
        return APIResponse(user_info)

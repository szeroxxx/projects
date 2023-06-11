from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from accounts.views import AuthUser, GetMenus, RoleListView, UserListView, UserRole, UserRoleView, UserView

router = DefaultRouter()
router.register(r"user", UserView, basename="user")
router.register(r"role", UserRoleView, basename="role")

urlpatterns = [
    url(r"^get_menu/$", GetMenus.as_view(), name="all_menu"),
    url(r"^users/$", UserListView.as_view(), name="users"),
    url(r"^user_roles/$", UserRole.as_view(), name="user_roles"),
    url(r"^roles/$", RoleListView.as_view(), name="roles"),
    url(r"^auth_user/$", AuthUser.as_view(), name="auth_user"),
    # url(r"^change_password/$", ChangePasswordView.as_view(), name="change_password"),
]
urlpatterns += router.urls

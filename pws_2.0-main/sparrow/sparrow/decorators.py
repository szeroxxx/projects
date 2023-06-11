# import ipaddress
from functools import wraps

from accounts.models import User
from base import views as base_views
from base.models import AppResponse
from base.util import Util
from django.conf import settings as project_settings
from django.http import HttpResponse

# from django.http import JsonResponse
from django.shortcuts import render


def check_view_permission(menu_dict):
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            """
            Wrapper with arguments to invoke the method
            do something with arg1 and arg2
            """
            user_perms_objs = Util.get_user_permissions(request.user.id)
            user = User.objects.filter(id=request.user.id).first()
            if user.is_superuser:
                return view_method(request, *args, **kwargs)
            permissions = False
            for menu in menu_dict:
                menu_code = list(menu.values())[0]
                for user_perms_obj in user_perms_objs:
                    if user_perms_obj["page_permission__act_code"] == "can_view" and user_perms_obj["page_permission__menu__menu_code"] == menu_code:
                        permissions = True
            if permissions is False:
                return render(request, "base/access_deny.html")
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper


def authentic_ip(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        c_ip = base_views.get_client_ip(args[0])

        if c_ip not in project_settings.ALLOWED_SQL_EXPLORER_IPS:
            return HttpResponse(AppResponse.msg(0, "Unauthorized access."), content_type="json")

        return function(*args, **kwargs)

    return decorator


def check_allowed_ips(function):
    @wraps(function)
    def decorator(request, *args, **kwrgs):
        # c_ip = base_views.get_client_ip(request)
        whitelist_ips = Util.get_sys_paramter("allowed_ip_list").para_value
        # clean_ips = []
        whitelist_ips = whitelist_ips.strip().replace("[", "").replace("]", "")
        # clean_ips = whitelist_ips.split(",")
        # for whitelist_ip in clean_ips:
        #     try:
        #         is_allowed_ip = ipaddress.ip_address(c_ip) in ipaddress.ip_network(whitelist_ip, False)
        #         if is_allowed_ip is True:
        #             break
        #     except ValueError:
        #         # manager.create_from_text("API BAD IP access:" + c_ip, class_name="check_allowed_ipss")
        #         return JsonResponse({"code": 0, "message": "API BAD IP access: " + c_ip})

        # if is_allowed_ip is False:
        #     return JsonResponse({"code": 0, "message": "API BAD IP access: " + c_ip})
        return function(request, *args, **kwrgs)

    return decorator

from django.shortcuts import render
from accounts.models import MainMenu
from accounts.models import User
from base.util import Util


def check_view_permission(menu_dict):

    def _method_wrapper(view_method):

        def _arguments_wrapper(request, *args, **kwargs) :
            """
            Wrapper with arguments to invoke the method
            do something with arg1 and arg2
            """
            user_perms_objs = Util.get_user_permissions(request.user.id)
            user = User.objects.filter(id = request.user.id).first()
            if user.is_superuser:
                return view_method(request, *args, **kwargs)       
                
            permissions = False
            for menu in menu_dict:
                menu_code = list(menu.values())[0]
                for user_perms_obj in user_perms_objs:
                    if user_perms_obj['page_permission__act_code'] == 'view' and user_perms_obj['page_permission__menu__menu_code'] == menu_code:
                        permissions = True

            if permissions == False:
                return render(request, 'base/access_deny.html')     
         
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper    
from django.shortcuts import render
from django.http import HttpResponse, response
from django.core import serializers
from base.models import AppResponse
from base.util import Util
from django.db.models import Q, CharField
from accounts.forms import PasswrecoveryForm, ResetPwdForm
from stronghold.decorators import public
from accounts.models import User, PasswordReset
from mails.views import  send_email_by_tmpl
from exception_log import manager
from django.db import connection
from post_office.models import EmailTemplate
from base.util import Util

@public
def passwrecovery(request):
    try:
        if request.method == 'POST':

            form = PasswrecoveryForm(request.POST)

            if form.is_valid():
                email = form.cleaned_data['email']
                user = User.objects.filter(email=email).first()

                if user is None:
                    return HttpResponse(AppResponse.msg(0, "Could not find email, sorry."), content_type='json')

                link = generateLink(request, user.id)
                ctx = {
                # 'app' : 'eC-verified',
                # 'user_name' : user.first_name + ' ' + user.last_name, 
                'reset_link' : link,
                # 'reset_forget_link' : link+'-forget',
                'email' : email
                }

                template =  EmailTemplate.objects.filter(name__icontains = 'reset_password').values('id').first()
                send_email_by_tmpl(True, 'public', [email], template['id'], ctx)
                return HttpResponse(AppResponse.msg(1, "Mail has been sent to change password."), content_type='json')

            else:
                return HttpResponse(AppResponse.msg(0, "Invalid form"), content_type='json')

        else:
            passwrecovery_form = PasswrecoveryForm()
            company_logo = Util.get_sys_paramter('COMPANY_LOGO').para_value
            return render(request, 'accounts/passwrecovery.html', {'form': passwrecovery_form, 'company_logo': company_logo })

    except Exception as e:
        raise
        return HttpResponse(AppResponse.msg(0, "Could not find email, sorry."), content_type='json')


def generateLink(request, userid):
    try:
        reset = PasswordReset(user_id=userid,is_used=False)
        reset.save()
        link = 'http://'+ request.META['HTTP_HOST'] + '/accounts/resetpwd/' +reset.resetuid
        return link
    except Exception as e:
        raise

@public
def resetpwd(request,uid):
    try:
        if request.method == 'POST':
            form = ResetPwdForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                reset = PasswordReset.objects.get(resetuid = uid)
                user = User.objects.get(id = reset.user.id)
                user.set_password(password)
                user.save()
                return HttpResponse(AppResponse.msg(1, "Password changed"), content_type='json')
            else:
                return HttpResponse(AppResponse.msg(0, form.errors), content_type='json')
        else:
            if '-forget' in uid:
                PasswordReset.objects.get(resetuid = uid.replace('-forget','')).delete()
                return HttpResponse("<h1>Request deleted, thanks.</h1>")   
            else:
                company_logo = Util.get_sys_paramter('COMPANY_LOGO').para_value
                rpf = ResetPwdForm()
                return render(request, 'accounts/resetpwd.html', {'form': rpf, 'uid' : uid, 'company_logo': company_logo})

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse("<h1>Something went wrong!</h1>")   

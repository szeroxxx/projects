import logging
from base.models import AppResponse
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from exception_log import manager
from post_office.models import EmailTemplate
from stronghold.decorators import public
from django.template.loader import render_to_string
from accounts.forms import PasswrecoveryForm, ResetPwdForm
from accounts.models import PasswordReset, User
from mails.views import send_mail
# from mails.tasks import task_send_email


@public
def passwrecovery(request):
    try:
        if request.method == "POST":

            form = PasswrecoveryForm(request.POST)

            if form.is_valid():
                email = form.cleaned_data["email"]
                user = User.objects.filter(email=email).first()

                if user is None:
                    return HttpResponse(AppResponse.msg(0, "Sorry, Could not find email."), content_type="json")

                link = generateLink(request, user.id)
                subject = "Sparrow - Account Recovery"
                message = render_to_string(
                        "accounts/password_reset_mail.html",
                        {
                            "reset_link": link,
                            "email": email,
                        },
                    )
                # template = EmailTemplate.objects.filter(name__icontains="reset_password").values("id").first()
                # send_email_by_tmpl(True, "public", [email], template["id"], ctx)
                send_mail(True, "public", [email], subject, message, "", "")
                return HttpResponse(AppResponse.msg(1, "Mail has been sent to your mail."), content_type="json")
            else:
                return HttpResponse(AppResponse.msg(0, "Invalid form"), content_type="json")

        else:
            passwrecovery_form = PasswrecoveryForm()
            return render(request, "accounts/passwrecovery.html", {"form": passwrecovery_form})

    except Exception as e:
        logging.exception("Something went wrong!")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def generateLink(request, userid):
    try:
        reset = PasswordReset(user_id=userid, is_used=False)
        reset.save()
        link = "http://" + request.META["HTTP_HOST"] + "/accounts/resetpwd/" + reset.resetuid
        return link
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, "Unable to generate the link, sorry."), content_type="json")


@public
def resetpwd(request, uid):
    try:
        if request.method == "POST":
            form = ResetPwdForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data["password"]
                reset = PasswordReset.objects.get(resetuid=uid)
                user = User.objects.get(id=reset.user.id)
                user.set_password(password)
                user.save()
                return HttpResponse(AppResponse.msg(1, "Password changed"), content_type="json")
            else:
                return HttpResponse(AppResponse.msg(0, form.errors), content_type="json")
        else:
            if "-forget" in uid:
                PasswordReset.objects.get(resetuid=uid.replace("-forget", "")).delete()
                return HttpResponse("<h1>Request deleted, thanks.</h1>")
            else:
                rpf = ResetPwdForm()
                return render(request, "accounts/resetpwd.html", {"form": rpf, "uid": uid})

    except Exception as e:
        manager.create_from_exception(e)
        return HttpResponse("<h1>Something went wrong!</h1>")

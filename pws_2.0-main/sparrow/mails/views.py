import logging
import smtplib
import threading
import urllib
import urllib.request
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sparrow.impersonate import Impersonate
import os
from django.shortcuts import render, render_to_response


from django.conf import settings

# from django.core.mail import send_mail as sys_send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, Template
from post_office.models import EmailTemplate

from base.models import AppResponse
from base.util import Util
from exception_log import manager
from messaging.models import SMSTemplate
from pws.models import Order_Attachment

# @shared_task(name='send_email_by_tmpl')
# def _send_email_by_tmpl(tenant_schema, to_emails, template_id, context):
#     with schema_context(tenant_schema):
#         try:
#             bcc_mails = []
#             para_codes = ['email_backend', 'email_host', 'email_host_user', 'email_host_password', 'email_port', 'email_use_ssl', 'email_from', 'email_bcc','email_from_name']
#             sys_parms = SysParameter.objects.filter(para_code__in = para_codes)
#             email_from = ''
#             for sys_parm in sys_parms:
#                 if sys_parm.para_code == 'email_backend':
#                     settings.EMAIL_BACKEND = sys_parm.para_value
#                 elif sys_parm.para_code == 'email_host':
#                     settings.EMAIL_HOST = sys_parm.para_value
#                 elif sys_parm.para_code == 'email_host_user':
#                     settings.EMAIL_HOST_USER = sys_parm.para_value
#                 elif sys_parm.para_code == 'email_host_password':
#                     settings.EMAIL_HOST_PASSWORD = sys_parm.para_value
#                 elif sys_parm.para_code == 'email_port':
#                     settings.EMAIL_PORT = int(sys_parm.para_value)
#                 elif sys_parm.para_code == 'email_use_ssl':
#                     settings.EMAIL_USE_SSL = sys_parm.para_value
#                 elif sys_parm.para_code == 'email_from_name':
#                     email_from += sys_parm.para_value
#                 elif sys_parm.para_code == 'email_from':
#                     email_from += '<'+ sys_parm.para_value + '>'
#                 elif sys_parm.para_code == 'email_bcc':
#                     if sys_parm.para_value.strip() != "" and sys_parm.para_value.lower() != "false":
#                         bcc_mails = bcc_mails + sys_parm.para_value.split(",")

#             settings.DEFAULT_FROM_EMAIL = email_from
#             if settings.EMAIL_HOST_USER == "" or settings.EMAIL_HOST_PASSWORD == "" or settings.EMAIL_PORT == "":
#                 return

#             email_template = EmailTemplate.objects.filter(id = template_id)[0]

#             mail.send(
#                 to_emails,
#                 bcc = bcc_mails,
#                 template=email_template,
#                 context=context,
#                 priority= 'now')

#         except Exception as e:
#             manager.create_from_exception(e)
#         finally:
#             close_old_connections()


def send_email_by_tmpl(use_thread, tenant_schema, to_emails, template_id, context):
    mail_config = get_mail_config()
    email_template = EmailTemplate.objects.filter(id=template_id).values("subject", "html_content").first()
    mail_context = Context(context)
    subject = Template(email_template["subject"]).render(mail_context)
    message = Template(email_template["html_content"]).render(mail_context)

    if use_thread:
        thread = threading.Thread(target=_send_mail, args=(mail_config, tenant_schema, to_emails, subject, message, []))
        thread.start()
    else:
        _send_mail(mail_config, tenant_schema, to_emails, subject, message, [])


def send_mail(use_thread, tenant_schema, to_emails, subject, message, attachments, cc_mails=[], mail_from=None, bcc_mails=[], headers=[], callback=None, callback_data=None):
    try:
        mail_config = get_mail_config()

        bcc_mails = bcc_mails + mail_config["bcc_mails"]
        if use_thread:
            thread = threading.Thread(
                target=_send_mail, args=(mail_config, tenant_schema, to_emails, subject, message, attachments, cc_mails, mail_from, bcc_mails, headers, callback, callback_data)
            )
            thread.start()
        else:
            _send_mail(mail_config, tenant_schema, to_emails, subject, message, attachments, cc_mails, mail_from, bcc_mails, headers, callback, callback_data)
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_mail_config():
    try:
        mail_config = {}
        email_from = ""
        bcc_mails = []

        mail_config["email_backend"] = Util.get_sys_paramter("email_backend").para_value
        mail_config["email_host"] = Util.get_sys_paramter("email_host").para_value
        mail_config["email_host_user"] = Util.get_sys_paramter("email_host_user").para_value
        mail_config["email_host_password"] = Util.get_sys_paramter("email_host_password").para_value
        mail_config["email_port"] = int(Util.get_sys_paramter("email_port").para_value)
        mail_config["email_use_ssl"] = Util.get_sys_paramter("email_use_ssl").para_value
        email_from += Util.get_sys_paramter("email_from_name").para_value
        email_from += "<" + Util.get_sys_paramter("email_from").para_value + ">"

        if Util.get_sys_paramter("email_bcc").para_value.strip() != "" and Util.get_sys_paramter("email_bcc").para_value.lower() != "false":
            bcc_mails = Util.get_sys_paramter("email_bcc").para_value.split(",")

        mail_config["default_from_email"] = email_from
        mail_config["bcc_mails"] = bcc_mails
        return mail_config
    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def _send_mail(mail_config, tenant_schema, to_emails, subject, message, attachments, cc_mails=[], mail_from=None, bcc_mails=[], headers=[], callback=None, callback_data=None):
    server = None
    exception = None
    try:
        if mail_config["email_host_user"] == "" or mail_config["email_host_password"] == "" or mail_config["email_port"] == "":
            return

        from_address = mail_config["default_from_email"]
        mail_server = mail_config["email_host"]
        port = int(mail_config["email_port"])
        user = mail_config["email_host_user"]
        password = mail_config["email_host_password"]
        ssl = mail_config["email_use_ssl"]
        msg = MIMEMultipart()
        email_from = ""
        if mail_from:
            if "," in mail_from and "pcbplanet.com" in mail_from:
                mail_from = mail_from.replace(" ", "").split(",")
                for mail in range(len(mail_from)):
                    if mail_from[mail].split("@")[1] == "pcbplanet.com":
                        mail_from = mail_from[mail]
                        break
            else:
                mail_from_ = mail_from.split("@")[1]
                mail_from = mail_from if mail_from_ == "pcbplanet.com" else None
            if mail_from:
                email_from += Util.get_sys_paramter("email_from_name").para_value
                email_from += "<" + mail_from + ">"
                msg["From"] = email_from
            else:
                msg["From"] = from_address
        else:
            msg["From"] = from_address
        msg["Subject"] = subject
        msg["To"] = ",".join(to_emails) if to_emails else ""
        msg["Cc"] = ",".join(cc_mails) if cc_mails else ""
        Cc_Emails = msg["Cc"].split(",")
        for header in headers:
            key = next(iter(header))
            msg[key] = str(header[key])
        recipients = to_emails + Cc_Emails + bcc_mails
        msg.attach(MIMEText(message, "html"))
        # msg.attach(MIMEText(message.encode('utf-8'), 'html'))

        for attachment in attachments:
            # with open(attachments[attachment], 'rb') as fil:
            with Impersonate():
                if os.path.exists(attachments[attachment]) is False:
                    return render_to_response("base/404.html")
                fil = open(attachments[attachment], "rb")

                part = MIMEApplication(fil.read(), Name=attachment)
            # After the file is closed
            part["Content-Disposition"] = 'attachment; filename="%s"' % attachment
            msg.attach(part)

        if ssl == "True":
            server = smtplib.SMTP_SSL(mail_server, port)
        else:
            server = smtplib.SMTP(mail_server, port)
            server.starttls()

        server.login(user, password)
        text = msg.as_string()
        server.sendmail(from_address, recipients, text)

    except Exception as e:
        logging.exception("Something went wrong.")
        manager.create_from_exception(e)

    finally:
        if server is not None:
            server.quit()
        if callback:
            callback(tenant_schema, exception, callback_data)


def mail_screen(request):
    try:
        return render(request, "mails/mail_screen.html")
    except Exception as e:
        logging.exception("Something went wrong!")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def send_sms(mobile_numbers, sms_template_id, context):
    try:
        company_code = Util.get_sys_paramter("company_code").para_value
        has_sms_service = True if Util.get_sys_paramter("ftr_sms_service") is not None and Util.get_sys_paramter("ftr_sms_service").para_value.lower() == "true" else False
        if settings.IS_LIVE and has_sms_service and company_code == "2":
            send_power_sms(mobile_numbers, sms_template_id, context)

    except Exception as e:
        manager.create_from_exception(e)


def send_power_sms(mobile_numbers, sms_template_id, context):
    sms_template = SMSTemplate.objects.filter(code=sms_template_id).first()
    username = "9898028859"
    password = "POWER@3008"
    senderid = "PCBPOW"
    to_mobile_numbers = ""
    for mobile_number in mobile_numbers:
        to_mobile_numbers += mobile_number + ","
    to_mobile_numbers = to_mobile_numbers[:-1]

    context = Context(context)
    content = Template(sms_template.content).render(context)
    url = "http://sms.dynasoft.in/sendsms.aspx?"
    data = urllib.parse.urlencode({"mobile": username, "pass": password, "senderid": senderid, "to": to_mobile_numbers, "msg": content})
    req = urllib.request.Request(url + data)
    req.add_header("Content-Type", "application/json")
    urllib.request.urlopen(req).read()


def test_mail(request):
    server = None
    try:
        if request.method == "POST":

            from_address = request.POST["from_email_address"]
            to_address = request.POST["send_to_email"]

            mail_server = request.POST["smtp_server"]
            port = int(request.POST["port_number"])
            user = request.POST["username"]
            password = request.POST["password"]
            ssl = request.POST["enable_ssl"]

            msg = MIMEMultipart()
            msg["From"] = from_address
            msg["To"] = to_address
            msg["Subject"] = "Sparrow - Test mail works."
            body = """
                    Hello,
                    This is a plain email.
                    Kind Regards,
                    Me
                    """

            msg.attach(MIMEText(body, "plain"))

            if ssl == "true":
                server = smtplib.SMTP_SSL(mail_server, port)
            else:
                print(mail_server, port)
                server = smtplib.SMTP(mail_server, port)
                server.starttls()

            server.login(user, password)
            text = msg.as_string()
            server.sendmail(from_address, to_address, text)
            server.quit()

            # tenant_schema = "public"
            # print(request.POST['from_email_address'])
            # print(request.POST['password'])

            # with schema_context(tenant_schema):
            #     settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
            #     settings.EMAIL_HOST = request.POST['smtp_server']
            #     settings.EMAIL_HOST_USER = request.POST['username']
            #     settings.EMAIL_HOST_PASSWORD = request.POST['password']
            #     settings.EMAIL_PORT = int(request.POST['port_number'])
            #     settings.EMAIL_USE_SSL = request.POST['enable_ssl']
            #     settings.DEFAULT_FROM_EMAIL = request.POST['from_email_address']

            #     subject = 'Sparrow - Test mail works.'
            #     to_emails = request.POST['send_to_email']
            #     cc_mails = []
            #     bcc_mails =[]
            #     message = 'Test mail from Sparrow.'
            #     attachments = {}

            #     manager.create_from_text("tenant_schema:"+tenant_schema + "======"+subject)

            #     mail.send(
            #         to_emails,
            #         cc = cc_mails,
            #         bcc = bcc_mails,
            #         subject = subject,
            #         message = message,
            #         html_message = message,
            #         attachments = attachments,
            #         priority = 'now'
            #     )

            return HttpResponse(AppResponse.msg(1, "Sended successfully"), content_type="json")
        return render(request, "mails/test_mail.html")
    except Exception as e:
        if server is not None:
            server.quit()

        logging.exception("Something")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


import imp
import mimetypes
import os
from pydoc import doc
import urllib
import urllib.parse
import requests
import json
import pdfkit
from auditlog import views as log_views
from auditlog.models import AuditAction
# from crm.models import Deal
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpResponse
from finance_api.rest_config import APIResponse
from rest_framework.decorators import api_view
from finance_api.settings import API_URL


# from azure.storage.blob import BlobClient



def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip




def upload(_app_name, _model_name, _object_id, _docfile, _file_type, _ip_addr, _checksum, _user, is_public, source_doc, _name=None, _size=None, doc_type="gen"):
        if _name is None:
            _name = _docfile._name

        if _size is None:
            _size = _docfile.size / 1024

        model = apps.get_model(_app_name, _model_name)
        file_type_ref = None
        if _file_type is not None and _file_type != "" and _file_type != "null":
            file_type_ref = int(_file_type)
        attachment = model(
            name=_name,
            object_id=_object_id,
            size=_size,
            ip_addr=_ip_addr,
            checksum=_checksum,
            user_id=_user,
            doc_type=doc_type,
            file_type_id=file_type_ref,
            is_public=is_public,
            source_doc=source_doc,
        )
        attachment.url = _docfile
        attachment.save()
        return APIResponse(code=1,message="File uploded.")

@api_view(['get'])
def download_attachment(request):
    app_name = request.GET.get("app") 
    model_name = request.GET.get("model") 
    uid = request.GET.get("uid")
    user_id = request.GET.get("user_id")
    return download_attachment_uid(app_name, model_name, uid, user_id)

def download_attachment_uid(app_name, model_name, uid, user_id):
    model = apps.get_model(app_name, model_name)
    attachment = model.objects.filter(uid=uid).first()
    file_name = attachment.name
    if attachment.file_type_id is None:
        file_path = str(settings.MEDIA_ROOT) + str(attachment.url)
        contenttype = mimetypes.guess_type(file_path)[0]
        if "s3.amazonaws.com" in settings.MEDIA_ROOT:
            key = default_storage.bucket.lookup(str(attachment.url))
            response = HttpResponse(key)
            response["Content-Length"] = key.size
        else:
            fp = open(file_path, "rb")
            response = HttpResponse(fp.read())
            fp.close()
            response["Content-Length"] = os.path.getsize(file_path)

        response["Content-Type"] = contenttype

        if contenttype is not None and contenttype.split("/")[-1] in ["pdf", "png", "jpg", "jpeg", "bmp", "gif"]:
            response["Content-Disposition"] = "inline;filename=%s" % urllib.parse.quote(file_name)
        else:
            response["Content-Disposition"] = "attachment; filename=%s" % urllib.parse.quote(file_name)
    else:
        config = pdfkit.configuration(wkhtmltopdf=str(settings.WKTHTML_PDF_PATH))
        options = {"page-size": "A4", "margin-top": "0.2in", "margin-right": "0.3in", "margin-bottom": "0.2in", "margin-left": "0.2in", "encoding": "UTF-8", "no-outline": None}
        data = pdfkit.from_url(file_path, False, configuration=config, options=options)
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = "inline;filename=%s" % urllib.parse.quote(file_name)

    if user_id is not None:
        return response
    if user_id is None:
        if attachment.is_public is True:
            return response
        else:
            return HttpResponse("You don't have permission to access this document.")

def delete_attachment(request):
    app_name = request.POST["app"]
    model_name = request.POST["model"]
    c_ip = get_client_ip(request)
    u_id = request.POST.get("user_id")
    model = apps.get_model(app_name, model_name)

    if request.POST.get("doc_uid") is not None:
        doc_uid = request.POST.get("doc_uid")
        attachment = model.objects.filter(uid=doc_uid).first()
    else:
        id = int(request.POST["id"])
        attachment = model.objects.filter(id=id).first()

    attachment.deleted = True
    attachment.is_public = False
    attachment.save()

    tag_model_name = model_name
    tag_model_name = tag_model_name.replace("_", "")
    tag_model_name = tag_model_name + "Tag"

    model_exist = False
    try:
        apps.get_model(app_name, tag_model_name)
        model_exist = True
    except LookupError:
        model_exist = False

    if model_exist:
        tag_model = apps.get_model(app_name, tag_model_name)
        doc_tag = tag_model.objects.filter(attachment_id=attachment.id)
        doc_tag.delete()
    os.remove(settings.MEDIA_ROOT + str(attachment.url))
    log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, c_ip, attachment.name + " deleted.")
    # object_id = attachment.object_id if attachment.object_id else 0
    return APIResponse(code =  1, message= "Data removed.")

    # return HttpResponse(json.dumps({"code": 1, "msg": "Data removed.", "object_id": object_id, "id": attachment.id}), content_type="json")

@api_view(['post'])
def get_document(request):
    number =  request.data.get("number")
    doctype =  request.data.get("doctype")
    response = None
    if number is None :
        return APIResponse(code=0,message="please select at least one record")
    if doctype == "invoice":
        headers = {'Content-Type': 'application/json','token':'HKt7854UHTFGR78#78'}
        response = requests.request("GET", API_URL+"salesapp/getdoc", data=json.dumps({"invoicenr": number,'doctype':doctype}), headers=headers)
        response = response.json()
        return APIResponse(response)
    elif doctype == "deliverynote":
        headers = {'Content-Type': 'application/json','token':'HKt7854UHTFGR78#78'}
        response = requests.request("GET", API_URL+"salesapp/getdoc", data=json.dumps({"deliverynr": number,'doctype':doctype}), headers=headers)
        response = response.json()
        return APIResponse(response)
    else:
        return APIResponse(code=0,message="does not exists doctype")
        
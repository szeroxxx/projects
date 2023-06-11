import datetime
import json
import logging
import mimetypes
import os
import re
import urllib
import urllib.parse

from datetime import date
from mptt.utils import get_cached_trees
from accounts.models import UserProfile
from attachment.document_service import Attachment as Document
from attachment.models import FileType, Tag
from auditlog import views as log_views
from auditlog.models import AuditAction
from base import views as base_views
from base.models import AppResponse, Base_Attachment
from base.util import Util
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from exception_log import manager
from stronghold.decorators import public
from base.models import BaseAttachmentTag, Base_Attachment
from sparrow.impersonate import Impersonate
from .models import Attachment
from django.db import transaction
from task.models import Message, Task
from django.contrib.contenttypes.models import ContentType


# from uuid import uuid4


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def delete_attachment(request):
    try:
        app_name = request.POST["app"]
        model_name = request.POST["model"]
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        if Util.has_perm("can_delete_attachment", user) is False:
            return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")

        c_ip = get_client_ip(request)
        u_id = request.session["userid"]
        model = apps.get_model(app_name, model_name)

        if request.POST.get("doc_uid") is not None:
            doc_uid = request.POST.get("doc_uid")
            attachment = model.objects.filter(uid=doc_uid).first()
        else:
            id = int(request.POST.get("id", None))
            attachment = model.objects.filter(id=id).first()
        if attachment:
            attachment.deleted = True
            attachment.is_public = False
            attachment.save()
            log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, c_ip, attachment.name + " deleted.")
            return HttpResponse(json.dumps({"code": 1, "msg": "Document has been deleted."}), content_type="json")

            # tag_model_name = model_name
            # tag_model_name = tag_model_name.replace("_", "")
            # tag_model_name = tag_model_name + "Tag"

            # model_exist = False
            # try:
            #     apps.get_model(app_name, tag_model_name)
            #     model_exist = True
            # except LookupError:
            #     model_exist = False

            # if model_exist:
            #     tag_model = apps.get_model(app_name, tag_model_name)
            #     doc_tag = tag_model.objects.filter(attachment_id=attachment.id)
            #     doc_tag.delete()

            # es_attachment = Document()
            # es_attachment.delete_attachment(attachment.id, model_name=model_name)
            # container_name = settings.AZURE_BLOB["container_name"]
            # conn_str = settings.AZURE_BLOB["conn_str"]
            # blob = BlobClient.from_connection_string(conn_str=conn_str, container_name=container_name, blob_name=str(attachment.url).split("/")[-1])
            # exists = blob.exists()
            # if exists:
            #     blob.delete_blob()
            # elif os.path.exists(str(settings.MEDIA_ROOT) + str(attachment.url)):
            #     os.remove(settings.MEDIA_ROOT + str(attachment.url))
            # if os.path.exists(str(settings.MEDIA_ROOT) + str(attachment.url)):
            #     os.remove(settings.MEDIA_ROOT + str(attachment.url))
            #     log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, c_ip, attachment.name + " deleted.")
            # object_id = attachment.object_id if attachment.object_id else 0
            # return HttpResponse(json.dumps({"code": 1, "msg": "Data removed.", "object_id": object_id, "id": attachment.id}), content_type="json")
        return HttpResponse(json.dumps({"code": 0}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def dialog_template(request):
    file_types = FileType.objects.filter(is_active=True)
    return render(request, "attachment/dialog.html", {"file_types": file_types})


"""
download: Responds with download stream, todo: This needs improvement, may not work.
"""


@csrf_exempt
@public
def download_attachment(request):
    app_name = request.GET["app"] if request.GET.get("a") is None else request.GET.get("a")
    model_name = request.GET["model"] if request.GET.get("m") is None else request.GET.get("m")
    uid = request.GET["uid"]
    user_id = request.user.id if request.user else None
    return download_attachment_(app_name, model_name, uid, user_id)


def download_attachment_(app_name, model_name, uid, user_id):
    try:
        model = apps.get_model(app_name, model_name)
        attachment = model.objects.filter(id=uid).first()
        # attachment = model.objects.filter(uid=uid).first()
        file_path = str(settings.FILE_SERVER_PATH) + str(attachment.claim_file_path)
        file_name = attachment.claim_file_name
        with Impersonate():
            if os.path.exists(file_path) is False:
                return render_to_response("base/404.html")
            # if attachment.file_type_id is not None:
            contenttype = mimetypes.guess_type(file_name)[0]
            fp = open(file_path, "rb")
            response = HttpResponse(fp.read())
            fp.close()
            response["Content-Length"] = os.path.getsize(file_path)
            response["Content-Type"] = contenttype
            if contenttype is not None and contenttype.split("/")[-1] in ["pdf", "png", "jpg", "jpeg", "bmp", "gif", "html"]:
                response["Content-Disposition"] = "attachment; filename=%s" % urllib.parse.quote(file_name)
            else:
                response["Content-Disposition"] = "attachment; filename=%s" % urllib.parse.quote(file_name)
            if user_id is not None:
                return response
            if user_id is None:
                if attachment.is_public is True:
                    return response
                else:
                    return HttpResponse("You don't have permission to access this document.")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def download_attachment_uid(app_name, model_name, uid, user_id):
    try:
        model = apps.get_model(app_name, model_name)
        attachment = model.objects.filter(uid=uid).first()
        file_path = str(settings.FILE_SERVER_PATH) + str(attachment.url)
        file_name = attachment.name
        if attachment.file_type_id is not None:
            contenttype = mimetypes.guess_type(file_path)[0]
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
            # config = pdfkit.configuration(wkhtmltopdf=str(settings.WKTHTML_PDF_PATH))
            # options = {
            #     "enable-local-file-access": "",
            #     "page-size": "A4",
            #     "margin-top": "0.2in",
            #     "margin-right": "0.3in",
            #     "margin-bottom": "0.2in",
            #     "margin-left": "0.2in",
            #     "encoding": "UTF-8",
            #     "no-outline": None,
            # }
            # return FileResponse(open(file_path, "rb"), content_type="application/pdf")
            # with open(file_path) as f:
            # # data = pdfkit.from_file(file_path, False, configuration=config, options=options)
            response = HttpResponse(f, content_type="application/pdf")
            response["Content-Disposition"] = "inline;filename=%s" % urllib.parse.quote(file_name)
            return response

        if user_id is not None:
            return response
        if user_id is None:
            if attachment.is_public is True:
                return response
            else:
                return HttpResponse("You don't have permission to access this document.")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_attachments(request):
    try:
        query = Q()
        query2 = Q()
        tag_ = request.POST.get("tag")
        object_id = request.POST.get("object_id")
        search_type = request.POST.get("search_type")
        app = request.POST.get("app")
        model = request.POST.get("model")
        search_data = request.POST.get("documentdata")

        if request.POST.get("customer"):
            query2.add(Q(company=request.POST.get("customer")), query2.connector)
        if search_data:
            query.add(Q(name__icontains=search_data), query.connector)
        if tag_:
            query.add(Q(tag__name=tag_), query.connector)
        es_attachment = Document()
        page_index = request.POST.get("page_index") if request.POST.get("page_index") is not None else 1
        results = es_attachment.get_attachments(int(page_index) - 1, 25, search_data, object_id, search_type, app, model)
        documents = results["hits"]["hits"]
        recordsTotal = results["hits"]["total"]["value"]
        response = {"data": [], "total_attachments": recordsTotal, "count": len(documents)}

        product_ids = []
        part_ids = []
        deal_ids = []
        user_ids = []
        for document in documents:
            user_ids.append(document["_source"]["user_id"])
            if document["_source"]["app_name"] == "part":
                part_ids.append(document["_source"]["entity_id"])
            if document["_source"]["app_name"] == "products":
                product_ids.append(document["_source"]["entity_id"])
            if document["_source"]["app_name"] == "crm":
                deal_ids.append(document["_source"]["entity_id"])

        user_data = {}
        users = UserProfile.objects.filter(is_deleted=False, user_id__in=user_ids).values("user_id", "profile_image", "user__first_name", "user__last_name")

        for user in users:
            user_data[user["user_id"]] = [{"first_name": user["user__first_name"], "last_name": user["user__last_name"], "profile_image": user["profile_image"]}]

        user_id = request.user.id
        user = User.objects.get(id=user_id)
        perms = ["can_add_update", "can_upload_document", "can_delete_attachment", "can_make_attachment_public"]
        permissions = Util.get_permission_role(user, perms)
        selected_tag_id = []

        for document in documents:
            if "tags" in document["_source"] and len(document["_source"]["tags"]) > 0:
                for tag in document["_source"]["tags"]:
                    selected_tag_id.append(tag["id"])

        all_tags = {}
        tags = Tag.objects.filter(id__in=selected_tag_id)
        for tag in tags:
            tag_name = get_hierarchy_tag(tag, tag.name)
            all_tags[tag.id] = tag_name
        start = int(page_index) - 1
        length = 25
        base_Attachment1 = Base_Attachment.objects.filter(query, query2, Q(deleted=False), Q(is_public=True)).values("user__username", "user", "is_public", "company__name", "tag__name", "tag__parent__name", "uid", "id", "name", "create_date", "title", "subject", "description", "user", "user__username")
        base_Attachment2 = Base_Attachment.objects.filter(query, query2, Q(deleted=False), Q(is_public=False), Q(user=request.user.id)).values("user__username", "user", "is_public", "company__name", "tag__name", "tag__parent__name", "uid", "id", "name", "create_date", "title", "subject", "description", "user", "user__username")
        base_Attachment = base_Attachment1.union(base_Attachment2).order_by('-create_date')[start : (start + length)]
        base_Attachment_count = base_Attachment1.union(base_Attachment2).order_by('-create_date').count()
        user_ids = [base_attach["user"] for base_attach in base_Attachment]
        users = UserProfile.objects.filter(user_id__in=user_ids).values("user_id__username", "profile_image")
        imageurl = {}
        for user in users:
            imageurl[user["user_id__username"]] = user["profile_image"]

        user_ids = [base_attach["user"] for base_attach in base_Attachment]
        users = User.objects.filter(id__in=user_ids).values("id", "first_name", "last_name")
        username = {}
        for user in users:
            username[user["id"]] = user["first_name"]+" "+user["last_name"]

        req_user = {}
        for user in base_Attachment:
            if user["user"] == request.user.id:
                req_user[user["id"]] = "true"
            else:
                req_user[user["id"]] = "false"
        response = {
            "record_total" : base_Attachment.count(),
            "base_Attachment_count": base_Attachment_count,
            "data": [],
            "tags": []
        }
        for base_Attachments in base_Attachment:
            response["data"].append(
                {
                    "id": base_Attachments["id"],
                    "name": base_Attachments["name"],
                    "create_date": Util.get_local_time(base_Attachments["create_date"], True),
                    "title": base_Attachments["title"],
                    "subject": base_Attachments["subject"],
                    "description": base_Attachments["description"],
                    "user_pic" : Util.get_resource_url("profile", str(imageurl[base_Attachments["user__username"]])) if base_Attachments["user__username"] in imageurl and imageurl[base_Attachments["user__username"]] else "",
                    "app_name": "base",
                    "model_name": "base_attachment",
                    "uid": base_Attachments["uid"] if base_Attachments["uid"] else None,
                    "is_public": base_Attachments["is_public"] if base_Attachments["is_public"] else None,
                    "permissions": json.dumps(permissions),
                    "customer_name": base_Attachments["company__name"],
                    "tag": base_Attachments["tag__name"],
                    "tag_parent": base_Attachments["tag__parent__name"],
                    "user__username": username[base_Attachments["user"]] if base_Attachments["user"] in username else "",
                    "req_user": req_user[base_Attachments["id"]] if base_Attachments["id"] in req_user else "",
                }
            )
        tag = Tag.objects.all()
        roots = get_cached_trees(tag)

        def form_a_tree(objects):
            tree = []
            for obj in objects:
                children = obj.get_children()
                # res_data = []
                # for res in response["data"]:
                #     if str(res["tag"]) == str(obj.name):
                #         res_data.append(res)
                # dictionary_category_tree = {'id': obj.id, 'text': obj.name, 'data': res_data}
                dictionary_category_tree = {'id': obj.id, 'text': obj.name}
                if children:
                    dictionary_category_tree.update({'nodes': form_a_tree(children)})
                tree.append(dictionary_category_tree)
            return tree
        response["tags"].append(form_a_tree(roots))
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def get_attchment_object(attachment):
    user = attachment.user
    user_name = user.first_name + " " + user.last_name
    user_id = user.id
    users = UserProfile.objects.filter(user_id=user_id).values("user_id", "profile_image")
    imageurl = {}
    for user in users:
        imageurl[user["user_id"]] = user["profile_image"]
    img_src = Util.get_resource_url("profile", str(imageurl[attachment.user_id])) if attachment.user_id in imageurl and imageurl[attachment.user_id] else ""
    file_type = ""
    if attachment.file_type is not None:
        file_type = attachment.file_type.description
    return {
        "attachment_id": attachment.id,
        "uid": attachment.uid,
        "name": attachment.name,
        "size": str(round(attachment.size, 2)),
        "url": str(attachment.url),
        "user": user_name,
        "source_doc": attachment.source_doc,
        "user_id": user_id,
        "entity_id": attachment.object_id,
        "create_date": Util.get_local_time(attachment.create_date),
        "file_type": file_type,
        "is_public": attachment.is_public,
        "created_on": Util.get_local_time(attachment.create_date),
        "title": attachment.title,
        "subject": attachment.subject,
        "img_src": img_src,
        "isSelected": False,
        "description": attachment.description,
        "workcenter_id": attachment.workcenter_id if hasattr(attachment, "workcenter_id") and attachment.workcenter_id else 0,
        "workcenter_name": attachment.workcenter.name if hasattr(attachment, "workcenter_id") and attachment.workcenter_id else "",
    }


@public
@csrf_exempt
def upload_attachment(request):
    response = {"data": []}
    try:
        app_name = request.POST["app"]
        ip_addr = get_client_ip(request)
        model_name = request.POST["model"]
        c_ip = get_client_ip(request)
        if "userid" in request.session:
            u_id = request.session["userid"]
        else:
            u_id = request.user.id
        file_name = request.FILES["file"]
        file_name_data = file_name.read()
        customer_id = request.POST["customer_id"]

        is_not_valid = (
            str(file_name)
            .lower()
            .endswith(
                (
                    ".bat",
                    ".exe",
                    ".cmd",
                    ".sh",
                    ".p",
                    ".cgi",
                    ".386",
                    ".dll",
                    ".com",
                    ".torrent",
                    ".js",
                    ".app",
                    ".jar",
                    ".pif",
                    ".vb",
                    ".vbscript",
                    ".wsf",
                    ".asp",
                    ".cer",
                    ".csr",
                    ".jsp",
                    ".drv",
                    ".sys",
                    ".ade",
                    ".adp",
                    ".bas",
                    ".chm",
                    ".cpl",
                    ".crt",
                    ".csh",
                    ".fxp",
                    ".hlp",
                    ".hta",
                    ".inf",
                    ".ins",
                    ".isp",
                    ".jse",
                    ".htaccess",
                    ".htpasswd",
                    ".ksh",
                    ".lnk",
                    ".mdb",
                    ".mde",
                    ".mdt",
                    ".mdw",
                    ".msc",
                    ".msi",
                    ".msp",
                    ".mst",
                    ".ops",
                    ".pcd",
                    ".prg",
                    ".reg",
                    ".scr",
                    ".sct",
                    ".shb",
                    ".shs",
                    ".url",
                    ".vbe",
                    ".vbs",
                    ".wsc",
                    ".wsf",
                    ".wsh",
                    ".php",
                    ".php1",
                    ".php2",
                    ".php3",
                    ".php4",
                    ".php5",
                )
            )
        )
        if is_not_valid:
            return HttpResponse(AppResponse.msg(0, "This file type is not allowed to upload."), content_type="json")
        rootFolderName = app_name + "\\" + model_name.replace("_attachment", "").lower()
        file_root_path = Attachment.get_file_rootpath(rootFolderName) + str("dev_11") + "\\"
        time = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        file_name = str(file_name).split(".")
        file_name = file_name[0] + "_" + time + "." + file_name[1]
        file_path = os.path.join(file_root_path, file_name)
        full_path = str(settings.FILE_SERVER_PATH) + file_path
        file_data = full_path.rsplit("\\", 1)
        with Impersonate():
            parent_dir = str(file_data[0])
            if not os.path.exists(os.path.join(parent_dir)):
                os.makedirs(parent_dir)
            if not os.path.isfile(full_path):
                with open(full_path, "wb") as fp:
                    fp.write(file_name_data)
                    fp.close()
                size = os.path.getsize(full_path) / 1024
        "base base_attachment 0 public\base\base\2023\5\17\ACB\pture_170523_153000.PNG 19 192.168.1.242 - 1 False  pture_170523_153000.PNG 40.5986328125  10 3"
        response["code"] = 1
        response["msg"] = "File uploaded."

    except Exception as e:
        response["code"] = 0
        response["msg"] = str(e)
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
    return HttpResponse(AppResponse.get(response), content_type="json")


# def attachment_change_access(request):
#     try:
#         app_name = request.POST["app"]
#         model_name = request.POST["model"]
#         user_id = request.user.id
#         user = User.objects.get(id=user_id)
#         permission = Util.has_perm("can_make_attachment_public", user)
#         if permission is False:
#             return HttpResponse(AppResponse.msg(0, Util.user_perm_msg), content_type="json")
#         attachment_id = int(request.POST["id"])
#         model = apps.get_model(app_name, model_name)

#         attachment = model.objects.filter(id=int(attachment_id)).first()
#         if attachment.is_public is True:
#             attachment.is_public = False
#         else:
#             attachment.is_public = True
#         attachment.save()
#         if attachment.is_public is True:
#             base_attachment = Base_Attachment.objects.filter(id=int(attachment_id)).values("name").first()
#             if base_attachment:
#                 if base_attachment["name"]:
#                     doc_name = base_attachment["name"]
#                     doc_name_ = os.path.splitext(doc_name)
#                     document_name = doc_name_[0]
#                     request_user = request.user.id
#                     request_user_id = User.objects.filter(id=request_user).values("id", "username").first()
#                     request_user_username = request_user_id["username"]
#                     request_user_id = request_user_id["id"]
#                     send_msg = []
#                     send_doc_operator = Operator.objects.filter(user__id=request_user_id).values("id", "operator_group").first()
#                     operator_group = send_doc_operator["operator_group"] if send_doc_operator["operator_group"] else None
#                     if operator_group:
#                         all_operators = Operator.objects.filter(operator_group=operator_group, is_deleted=False).values("user_id")
#                         for data in all_operators:
#                             if data["user_id"] not in send_msg:
#                                 send_msg.append(data["user_id"])
#                     name = "Document updated " " " + "" + document_name + " " "by" " " + request_user_username + ""
#                     description = "Document updated " " " + "<b>" + "" + document_name + " " + "<b>"
#                     content_type = ContentType.objects.filter(app_label=app_name.lower(), model=model_name.lower()).first()
#                     assign_to_op = Operator.objects.filter(user_id__in=send_msg).values("id")
#                     assign_to = [x["id"] for x in assign_to_op]
#                     assign_to_ = ",".join(map(str, assign_to))
#                     task = Task.objects.create(name=name, content_type=content_type, description=description, created_by_id=request_user, assign_to=assign_to_)
#                     if task:
#                         message = []
#                         for id in assign_to:
#                             if not Message.objects.filter(task_id_id=task.id, operator_id_id=id):
#                                 message.append(Message(task_id_id=task.id, operator_id_id=id))
#                         Message.objects.bulk_create(message)

#         response = {"data": []}
#         response["access"] = attachment.is_public
#         response["id"] = attachment.id
#         response["permission"] = permission
#         return HttpResponse(AppResponse.get(response), content_type="json")

#     except Exception as e:
#         manager.create_from_exception(e)
#         return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def upload_and_save_attachment(data, app_name, model_name, object_id, u_id, c_ip, code, file_name):
    try:
        # domain = request.META['HTTP_HOST']
        file_type = FileType.objects.filter(code=code, is_active=True).first()
        rootFolderName = app_name + "/" + model_name.replace("_attachment", "").lower()
        file_rootpath = Attachment.get_file_rootpath(rootFolderName)
        file_path = os.path.join(file_rootpath, file_name)
        full_path = str(settings.MEDIA_ROOT) + file_path
        data_new = full_path.rsplit("/", 1)
        if len(data_new) > 0 and data_new[0] != "":
            parent_dir = str(data_new[0])
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
        if not os.path.isfile(full_path):
            with open(full_path, "wb") as f:
                f.write(data)
            size = os.path.getsize(full_path) / 1024
            # upload(False, app_name, model_name, object_id, file_path, file_type.id, c_ip, "-", u_id, False, "", file_name, size)
            upload(app_name, model_name, object_id, file_path, file_type.id, c_ip, "-", u_id, False, "", file_name, size)

        return full_path
    except Exception as e:
        manager.create_from_exception(e)
        return ""


def upload_claim_file(_app_name, _model_name,quality_claim ,claim_file_name, claim_file_path,claim_created_by,claim_created_date,is_file_deleted,_docfile, title=""):
    if title == "":
        title = _name.split(".")[0]
    if _name is None:
        _name = _docfile._name
    if _size is None:
        _size = _docfile.size / 1024
    model = apps.get_model(_app_name, _model_name)
    claim_file = model(
        quality_claim=quality_claim,
        claim_file_name=claim_file_name,
        claim_file_path=claim_file_path,
        claim_created_by=claim_created_by,
        claim_created_date=claim_created_date,
        is_file_deleted=is_file_deleted,
        )
    claim_file.save()
    claim_file.url = _docfile
    claim_file.save()
    pass




def upload(_app_name, _model_name, _object_id, _docfile, _file_type, _ip_addr, _checksum, _user_id, is_public, source_doc, _name=None, _size=None, doc_type="gen", customer_id=None, tag=None, title=""):
    try:
        if title == "":
            title = _name.split(".")[0]
        if _name is None:
            _name = _docfile._name
        if _size is None:
            _size = _docfile.size / 1024
        model = apps.get_model(_app_name, _model_name)
        file_type_ref = None
        if _file_type is not None and _file_type != "" and _file_type != "null":
            file_type_ref = int(_file_type)
        if _model_name == "base_attachment":
            attachment = model(
                name=_name,
                object_id=_object_id,
                size=_size,
                ip_addr=_ip_addr,
                checksum=_checksum,
                user_id=_user_id,
                doc_type=doc_type,
                file_type_id=file_type_ref,
                is_public=is_public,
                source_doc=source_doc,
                company_id=customer_id,
                tag_id=tag,
                title=title
            )
            attachment.save()
            attachment.url = _docfile
            attachment.save()
        else:
            attachment = model(
                name=_name,
                object_id=_object_id,
                size=_size,
                ip_addr=_ip_addr,
                checksum=_checksum,
                user_id=_user_id,
                doc_type=doc_type,
                file_type_id=file_type_ref,
                is_public=is_public,
                source_doc=source_doc,
            )
            attachment.save()
            attachment.url = _docfile
            attachment.save()
        # Indext attachment in ES
        Document().insert([attachment], app_name=_app_name, model_name=_model_name)

        # log_views.insert(_app_name, _model_name, [attachment.id], AuditAction.INSERT, _user_id, _ip_addr, _name + " uploaded.")
        return attachment
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return None
        # return HttpResponse(AppResponse.msg(0, str(e)), content_type = 'json')


def attachment_properties(request):
    try:
        # attachment_es_update = {}
        field_name = request.POST.get("field_name")
        app_name = request.POST.get("app")
        model_name = request.POST.get("model")

        value = request.POST.get("value")
        attachment_id = request.POST["attachment_id"]
        object_id = int(request.POST["object_id"])
        attachment = apps.get_model(app_name, model_name)
        attachment_saves = attachment.objects.filter(id=attachment_id).first()
        es_attachment = Document()

        if str(field_name) == "title":
            attachment_saves.title = value
            es_attachment.update_attachment(attachment_id=attachment_id, title=value, app_name=app_name, model_name=model_name)

        if str(field_name) == "subject":
            attachment_saves.subject = value
            es_attachment.update_attachment(attachment_id=attachment_id, subject=value, app_name=app_name, model_name=model_name)

        if str(field_name) == "description":
            attachment_saves.description = value
            es_attachment.update_attachment(attachment_id=attachment_id, description=value, app_name=app_name, model_name=model_name)

        if str(field_name) == "workcenter_id":
            attachment_saves.workcenter_id = value
        attachment_saves.save()

        # document_service.Attachment.update_attachment(**attachment_es_update)

        attachments = attachment.objects.filter(object_id=object_id, deleted=False).order_by("id")

        response = {
            "data": [],
        }
        for attachment in attachments:
            response["data"].append(get_attchment_object(attachment))
        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


# @check_view_permission([{"attachments": "mo_documents"}])
def documents(request):

    user_id = request.user.id
    user = User.objects.get(id=user_id)
    perms = ["can_add_update", "can_upload_document", "can_delete_attachment", "can_make_attachment_public"]
    permissions = Util.get_permission_role(user, perms)
    tags = Tag.objects.all()
    tag_list = []
    for tag in tags:
        tag_name = get_hierarchy_tag(tag, tag.name)
        tag_list.append(tag_name)

    return render(request, "attachment/documents.html", {"permissions": json.dumps(permissions), "tag_list": tag_list})


def document(request, type=None, id=None):
    try:
        if type == "edit":
            model = apps.get_model("base", "base_attachment")
            document_data = model.objects.filter(id=id).first()
            file_path = str(settings.FILE_SERVER_PATH) + str(document_data.url)
            with Impersonate():
                HtmlFile = open(file_path, "r")
                source_code = HtmlFile.read()
                base_attac_tag_obj = Base_Attachment.objects.filter(id=id).values_list("tag_id", flat=True).distinct()
                return render(
                    request,
                    "attachment/document.html",
                    {"document_data": document_data, "source_code": source_code, "base_attac_tag_obj": ",".join(str(x) for x in base_attac_tag_obj)},
                )
        return render(request, "attachment/document.html")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def document_save(request):
    try:
        id = int(request.POST.get("id"))
        ip_addr = get_client_ip(request)
        title = request.POST.get("title")
        title = re.sub("[^a-zA-Z0-9_ ]", "", title)
        file_name = title.rstrip() + ".html"
        template = request.POST.get("template")
        app_name = "base"
        model_name = "base_attachment"
        model = apps.get_model(app_name, model_name)
        u_id = request.user.id
        c_ip = get_client_ip(request)
        customer = request.POST.get("customer")
        tag = request.POST.get("tag")
        customer_name = Company.objects.filter(id=customer).values("name").first()
        customer_name = customer_name["name"]
        file_type = FileType.objects.filter(code="document", is_active=True).first()
        rootFolderName = app_name + "\\" + model_name.replace("_attachment", "").lower()
        file_root_path = Attachment.get_file_rootpath(rootFolderName) + str(customer_name) + "\\"
        time = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        file_name = file_name.split(".")
        file_name = file_name[0] + "_" + time + "." + file_name[1]
        file_path = os.path.join(file_root_path, file_name)
        full_path = str(settings.FILE_SERVER_PATH) + file_path
        file_data = full_path.rsplit("\\", 1)
        with Impersonate():
            parent_dir = str(file_data[0])
            if not os.path.exists(os.path.join(parent_dir)):
                os.makedirs(parent_dir)
            if not os.path.isfile(full_path):
                with open(full_path, "w") as fp:
                    fp.write(template)
                    fp.close()
                size = os.path.getsize(full_path) / 1024
                attachment = upload(app_name, model_name, id, file_path, file_type.id, c_ip, "-", u_id, False, "", file_name, size, "", customer, tag, title)
                log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, ip_addr, "(" + file_name + ")" + " " + "Document uploaded.")
        if id == 0 :
            return HttpResponse(json.dumps({"code": 1, "msg": "Document has been created", "id": id}), content_type="json")
        else:
            attachment = model.objects.filter(id=id).first()
            attachment.deleted = True
            attachment.is_public = False
            attachment.save()
            log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, c_ip, attachment.name + " Updated.")
            return HttpResponse(json.dumps({"code": 1, "msg": "Document has been updated", "id": id}), content_type="json")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
        # todays_date = date.today()
        # file_path = "public" + "\\" + "base" + "\\" + "base" + "\\" + str(todays_date.year) + "\\" + str(todays_date.month) + "\\" + str(todays_date.day) + "\\" + file_name
        # description = request.POST.get("description")

        # ip_addr = get_client_ip(request)

        # model = apps.get_model(app_name, model_name)

        # file_type_ref = FileType.objects.filter(name="Document").first().id
        # name = title.rstrip() + ".pdf"
        # todays_date = date.today()
        # es_attachment = Document()
        # id = int(request.POST.get("id"))
        # title = request.POST.get("title")
        # file_name_data = title.read()
        # file_name_ = str(title)
        # app_name = "base"
        # model_name = "base_attachment"
        # u_id = request.user.id
        # upload_and_save_impersonate(file_name_data, app_name, model_name, id, u_id, c_ip, "document", file_name_, "customer", "")

        # if id is not None and int(id) not in [0, -1]:
        #     attachment = model.objects.filter(id=id).first()
        #     with open(settings.MEDIA_ROOT + str(attachment.url), "w") as docfile:
        #         docfile.write(template)
        #     size = os.stat(settings.MEDIA_ROOT + str(attachment.url)).st_size
        #     if size > 10000000:
        #         return HttpResponse(AppResponse.msg(0, "File more than 10MB size is not allowed."), content_type="json")
        #     attachment.name = name
        #     attachment.size = size
        #     attachment.title = request.POST.get("title")
        #     attachment.description = description
        #     attachment.ip_addr = ip_addr
        #     attachment.user_id = u_id
        #     msg = "Document updated"
        #     attachment.save()
        #     Document().insert([attachment], app_name=app_name, model_name=model_name, status="update")
        #     log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, ip_addr, name + " Updtaed file.")
        # else:
        #     path = "public" + "/base/base/" + "{}/{}/{}/".format(str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day))
        #     folder_path = os.path.join(settings.MEDIA_ROOT, str(path))
        #     if not os.path.exists(folder_path):
        #         os.makedirs(folder_path)
        #     with open(settings.MEDIA_ROOT + file_path, "w") as docfile:
        #         docfile.write(template)

        #     size = os.stat(settings.MEDIA_ROOT + file_path).st_size / 1024

        #     if size > 10000000:
        #         return HttpResponse(AppResponse.msg(0, "File more than 10MB size is not allowed."), content_type="json")
        #     attachment = model(
        #         name=name,
        #         object_id=0,
        #         url=file_path,
        #         size=size,
        #         title=request.POST.get("title"),
        #         description=description,
        #         ip_addr=ip_addr,
        #         checksum="-",
        #         user_id=u_id,
        #         doc_type="gen",
        #         file_type_id=file_type_ref,
        #         is_public=False,
        #         source_doc="",
        #     )

        #     path = (
        #         "public"
        #         + "\\"
        #         + "base"
        #         + "\\"
        #         + "base"
        #         + "\\"
        #         + str(todays_date.year)
        #         + "\\"
        #         + str(todays_date.month)
        #         + "\\"
        #         + str(todays_date.day)
        #         + "\\"
        #         + attachment.uid
        #         + "_"
        #         + file_name
        #     )
        #     attachment.url = path
        #     new_file_path = settings.MEDIA_ROOT + path
        #     os.rename(settings.MEDIA_ROOT + file_path, new_file_path)
        #     msg = "Document saved"
        #     attachment.save()
        #     Document().insert([attachment], app_name=app_name, model_name=model_name)
        #     log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, ip_addr, name + " uploaded.")

        # modelname = app_name + "AttachmentTag"
        # model = apps.get_model(app_name, modelname)
        # base_doc_tag = model.objects.filter(attachment_id=attachment.id)
        # base_doc_tag.delete()
        # tags = []
        # for tag_id in tag_ids:
        #     tags.append({"id": int(tag_id)})
        #     model.objects.create(tag_id=int(tag_id), attachment_id=attachment.id)
        # es_attachment.update_attachment(attachment_id=attachment.id, title=request.POST.get("title"), description=description, tags=tags, app_name=app_name, model_name=model_name)
        # log_views.insert(app_name, model_name, [attachment.id], AuditAction.INSERT, u_id, ip_addr, name + " uploaded.")


def tags(request):
    return render(request, "attachment/tags.html")


def tag_search(request):
    try:
        request.POST = Util.get_post_data(request)
        start = int(request.POST["start"])
        length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        query = Q()

        if request.POST.get("name__icontains") is not None:
            query.add(Q(name__icontains=str(request.POST.get("name__icontains"))), query.connector)

        recordsTotal = Tag.objects.filter(query).count()
        tags = Tag.objects.filter(query).order_by(sort_col)[start : (start + length)]
        response = {
            "draw": request.POST["draw"],
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "data": [],
        }

        for tag in tags:
            response["data"].append({"id": tag.id, "name": tag.name, "created_on": Util.get_local_time(tag.created_on), "created_by": tag.created_by.username})

        return HttpResponse(AppResponse.get(response), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong!")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def tag(request, id=None):
    try:
        if request.method == "POST":
            id = request.POST.get("id")
            name = request.POST.get("name")
            parent = request.POST.get("parent")
            c_ip = base_views.get_client_ip(request)
            user_id = request.user.id
            if id is None or (Util.is_integer(id) and int(id) in [0, -1]):
                if Tag.objects.filter(name__iexact=name).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Tag name already exists."}), content_type="json")
                base_attach_tag = Tag.objects.create(name=name, created_by_id=user_id, parent_id=parent)
                action = AuditAction.INSERT
                log_views.insert("attachment", "tag", [base_attach_tag.id], action, user_id, c_ip, name + " Inserted")
                return HttpResponse(json.dumps({"code": 1, "msg": "Tag saved.", "id": base_attach_tag.id}), content_type="json")
            else:
                tag = Tag.objects.get(id=int(id))
                if Tag.objects.filter(name__iexact=name).exclude(name__iexact=tag.name).count() > 0:
                    return HttpResponse(AppResponse.get({"code": 0, "msg": "Tag name already exists."}), content_type="json")
                base_attach_tag = Tag.objects.filter(id=id).update(name=name, created_by_id=user_id, parent_id=parent)
                action = AuditAction.UPDATE
                log_views.insert("attachment", "tag", [id], action, user_id, c_ip, name + " Updated")
                return HttpResponse(json.dumps({"code": 1, "msg": "Tag saved.", "id": tag.id}), content_type="json")
        else:
            tag_data = Tag.objects.filter(id=id).first()
            return render(request, "attachment/tag.html", {"tag_data": tag_data})
    except Exception as e:
        logging.exception("Something")
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def check_tag_use(request):
    try:
        post_ids = request.POST.get("ids")

        ids = [int(x) for x in post_ids.split(",")]

        tag_id = BaseAttachmentTag.objects.filter(tag_id__in=ids)
        in_use = False

        if len(tag_id) > 0:
            in_use = True

        return HttpResponse(json.dumps({"code": 1, "data": in_use}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, "Error occurred."), content_type="json")


def tag_del(request):
    try:
        post_ids = request.POST.get("ids")

        if not post_ids:
            return HttpResponse(AppResponse.msg(0, "Please select atleast one record."), content_type="json")

        ids = [int(x) for x in post_ids.split(",")]

        base_attacg_tag_delete = BaseAttachmentTag.objects.filter(tag_id__in=ids)
        base_attacg_tag_delete.delete()

        tag_delete = Tag.objects.filter(id__in=ids)
        tag_delete.delete()

        return HttpResponse(json.dumps({"code": 1, "msg": "Data removed."}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, "Error occurred."), content_type="json")


def get_hierarchy_tag(tag, tag_name):
    if tag.parent_id is None:
        return tag_name
    else:
        tag_name = tag.parent.name + "/" + tag_name
        sub_tag = tag.parent
        return get_hierarchy_tag(sub_tag, tag_name)


def save_doc_tag(request):
    try:
        attachment_id = int(request.POST.get("attachment_id"))
        app_name = request.POST.get("app_name")
        model_name = request.POST.get("model_name")
        tag_id_list = request.POST.get("tag_list")
        es_attachment = Document()
        tags = []

        modelname = model_name
        modelname = modelname.replace("_", "")
        modelname = modelname + "Tag"

        model = apps.get_model(app_name, modelname)
        base_doc_tag = model.objects.filter(attachment_id=attachment_id)
        base_doc_tag.delete()
        data = []
        if tag_id_list != "":
            tad_ids = [int(x) for x in tag_id_list.split(",")]

            for tad_id in tad_ids:
                model.objects.create(attachment_id=attachment_id, tag_id=tad_id)
                tags.append({"id": tad_id})
            attachment_tags = Tag.objects.filter(id__in=tad_ids)
            for tag in attachment_tags:
                tag_name = get_hierarchy_tag(tag, tag.name)
                data.append({"id": tag.id, "name": tag_name})
        es_attachment.update_attachment(attachment_id=attachment_id, tags=tags, app_name=app_name, model_name=model_name)
        return HttpResponse(json.dumps({"code": 1, "msg": "", "data": data}), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, "Error occurred."), content_type="json")


def files(request, id):
    files_detail = QualityClaimFiles.objects.filter(quality_claim_id=id).values("id").first()
    # customer_user_id = CompanyUser.objects.filter(user=request.user.id).values("id").first()
    customer_user = None
    # if customer_user_id is None:
    #     customer_user = False
    # else:
    #     customer_user = True

    return render(request, "attachment/files.html", {"order_detail": files_detail, "customer_user": customer_user})


def files_search(request):
    try:
        request.POST = Util.get_post_data(request)
        app_name = request.POST.get("app_name")
        show_all = request.POST.get("show_all")
        model_name = request.POST.get("model_name")
        object_id = request.POST.get("object_id")
        # start = int(request.POST["start"])
        # length = int(request.POST["length"])
        sort_col = Util.get_sort_column(request.POST)
        query = Q()
        if app_name and model_name and object_id:
            query.add(Q(quality_claim_id=object_id), query.connector)
            # if not show_all:
            #     query.add(Q(deleted=False), query.connector)
            attachment = apps.get_model(app_name, model_name)
            attachments = (
                attachment.objects.filter(query).values("id", "claim_file_name", "claim_file_path", "claim_created_date","size").order_by(sort_col)
            )
            recordsTotal = attachment.objects.filter(query).count()
            response = {
                "draw": request.POST["draw"],
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                "data": [],
            }
            for attachment in attachments:
                response["data"].append(
                    {
                        "id": attachment["id"],
                        "claim_file_name": attachment["claim_file_name"],
                        "claim_file_path": attachment["claim_file_path"],
                        "size": str(attachment["size"]) + " KB",
                        "claim_created_date": Util.get_local_time(attachment["claim_created_date"], True),
                        "uid": attachment["id"],
                        "recordsTotal": recordsTotal,
                    }
                )
            return HttpResponse(AppResponse.get(response), content_type="json")
        else:
            return HttpResponse(AppResponse.msg(0, "Error"), content_type="json")
    except Exception as e:
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, "Error occurred."), content_type="json")


def download_attachment_impersonate(app_name, model_name, uid, user_id):
    try:
        model = apps.get_model(app_name, model_name)
        attachment = model.objects.filter(uid=uid).first()
        file_path = str(settings.FILE_SERVER_PATH) + str(attachment.url)
        file_name = attachment.name
        with Impersonate():
            if os.path.exists(file_path) is False:
                return render_to_response("base/404.html")
            file_data = open(file_path, "rb")
        mime_type = mimetypes.guess_type(file_name)
        response = HttpResponse(file_data, content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % file_name

        if user_id is not None:
            return response
        if user_id is None:
            if attachment.is_public is True:
                return response
            else:
                return HttpResponse("You don't have permission to access this document.")
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def upload_and_save_impersonate(data, app_name, model_name, object_id, u_id, c_ip, code, file_name, source_doc, source_doc_):
    try:
        with transaction.atomic():
            if model_name == "Remark_Attachment":
                file_type = FileType.objects.filter(code=code, is_active=True).values("id", "name").first()
                rootFolderName = app_name + "\\" + model_name.replace("_attachment", "").lower()
                file_root_path = Attachment.get_file_rootpath(rootFolderName) + str(source_doc) + "\\"
                time = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
                file_name = os.path.splitext(file_name)
                file_name = file_name[0] + "_" + time + file_name[1]
                file_path = os.path.join(file_root_path, file_name)
                full_path = str(settings.FILE_SERVER_PATH) + file_path
                file_data = full_path.rsplit("\\", 1)
                with Impersonate():
                    parent_dir = str(file_data[0])
                    if not os.path.exists(os.path.join(parent_dir)):
                        os.makedirs(parent_dir)
                    if not os.path.isfile(full_path):
                        with open(full_path, "wb") as fp:
                            fp.write(data)
                            fp.close()
                        size = os.path.getsize(full_path) / 1024
                        upload(app_name, model_name, object_id, file_path, file_type["id"], c_ip, "-", u_id, False, source_doc_, file_name, size)
            else:
                operator = None
                if model_name == "order_attachment":
                    order = Order.objects.filter(id=object_id).values("id", "operator").first()
                    if order:
                        if order["operator"]:
                            operator = order["operator"]
                file_type = FileType.objects.filter(code=code, is_active=True).values("id", "name").first()
                query = Q()
                if source_doc_:
                    query.add(Q(name__icontains=source_doc_), query.connector)
                order_attachment = Order_Attachment.objects.filter(query, object_id=object_id, file_type__code=code).values("name", "id", "url").last()
                to_order_attachment = 0
                if order_attachment:
                    to_order_attachment = Order_Attachment.objects.filter(query, object_id=object_id, file_type__code=code).count()
                    order_attachment1 = os.path.splitext(order_attachment["name"])
                    order_attachment2 = order_attachment1[0] + "-" + str(to_order_attachment) + order_attachment1[1]
                    url_filename = order_attachment["url"].rsplit("\\", 1)
                    url_new = url_filename[0] + "\\" + order_attachment2
                    Order_Attachment.objects.filter(id=order_attachment["id"]).update(name=order_attachment2, url=url_new)
                if source_doc_:
                    file_type_name = file_type["name"].split(" ")[0] + "_" + source_doc_
                else:
                    file_type_name = file_type["name"].split(" ")[0] + "_" + source_doc
                rootFolderName = app_name + "\\" + model_name.replace("_attachment", "").lower()
                file_root_path = Attachment.get_file_rootpath(rootFolderName) + str(source_doc) + "\\"
                file_name = os.path.splitext(file_name)
                file_name = file_type_name + file_name[1]
                file_path = os.path.join(file_root_path, file_name)
                full_path = str(settings.FILE_SERVER_PATH) + file_path
                file_data = full_path.rsplit("\\", 1)
                with Impersonate():
                    parent_dir = str(file_data[0])
                    if not os.path.exists(os.path.join(parent_dir)):
                        os.makedirs(parent_dir)
                    if order_attachment:
                        url_filename_ser = str(settings.FILE_SERVER_PATH) + order_attachment["url"]
                        if os.path.isfile(url_filename_ser):
                            file_name_ = os.path.splitext(file_name)
                            file_name_ = file_type_name + "-" + str(to_order_attachment) + file_name_[1]
                            full_path_ = str(settings.FILE_SERVER_PATH) + url_filename[0] + "\\" + file_name_
                            os.rename(url_filename_ser, full_path_)
                    if not os.path.isfile(full_path):
                        with open(full_path, "wb") as fp:
                            fp.write(data)
                            fp.close()
                        size = os.path.getsize(full_path) / 1024
                        upload(app_name, model_name, object_id, file_path, file_type["id"], c_ip, "-", u_id, False, source_doc_, file_name, size)
                        log_views.insert_(app_name, model_name, [object_id], AuditAction.INSERT, u_id, c_ip, file_name + " has been Upload.", operator, None)
            return full_path
    except Exception as e:
        logging.exception(e)
        manager.create_from_exception(e)
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")


def upload_attachment_impersonate(request):
    response = {}
    try:
        with transaction.atomic():
            app_name = request.POST["app"]
            model_name = request.POST["model"]
            file_type_id = request.POST.get("file_type")
            file_code = FileType.objects.filter(id=file_type_id).values("code").first()
            object_id = int(request.POST["object_id"])
            order_number = request.POST["order_number"]
            c_ip = get_client_ip(request)
            if "userid" in request.session:
                u_id = request.session["userid"]
            else:
                u_id = request.user.id
            file_name = request.FILES["file"]
            file_name_data = file_name.read()
            file_name_ = str(file_name)
            is_not_valid = (
                str(file_name)
                .lower()
                .endswith(
                    (
                        ".bat",
                        ".exe",
                        ".cmd",
                        ".sh",
                        ".p",
                        ".cgi",
                        ".386",
                        ".dll",
                        ".com",
                        ".torrent",
                        ".js",
                        ".app",
                        ".jar",
                        ".pif",
                        ".vb",
                        ".vbscript",
                        ".wsf",
                        ".asp",
                        ".cer",
                        ".csr",
                        ".jsp",
                        ".drv",
                        ".sys",
                        ".ade",
                        ".adp",
                        ".bas",
                        ".chm",
                        ".cpl",
                        ".crt",
                        ".csh",
                        ".fxp",
                        ".hlp",
                        ".hta",
                        ".inf",
                        ".ins",
                        ".isp",
                        ".jse",
                        ".htaccess",
                        ".htpasswd",
                        ".ksh",
                        ".lnk",
                        ".mdb",
                        ".mde",
                        ".mdt",
                        ".mdw",
                        ".msc",
                        ".msi",
                        ".msp",
                        ".mst",
                        ".ops",
                        ".pcd",
                        ".prg",
                        ".reg",
                        ".scr",
                        ".sct",
                        ".shb",
                        ".shs",
                        ".url",
                        ".vbe",
                        ".vbs",
                        ".wsc",
                        ".wsf",
                        ".wsh",
                        ".php",
                        ".php1",
                        ".php2",
                        ".php3",
                        ".php4",
                        ".php5",
                    )
                )
            )
            if is_not_valid:
                return HttpResponse(AppResponse.msg(0, "This file type is not allowed to upload."), content_type="json")
            Order_Attachment.objects.filter(object_id=object_id, file_type__code=file_code["code"]).update(deleted=True)
            upload_and_save_impersonate(file_name_data, app_name, model_name, object_id, request.user.id, c_ip, file_code["code"], file_name_, order_number, "")
            response["code"] = 1
            response["msg"] = "File uploaded."
    except Exception as e:
        response["code"] = 0
        response["msg"] = str(e)
        manager.create_from_exception(e)
        logging.exception("Something went wrong.")
        return HttpResponse(AppResponse.msg(0, str(e)), content_type="json")
    return HttpResponse(AppResponse.get(response), content_type="json")

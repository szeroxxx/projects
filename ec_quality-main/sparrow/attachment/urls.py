from django.conf.urls import url

from . import views

app_name = "attachment"
urlpatterns = [
    url(r"^get_attachments", views.get_attachments, name="get_attachments"),
    url(r"^upload_attachment_impersonate", views.upload_attachment_impersonate, name="upload_attachment_impersonate"),
    url(r"^upload_attachment", views.upload_attachment, name="upload_attachment"),
    url(r"^del_attachment", views.delete_attachment, name="delete_attachment"),
    url(r"^dwn_attachment", views.download_attachment, name="attachment_download"),
    url(r"^dialog_template/$", views.dialog_template, name="dialog_template"),
    url(r"^attachment_change_access/$", views.attachment_change_access, name="attachment_change_access"),
    url(r"^attachment_properties/$", views.attachment_properties, name="attachment_properties"),
    url(r"^documents$", views.documents, name="documents"),
    url(r"^document/([^/]+)/(\d+)/$", views.document, name="document"),
    url(r"^document_save/$", views.document_save, name="document_save"),
    url(r"^tags/$", views.tags, name="tags"),
    url(r"^tag/$", views.tag, name="tag_add"),
    url(r"^tag_search/$", views.tag_search, name="tag_search"),
    url(r"^tag_del/$", views.tag_del, name="tag_del"),
    url(r"^tag/(\d+)/$", views.tag, name="tag_edit"),
    url(r"^save_doc_tag/$", views.save_doc_tag, name="save_doc_tag"),
    url(r"^check_tag_use/$", views.check_tag_use, name="check_tag_use"),
    url(r"^files_search/$", views.files_search, name="check_tag_use"),
    url(r"^files/(\d+)/$", views.files, name="files"),
]

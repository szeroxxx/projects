from django.conf.urls import url

from . import views

app_name = "attachment"
urlpatterns = [
    url(r"^dwn_attachment", views.download_attachment, name="attachment_download"),
    url(r"^get_doc", views.get_document, name="get_doc"),
    
]

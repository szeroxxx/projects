from django.conf.urls import url

from . import views

app_name = 'baseimport'
urlpatterns = [
    url(r'^load_import_template/([^/]+)/$', views.load_import_template, name='load_import_template'),
    url(r'^generate_file_data/$', views.generate_file_data, name='generate_file_data'),
    url(r'^export_sample_product/(\d+)/$', views.export_sample_product, name='export_sample_product')
]
from django.conf.urls import url
from django.urls import path

from . import common_view, customers_view, inquiries_view, orders_view, views

urlpatterns = [
    url(r"^customers/$", customers_view.customers, name="views_customers"),
    url(r"^customers_search/$", customers_view.customers_search, name="views_customers_search"),
    url(r"^validate_customer_login/$", common_view.validate_customer_login, name="validate_customer_login"),
    url(r"^validate_customer_login_modal/$", common_view.validate_customer_login_modal, name="validate_customer_login_modal"),
    url(r"^customer_login/([^/]+)/([^/]+)/(\d+)/(\d+)/$", common_view.launch_customer_login, name="views_customer_login"),
    url(r"^customer/([^/]+)/(\d+)/([^/]+)/([^/]+)/$", customers_view.get_customer, name="get_customer"),
    url(r"^customer_addresses/(\d+)/$", customers_view.get_customer_addresses, name="get_customer_addresses"),
    url(r"^customer_users/(\d+)/$", customers_view.get_customer_users, name="get_customer_users"),
    # url(r"^customer_activities/(\d+)/$", customers_view.get_customer_activities, name="get_customer_activities"),
    url(r"^get_customer_address/$", customers_view.get_customer_address, name="get_customer_address"),
    url(r"^save_customer_address/$", customers_view.save_customer_address, name="save_customer_address"),
    url(r"^export_customers/$", customers_view.export_customers, name="export_customers"),
    url(r"^orders/$", orders_view.orders, name="views_orders"),
    url(r"^orders_search/$", orders_view.orders_search, name="views_orders_search"),
    url(r"^export_orders/$", orders_view.export_orders, name="export_orders"),
    url(r"^get_ec_doc/([^/]+)/([^/]+)/$", common_view.get_ec_doc, name="get_ec_doc"),
    url(r"^get_ec_doc_inq/([^/]+)/([^/]+)/$", common_view.get_ec_doc_inq, name="get_ec_doc_inq"),
    url(r"^get_ec_customer_inv_doc/([^/]+)/([^/]+)/([^/]+)/$", common_view.get_ec_customer_inv_doc, name="get_ec_customer_inv_doc"),
    url(r"^pcbvis/([^/]+)/$", common_view.pcbvis, name="pcbvis"),
    url(r"^pcbavis/([^/]+)/$", common_view.pcbavis, name="pcbavis"),
    url(r"^inquiries/$", inquiries_view.inquiries, name="views_inquiries"),
    url(r"^inquiries_search/$", inquiries_view.inquiries_search, name="views_inquiries_search"),
    url(r"^export_inquiries/$", inquiries_view.export_inquiries, name="export_inquiries"),
    url(r"^get_cust_user_view/$", customers_view.get_cust_user_view, name="get_cust_user_view"),
    url(r"^save_customer_user/$", customers_view.save_customer_user, name="save_customer_user"),
    url(r"^save_customer_data/$", customers_view.save_customer_data, name="save_customer_data"),
    url(r"^new_customers/$", views.new_customers, name="new_customers"),
    url(r"^new_customers_search/$", views.new_customers_search, name="new_customers_search"),
    url(r"^get_call_reports/(\d+)/$", customers_view.get_call_reports, name="get_call_reports"),
    url(r"^survey_report/$", customers_view.survey_report, name="survey_report"),
    url(r"^survey_report/(\d+)/(\d+)/([^/]+)/([^/]+)/$", customers_view.survey_report, name="survey_report"),
    url(r"^public_survey_report/(\d+)/(\d+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)/$", customers_view.public_survey_report, name="public_survey_report"),
    url(r"^save_survey_report/([^/]+)/$", customers_view.save_survey_report, name="save_survey_report"),
    url(r"^all_call_reports/$", customers_view.all_call_reports, name="all_call_reports"),
    url(r"^all_call_reports_search/$", customers_view.all_call_reports_search, name="all_call_reports_search"),
    url(r"^update_included_steam/$", views.update_included_steam, name="update_included_steam"),
    url(r"^first_deliveries/$", views.first_deliveries, name="first_deliveries"),
    url(r"^first_deliveries_search/$", views.first_deliveries_search, name="first_deliveries_search"),
    url(r"^get_delivery_note/([^/]+)/$", views.get_delivery_note, name="get_delivery_note"),
    url(r"^create_task/$", views.create_task, name="create_task"),
    url(r"printing_needs/$", customers_view.printing_needs,name="printing_needs"),
    url(r"printing_need_search/$", customers_view.printing_need_search,name="printing_need_search"),

]
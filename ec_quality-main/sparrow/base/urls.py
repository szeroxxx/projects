from django.conf.urls import url

from base import lookups as lookups_view
from base import pagers as pagers_view
from base import search_view

from . import scheduler_view, views

app_name = "base"
urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^dashboard/$", views.dashboard, name="dashboard"),
    url(r"^iframe_index/$", views.iframe_index, name="iframe_index"),
    url(r"^vcdb/$", views.open_iframe_index, name="vcdb"),
    # url(r"^release_note/$", views.release_note, name="release_note"),
    # url(r"^release_note/(\d+)/$", views.release_note, name="release_note"),
    # url(r"^search_release_notes/$", views.search_release_notes, name="search_release_notes"),
    # url(r"^save_release_note/$", views.save_release_note, name="save_release_note"),
    # url(r"^edit_release_note/$", views.edit_release_note, name="edit_release_note"),
    # url(r"^delete_release_note/$", views.delete_release_note, name="delete_release_note"),
    # url(r"^upload_release_note_media/$", views.upload_release_note_media, name="upload_release_note_media"),
    url(r"^lookups/([^/]+)/$", lookups_view.lookups, name="lookups"),
    url(r"^pagers/$", pagers_view.pagers, name="pagers"),
    url(r"^get_app_data/$", views.get_app_data, name="get_app_data"),
    url(r"^sysparameters/$", views.sysparameters, name="sysparameters"),
    url(r"^sysparameter_search/$", views.sysparameter_search, name="sysparameter_search"),
    url(r"^sysparameter/$", views.sysparameter, name="sysparameter_add"),
    url(r"^sysparameter/(\d+)/$", views.sysparameter, name="sysparameter_edit"),
    url(r"^sysparameter_del/$", views.sysparameter_del, name="sysparameter_delete"),
    url(r"^add_page_favorite/$", views.add_page_favorite, name="add_page_favorite"),
    url(r"^delete_page_favorite/$", views.delete_page_favorite, name="delete_page_favorite"),
    url(r"^currencyrates/$", views.currencyrates, name="currencyrates"),
    url(r"^currencyrate_search/$", views.currencyrate_search, name="currencyrate_search"),
    url(r"^currencyrate/$", views.currencyrate, name="currencyrate_add"),
    url(r"^get_currencyrate/$", views.get_currencyrate, name="get_currencyrate"),
    url(r"^del_currencyrates/$", views.del_currencyrates, name="del_currencyrates"),
    url(r"^create_remark/$", views.create_remark_view, name="create_remark"),
    url(r"^get_remarks/$", views.get_remarks, name="get_remarks"),
    url(r"^delete_remark/$", views.delete_remark, name="delete_remark"),
    url(r"^edit_remark/$", views.edit_remark, name="edit_remark"),
    url(r"^check_edit_remark_perm/$", views.check_edit_remark_perm, name="check_edit_remark_perm"),
    url(r"^check_subscription/$", views.check_subscription, name="check_subscription"),
    url(r"^subscribe_item/$", views.subscribe_item, name="subscribe_item"),
    url(r"^unsubscribe_item/$", views.unsubscribe_item, name="unsubscribe_item"),
    url(r"^add_variable_to_context/$", views.add_variable_to_context, name="add_variable_to_context"),
    url(r"^set_col_order/$", views.set_col_order, name="set_col_order"),
    url(r"^get_all_user_list/$", views.get_all_user_list, name="get_all_user_list"),
    url(r"^exportdata/$", views.export_db_data, name="exportdata"),
    url(r"^search/$", search_view.search, name="app_search"),
    # === Task Schedular ====
    url(r"^task_scheduler/$", scheduler_view.task_scheduler, name="task_scheduler"),
    url(r"^task_schedulers/$", scheduler_view.task_schedulers, name="task_schedulers"),
    url(r"^task_schedulers_search/$", scheduler_view.task_schedulers_search, name="task_schedulers_search"),
    url(r"^save_task_schedule/$", scheduler_view.save_task_schedule, name="save_task_schedule"),
    url(r"^delete_task_scheduler/$", scheduler_view.delete_task_scheduler, name="delete_task_scheduler"),
    url(r"^run_scheduler/$", scheduler_view.run_scheduler, name="run_scheduler"),
    url(r"^change_status/$", scheduler_view.change_status, name="change_status"),
    # == Scheduler Format
    url(r"^sheduler_format/([^/]+)/$", scheduler_view.sheduler_format, name="sheduler_format"),
    url(r"^add_exchange_rate/$", views.add_exchange_rate, name="add_exchange_rate"),
    url(r"^start_schedulers/$", scheduler_view.start_schedulers, name="start_schedulers"),
    url(r"^insert_system_scheduler/$", scheduler_view.insert_system_scheduler, name="insert_system_scheduler"),
    url(r"^settings/$", views.settings, name="settings"),
    url(r"^admin_utilities/$", views.admin_utilities, name="admin_utilities"),
    # url(r"^app_view_redirect/$", views.app_view_redirect, name="app_view_redirect"),
    # url(r"^generate_token/$", views.generate_token, name="generate_token"),
    # url(r"^upload_wysiwyg_media/$", views.upload_wysiwyg_media, name="upload_wysiwyg_media"),
    # url(r"^delete_wysiwyg_media/$", views.delete_wysiwyg_media, name="delete_wysiwyg_media"),
]

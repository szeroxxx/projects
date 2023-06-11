from django.conf.urls import url

from task import views


app_name = 'task'
urlpatterns = [
    url(r'^get_tasks/([^/]+)/([^/]+)/(\d+)/$', views.get_tasks, name='get_tasks'),
    url(r'^tasks/$', views.tasks, name='tasks'),
    url(r'^tasks/([^/]+)/$', views.tasks, name='tasks'),
    url(r'^task/$', views.task, name='task'),
    url(r'^save_task/$', views.save_task, name='save_task'),
    url(r'^task_delete/$', views.task_delete, name='task_delete'),
    url(r'^get_task_calendar/$', views.get_task_calendar, name='get_task_calendar'),
    url(r'^change_event_date/$', views.change_event_date, name = 'change_event_date'),
    url(r'^task_reminder/([^/]+)/$', views.task_reminder, name = 'task_reminder'),
    url(r'^task_kanban_data/$', views.task_kanban_data, name='task_kanban_data'),
    url(r'^change_task_status/$', views.change_task_status, name='change_task_status')
]
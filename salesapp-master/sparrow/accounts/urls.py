from django.conf.urls import url

from . import passwrecovery_view, users_view, views

app_name = 'accounts'
urlpatterns = [
    url(r'^signin', views.signin, name='signin'),
    url(r'^signout', views.signout, name='signout'),
    url(r'^authcheck', views.authcheck, name='authcheck'),
    url(r'^passwrecv/$', passwrecovery_view.passwrecovery, name='passwrecv'),
    url(r'^resetpwd/([^/]+)', passwrecovery_view.resetpwd, name='resetpwd'),
    url(r'^profile', views.profile, name='profile'),
    url(r'^save_profile/$', views.save_profile, name='save_profile'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^users/$', users_view.users, name="views_users"),
    url(r'^users_search/', users_view.users_search, name='users_search'),
    url(r'^user/$', users_view.user, name='user_add'),
    url(r'^user/(\d+)/$', users_view.user, name='user_edit'),
    url(r'^users_del/$', users_view.users_del, name='users_del'),
    url(r'^get_background_images/$', views.get_background_images, name='get_background_images'),
    url(r'^roles/$', views.roles, name='roles'),
    url(r'^roles_search/$', views.roles_search, name='roles_search'),
    url(r'^role/$', views.role, name='role_add'),
    url(r'^role/(\d+)/$', views.role, name='role_edit'),
    url(r'^role_del/$', views.role_del, name='role_del'),
    url(r'^send_notification_token/$', views.send_notification_token, name='send_notification_token'),
    url(r'^notification_authentication/$', views.notification_authentication, name='notification_authentication'),
    url(r'^notification_delete/$', views.notification_delete, name='notification_delete'),
    url(r'^company/$', views.company, name="company"),
    url(r'^verify2FactorAuth', views.tfa_page, name='tfa_page'),
    url(r'^two_fact_auth', views.two_fact_auth, name='two_fact_auth'),
    url(r'^save_user_role', views.save_user_role, name='save_user_role'),
]

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from customer.views import (AddressView, CodeView, ContactView, CountryView,
                            CustomerView, ECUserView, edit_profile, customer_login)

router = DefaultRouter(trailing_slash=True)

router.register(r"customer",CustomerView,basename="customer")
router.register(r"contact",ContactView,basename="contact")
router.register(r"user",ECUserView,basename="user")
router.register(r"address",AddressView,basename="address")
router.register(r"code",CodeView,basename="code")
router.register(r"country",CountryView,basename="country")


urlpatterns = [
    url(r"edit_profile/$", edit_profile, name="edit_profile"),
    url(r"customer_login/$", customer_login, name="customer_login"),
    ]
urlpatterns += router.urls

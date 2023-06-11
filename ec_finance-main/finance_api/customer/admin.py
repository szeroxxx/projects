
from django.contrib import admin

# # Register your models here.
from customer.models import Address, Contact, Country, Customer, State, User

admin.site.register(Customer)
admin.site.register(State)
admin.site.register(User)
admin.site.register(Contact)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display =["name","code"]
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["customer","address_type"]

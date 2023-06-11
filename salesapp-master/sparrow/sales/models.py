from django.contrib.postgres.fields import JSONField
from django.db import models
from datetime import datetime, time

class ECModel(models.Model):
    rid = models.IntegerField(null=False)
    data = JSONField()

    class Meta:
        abstract = True
    
    def clear_and_insert_data(self, entity, objects):
        if len(objects) > 0:
            entity.objects.all().delete()
            entity.objects.bulk_create(objects)

    def rebuild_data(self, data):
        pass

class Customers(ECModel):
    
    def rebuild_data(self, data):
        customers = []
        for cust in data:
            if cust['registration_date']:
                cust['registration_date'] = datetime.strptime(cust['registration_date'], '%d/%m/%Y %I:%M %p').isoformat()

            customer = Customers(rid = 0, data = cust)
            customers.append(customer)

        super().clear_and_insert_data(Customers, customers)

class Orders(ECModel):
    
    def rebuild_data(self, data):
        orders = []
        for ord_data in data:
            if ord_data['order_date']:
                ord_data['order_date'] = datetime.strptime(ord_data['order_date'], '%d/%m/%Y %I:%M %p').isoformat()

            if ord_data['first_orderdate']:
                ord_data['first_orderdate'] = datetime.strptime(ord_data['first_orderdate'], '%d/%m/%Y %I:%M %p').isoformat()

            order = Orders(rid = 0, data = ord_data)
            orders.append(order)

        super().clear_and_insert_data(Orders, orders)

class Inquiries(ECModel):
    
    def rebuild_data(self, data):
        inquiries = []
        for inq_data in data:
            if inq_data['inquiry_date']:
                inq_data['inquiry_date'] = datetime.strptime(inq_data['inquiry_date'], '%d/%m/%Y %I:%M %p').isoformat()

            inquiry = Inquiries(rid = 0, data = inq_data)
            inquiries.append(inquiry)

        super().clear_and_insert_data(Inquiries, inquiries)
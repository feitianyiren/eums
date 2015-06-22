from django.db import models
from eums.models import SalesOrder
from eums.models.order_item import OrderItem


class SalesOrderItem(OrderItem):
    sales_order = models.ForeignKey(SalesOrder)
    net_price = models.DecimalField(max_digits=20, decimal_places=4)
    net_value = models.DecimalField(max_digits=20, decimal_places=4)
    issue_date = models.DateField()
    delivery_date = models.DateField(null=True)
    description = models.CharField(max_length=255)

    class Meta:
        app_label = 'eums'
        unique_together = ('item', 'item_number', 'sales_order')

    def purchase_order_item(self):
        return self.purchaseorderitem_set.all().first()

    def __unicode__(self):
        return '%s' % self.description


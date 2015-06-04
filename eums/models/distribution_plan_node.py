from django.conf import settings
from django.db import models
import requests

from eums.models import DistributionPlan, Consignee


class DistributionPlanNode(models.Model):
    IMPLEMENTING_PARTNER = 'IMPLEMENTING_PARTNER'
    MIDDLE_MAN = 'MIDDLE_MAN'
    END_USER = 'END_USER'
    DIRECT_DELIVERY = 'DIRECT_DELIVERY'
    THROUGH_WAREHOUSE = 'WAREHOUSE'

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    distribution_plan = models.ForeignKey(DistributionPlan)
    location = models.CharField(max_length=255)
    mode_of_delivery = models.CharField(max_length=255, choices=(
        (DIRECT_DELIVERY, "Direct Delivery"), (THROUGH_WAREHOUSE, 'Warehouse')))
    consignee = models.ForeignKey(Consignee)
    contact_person_id = models.CharField(max_length=255)
    tree_position = models.CharField(max_length=255, choices=((MIDDLE_MAN, 'Middleman'), (END_USER, 'End User'),
                                                              (IMPLEMENTING_PARTNER, 'Implementing Partner')))
    item = models.ForeignKey('SalesOrderItem')
    targeted_quantity = models.IntegerField()
    track = models.BooleanField(default=False)
    planned_distribution_date = models.DateField(null=False)
    remark = models.TextField(blank=True, null=True)

    def build_contact(self):
        response = requests.get("%s%s/" % (settings.CONTACTS_SERVICE_URL, self.contact_person_id))
        result = response.json() if response.status_code is 200 else None
        return result

    def __unicode__(self):
        return "%s %s %s " % (self.consignee.name, self.tree_position, str(self.distribution_plan))

    def get_ip(self):
        if not self.parent:
            return {'id': self.id, 'location': self.location}
        else:
            return self.parent.get_ip()

    def current_run(self):
        return self.noderun_set.filter(status='scheduled').first()

    def completed_run(self):
        return self.noderun_set.filter(status='completed').first()

    def latest_run(self):
        return self.noderun_set.all().last()

    def _completed_runs(self):
        return self.noderun_set.filter(status='completed')

    def responses(self):
        return dict(map(lambda run: (run, run.answers()), self._completed_runs()))
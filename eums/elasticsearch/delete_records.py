from django.db import models
from djorm_pgarray.fields import IntegerArrayField


class DeleteRecords(models.Model):
    nodes_to_delete = IntegerArrayField(dimension=1)

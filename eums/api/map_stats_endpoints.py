from decimal import Decimal
from django.db.models import Q, Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from eums.models import DistributionPlanNode as DeliveryNode, MultipleChoiceQuestion, Flow, Runnable, Option, \
    MultipleChoiceAnswer, Run


class DistrictStats(APIView):
    def __init__(self):
        super(DistrictStats, self).__init__()
        self.end_user_flow = Flow.objects.get(for_runnable_type=Runnable.END_USER)
        self.was_product_received = MultipleChoiceQuestion.objects.get(label='productReceived', flow=self.end_user_flow)
        self.product_was_received = Option.objects.get(text='Yes', question=self.was_product_received)
        self.product_was_not_received = Option.objects.get(text='No', question=self.was_product_received)
        self.end_user_nodes = DeliveryNode.objects.filter(tree_position=DeliveryNode.END_USER, track=True)
        self.successful_delivery_answers = MultipleChoiceAnswer.objects.filter(
            question=self.was_product_received, value=self.product_was_received).filter(
            Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed)
        )
        self.unsuccessful_delivery_answers = MultipleChoiceAnswer.objects.filter(
            question=self.was_product_received, value=self.product_was_not_received).filter(
            Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed)
        )

    def number_of_successful_deliveries(self):
        return self.successful_delivery_answers.count()

    def number_of_non_response_deliveries(self):
        runs_with_answers = MultipleChoiceAnswer.objects.filter(question=self.was_product_received).values_list(
            'run_id')
        return self.end_user_nodes.exclude(run__id__in=runs_with_answers).distinct().count()

    def total_deliveries(self):
        return self.end_user_nodes.count()

    def number_of_unsuccessful_deliveries(self):
        return self.total_deliveries() - self.number_of_successful_deliveries() - self.number_of_non_response_deliveries()

    def get(self, request, *args, **kwargs):
        consignee_type = request.GET.get('consigneeType', DeliveryNode.END_USER)

        if consignee_type == DeliveryNode.END_USER:
            return Response({
                'totalNumberOfDeliveries': self.total_deliveries(),
                'numberOfSuccessfulProductDeliveries': self.number_of_successful_deliveries(),
                'percentageOfSuccessfulDeliveries': self.percent_successful_deliveries(),
                'numberOfUnsuccessfulProductDeliveries': self.number_of_unsuccessful_deliveries(),
                'percentageOfUnsuccessfulDeliveries': self.percent_unsuccessful_deliveries(),
                'numberOfNonResponseToProductReceived': self.number_of_non_response_deliveries(),
                'percentageOfNonResponseToProductReceived': self.percent_non_response_deliveries(),
                'totalValueOfDeliveries': self.total_delivery_value(),
                'totalValueOfSuccessfulDeliveries': self.total_successful_delivery_value(),
                'percentageValueOfSuccessfulDeliveries': self.percentage_value_of_successful_deliveries(),
                'totalValueOfUnsuccessfulProductDeliveries': self.total_unsuccessful_delivery_value(),
                'percentageValueOfUnsuccessfulDeliveries': self.percentage_value_of_unsuccessful_deliveries(),
                'totalValueOfNonResponseToProductReceived': self.total_value_of_non_response_deliveries(),
                'percentageValueOfNonResponseToProductReceived': self.percentage_value_of_non_response_deliveries(),
            })

    def percent_successful_deliveries(self):
        return self._percentage_of_total_deliveries(self.number_of_successful_deliveries())

    def percent_unsuccessful_deliveries(self):
        return self._percentage_of_total_deliveries(self.number_of_unsuccessful_deliveries())

    def percent_non_response_deliveries(self):
        return self._percentage_of_total_deliveries(self.number_of_non_response_deliveries())

    def _percentage_of_total_deliveries(self, quantity):
        total_deliveries = self.total_deliveries()
        percent = Decimal(quantity) / total_deliveries * 100
        return round(percent, 1)

    def total_delivery_value(self):
        return self._get_nodes_total_value(self.end_user_nodes)

    def total_successful_delivery_value(self):
        successful_delivery_runs = self.successful_delivery_answers.values_list('run_id')
        successful_nodes = self.end_user_nodes.filter(run__id__in=successful_delivery_runs)
        return self._get_nodes_total_value(successful_nodes)

    @staticmethod
    def _get_nodes_total_value(queryset):
        return queryset.aggregate(total_value=Sum('total_value'))['total_value']

    def percentage_value_of_successful_deliveries(self):
        return self._percentage_of_total_value_delivered(self.total_successful_delivery_value())

    def _percentage_of_total_value_delivered(self, quantity):
        total_delivery_value = self.total_delivery_value()
        percent = Decimal(quantity) / total_delivery_value * 100
        return round(percent, 1)

    def total_unsuccessful_delivery_value(self):
        unsuccessful_delivery_runs = self.unsuccessful_delivery_answers.values_list('run_id')
        unsuccessful_nodes = self.end_user_nodes.filter(run__id__in=unsuccessful_delivery_runs)
        return self._get_nodes_total_value(unsuccessful_nodes)

    def percentage_value_of_unsuccessful_deliveries(self):
        return self._percentage_of_total_value_delivered(self.total_unsuccessful_delivery_value())

    def total_value_of_non_response_deliveries(self):
        return self.total_delivery_value() - self.total_successful_delivery_value() - self.total_unsuccessful_delivery_value()

    def percentage_value_of_non_response_deliveries(self):
        return self._percentage_of_total_value_delivered(self.total_value_of_non_response_deliveries())

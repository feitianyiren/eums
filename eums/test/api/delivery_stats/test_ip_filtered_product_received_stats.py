from eums.models import Run, MultipleChoiceQuestion
from eums.test.api.delivery_stats.delivery_stats_test_case import DeliveryStatsTestCase
from eums.test.config import BACKEND_URL
from eums.test.factories.answer_factory import MultipleChoiceAnswerFactory
from eums.test.factories.consignee_factory import ConsigneeFactory
from eums.test.factories.delivery_factory import DeliveryFactory
from eums.test.factories.delivery_node_factory import DeliveryNodeFactory
from eums.models.distribution_plan_node import DistributionPlanNode as DeliveryNode
from eums.test.factories.purchase_order_item_factory import PurchaseOrderItemFactory
from eums.test.factories.run_factory import RunFactory

ENDPOINT_URL = BACKEND_URL + 'delivery-stats/details/'


class ProductReceivedStatsForIPTest(DeliveryStatsTestCase):
    def setUp(self):
        super(ProductReceivedStatsForIPTest, self).setUp()
        self.selected_ip = ConsigneeFactory(name='WAKISO DHO')
        self.other_ip = ConsigneeFactory()
        self.setup_responses()

    def test_check_that_other_location_data_is_present(self):
        response = self.client.get('%s?treePosition=END_USER' % ENDPOINT_URL)
        self.assertEqual(response.data.get('totalNumberOfDeliveries'), 6)

    def test_should_provide_product_received_question_stats_for_an_ip(self):
        response = self.client.get('%s?treePosition=END_USER&ip=%s' % (ENDPOINT_URL, self.selected_ip.id))
        self.assert_delivery_stats_are_filtered_for_selected_ip(response)

    def test_should_provide_only_relevant_stats_for_logged_in_ip(self):
        self.logout()
        self.log_consignee_in(self.selected_ip)
        response = self.client.get(ENDPOINT_URL)
        self.assert_delivery_stats_are_filtered_for_selected_ip(response)

    def assert_delivery_stats_are_filtered_for_selected_ip(self, response):
        self.assertEqual(response.data.get('totalNumberOfDeliveries'), 3)
        self.assertEqual(response.data.get('totalValueOfDeliveries'), 1000)
        self.assertEqual(response.data.get('numberOfSuccessfulProductDeliveries'), 1)
        self.assertEqual(response.data.get('numberOfUnsuccessfulProductDeliveries'), 1)
        self.assertEqual(response.data.get('numberOfNonResponseToProductReceived'), 1)
        self.assertEqual(response.data.get('percentageOfSuccessfulDeliveries'), 33.3)
        self.assertEqual(response.data.get('percentageOfUnsuccessfulDeliveries'), 33.3)
        self.assertEqual(response.data.get('percentageOfNonResponseToProductReceived'), 33.3)
        self.assertEqual(response.data.get('totalValueOfSuccessfulDeliveries'), 100)
        self.assertEqual(response.data.get('totalValueOfUnsuccessfulProductDeliveries'), 300)
        self.assertEqual(response.data.get('totalValueOfNonResponseToProductReceived'), 600)
        self.assertEqual(response.data.get('percentageValueOfSuccessfulDeliveries'), 10.0)
        self.assertEqual(response.data.get('percentageValueOfUnsuccessfulDeliveries'), 30.0)
        self.assertEqual(response.data.get('percentageValueOfNonResponseToProductReceived'), 60.0)

    def setup_responses(self):
        DeliveryNode.objects.all().delete()
        MultipleChoiceQuestion.objects.all().delete()
        from eums.fixtures.end_user_questions import seed_questions
        questions, options = seed_questions()
        po_item = PurchaseOrderItemFactory(quantity=100, value=1000)

        selected_ip_root_node = DeliveryNodeFactory(
            quantity=1000,
            tree_position=DeliveryNode.IMPLEMENTING_PARTNER,
            consignee=self.selected_ip,
            distribution_plan=DeliveryFactory(track=True),
            track=True
        )
        end_user_node_one = DeliveryNodeFactory(
            tree_position=DeliveryNode.END_USER,
            track=True, parents=[(selected_ip_root_node, 10)],
            item=po_item,
        )
        MultipleChoiceAnswerFactory(
            run=RunFactory(runnable=end_user_node_one, status=Run.STATUS.scheduled),
            question=questions['WAS_PRODUCT_RECEIVED'],
            value=options['PRODUCT_WAS_RECEIVED']
        )

        end_user_node_two = DeliveryNodeFactory(
            tree_position=DeliveryNode.END_USER,
            track=True,
            parents=[(selected_ip_root_node, 30)],
            item=po_item,
        )
        MultipleChoiceAnswerFactory(
            run=RunFactory(runnable=end_user_node_two, status=Run.STATUS.scheduled),
            question=questions['WAS_PRODUCT_RECEIVED'],
            value=options['PRODUCT_WAS_NOT_RECEIVED']
        )

        non_response_node_one = DeliveryNodeFactory(
            tree_position=DeliveryNode.END_USER,
            track=True,
            parents=[(selected_ip_root_node, 60)],
            item=po_item,
        )
        RunFactory(runnable=non_response_node_one, status=Run.STATUS.scheduled)

        other_ip_root_node = DeliveryNodeFactory(
            quantity=1000,
            tree_position=DeliveryNode.IMPLEMENTING_PARTNER,
            consignee=self.other_ip,
            distribution_plan=DeliveryFactory(track=True),
            track=True
        )
        end_user_node_three = DeliveryNodeFactory(
            tree_position=DeliveryNode.END_USER,
            track=True,
            parents=[(other_ip_root_node, 10)],
            item=po_item,
        )
        MultipleChoiceAnswerFactory(
            run=RunFactory(runnable=end_user_node_three, status=Run.STATUS.scheduled),
            question=questions['WAS_PRODUCT_RECEIVED'],
            value=options['PRODUCT_WAS_RECEIVED']
        )

        end_user_node_four = DeliveryNodeFactory(
            tree_position=DeliveryNode.END_USER,
            track=True,
            parents=[(other_ip_root_node, 30)],
            item=po_item,
        )
        MultipleChoiceAnswerFactory(
            run=RunFactory(runnable=end_user_node_four, status=Run.STATUS.scheduled),
            question=questions['WAS_PRODUCT_RECEIVED'],
            value=options['PRODUCT_WAS_NOT_RECEIVED']
        )

        non_response_node_two = DeliveryNodeFactory(
            tree_position=DeliveryNode.END_USER,
            track=True,
            parents=[(other_ip_root_node, 60)],
            item=po_item,
        )
        RunFactory(runnable=non_response_node_two, status=Run.STATUS.scheduled)

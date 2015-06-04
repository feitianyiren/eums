from unittest import TestCase

from django.conf import settings
from eums.test.factories.node_run_factory import NodeRunFactory
from mock import patch

from eums.models import DistributionPlanNode, NodeRun

from eums.rapid_pro.fake_response import FakeResponse
from eums.test.factories.answer_factory import MultipleChoiceAnswerFactory, NumericAnswerFactory
from eums.test.factories.distribution_plan_node_factory import DistributionPlanNodeFactory as NodeFactory, \
    DistributionPlanNodeFactory
from eums.test.factories.item_factory import ItemFactory
from eums.test.factories.option_factory import OptionFactory
from eums.test.factories.question_factory import NumericQuestionFactory, MultipleChoiceQuestionFactory
from eums.test.factories.sales_order_item_factory import SalesOrderItemFactory


class DistributionPlanNodeTest(TestCase):
    def setUp(self):
        self.node = DistributionPlanNodeFactory()

    def test_should_have_all_expected_fields(self):
        fields = self.node._meta._name_map

        self.assertEqual(len(self.node._meta.fields), 13)
        for field in ['parent', 'distribution_plan', 'consignee', 'tree_position', 'location', 'mode_of_delivery',
                      'contact_person_id', 'item_id', 'targeted_quantity', 'planned_distribution_date', 'remark',
                      'id', 'track']:
            self.assertIn(field, fields)

    @patch('requests.get')
    def test_should_build_contact_with_details_from_contacts_service(self, mock_get):
        contact_id = '54335c56b3ae9d92f038abb0'
        fake_contact_json = {'firstName': "test", 'lastName': "user1", 'phone': "+256 782 443439", '_id': contact_id}
        fake_response = FakeResponse(fake_contact_json, 200)
        node = NodeFactory(contact_person_id=contact_id)
        mock_get.return_value = fake_response

        contact = node.build_contact()

        self.assertEqual(contact, fake_contact_json)
        mock_get.assert_called_with("%s%s/" % (settings.CONTACTS_SERVICE_URL, contact_id))

    def test_gets_all_response_for_node_consignee(self):
        multichoice_question = MultipleChoiceQuestionFactory(label='productReceived')
        yes_option = OptionFactory(text='Yes', question=multichoice_question)
        no_option = OptionFactory(text='No', question=multichoice_question)

        sugar = ItemFactory(description='Sugar')
        salt = ItemFactory(description='Salt')

        numeric_question = NumericQuestionFactory(label='AmountReceived')
        item = SalesOrderItemFactory(item=salt, description='10 bags of salt')

        salt_node = DistributionPlanNodeFactory(targeted_quantity=100,
                                                item=item)
        node_run = NodeRunFactory(node=salt_node, status='completed')

        sugar_item = SalesOrderItemFactory(item=sugar, description='10 bags of sugar')
        sugar_node = DistributionPlanNodeFactory(targeted_quantity=100,
                                                     item=sugar_item)
        sugar_node_run = NodeRunFactory(node=sugar_node, status='completed')

        multiple_answer_one = MultipleChoiceAnswerFactory(node_run=node_run, question=multichoice_question,
                                                          value=yes_option)
        numeric_answer_one = NumericAnswerFactory(node_run=node_run, value=80, question=numeric_question)

        multiple_answer_two = MultipleChoiceAnswerFactory(node_run=sugar_node_run,
                                                          question=multichoice_question, value=no_option)
        numeric_answer_two = NumericAnswerFactory(node_run=sugar_node_run, value=80,
                                                  question=numeric_question)
        salt_node_responses = salt_node.responses()
        sugar_node_responses = sugar_node.responses()

        self.assertIn(multiple_answer_one, salt_node_responses[node_run])
        self.assertIn(numeric_answer_one, salt_node_responses[node_run])

        self.assertIn(multiple_answer_two, sugar_node_responses[sugar_node_run])
        self.assertIn(numeric_answer_two, sugar_node_responses[sugar_node_run])

    def test_should_get_node_run_with_status_scheduled(self):
        node_run = NodeRunFactory(node=self.node,
                                  status=NodeRun.STATUS.scheduled)
        self.assertEqual(self.node.current_run(), node_run)

    def test_should_not_get_node_run_with_status_completed(self):
        NodeRunFactory(node=self.node, status=NodeRun.STATUS.completed)
        self.assertEqual(self.node.current_run(), None)

    def test_should_not_get_node_run_with_status_expired(self):
        NodeRunFactory(node=self.node, status=NodeRun.STATUS.expired)
        self.assertEqual(self.node.current_run(), None)

    def test_should_not_get_node_run_with_status_cancelled(self):
        NodeRunFactory(node=self.node, status=NodeRun.STATUS.cancelled)
        self.assertEqual(self.node.current_run(), None)

    def test_should_get_the_completed_node_run(self):
        self.assertIsNone(self.node.completed_run())

        node_run = NodeRunFactory(node=self.node,
                                  status=NodeRun.STATUS.completed)

        self.assertEqual(self.node.completed_run(), node_run)

    def test_should_get_latest_run(self):
        first_run = NodeRunFactory(node=self.node)

        self.assertEqual(self.node.latest_run(), first_run)

        second_run = NodeRunFactory(node=self.node)

        self.assertEqual(self.node.latest_run(), second_run)


from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from mock import MagicMock
from eums.models import Flow, Consignee, DistributionPlanNode
from eums.test.api.authorization.authenticated_api_test_case import AuthenticatedAPITestCase
from eums.test.config import BACKEND_URL
from eums.test.factories.answer_factory import MultipleChoiceAnswerFactory, TextAnswerFactory, NumericAnswerFactory
from eums.test.factories.consignee_factory import ConsigneeFactory
from eums.test.factories.delivery_factory import DeliveryFactory
from eums.test.factories.delivery_node_factory import DeliveryNodeFactory
from eums.test.factories.flow_factory import FlowFactory
from eums.test.factories.item_factory import ItemFactory
from eums.test.factories.option_factory import OptionFactory
from eums.test.factories.programme_factory import ProgrammeFactory
from eums.test.factories.purchase_order_factory import PurchaseOrderFactory
from eums.test.factories.purchase_order_item_factory import PurchaseOrderItemFactory
from eums.test.factories.question_factory import MultipleChoiceQuestionFactory, TextQuestionFactory, \
    NumericQuestionFactory
from eums.test.factories.release_order_factory import ReleaseOrderFactory
from eums.test.factories.release_order_item_factory import ReleaseOrderItemFactory
from eums.test.factories.run_factory import RunFactory

ENDPOINT_URL = BACKEND_URL + 'item-feedback-report/'


class ItemFeedbackReportEndPointTest(AuthenticatedAPITestCase):
    def test_returns_200_when_admin(self):
        self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL)

        self.assertEqual(response.status_code, 200)

    def test_should_return_items_and_all_their_answers(self):
        node_one, purchase_order_item, _, node_two, _, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?field=answers.amountReceived.value&order=desc',
                                   content_type='application/json')
        results = response.data['results']

        self.assertEqual(len(response.data['results']), 8)
        self.assertFieldExists({'item_description': purchase_order_item.item.description}, results)
        self.assertFieldExists({'programme': {'id': node_one.programme.id, 'name': node_one.programme.name}}, results)
        self.assertFieldExists({'consignee': node_one.consignee.name}, results)
        self.assertFieldExists({'implementing_partner': node_one.ip.name}, results)
        self.assertFieldExists({'contact_person_id': node_one.contact_person_id}, results)
        self.assertFieldExists({'order_number': purchase_order_item.purchase_order.order_number}, results)
        self.assertFieldExists({'quantity_shipped': node_one.quantity_in()}, results)
        self.assertFieldExists({'value': node_one.total_value}, results)
        self.assertFieldExists({'tree_position': node_one.tree_position}, results)
        self.assertFieldExists({'additional_remarks': node_one.additional_remarks}, results)
        self.assertGreaterEqual(len(results[0]['answers']), 3)
        self.assertEqual(results[0]['answers'].get('amountReceived').get('remark'), 'Some remark 2')

    def test_should_return_assigned_to_self_items_and_all_their_answers(self):
        node_one, purchase_order_item, _, node_two, _, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?field=answers.amountReceived.value&order=desc',
                                   content_type='application/json')
        results = response.data['results']

        self.assertEqual(len(response.data['results']), 8)
        self.assertFieldExists({'item_description': purchase_order_item.item.description}, results)
        self.assertFieldExists(
                {'programme': {'id': assign_to_self_node.programme.id, 'name': assign_to_self_node.programme.name}},
                results)
        self.assertFieldExists({'consignee': assign_to_self_node.consignee.name}, results)
        self.assertFieldExists({'implementing_partner': assign_to_self_node.ip.name}, results)
        self.assertFieldExists({'contact_person_id': assign_to_self_node.contact_person_id}, results)
        self.assertFieldExists({'order_number': purchase_order_item.purchase_order.order_number}, results)
        self.assertFieldExists({'quantity_shipped': assign_to_self_node.quantity_in()}, results)
        self.assertFieldExists({'value': assign_to_self_node.total_value}, results)
        self.assertFieldExists({'tree_position': assign_to_self_node.tree_position}, results)
        self.assertFieldExists({'additional_remarks': assign_to_self_node.additional_remarks}, results)

    def test_should_return_paginated_items_and_all_their_answers(self):
        total_number_of_items = 20
        self.setup_multiple_nodes_with_answers(total_number_of_items)

        response = self.client.get(ENDPOINT_URL, content_type='application/json')

        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('/api/item-feedback-report/?page=2', response.data['next'])
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['count'], total_number_of_items)
        self.assertEqual(response.data['pageSize'], 10)

        response = self.client.get(ENDPOINT_URL + '?page=2', content_type='application/json')

        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['next'], None)
        self.assertIn('/api/item-feedback-report/?page=1', response.data['previous'])
        self.assertEqual(response.data['count'], total_number_of_items)
        self.assertEqual(response.data['pageSize'], 10)

    def test_should_filter_answers_by_item_description(self):
        node_one, _, release_order_item, node_two, _, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?item_description=baba', content_type='application/json')

        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertDictContainsSubset({'item_description': release_order_item.item.description}, results[0])

    def test_should_filter_answers_by_location(self):
        node_one, _, release_order_item, node_two, _, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?location=Fort portal', content_type='application/json')

        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertDictContainsSubset({'location': 'Fort portal'}, results[0])

    def test_should_filter_answers_by_programme(self):
        node_one, _, _, node_two, _, _, assign_to_self_node = self.setup_nodes_with_answers()
        response = self.client.get(ENDPOINT_URL + '?programme_id=%s' % node_one.programme.id,
                                   content_type='application/json')

        results = response.data['results']
        self.assertEqual(len(results), 4)
        self.assertDictContainsSubset({'programme': {'id': node_one.programme.id, 'name': node_one.programme.name}},
                                      results[0])

    def test_should_filter_answers_by_implementing_partner(self):
        node_one, _, _, node_two, _, ip, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?ip_id=%s' % ip.id,
                                   content_type='application/json')

        results = response.data['results']
        self.assertEqual(len(results), 8)

    def test_should_filter_answers_by_purchase_order_number(self):
        node_one, _, _, node_two, _, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?po_waybill=329', content_type='application/json')

        results = response.data['results']
        self.assertEqual(len(results), 6)
        self.assertDictContainsSubset({'order_number': node_one.item.number()}, results[0])

    def test_should_filter_answers_by_waybill(self):
        node_one, _, _, _, ip_node_two, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?po_waybill=5540', content_type='application/json')

        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertDictContainsSubset({'order_number': ip_node_two.item.number()}, results[0])

    def test_should_filter_answers_by_tree_position_implementing_partner(self):
        node_one, _, _, _, ip_node_two, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?tree_position=IMPLEMENTING_PARTNER',
                                   content_type='application/json')

        results = response.data['results']
        self.assertEqual(len(results), 4)
        self.assertDictContainsSubset({'consignee': ip_node_two.consignee.name}, results[0])

    def test_should_filter_answers_by_tree_position_middle_man(self):
        node_one, _, _, _, ip_node_two, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?tree_position=MIDDLE_MAN', content_type='application/json')

        results = response.data['results'][0]

        self.assertEqual(len(response.data['results']), 1)
        self.assertDictContainsSubset({'consignee': 'middle man one'}, results)
        self.assertEqual(len(results['answers']), 3)

    def test_should_filter_by_received(self):
        node_one, _, _, _, ip_node_two, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?received=No', content_type='application/json')
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(ENDPOINT_URL + '?received=Yes', content_type='application/json')
        self.assertEqual(len(response.data['results']), 6)

    def test_should_filter_by_satisfied(self):
        node_one, _, _, _, ip_node_two, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?satisfied=No', content_type='application/json')
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(ENDPOINT_URL + '?satisfied=Yes', content_type='application/json')
        self.assertEqual(len(response.data['results']), 4)

    def test_should_filter_by_quality(self):
        node_one, _, _, _, ip_node_two, _, assign_to_self_node = self.setup_nodes_with_answers()

        response = self.client.get(ENDPOINT_URL + '?quality=Good', content_type='application/json')
        self.assertEqual(len(response.data['results']), 2)

        response = self.client.get(ENDPOINT_URL + '?quality=Damaged', content_type='application/json')
        self.assertEqual(len(response.data['results']), 3)

    def test_unicef_admin_should_have_permission_to_view_item_feedback_report(self):
        self.log_and_assert_view_item_feedback_report_permission(self.log_unicef_admin_in, HTTP_200_OK)

    def test_unicef_editor_should_have_permission_to_view_item_feedback_report(self):
        self.log_and_assert_view_item_feedback_report_permission(self.log_unicef_editor_in, HTTP_200_OK)

    def test_unicef_viewer_should_have_permission_to_view_item_feedback_report(self):
        self.log_and_assert_view_item_feedback_report_permission(self.log_unicef_viewer_in, HTTP_200_OK)

    def test_ip_editor_should_have_permission_to_view_item_feedback_report(self):
        self.log_and_assert_view_item_feedback_report_permission(self.log_ip_editor_in, HTTP_200_OK)

    def test_ip_viewer_should_have_permission_to_view_item_feedback_report(self):
        self.log_and_assert_view_item_feedback_report_permission(self.log_ip_viewer_in, HTTP_200_OK)

    def setup_nodes_with_answers(self):
        DistributionPlanNode.append_positive_answers = MagicMock(return_value=None)
        ip = ConsigneeFactory(name='ip one')
        middle_man = ConsigneeFactory(name='middle man one', type=Consignee.TYPES.middle_man)
        end_user_one = ConsigneeFactory(name='consignee one', type=Consignee.TYPES.end_user)
        end_user_two = ConsigneeFactory(name='consignee two', type=Consignee.TYPES.end_user)
        programme_one = ProgrammeFactory(name='my first programme')
        programme_two = ProgrammeFactory(name='my second programme')
        programme_three = ProgrammeFactory(name='my third programme')
        purchase_order_item = PurchaseOrderItemFactory(item=ItemFactory(description='Mama kit'),
                                                       purchase_order=PurchaseOrderFactory(order_number=329293))
        release_order_item = ReleaseOrderItemFactory(item=ItemFactory(description='Baba bla bla'),
                                                     release_order=ReleaseOrderFactory(waybill=5540322))

        ip_node_one = DeliveryNodeFactory(consignee=ip, item=purchase_order_item, quantity=1500,
                                          programme=programme_one, track=True,
                                          distribution_plan=DeliveryFactory(track=True),
                                          location='Fort portal', tree_position=Flow.Label.IMPLEMENTING_PARTNER)
        ip_node_two = DeliveryNodeFactory(consignee=ip, item=release_order_item, quantity=100,
                                          distribution_plan=DeliveryFactory(track=True), programme=programme_two,
                                          location='Kampala', tree_position=Flow.Label.IMPLEMENTING_PARTNER, track=True)
        ip_node_three = DeliveryNodeFactory(consignee=ip, item=release_order_item, quantity=100,
                                            distribution_plan=DeliveryFactory(track=True), programme=programme_two,
                                            location='Gulu', tree_position=Flow.Label.IMPLEMENTING_PARTNER, track=True)
        ip_node_four = DeliveryNodeFactory(consignee=ip, item=purchase_order_item, quantity=100,
                                           distribution_plan=DeliveryFactory(track=True), programme=programme_three,
                                           location='Gulu', tree_position=Flow.Label.IMPLEMENTING_PARTNER, track=True)

        middle_man_node = DeliveryNodeFactory(consignee=middle_man, item=purchase_order_item,
                                              programme=programme_one, location='Wakiso', track=True,
                                              tree_position=Flow.Label.MIDDLE_MAN, parents=[(ip_node_one, 1500)],
                                              distribution_plan=None)
        end_user_node_one = DeliveryNodeFactory(consignee=end_user_one,
                                                item=purchase_order_item, parents=[(middle_man_node, 1000)],
                                                programme=programme_one, location='Amuru', track=True,
                                                distribution_plan=None)
        end_user_node_two = DeliveryNodeFactory(consignee=end_user_two, item=purchase_order_item, track=True,
                                                parents=[(middle_man_node, 500)], programme=programme_one,
                                                distribution_plan=None)
        assign_to_self_node = DeliveryNodeFactory(consignee=ip, item=purchase_order_item,
                                                  tree_position=Flow.Label.END_USER, parents=[(ip_node_four, 93)],
                                                  programme=programme_three, distribution_plan=None,
                                                  is_assigned_to_self=True)

        # IP_ITEM Flow and Questions
        ip_item_flow = FlowFactory(label=Flow.Label.IMPLEMENTING_PARTNER)
        ip_item_question_1 = MultipleChoiceQuestionFactory(text='Was the item received?', label='itemReceived',
                                                           when_answered='update_consignee_inventory',
                                                           flow=ip_item_flow, position=1)
        ip_item_option_1 = OptionFactory(text='Yes', question=ip_item_question_1)
        ip_item_option_no = OptionFactory(text='No', question=ip_item_question_1)
        ip_item_question_2 = NumericQuestionFactory(text='How much was received?', label='amountReceived',
                                                    when_answered='update_consignee_stock_level', flow=ip_item_flow,
                                                    position=3)
        ip_item_question_3 = MultipleChoiceQuestionFactory(text='What is the quality of the product?',
                                                           label='qualityOfProduct',
                                                           flow=ip_item_flow, position=3)
        ip_item_option_2 = OptionFactory(text='Good', question=ip_item_question_3)
        ip_item_option_3 = OptionFactory(text='Damaged', question=ip_item_question_3)
        ip_item_question_4 = MultipleChoiceQuestionFactory(text='Are you satisfied with the product?',
                                                           label='satisfiedWithProduct', flow=ip_item_flow, position=4)
        ip_item_option_4 = OptionFactory(text='Yes', question=ip_item_question_4)
        ip_item_option_5 = OptionFactory(text='No', question=ip_item_question_4)

        # MIDDLE_MAN Flow and Questions
        middle_man_flow = FlowFactory(label=Flow.Label.MIDDLE_MAN)
        mm_question_1 = MultipleChoiceQuestionFactory(text='Was product received?', label='productReceived',
                                                      flow=middle_man_flow, position=1)
        mm_option_1 = OptionFactory(text='Yes', question=mm_question_1)
        mm_option_2 = OptionFactory(text='No', question=mm_question_1)
        mm_question_2 = TextQuestionFactory(label='dateOfReceipt', flow=middle_man_flow,
                                            text='When was item received?', position=2)
        mm_question_3 = NumericQuestionFactory(text='What is the amount received?', label='amountReceived',
                                               flow=middle_man_flow, position=3)

        end_user_flow = FlowFactory(label=Flow.Label.END_USER)
        eu_question_1 = MultipleChoiceQuestionFactory(text='Was the item received?', label='itemReceived',
                                                      flow=end_user_flow, position=1)
        eu_option_1 = OptionFactory(text='Yes', question=eu_question_1)
        eu_question_2 = NumericQuestionFactory(text='How much was received?', label='amountReceived',
                                               flow=end_user_flow)
        eu_question_3 = MultipleChoiceQuestionFactory(text='What is the quality of the product?',
                                                      label='qualityOfProduct', flow=end_user_flow, position=3)
        eu_option_3 = OptionFactory(text='Damaged', question=eu_question_3)
        eu_option_3_1 = OptionFactory(text='Good', question=eu_question_3)
        eu_question_4 = MultipleChoiceQuestionFactory(text='Are you satisfied with the product?',
                                                      label='satisfiedWithProduct', flow=end_user_flow, position=4)
        eu_option_4 = OptionFactory(text='Yes', question=eu_question_4)
        eu_question_5 = TextQuestionFactory(label='dateOfReceipt', flow=end_user_flow,
                                            text='When was Delivery Received?')

        ip_run_one = RunFactory(runnable=ip_node_one)
        MultipleChoiceAnswerFactory(question=ip_item_question_1, run=ip_run_one, value=ip_item_option_1)
        NumericAnswerFactory(question=ip_item_question_2, run=ip_run_one, value=1500)
        MultipleChoiceAnswerFactory(question=ip_item_question_3, run=ip_run_one, value=ip_item_option_2)
        MultipleChoiceAnswerFactory(question=ip_item_question_4, run=ip_run_one, value=ip_item_option_4)

        ip_run_three = RunFactory(runnable=ip_node_three)
        MultipleChoiceAnswerFactory(question=ip_item_question_1, run=ip_run_three, value=ip_item_option_no)

        ip_run_two = RunFactory(runnable=ip_node_two)
        MultipleChoiceAnswerFactory(question=ip_item_question_1, run=ip_run_two, value=ip_item_option_1)
        NumericAnswerFactory(question=ip_item_question_2, run=ip_run_two, value=50)
        MultipleChoiceAnswerFactory(question=ip_item_question_3, run=ip_run_two, value=ip_item_option_3)
        MultipleChoiceAnswerFactory(question=ip_item_question_4, run=ip_run_two, value=ip_item_option_5)

        middle_man_node_run = RunFactory(runnable=middle_man_node)
        MultipleChoiceAnswerFactory(question=mm_question_1, run=middle_man_node_run, value=mm_option_1)
        TextAnswerFactory(question=mm_question_2, run=middle_man_node_run, value='2014-9-25')
        NumericAnswerFactory(question=mm_question_3, run=middle_man_node_run, value=1501, remark='Some remark 2')

        end_user_run_one = RunFactory(runnable=end_user_node_one)
        MultipleChoiceAnswerFactory(question=eu_question_1, run=end_user_run_one, value=eu_option_1)
        NumericAnswerFactory(question=eu_question_2, run=end_user_run_one, value=5)
        MultipleChoiceAnswerFactory(question=eu_question_3, run=end_user_run_one, value=eu_option_3)
        MultipleChoiceAnswerFactory(question=eu_question_4, run=end_user_run_one, value=eu_option_4)
        TextAnswerFactory(run=end_user_run_one, question=eu_question_5, value='2014-10-10')

        end_user_run_two = RunFactory(runnable=end_user_node_two)
        MultipleChoiceAnswerFactory(question=eu_question_1, run=end_user_run_two, value=eu_option_1)
        NumericAnswerFactory(question=eu_question_2, run=end_user_run_two, value=500)
        MultipleChoiceAnswerFactory(question=eu_question_3, run=end_user_run_two, value=eu_option_3)
        MultipleChoiceAnswerFactory(question=eu_question_4, run=end_user_run_two, value=eu_option_4)
        TextAnswerFactory(question=eu_question_5, run=end_user_run_two, value='2013-12-12')

        assign_to_self_run = RunFactory(runnable=assign_to_self_node)
        MultipleChoiceAnswerFactory(question=eu_question_1, run=assign_to_self_run, value=eu_option_1)
        NumericAnswerFactory(question=eu_question_2, run=assign_to_self_run, value=500)
        TextAnswerFactory(question=eu_question_5, run=assign_to_self_run, value='2013-12-14')
        MultipleChoiceAnswerFactory(question=eu_question_3, run=assign_to_self_run, value=eu_option_3_1)
        MultipleChoiceAnswerFactory(question=eu_question_4, run=assign_to_self_run, value=eu_option_4)

        return end_user_node_one, purchase_order_item, release_order_item, end_user_node_two, ip_node_two, ip, assign_to_self_node

    def setup_multiple_nodes_with_answers(self, number_of_nodes):
        consignee_one = ConsigneeFactory(name='consignee one')
        programme_one = ProgrammeFactory(name='my first programme')
        po_item = PurchaseOrderItemFactory(item=ItemFactory(description='Mama kit'),
                                           purchase_order=PurchaseOrderFactory(order_number=329293))

        flow = FlowFactory(label='WEB')
        question_1 = MultipleChoiceQuestionFactory(text='Was the item received?', label='itemReceived', flow=flow,
                                                   position=1)
        option_1 = OptionFactory(text='Yes', question=question_1)
        question_2 = NumericQuestionFactory(text='How much was received?', label='amountReceived', flow=flow)
        question_3 = MultipleChoiceQuestionFactory(text='What is the quality of the product?', label='qualityOfProduct',
                                                   flow=flow, position=3)
        option_3 = OptionFactory(text='Damaged', question=question_3)
        question_4 = MultipleChoiceQuestionFactory(text='Are you satisfied with the product?',
                                                   label='satisfiedWithProduct', flow=flow, position=4)
        option_4 = OptionFactory(text='Yes', question=question_4)
        question_5 = TextQuestionFactory(label='dateOfReceipt', flow=flow, text='When was Delivery Received?')
        nodes = []

        for index in range(number_of_nodes):
            node = DeliveryNodeFactory(consignee=consignee_one, item=po_item, programme=programme_one,
                                       distribution_plan=DeliveryFactory(track=True),
                                       track=True)

            run_one = RunFactory(runnable=node)
            MultipleChoiceAnswerFactory(question=question_1, run=run_one, value=option_1)
            NumericAnswerFactory(question=question_2, run=run_one, value=5)
            MultipleChoiceAnswerFactory(question=question_3, run=run_one, value=option_3)
            MultipleChoiceAnswerFactory(question=question_4, run=run_one, value=option_4)
            TextAnswerFactory(run=run_one, question=question_5, value='2014-10-10')
            nodes.append(node)

        return nodes

    def log_and_assert_view_item_feedback_report_permission(self, log_func, status_code):
        log_func()
        self.assertEqual(self.client.get(ENDPOINT_URL).status_code, status_code)

    def assertFieldExists(self, field, value_list):
        field_exists = False
        for key, value in field.iteritems():
            for actual in value_list:
                if key in actual and value == actual[key]:
                    field_exists = True
                    break
        self.assertTrue(field_exists)

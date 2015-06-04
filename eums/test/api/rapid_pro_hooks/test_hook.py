from urllib import quote_plus
from eums.test.factories.distribution_plan_node_factory import DistributionPlanNodeFactory
from eums.test.factories.node_run_factory import NodeRunFactory

from mock import patch
from rest_framework.test import APITestCase

from eums.test.factories.RunQueueFactory import RunQueueFactory
from eums.models import MultipleChoiceAnswer, TextAnswer, NumericAnswer, RunQueue, NodeRun, Flow, \
    MultipleChoiceQuestion, Option, NumericQuestion, TextQuestion
from eums.test.config import BACKEND_URL
from eums.test.factories.flow_factory import FlowFactory


HOOK_URL = BACKEND_URL + 'hook/'


class HookTest(APITestCase):
    def setUp(self):
        self.PHONE = '+12065551212'
        self.flow_id = 2436
        self.flow = FlowFactory.create(rapid_pro_id=self.flow_id)

    def test_should_record_an_answer_of_type_multiple_choice_for_a_node_from_request_data(self):
        uuid = '2ff9fab3-4c12-400e-a2fe-4551fa1ebc18'

        question, _ = MultipleChoiceQuestion.objects.get_or_create(
            uuids=[uuid], text='Was item received?', label='productReceived'
        )

        Option.objects.get_or_create(text='Yes', question=question)
        Option.objects.get_or_create(text='No', question=question)

        node_run = NodeRunFactory(phone=self.PHONE)

        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid, 'Yes', 'Yes', 'productReceived')

        response = self.client.post(HOOK_URL, url_params)
        expected_question = MultipleChoiceQuestion.objects.get(uuids=[uuid])
        yes_option = expected_question.option_set.get(text='Yes')

        answers = MultipleChoiceAnswer.objects.filter(question__uuids=[uuid], node_run=node_run)
        created_answer = answers.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(created_answer.value, yes_option)

    def test_should_record_an_answer_of_type_multiple_choice_for_a_node__with_multiple_uuids_from_request_data(self):
        uuidS = ['2ff9fab3-4c12-400e-a2fe-4551fa1ebc18', 'abc9c005-7a7c-44f8-b946-e970a361b6cf']

        question, _ = MultipleChoiceQuestion.objects.get_or_create(
            uuids=[uuidS], text='Was item received?', label='productReceived'
        )

        Option.objects.get_or_create(text='Yes', question=question)
        Option.objects.get_or_create(text='No', question=question)

        node_run = NodeRunFactory(phone=self.PHONE)

        uuid_for_no = uuidS[1]
        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid_for_no, 'No', 'No', 'productReceived')

        response = self.client.post(HOOK_URL, url_params)
        expected_question = MultipleChoiceQuestion.objects.get(uuids=[uuidS])
        no_option = expected_question.option_set.get(text='No')

        answers = MultipleChoiceAnswer.objects.filter(question__uuids=[uuidS], node_run=node_run)
        created_answer = answers.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(created_answer.value, no_option)

    def test_should_record_an_answer_of_type_text_for_a_node_from_request_data(self):
        uuid = 'abc9c005-7a7c-44f8-b946-e970a361b6cf'

        TextQuestion.objects.get_or_create(uuids=[uuid], text='What date was it received?', label='dateOfReceipt')

        node_run = NodeRunFactory(phone=('%s' % self.PHONE))
        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid, 'Some Text', None, 'dateOfReceipt')

        response = self.client.post(HOOK_URL, url_params)

        answers = TextAnswer.objects.filter(question__uuids=[uuid], node_run=node_run)
        created_answer = answers.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(created_answer.value, 'Some Text')

    def test_should_record_an_answer_of_type_numeric_for_a_node_from_request_data(self):
        uuid = '6c1cf92d-59b8-4bd3-815b-783abd3dfad9'

        NumericQuestion.objects.get_or_create(uuids=[uuid], text='How much was received?', label='amountReceived')

        node_run = NodeRunFactory(phone=('%s' % self.PHONE))
        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid, 42, None, 'amountReceived')

        response = self.client.post(HOOK_URL, url_params)

        answers = NumericAnswer.objects.filter(question__uuids=[uuid], node_run=node_run)
        created_answer = answers.first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(created_answer.value, 42)

    @patch('eums.api.rapid_pro_hooks.hook._schedule_next_run')
    @patch('eums.models.RunQueue.dequeue')
    def test_should_dequeue_next_node_when_question_is_final(self, mock_run_queue_dequeue,
                                                             mock_schedule_next_run):
        mock_schedule_next_run.return_value = None
        uuid = '6c1cf92d-59b8-4bd3-815b-783abd3dfad9'

        question, _ = NumericQuestion.objects.get_or_create(uuids=[uuid], text='How much was received?',
                                                            label='amountReceived')

        node = DistributionPlanNodeFactory()

        NodeRunFactory(node=node, phone=self.PHONE)

        mock_run_queue_dequeue.return_value = RunQueueFactory(
            node=node,
            contact_person_id=node.contact_person_id)

        self.flow.end_nodes = [[question.id, Flow.NO_OPTION]]
        self.flow.save()
        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid, '42', None, 'amountReceived')
        self.client.post(HOOK_URL, url_params)

        mock_schedule_next_run.assert_called_with(node)

    @patch('eums.api.rapid_pro_hooks.hook._schedule_next_run')
    @patch('eums.models.RunQueue.dequeue')
    def test_should_mark_node_run_as_complete_when_question_is_final(self, mock_run_queue_dequeue,
                                                                     mock_schedule_next_run):
        mock_schedule_next_run.return_value = None
        uuid = '6c1cf92d-59b8-4bd3-815b-783abd3dfad9'

        question, _ = NumericQuestion.objects.get_or_create(uuids=[uuid], text='How much was received?',
                                                            label='amountReceived')

        node = DistributionPlanNodeFactory()
        node_run = NodeRunFactory(node=node, phone=self.PHONE,
                                  status=NodeRun.STATUS.scheduled)

        mock_run_queue_dequeue.return_value = RunQueueFactory(
            node=node,
            contact_person_id=node.contact_person_id)
        self.flow.end_nodes = [[question.id, Flow.NO_OPTION]]
        self.flow.save()

        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid, '42', None, 'amountReceived')
        self.client.post(HOOK_URL, url_params)

        node_run = NodeRun.objects.get(id=node_run.id)
        self.assertEqual(node_run.status, NodeRun.STATUS.completed)

    @patch('eums.api.rapid_pro_hooks.hook._schedule_next_run')
    @patch('eums.models.RunQueue.dequeue')
    def test_should_not_mark_node_run_as_complete_when_question_is_not_final(self, mock_run_queue_dequeue,
                                                                             mock_schedule_next_run):
        mock_schedule_next_run.return_value = None

        uuid = '6c1cf92d-59b8-4bd3-815b-783abd3dfad9'

        NumericQuestion.objects.get_or_create(uuids=[uuid], text='How much was received?', label='amountReceived')

        node = DistributionPlanNodeFactory()
        original_status = NodeRun.STATUS.scheduled
        node_run = NodeRunFactory(node=node, phone=self.PHONE,
                                  status=original_status)
        mock_run_queue_dequeue.return_value = RunQueueFactory(
            node=node,
            contact_person_id=node.contact_person_id)

        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid, '42', None, 'amountReceived')
        self.client.post(HOOK_URL, url_params)

        node_run = NodeRun.objects.get(id=node_run.id)
        self.assertEqual(node_run.status, original_status)

    @patch('eums.api.rapid_pro_hooks.hook._schedule_next_run')
    @patch('eums.models.RunQueue.dequeue')
    def test_should_mark_run_returned_by_dequeue_as_started(self, mock_run_queue_dequeue, mock_schedule_next_run):
        uuid = '6c1cf92d-59b8-4bd3-815b-783abd3dfad9'

        mock_schedule_next_run.return_value = None
        question, _ = NumericQuestion.objects.get_or_create(uuids=[uuid], text='How much was received?',
                                                            label='amountReceived')

        node = DistributionPlanNodeFactory()
        url_params = self.__create_rapid_pro_url_params(self.PHONE, uuid, '42', None, 'amountReceived')

        NodeRunFactory(node=node, phone=self.PHONE)

        next_run = RunQueueFactory(node=node,
                                   contact_person_id=node.contact_person_id)
        mock_run_queue_dequeue.return_value = next_run

        self.flow.end_nodes = [[question.id, Flow.NO_OPTION]]
        self.flow.save()

        self.client.post(HOOK_URL, url_params)

        run_returned_by_dequeue = RunQueue.objects.get(id=next_run.id)

        self.assertEqual(run_returned_by_dequeue.status, RunQueue.STATUS.started)

    def __create_rapid_pro_url_params(self, phone, uuid, text="Yes", category=None, label=""):
        return {u'run': [u'4621789'], u'relayer': [u'138'], u'text': [u'%s' % text], u'flow': [u'%s' % self.flow_id],
                u'phone': [u'%s' % phone], u'step': [u'%s' % uuid],
                u'values': [u'[{"category": {"eng": "%s"}, "time": "2014-10-22T11:56:52.836354Z", '
                            u'"text": "Yes", "rule_value": "Yes", "value": "Yes", "label": "%s"}]' % (category, label)],
                u'time': [u'2014-10-22T11:57:35.606372Z']}
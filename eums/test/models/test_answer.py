from unittest import TestCase

from mock import patch

from eums.test.factories.answer_factory import TextAnswerFactory, MultipleChoiceAnswerFactory
from eums.test.factories.question_factory import TextQuestionFactory, MultipleChoiceQuestionFactory


class AnswerTest(TestCase):
    @patch('eums.models.question_hooks.update_consignee_stock_level.run')
    @patch('eums.models.question_hooks.update_consignee_stock_level.__init__')
    def test_should_call_post_create_answer_hook_on_save_if_question_specifies_a_hook(self, mock_constructor, mock_run):
        mock_constructor.return_value = None
        question = TextQuestionFactory(when_answered='update_consignee_stock_level')
        answer = TextAnswerFactory(question=question)
        mock_constructor.assert_called_with(answer)
        mock_run.assert_called()

    @patch('eums.models.question_hooks.update_consignee_stock_level.run')
    def test_should_not_call_post_create_answer_hook_for_questions_that_have_none(self, mock_run):
        question = TextQuestionFactory()
        TextAnswerFactory(question=question)
        self.assertEqual(mock_run.call_count, 0)

    @patch('eums.models.question_hooks.update_consignee_stock_level.rollback')
    @patch('eums.models.question_hooks.update_consignee_stock_level.run')
    def test_should_roll_back_hook_effect_when_answer_is_deleted(self, mock_rollback, mock_run):
        question = MultipleChoiceQuestionFactory(when_answered='update_consignee_stock_level')
        answer = MultipleChoiceAnswerFactory(question=question)
        mock_run.return_value = None
        answer.delete()
        mock_rollback.assert_called()

    @patch('eums.models.question_hooks.update_consignee_stock_level.run')
    @patch('eums.models.question_hooks.update_consignee_stock_level.__init__')
    def test_should_call_post_create_answer_hook_for_multiple_choice_question(self, mock_constructor, mock_run):
        mock_constructor.return_value = None
        question = MultipleChoiceQuestionFactory(when_answered='update_consignee_stock_level')
        answer = MultipleChoiceAnswerFactory(question=question)
        mock_constructor.assert_called_with(answer)
        mock_run.assert_called()

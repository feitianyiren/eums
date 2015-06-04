from eums.test.api.authenticated_api_test_case import AuthenticatedAPITestCase

from eums.test.api.api_test_helpers import create_consignee, create_distribution_plan, create_distribution_plan_node, \
    create_sales_order_item
from eums.test.config import BACKEND_URL


ENDPOINT_URL = BACKEND_URL + 'consignee/'


class ConsigneeEndpointTest(AuthenticatedAPITestCase):
    def test_should_create_consignee(self):
        consignee_details = {'name': "Save the Children", 'type': "implementing_partner"}

        created_consignee = create_consignee(self)

        self.assertDictContainsSubset(consignee_details, created_consignee)

    def test_should_get_consignee(self):
        consignee_details = create_consignee(self)

        get_response = self.client.get(ENDPOINT_URL)

        self.assertEqual(get_response.status_code, 200)
        self.assertDictContainsSubset(consignee_details, get_response.data[0])

    def test_should_get_consignees_sorted_by_name(self):
        consignee_one_details = {'name': "Save the Children", 'type': "implementing_partner"}
        consignee_two_details = {'name': "Feed the Children", 'type': "implementing_partner"}

        create_consignee(self, consignee_one_details)
        create_consignee(self, consignee_two_details)

        get_response = self.client.get(ENDPOINT_URL)

        self.assertEqual(get_response.status_code, 200)
        self.assertDictContainsSubset(consignee_two_details, get_response.data[0])
        self.assertDictContainsSubset(consignee_one_details, get_response.data[1])

    def test_should_search_for_consignee_by_type(self):
        implementing_partner = {'name': "Save the Children", 'type': 'implementing_partner'}
        middle_man = {'name': "Kibuli DHO", 'type': 'middle_man'}

        implementing_partner_details = create_consignee(self, implementing_partner)
        create_consignee(self, middle_man)

        get_response = self.client.get(ENDPOINT_URL + '?search=implementing_partner')

        self.assertEqual(get_response.status_code, 200)
        self.assertDictContainsSubset(implementing_partner_details, get_response.data[0])

    def test_should_search_for_consignee_at_top_level(self):
        implementing_partner = {'name': "Save the Children", 'type': 'implementing_partner'}
        middle_man = {'name': "Kibuli DHO", 'type': 'middle_man'}

        implementing_partner_details = create_consignee(self, implementing_partner)
        create_consignee(self, middle_man)
        plan_id = create_distribution_plan(self)
        item = create_sales_order_item(self)
        node_details = {'item': item['id'], 'targeted_quantity': 1, 'distribution_plan': plan_id,
                        'planned_distribution_date': '2015-04-23', 'consignee': implementing_partner_details['id'],
                        'tree_position': 'END_USER',
                        'location': 'Kampala', 'mode_of_delivery': 'WAREHOUSE', 'contact_person_id': u'1234', }

        create_distribution_plan_node(self, node_details)

        get_response = self.client.get(ENDPOINT_URL + '?node=top')

        self.assertEqual(get_response.status_code, 200)
        self.assertDictContainsSubset(implementing_partner_details, get_response.data[0])
        self.assertEqual(1, len(get_response.data))

        get_response = self.client.get(ENDPOINT_URL + '?node=1')
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(2, len(get_response.data))

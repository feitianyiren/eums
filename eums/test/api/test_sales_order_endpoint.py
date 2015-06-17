import datetime

from eums.test.api.api_test_helpers import create_sales_order, create_programme, create_release_order
from eums.test.api.authenticated_api_test_case import AuthenticatedAPITestCase
from eums.test.config import BACKEND_URL


ENDPOINT_URL = BACKEND_URL + 'sales-order/'


class SalesOrderEndPointTest(AuthenticatedAPITestCase):
    def test_should_create_sales_order(self):
        programme = create_programme()
        sales_order_details = {'order_number': 345553, 'date': datetime.date(2014, 10, 5),
                               'programme': programme.id, 'description': 'test'}
        response = self.client.post(ENDPOINT_URL, sales_order_details, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertDictContainsSubset(sales_order_details, response.data)

    def test_should_get_sales_orders(self):
        created_sales_order = create_sales_order(self)
        get_response = self.client.get(ENDPOINT_URL)
        self.assertEqual(get_response.status_code, 200)
        self.assertDictContainsSubset(created_sales_order, get_response.data[0])

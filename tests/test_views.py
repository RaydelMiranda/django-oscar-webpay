import mock
import uuid

from django.test import TestCase
from django.core.urlresolvers import reverse
from oscar.core.loading import get_model

from test_utils import Patchers

Basket = get_model('basket', 'Basket')


class TestWebPayViewsBase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.external_url = 'http://mocked_url.com'
        cls.token = str(uuid.uuid4())
        super(TestWebPayViewsBase, cls).setUpClass()


class TesWebPayViewsRedirectSuccess(TestWebPayViewsBase):

    def test_redirect_logic_success(self):

        patchers = {
            'mock_get_webpay_client': mock.patch(
                'oscar.apps.order.utils.OrderNumberGenerator.order_number', autospec=True
            ),
            'mock_order_number': mock.patch('oscar_webpay.gateway.get_webpay_client')
        }

        with Patchers(patchers) as patcher:
            # Configuring mocks
            patcher.mock_order_number.return_value = 100000
            patcher.mock_get_webpay_client.return_value = {'url': self.external_url, 'token': self.token}

            # Test the use of the correct template.
            with self.assertTemplateUsed('oscar_webpay/checkout/webpay_form.html'):
                response = self.client.get(
                    reverse(
                        'webpay-redirect',
                        kwargs={'return_url_name': 'return-url-name', 'final_url_name': 'final-url-name'}
                    )
                )

                self.assertRedirects(
                    response,
                    reverse('webpay-form', kwargs={'url': self.external_url, 'token': self.token}),
                )


class TestWebPayRedirectViewsFail(TestWebPayViewsBase):

    def test_redirect_logic_fail(self):
        patchers = {
            'mock_get_webpay_client': mock.patch(
                'oscar.apps.order.utils.OrderNumberGenerator.order_number', autospec=True
            ),
            'mock_order_number': mock.patch('oscar_webpay.gateway.get_webpay_client')
        }

        with Patchers(patchers) as patcher:
            # Configuring mocks
            patcher.mock_order_number.return_value = 100000
            patcher.mock_get_webpay_client.side_effect = Exception('Test exception')

            response = self.client.get(
                reverse(
                    'webpay-redirect',
                    kwargs={'return_url_name': 'return-url-name', 'final_url_name': 'final-url-name'}
                )
            )

            self.assertRedirects(response, reverse('basket:summary'))

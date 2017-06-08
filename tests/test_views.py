import mock
import uuid

from django.test import TestCase
from django.core.urlresolvers import reverse
from oscar.core.loading import get_model


Basket = get_model('basket', 'Basket')


class TestWebPayViewsBase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.external_url = 'http://mocked_url.com'
        cls.token = str(uuid.uuid4())
        super(TestWebPayViewsBase, cls).setUpClass()


class TesWebPayViewsRedirectSuccess(TestWebPayViewsBase):

    @mock.patch('oscar.apps.order.utils.OrderNumberGenerator.order_number')
    @mock.patch('oscar_webpay.views.get_webpay_client')
    def test_redirect_logic_success(self, mock_get_webpay_client, mock_order_number):

        # Configuring mocks
        mock_order_number.return_value = 100000
        mock_get_webpay_client.return_value = {'url': self.external_url, 'token': self.token}

        # Test the use of the correct template.
        with self.assertTemplateUsed('oscar_webpay/checkout/webpay_form.html'):
            response = self.client.get(
                reverse(
                    'webpay-redirect',
                    kwargs={
                        'return_url_name': 'webpay-success',
                        'final_url_name': 'webpay-end-redirect'
                    }
                )
            )

            self.assertRedirects(
                response,
                reverse('webpay-form', kwargs={'url': self.external_url, 'token': self.token}),
            )


class TestWebPayRedirectViewsFail(TestWebPayViewsBase):

    @mock.patch('oscar.apps.order.utils.OrderNumberGenerator.order_number')
    @mock.patch('oscar_webpay.views.get_webpay_client', autospec=True)
    def test_redirect_logic_fail(self, mock_order_number, mock_get_webpay_client):
        # Configuring mocks
        mock_order_number.return_value = 100000
        mock_get_webpay_client.side_effect = Exception('Intentional exception raised for get_webpay_client')

        response = self.client.get(
            reverse(
                'webpay-redirect',
                kwargs={
                    'return_url_name': reverse('webpay-success'),
                    'final_url_name': reverse('webpay-end-redirect')
                }
            )
        )

        self.assertRedirects(response, reverse('basket:summary'))

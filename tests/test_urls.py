import uuid

from django.test import SimpleTestCase
from django.core.urlresolvers import resolve


class TestUrls(SimpleTestCase):

    def test_webpay_redirect(self):
        match = resolve('/test/webpay_redirect/return-url-name/final-url-name/')
        self.assertEqual(match.url_name, 'webpay-redirect')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {'return_url_name': 'return-url-name', 'final_url_name': 'final-url-name'})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayRedirectView')

    def test_webpay_form(self):

        token = str(uuid.uuid4())
        match = resolve('/test/webpay_form/{}/{}/'.format('http://mocked_url-123.com', token))
        self.assertEqual(match.url_name, 'webpay-form')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {'url': 'http://mocked_url-123.com', 'token': token})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayRedirectForm')

    def test_webpay_success(self):
        match = resolve('/test/webpay_success/')
        self.assertEqual(match.url_name, 'webpay-success')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayPaymentSuccessView')

    def test_webpay_place_order(self):
        match = resolve('/test/webpay_place_order/')
        self.assertEqual(match.url_name, 'webpay-place-order')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayPaymentSuccessView')

    def test_webpay_thanks(self):
        match = resolve('/test/webpay_thanks/')
        self.assertEqual(match.url_name, 'webpay-txns')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayThankYouView')

    def test_webpay_fail(self):
        match = resolve('/test/webpay_fail/')
        self.assertEqual(match.url_name, 'webpay-fail')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayFail')

    def test_webpay_cancel(self):
        match = resolve('/test/webpay_cancel/')
        self.assertEqual(match.url_name, 'webpay-cancel')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayCancel')

    def test_webpay_end_redirect(self):
        match = resolve('/test/webpay_end_redirect/')
        self.assertEqual(match.url_name, 'webpay-end-redirect')
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})
        self.assertEqual(match._func_path, 'oscar_webpay.views.WebPayEndRedirect')





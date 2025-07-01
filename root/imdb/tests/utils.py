from django.test import TestCase, RequestFactory

from ..randoms import randoms, random
from ..models import MockModel
from ..redirect import get_redirect_or_referer


class RandomsTestCase(TestCase):
    def setUp(self):
        # Create some objects to use as a source for random selection
        self.objects = [MockModel.objects.create() for _ in range(10)]
        random.seed(10)

    def tearDown(self):
        random.seed(None)

    def test_randoms(self):
        # Call the randoms function with a limit of 5
        results1 = randoms(MockModel.objects.all(), 5)

        # Call the randoms function again with the same arguments
        results2 = randoms(MockModel.objects.all(), 5)

        # Check that the two sets of results are not equal
        self.assertNotEqual(results1, results2)

        # Check that all the results are instances of MyModel
        for result in results1:
            self.assertIsInstance(result, MockModel)

        # Check that all the results are in the source queryset
        for result in results1:
            self.assertIn(result, self.objects)

        # Check the same conditions for the second set of results
        for result in results2:
            self.assertIsInstance(result, MockModel)
        for result in results2:
            self.assertIn(result, self.objects)


class GetRedirectOrRefererTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_redirect_to_priority(self):
        request = self.factory.get('/some/url/?redirect_to=/some/other/url/', HTTP_REFERER='/some/referer/url')
        result = get_redirect_or_referer(request)
        self.assertEqual(result, '/some/other/url/')

    def test_redirect_to(self):
        # Create a request with a redirect_to query parameter
        request = self.factory.get('/some/url/?redirect_to=/some/other/url/')
        result = get_redirect_or_referer(request)
        self.assertEqual(result, '/some/other/url/')

    def test_http_referer(self):
        # Create a request with an HTTP_REFERER header
        request = self.factory.get('/some/url/', HTTP_REFERER='/some/other/url/')
        result = get_redirect_or_referer(request)
        self.assertEqual(result, '/some/other/url/')

    def test_no_redirect_or_referer(self):
        # Create a request with no redirect_to or HTTP_REFERER
        request = self.factory.get('/some/url/')
        result = get_redirect_or_referer(request)
        self.assertIsNone(result)

from django.test import TestCase

from bmrs.decorators.decorator_bmrs_api_vars_required import \
                                        bmrs_api_vars_required
from bmrs.decorators.decorator_request_params_required import \
                                        request_params_required


class TestAllDecoratorsTestCase(TestCase):
    
    @bmrs_api_vars_required
    def test_decorator_bmrs_api_vars_required(self,
                                              host,
                                              version,
                                              url_end_str,
                                              api_scripting_key,
                                              **kwargs):
        
        """
        Test that the bmrs_api_vars_required decorator correctly populates 
        the expected arguments from the environment variables.
        """
        
        self.assertIsNotNone(host)
        self.assertIsNotNone(version)
        self.assertIsNotNone(url_end_str)
        self.assertIsNotNone(api_scripting_key)
        
        self.assertIsInstance(host, str)
        self.assertIsInstance(version, str)
        self.assertIsInstance(url_end_str, str)
        self.assertIsInstance(api_scripting_key, str)
        
    @request_params_required
    def test_decorator_request_params_required(self, 
                                               timeout, 
                                               max_tries,
                                               **kwargs):
        """
        Test that the request_params_required decorator correctly populates 
        the expected arguments from the environment variables.
        """
        
        self.assertIsNotNone(timeout)
        self.assertIsNotNone(max_tries)
        
        self.assertIsInstance(timeout, int)
        self.assertIsInstance(max_tries, int)
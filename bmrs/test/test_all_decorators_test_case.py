from django.test import TestCase

from bmrs.decorators.decorator_bmrs_api_vars_required import \
                                        bmrs_api_vars_required
from bmrs.decorators.decorator_aiohttp_params_required import \
                                        aiohttp_params_required
from bmrs.decorators.decorator_report_column_headers_required import \
                                        report_column_headers_required


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
        
        
    @aiohttp_params_required
    def test_decorator_request_params_required(self, 
                                               timeout, 
                                               max_tries,
                                               max_concurrent_tasks,
                                               rate_limit_sleep_time,
                                               **kwargs):
        """
        Test that the request_params_required decorator correctly populates 
        the expected arguments from the environment variables.
        """
        
        self.assertIsNotNone(timeout)
        self.assertIsNotNone(max_tries)
        self.assertIsNotNone(max_concurrent_tasks)
        self.assertIsNotNone(rate_limit_sleep_time)
        
        self.assertIsInstance(timeout, int)
        self.assertIsInstance(max_tries, int)
        self.assertIsInstance(max_concurrent_tasks, int)
        self.assertIsInstance(rate_limit_sleep_time, int)
        
        
    @report_column_headers_required
    def test_report_column_headers_required(self, 
                                            b1770_column,
                                            b1780_column) -> None:
        """
        Test that the request_params_required decorator correctly populates 
        the expected arguments from the environment variables.
        """
        
        self.assertIsNotNone(b1770_column)
        self.assertIsNotNone(b1780_column)
        
        self.assertIsInstance(b1770_column, str)
        self.assertIsInstance(b1780_column, str)

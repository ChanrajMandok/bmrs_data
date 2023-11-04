import asyncio
import unittest

from unittest.mock import patch, AsyncMock
from bmrs.services.service_bmrs_data_retriever import ServiceBmrsDataRetriever


class TestServiceBmrsDataRetrieverTestCase(unittest.TestCase):
    """
    Test cases for the ServiceBmrsDataRetriever class to ensure it retrieves and handles data.
    """


    def setUp(self):
        """
        Set up the ServiceBmrsDataRetriever instance with configurations before each test.
        """
        self.bmrs_data_retriever = \
                    ServiceBmrsDataRetriever(timeout=10,
                                            max_tries=3,
                                            max_concurrent_tasks=5,
                                            rate_limit_sleep_time=30
                                            )


    @patch('bmrs.services.service_bmrs_data_retriever.ServiceBmrsDataRetriever.retrieve_all_data',\
                                                                                new_callable=AsyncMock)
    def test_sync_retrieve_all_data_success(self, 
                                            mock_retrieve_all_data):
        """
        Test the synchronous wrapper around the asynchronous retrieve_all_data method .
        """
        # Mocked data and report parameters
        report_name = 'B1770'
        settlement_date = '2023-01-01'
        mock_retrieve_all_data.return_value = [{'data': 'mock_data'}] * 10

        # Call the synchronous retrieve method
        data = self.bmrs_data_retriever.sync_retrieve_all_data(report_name=report_name,
                                                               settlement_date=settlement_date,
                                                               range_start=1,
                                                               range_end=10)

        # Assertions to ensure correct method call and data retrieval
        mock_retrieve_all_data.assert_awaited_with(report_name=report_name,
                                                   settlement_date=settlement_date,
                                                   range_start=1,
                                                   range_end=10
                                                   )
        
        self.assertEqual(len(data), 10, "Data length does not match the expected number of entries.")
        self.assertEqual(data[0]['data'], 'mock_data', "Data content does not match the expected mock data.")


    def test_sync_retrieve_all_data_invalid_report(self):
        """
        Test the behavior of sync_retrieve_all_data with an invalid report name.
        """
        # Invalid report parameters
        report_name = 'INVALID_REPORT'
        settlement_date = '2023-01-01'

        # Assert that an error log is produced and the result is empty for an invalid report name
        with self.assertLogs('bmrs.services  ', level='ERROR') as cm:
            
            result = self.bmrs_data_retriever.sync_retrieve_all_data(report_name = report_name,
                                                                     settlement_date = settlement_date)
            
            self.assertEqual(result, [], "Result is not empty on invalid report name.")
            
            expected_log_message = "Invalid 'report_name'. It should be a non-empty string starting with 'B' followed by numbers."
            self.assertIn(expected_log_message, cm.output[0], "Expected error message not found in log output.")


    @patch('bmrs.services.service_bmrs_data_retriever.ServiceBmrsDataRetriever.retrieve_all_data',\
                                                                                new_callable=AsyncMock)
    def test_sync_retrieve_all_data_rate_limit(self, mock_retrieve_all_data):
        """
        Test sync_retrieve_all_data method's handling of a rate limit exception (TimeoutError).
        """
        report_name = 'B1770'
        settlement_date = '2023-01-01'
        mock_retrieve_all_data.side_effect = asyncio.TimeoutError

        # Assert that a TimeoutError is raised when a rate limit is hit
        with self.assertRaises(asyncio.TimeoutError, msg="TimeoutError not raised when expected due to rate limiting."):
            self.bmrs_data_retriever.sync_retrieve_all_data(report_name, settlement_date)


    @patch('bmrs.services.service_bmrs_data_retriever.ServiceBmrsDataRetriever.retrieve_all_data',\
                                                                                new_callable=AsyncMock)
    def test_sync_retrieve_all_data_default_range(self, mock_retrieve_all_data):
        """
        Test sync_retrieve_all_data with its default range to ensure proper handling of default parameters.
        """
        # Default range parameters
        report_name = 'B1770'
        settlement_date = '2023-01-01'
        mock_retrieve_all_data.return_value = [{'data': 'mock_data'}] * 50

        # Retrieval with default range
        data = self.bmrs_data_retriever.sync_retrieve_all_data(report_name=report_name,
                                                               settlement_date=settlement_date)

        # Assertions to confirm the default range handling and data content
        self.assertEqual(len(data), 50, "Data length does not match expected number of entries for default range.")
        self.assertTrue(all(d['data'] == 'mock_data' for d in data), "Not all entries match the expected 'mock_data'.")
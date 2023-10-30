import requests

from unittest import TestCase, mock

from bmrs.services.service_bmrs_data_retriever import ServiceBmrsDataRetriever


class TestServiceBmrsDateRetrieverTestCase(TestCase): 
    
    def setUp(self):
        self.data_retriever = ServiceBmrsDataRetriever(timeout=2, max_tries=3)

    @mock.patch('bmrs.services.service_bmrs_data_retriever.requests.Session.get')
    def test_successful_data_retrieval(self, mock_get):
        """
        Test the scenario where data is successfully retrieved.

        Given a valid request, the function should create a file with the expected content.
        """
        
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = b"Some CSV content"
        mock_get.return_value = mock_response

        self.data_retriever.retrieve_data('1', 'B1770', '2023-10-01', 'csv')

        # Check file creation
        with open("B1770_2023-10-01.csv", 'rb') as file:
            self.assertEqual(file.read(), b"Some CSV content")

    @mock.patch('bmrs.services.service_bmrs_data_retriever.requests.Session.get', side_effect=requests.Timeout)
    def test_request_timeout(self, mock_get):
        """
        Test the scenario where a request times out.

        The function should log the timeout error and the attempt number.
        """
        
        with self.assertLogs('bmrs.services', level='ERROR') as cm:
            self.data_retriever.retrieve_data('1', 'B1770', '2023-10-01', 'csv')
        self.assertIn("Attempt 1 failed due to timeout.", cm.output[0])

    @mock.patch('bmrs.services.service_bmrs_data_retriever.requests.Session.get', side_effect=requests.ConnectionError)
    def test_connection_error(self, mock_get):
        """
        Test the scenario where there's a connection error.

        The function should log the connection error and the attempt number.
        """
        
        with self.assertLogs('bmrs.services', level='ERROR') as cm:
            self.data_retriever.retrieve_data('1', 'B1770', '2023-10-01', 'csv')
        self.assertIn("Attempt 1 failed due to connection error.", cm.output[0])

    @mock.patch('bmrs.services.service_bmrs_data_retriever.requests.Session.get', side_effect=requests.Timeout)
    def test_max_retries(self, mock_get):
        """
        Test the scenario where max retries are hit.

        If the max retries limit is reached, the function should log a message indicating the failure.
        """
        
        with self.assertLogs('bmrs.services', level='ERROR') as cm:
            self.data_retriever.retrieve_data('1', 'B1770', '2023-10-01', 'csv')
        self.assertIn(f"Failed to retrieve data after {self.data_retriever.max_retries} attempts.", cm.output[-1])

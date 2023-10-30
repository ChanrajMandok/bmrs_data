from unittest import TestCase, mock

from bmrs.services.service_bmrs_build_url import ServiceBmrsBuildUrl
from bmrs.services.service_bmrs_data_retriever import ServiceBmrsDataRetriever


class TestServiceBmrsBuildUrlTestCase(TestCase): 
    
    @mock.patch("bmrs.services.service_bmrs_build_url.bmrs_api_vars_required", lambda x: x)
    def setUp(self):
        self._service_bmrs_build_url = ServiceBmrsBuildUrl()
        self._service_bmrs_data_retriever = ServiceBmrsDataRetriever()
    
    def test_service_bmrs_build_url(self):
        """
        Test the functionality of the ServiceBmrsBuildUrl class.
        
        Given certain input parameters, it should return a correctly formatted URL.
        """
        
        period = '1'
        report_name = 'B1770'
        file_format = 'xml'
        settlement_date = '2023-10-01'
        
        desired_url_outcome = 'https://api.bmreports.com/BMRS/B1770/V1?APIKey=2zsd43hl5hjii36&&SettlementDate=2023-10-01&Period=1&ServiceType=xml'
        
        url = self._service_bmrs_build_url.build_url(period=period,
                                                     report_name=report_name, 
                                                     service_type=file_format,
                                                     settlement_date=settlement_date)
        
        self.assertIsNotNone(url)
        self.assertIsInstance(url, str)
        self.assertEqual(url, desired_url_outcome)
        
        
    def test_invalid_period(self):
        """
        Test the scenario where an invalid period is provided.
        
        An invalid period should trigger a logging error, indicating the period should be between 1-50.
        """
        
        with self.assertLogs('bmrs.services', level='ERROR') as cm:
            self._service_bmrs_build_url.build_url(period="100", report_name="B1770", settlement_date="2023-10-01")
        self.assertIn("Invalid 'period'. It should be a number in the range 1-50.", cm.output[0])


    def test_invalid_settlement_date(self):
        """
        Test the scenario where an invalid settlement date is provided.
        
        An invalid date format should trigger a logging error.
        """
        
        with self.assertLogs('bmrs.services', level='ERROR') as cm:
            self._service_bmrs_build_url.build_url(period="1", report_name="B1770", settlement_date="2023-113-01")
        self.assertIn("Invalid 'settlement_date'. It should be in the format YYYY-MM-DD.", cm.output[0])


    def test_invalid_service_type(self):
        """
        Test the scenario where an invalid service type is provided.
        
        Only 'csv' and 'xml' should be accepted service types, and others should trigger a logging error.
        """
        
        with self.assertLogs('bmrs.services', level='ERROR') as cm:
            self._service_bmrs_build_url.build_url(period="1", report_name="B1770", settlement_date="2023-10-01", service_type="json")
        self.assertIn("Invalid 'service_type'. Allowed values are 'csv' and 'xml'.", cm.output[0])

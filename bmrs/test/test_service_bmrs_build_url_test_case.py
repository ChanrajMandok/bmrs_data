from unittest import TestCase, mock

from bmrs.services.service_bmrs_build_url import ServiceBmrsBuildUrl


class TestServiceBmrsBuildUrlTestCase(TestCase): 
    
    @mock.patch("bmrs.services.service_bmrs_build_url.bmrs_api_vars_required", lambda x: x)
    def setUp(self):
        self._service_bmrs_build_url = ServiceBmrsBuildUrl()

    def test_service_bmrs_build_url(self):
        """Test the functionality of the ServiceBmrsBuildUrl class."""
        
        period = '1'
        report_name = 'B1770'
        file_format = 'xml'
        settlement_date = '2023-10-01'
        
        desired_url_outcome = \
        'https://api.bmreports.com/BMRS/B1770/V1?APIKey=2zsd43hl5hjii36&&SettlementDate=2023-10-01&Period=1&ServiceType=xml'
        
        url = self._service_bmrs_build_url.build_url(period=period,
                                                     report_name=report_name, 
                                                     service_type=file_format,
                                                     settlement_date=settlement_date)
        
        self.assertIsNotNone(url)
        self.assertIsInstance(url, str)
        self.assertEqual(url, desired_url_outcome)
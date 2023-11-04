import re

from typing import Optional

from bmrs.services import logger
from bmrs.decorators.decorator_bmrs_api_vars_required import \
                                        bmrs_api_vars_required


class ServiceBmrsBuildUrl:


    @bmrs_api_vars_required
    def build_url(self,
                  period: str,
                  report_name: str, 
                  settlement_date: str,
                  host: Optional[str] = None,
                  version: Optional[str] = None,
                  url_end_str: Optional[str] = None,
                  api_scripting_key: Optional[str] = None,
                  service_type: str = "xml") -> Optional[str]:
        """
        Constructs the BMRS URL based on provided parameters.
        
        Args:
            report_name: Name of the report to fetch.
            period: Specific period for the report.
            settlement_date: Settlement date for the report.
            host: Base BMRS API URL (typically injected by decorator).
            version: API version (typically injected by decorator).
            url_end_str: URL ending format string (typically injected by decorator).
            api_scripting_key: API key for BMRS (typically injected by decorator).
            service_type: Desired response format ('csv' or 'xml'). Default is 'xml'.
        """
        
        # Checks
                # Validating the 'period' parameter
        try:
            # Ensure 'period' is an integer between 1 and 50 (inclusive)
            if not 1 <= int(period) <= 50:
                logger.error(f"{self.__class__.__name__}: Invalid 'period'. It should be a number in the range 1-50.")
                return None
        except ValueError:
            # Catch the error if 'period' is not convertible to an integer
            logger.error(f"{self.__class__.__name__}: 'period' should be a string representation of a number.")
            return None

        # Validate the 'report_name' parameter to ensure it's a non-empty string
        if not report_name or not isinstance(report_name, str) \
                                        or not re.match(r'^B\d+$', report_name):
            logger.error(f"{self.__class__.__name__}: Invalid 'report_name'. It should be a non-empty string starting with 'B' followed by numbers.")
            return None

        # Validate the 'settlement_date' format using regex matching
        if not settlement_date or not re.match(r"^\d{4}-\d{2}-\d{2}$", settlement_date):
            logger.error(f"{self.__class__.__name__}: Invalid 'settlement_date'. It should be in the format YYYY-MM-DD.")
            return None

        # Check that 'service_type' is either 'csv' or 'xml'
        if service_type not in ['csv', 'xml']:
            logger.error(f"{self.__class__.__name__}: Invalid 'service_type'. Allowed values are 'csv' and 'xml'.")
            return None

        # Check for missing or empty essential parameters
        if not all([host, version, url_end_str, api_scripting_key]):
            logger.error(f"{self.__class__.__name__}: Some essential parameters are missing or empty.")
            return None
        
        # Construct the URL using the provided parameters
        url = (f"{host}{report_name}/{version}?APIKey={api_scripting_key}&"
               f"{url_end_str.format(SettlementDate=settlement_date, Period=period, ServiceType=service_type)}")
        
        return url
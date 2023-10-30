import brotli
import requests

from typing import Optional

from bmrs.services import logger
from bmrs.decorators.decorator_request_params_required import \
                                        request_params_required
from bmrs.services.service_bmrs_build_url import ServiceBmrsBuildUrl
from bmrs.services.service_bmrs_decode_response import ServiceBmrsDecodeResponse


class ServiceBmrsDataRetriever:
    
    @request_params_required
    def __init__(self,
                 timeout, 
                 max_tries) -> None:
        self.timeout = timeout
        self.max_retries = max_tries

        self.service_build_url = ServiceBmrsBuildUrl()
        self.service_bmrs_decode_response = ServiceBmrsDecodeResponse()
    
    def retrieve_data(self, 
                      period: str,
                      report_name: str, 
                      settlement_date: str, 
                      file_format: str = 'csv',
                      filename: Optional[str] = None) -> None:
        """
        Retrieves BMRS data and saves it to a file.

        Args:
            period: Specific period for the report.
            report_name: Name of the report to fetch.
            settlement_date: Settlement date for the report.
            file_format: Desired response format ('csv' or 'xml'). Default is 'csv'.
            filename: Filename to save the content. If not provided, default is {report_name}_{settlement_date}.
        """
        if file_format not in ['csv', 'xml']:
            logger.error(f"Invalid file format '{file_format}'. Allowed values are 'csv' and 'xml'.")
            return

        # If filename is not provided, use default
        if filename is None:
            filename = f"{report_name}_{settlement_date}"

        if not filename.endswith(('csv', 'xml')):
            filename = f"{filename}.{file_format}"

        url = self.service_build_url.build_url(period=period,
                                               report_name=report_name, 
                                               service_type=file_format,
                                               settlement_date=settlement_date)

        session = requests.Session()

        for attempt in range(self.max_retries):
            try: 
                response = session.get(url, timeout=self.timeout)

                if response.status_code == 200:
                    with open(filename, 'wb') as file: 
                        file.write(response.content)
                    logger.info(f"File saved to {filename}")
                    return  

                logger.error(f'Error: {response.status_code}')

            except requests.Timeout:
                logger.error(f'Attempt {attempt + 1} failed due to timeout.')

            except requests.ConnectionError:
                logger.error(f'Attempt {attempt + 1} failed due to connection error.')

        logger.error(f"Failed to retrieve data after {self.max_retries} attempts.")

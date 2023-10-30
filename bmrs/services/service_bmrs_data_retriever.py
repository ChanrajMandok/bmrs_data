import xml
import time
import asyncio
import xmltodict

from typing import Any, Union, Optional
from aiohttp import ClientSession, ClientTimeout, ClientError

from bmrs.services import logger
from bmrs.decorators.decorator_aiohttp_params_required import \
                                        aiohttp_params_required
from bmrs.services.service_bmrs_build_url import ServiceBmrsBuildUrl


class ServiceBmrsDataRetriever:
    
    @aiohttp_params_required
    def __init__(self,
                 timeout, 
                 max_tries, 
                 max_concurrent_tasks,
                 url_builder = None) -> None:
        self.timeout = timeout
        self.max_retries = max_tries
        self.max_concurrent_tasks = max_concurrent_tasks
        self.service_build_url = url_builder if url_builder else ServiceBmrsBuildUrl()


    def sync_retrieve_all_data(self,
                               report_name: str,
                               settlement_date: str,
                               range_start: Optional[int] = 1,
                               range_end : Optional[int] = 50,
                               ) -> list[Union[dict[str, Any], list[dict[str, Any]]]]:
        """
        Synchronously retrieves data for all periods using the retrieve_data method.
        
        Args:
            report_name: Name of the report to fetch.
            settlement_date: Settlement date for the report.
            range_start: The starting period for the report.
            range_end: The ending period for the report.
        """
        
        start_time = time.time()
        ts_data = asyncio.run(self.retrieve_all_data(range_end=range_end,
                                                     range_start=range_start,
                                                     report_name=report_name,
                                                     settlement_date=settlement_date)) 
        elapsed_time = time.time() - start_time
        logger.info(f"{self.__class__.__name__}: {report_name} - {len(ts_data)} api calls in {elapsed_time:.2f} seconds via Asyncio")
    
        return ts_data


    async def retrieve_all_data(self, 
                                range_end : int,
                                report_name: str, 
                                range_start: int,
                                settlement_date: str,
                                ) -> list[Union[dict[str, Any], list[dict[str, Any]]]]:
        """
        Concurrently retrieves data for periods between range_start and range_end using the retrieve_data method.

        Args:
            range_end: The ending period for the report.
            report_name: Name of the report to fetch.
            range_start: The starting period for the report.
            settlement_date: Settlement date for the report.
        """
        
        semaphore = asyncio.Semaphore(int(self.max_concurrent_tasks))

        async def bound_retrieve(period: int) -> Union[dict[str, Any], list[dict[str, Any]]]:
            async with semaphore:
                return await self.retrieve_data(str(period), report_name, settlement_date)

        tasks = [bound_retrieve(period) for period in range(range_start, range_end + 1)]

        results = await asyncio.gather(*tasks)

        flattened_results = [
                            item for sublist in results
                            for item in (sublist if isinstance(sublist, list) else [sublist])
                            if item is not None
                            ]
        
        return flattened_results
    
    async def retrieve_data(self,
                            period: str,
                            report_name: str, 
                            settlement_date: str, 
                            file_format: str = 'xml'
                            ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """
        Retrieves BMRS data.

        Args:
            period: Specific period for the report.
            report_name: Name of the report to fetch.
            settlement_date: Settlement date for the report.
            file_format: Desired response format ('csv' or 'xml'). Default is 'xml'.
        """
        
        if file_format not in ['csv', 'xml']:
            logger.error(f"{self.__class__.__name__}:Invalid file format '{file_format}'. "
                         "Allowed values are 'csv' and 'xml'.")
            return

        url = self.service_build_url.build_url(period=period,
                                               report_name=report_name,
                                               service_type=file_format,
                                               settlement_date=settlement_date)

        timeout = ClientTimeout(total=self.timeout)
        async with ClientSession(timeout=timeout) as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content_str = await response.text()
                            try:
                                content_data = xmltodict.parse(content_str)
                                items = content_data['response']['responseBody']['responseList']['item']
                                if isinstance(items, dict): 
                                    return items
                                elif isinstance(items, list):
                                    return items[-1]
                                else:
                                    logger.error(f"{self.__class__.__name__}: Unexpected type for 'items' in XML structure.")
                                    return None
                            except (xml.parsers.expat.ExpatError, KeyError):
                                continue

                        else:
                            logger.error(f'{self.__class__.__name__}:Error: {response.status}')
                            continue 

                except (ClientError, Exception) as e:
                    logger.error(f"{self.__class__.__name__}:Unexpected error on attempt {attempt + 1}: {e}")
                    continue 
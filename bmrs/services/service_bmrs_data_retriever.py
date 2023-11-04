import time
import asyncio
import xmltodict

from typing import Any, Union, Optional
from aiohttp import ClientResponseError, ClientSession, ClientTimeout

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
                 rate_limit_sleep_time,
                 url_builder=None) -> None:
        self.timeout = timeout
        self.max_retries = max_tries
        # Limit the number of concurrent tasks to avoid overloading resources.
        self.max_concurrent_tasks = max_concurrent_tasks
        # Time to sleep if rate-limited.
        self.rate_limit_sleep_time = rate_limit_sleep_time
        # Using dependency injection to allow custom URL builders. 
        # Defaults to ServiceBmrsBuildUrl if none is provided.
        self.service_build_url = url_builder if url_builder else ServiceBmrsBuildUrl()


    def sync_retrieve_all_data(self,
                               report_name: str,
                               settlement_date: str,
                               range_start: Optional[int] = 1,
                               range_end : Optional[int] = 50,
                               ) -> list[Union[dict[str, Any], list[dict[str, Any]]]]:
        """
        Synchronously retrieves BMRS data for all periods by calling the asynchronous retrieve_all_data method.
        
        Args:
            report_name: The identifier for the specific report to be fetched.
            settlement_date: The date for which the data needs to be fetched in the format 'YYYY-MM-DD'.
            range_start: The initial period number to start fetching the data from (inclusive). Default is 1.
            range_end: The final period number till which the data needs to be fetched (inclusive). Default is 50.
        """
        
        # A wrapper to run async function in a synchronous context.
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
        Concurrently retrieves BMRS data for a range of periods using asynchronous requests.
        
        Args:
            range_end: The final period number till which the data needs to be fetched (inclusive).
            report_name: The identifier for the specific report to be fetched.
            range_start: The initial period number to start fetching the data from (inclusive).
            settlement_date: The date for which the data needs to be fetched in the format 'YYYY-MM-DD'.
        """
        
        # Using a semaphore to manage the max number of concurrent tasks
        semaphore = asyncio.Semaphore(int(self.max_concurrent_tasks))
        # This inner function fetches data for a specific period 
        # while respecting the concurrency limits set by the semaphore.
        async def bound_retrieve(period: int) -> Union[dict[str, Any], list[dict[str, Any]]]:
            async with semaphore:
                return await self.retrieve_data(str(period), report_name, settlement_date)
        
        # Creating tasks for all desired periods.
        tasks = [bound_retrieve(period) for period in range(range_start, range_end + 1)]

        # Concurrently running all tasks.
        results = await asyncio.gather(*tasks)
        
        # Flattening the results.
        # Some responses might return a list of items, so we ensure they're all flattened into a single list.
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
        Retrieves BMRS data for a specific period and report asynchronously.

        Args:
            period: The specific period number for which the data needs to be fetched.
            report_name: The identifier for the specific report to be fetched.
            settlement_date: The date for which the data needs to be fetched in the format 'YYYY-MM-DD'.
            file_format: The format in which the response is expected. Can be either 'csv' or 'xml'. Default is 'xml'.

        Returns:
            A dictionary containing data for the specified period. If the data consists of multiple items, a list of 
            dictionaries is returned.
        """
        
        # Ensuring that the file format is valid.
        if file_format not in ['csv', 'xml']:
            logger.error(f"{self.__class__.__name__}:Invalid file format '{file_format}'. "
                         "Allowed values are 'csv' and 'xml'.")
            return

        # Constructing the URL.
        url = self.service_build_url.build_url(period=period,
                                               report_name=report_name,
                                               service_type=file_format,
                                               settlement_date=settlement_date)
        
        if not url: 
            return None
        
        # Setting a timeout for the request.
        timeout = ClientTimeout(total=self.timeout)
        for attempt in range(self.max_retries):
            try:
                async with ClientSession(timeout=timeout) as session:
                    response = await session.get(url)
                    
                    # If rate limited, log it, sleep for specified time, and retry.
                    if response.status == 429:
                        logger.warning(f"{self.__class__.__name__}: Rate limit hit. Sleeping for 30 seconds.")
                        await asyncio.sleep(self.rate_limit_sleep_time)
                        continue

                    # If any other non-successful HTTP status code, raise an exception.
                    response.raise_for_status()  
                    content_str = await response.text()
                    if not content_str.strip():
                        pass
                    content_data = xmltodict.parse(content_str)
                    items = content_data['response']['responseBody']['responseList']['item']
                    # Handling various types of returned data.
                    if isinstance(items, dict): 
                        return items
                    elif isinstance(items, list):
                        # If it's a list, return the last item. 
                        # Assumption: The last item is the most relevant, but this could be tailored based on requirements.
                        return items[-1]
                    else:
                        logger.error(f"{self.__class__.__name__}: Unexpected type for 'items' in XML structure.")
                        return None

            except ClientResponseError as e:
                logger.warning(f"{self.__class__.__name__}: Error on attempt {attempt + 1} - {e}.")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)  
                else:
                    logger.error(f"{self.__class__.__name__}: Max retries reached. Giving up on {url}.")
            except Exception as unexpected_e:
                if 'responseBody' not in str(unexpected_e):
                    logger.error(f"{self.__class__.__name__}: Unexpected error: {unexpected_e}")
                return
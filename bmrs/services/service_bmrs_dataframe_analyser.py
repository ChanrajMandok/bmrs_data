import pandas as pd

from bmrs.services import logger
from bmrs.decorators.decorator_report_column_headers_required import \
                                        report_column_headers_required


class ServiceBmrsDataframeAnalyser:
    
    
    @report_column_headers_required
    def __init__(self, 
                 b1770_column: str, 
                 b1780_column: str) -> None:
        # Initializing the columns for the reports B1770 and B1780
        self.b1770_column = b1770_column
        self.b1780_column = b1780_column
        
        
    def calculate_imbalances(self,
                        report_name: str,
                        report_ts_dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Print a formatted statement based on the provided report name and dataframe.

        Args:
        - report_name (str): Name of the report, either 'B1770' or 'B1780'.
        - report_ts_dataframe (pd.DataFrame): Timeseries dataframe of the report data.
        
        Logic:
        For B1770:
        - `total_daily_imbalance_cost` is computed by summing up all the values 
        under the column specified by `b1770_column`.

        For B1780:
        - First, the `sum_of_imbalances` is calculated by summing up all the values 
        under the column specified by `b1780_column`.
        - `daily_imbalance_unit_rate` is then derived by dividing the `sum_of_imbalances`
        by the number of entries (rows) in the dataframe. This gives the average
        imbalance per unit time for that day.
        """
        
        # Get the first datetime index from the DataFrame
        first_datetime_index = report_ts_dataframe.index[0]

        # Format the datetime to a pretty string ('dd-mm-yyyy')
        pretty_date = self.get_pretty_date(timestamp=first_datetime_index)

        # Handle calculations for report B1770
        if report_name == 'B1770':
            column_name = self.b1770_column
            total_daily_imbalance_cost = report_ts_dataframe[column_name].sum()
            logger.info(f"{self.__class__.__name__}: {pretty_date} total daily imbalance cost £{total_daily_imbalance_cost:.2f}")

        # Handle calculations for report B1780
        elif report_name == 'B1780':
            column_name = self.b1780_column
            sum_of_imbalances = report_ts_dataframe[column_name].sum()
            daily_imbalance_unit_rate = sum_of_imbalances / len(report_ts_dataframe)
            logger.info(f"{self.__class__.__name__}: {pretty_date} daily imbalance unit rate {daily_imbalance_unit_rate:.2f} Mwh")
            
            # Calculate absolute imbalance volumes
            self._calculate_absolute_imbalance_volumes(column=column_name,
                                                       volumes_ts_dataframe=report_ts_dataframe)
            
            return report_ts_dataframe
            
            
        else:
            logger.error(f"{self.__class__.__name__}: Invalid report name provided: {report_name}")
            return None
        
        
    def _calculate_absolute_imbalance_volumes(self,
                                              column: str,
                                              volumes_ts_dataframe: pd.DataFrame)-> pd.DataFrame:
        
        """
        Calculate and return the hour with the highest absolute imbalance volume.

        Logic:
        - The absolute value of each imbalance is computed to represent the magnitude without considering 
          direction (positive or negative).
        - The dataframe is resampled on an hourly basis, and the absolute imbalances are aggregated to provide
           the total absolute imbalance for each hour.
        - The hour with the maximum absolute imbalance is identified. This is significant as it indicates the
           period with the highest deviation from equilibrium.

        Args:
        - column (str): The name of the column in the dataframe that represents the imbalance values.
        - volumes_ts
        """
        # Calculate absolute imbalance for each entry
        volumes_ts_dataframe.loc[:, 'AbsoluteImbalance'] = volumes_ts_dataframe[column].abs()
        
        # Resample to hourly data and sum the absolute imbalances
        hourly_abs_imbalance = volumes_ts_dataframe.resample('H').sum()['AbsoluteImbalance']
        # Identify the hour with the maximum absolute imbalance
        max_hour = hourly_abs_imbalance.idxmax()
        
        pretty_date = self.get_pretty_date(timestamp=max_hour, granularity='HH')
        logger.info(f"{self.__class__.__name__}: {pretty_date} highest absolute hourly imbalance volume occured at {pretty_date}")
        
        return volumes_ts_dataframe
   
   
    def get_pretty_date(self,
                        timestamp: pd.Timestamp, 
                        granularity: str = 'DD') -> str:
        """
        Convert a timestamp into a formatted string. The granularity of the date can 
        be controlled using the 'granularity' argument.

        Args:
        - timestamp (pd.Timestamp): Timestamp to format.
        - granularity (str): Level of detail in the date. Accepts 'DD' or 'HH'. 
        'DD' returns format 'dd-mm-yyyy' and 'HH' returns 'dd-mm-yyyy hh:mm'.
        """
        
        if granularity == 'DD':
            return timestamp.strftime('%d-%m-%Y')
        elif granularity == 'HH':
            return timestamp.strftime('%d-%m-%Y %H:%M')
        else:
            raise ValueError(f"Invalid granularity provided: {granularity}. Expected 'DD' or 'HH'.")

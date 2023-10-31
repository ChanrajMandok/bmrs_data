import pandas as pd

from bmrs.converters import logger
from bmrs.decorators.decorator_report_column_headers_required import \
                                        report_column_headers_required


class ConverterDictToDataFrame:
    """
    A converter class to transform a dictionary to a pandas DataFrame object.
    """
    
    @report_column_headers_required
    def __init__(self, 
                 b1770_column: str, 
                 b1780_column: str) -> None:
        # Initializing the columns for the reports B1770 and B1780
        self.b1770_column = b1770_column
        self.b1780_column = b1780_column


    def convert(self, 
                report_name: str, 
                report_output: list[dict]) -> pd.DataFrame:
        """
        Converts the given report_output dictionary to a DataFrame.

        Args:
            report_name (str): Name of the report, either 'B1770' or 'B1780'.
            report_output (dict): Dictionary containing the report data.
        """
        try:
            # Determine the column name based on the provided report name
            if report_name == 'B1770':
                column_name = self.b1770_column
            elif report_name == 'B1780':
                column_name = self.b1780_column
            else:
                logger.error(f"{self.__class__.__name__}:Invalid report name provided: {report_name}")
                return None

            # Convert the report output list of dictionaries to a pandas DataFrame
            df = pd.DataFrame(report_output)

            # Convert the 'settlementDate' column to a datetime format
            df['settlementDate'] = pd.to_datetime(df['settlementDate'])
            # Convert the 'settlementDate' column to a datetime format
            df['settlementPeriod'] = df['settlementPeriod'].astype(int)
            
            # Calculate the actual datetime for each entry based on the settlementDate and settlementPeriod
            # The timedelta is computed using settlementPeriod. Subtracting 1 as periods start from 00:00 for 1
            df['datetime'] = df['settlementDate'] + pd.to_timedelta((df['settlementPeriod'] - 1) * 30, unit='m')
            
            # Convert the desired column (based on report name) to float type for numerical operations
            df[column_name] = df[column_name].astype(float)
            
            # Filter out and keep only the necessary columns
            output_df = df[['datetime', column_name]]
            
            # Set the computed 'datetime' column as the index for the output DataFrame
            output_df.set_index('datetime', inplace=True)
            
            # Log information regarding the size of the created time series
            logger.info(f"{self.__class__.__name__}: Time Series For {report_name} generated of length {len(output_df)}")

            return output_df
            
        except Exception as e:
            # Handle and log any unexpected errors during the conversion process
            logger.error(f"{self.__class__.__name__}: Invalid Df Operation: {report_name}")
            return None 
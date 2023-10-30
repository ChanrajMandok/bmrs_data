import pandas as pd

from bmrs.converters import logger
from bmrs.decorators.decorator_report_column_headers_required import \
                                        report_column_headers_required


class ConverterDictToDataFrame:
    """
    A converter class to transform a given dictionary to a pandas DataFrame.
    """
    
    @report_column_headers_required
    def __init__(self, 
                 b1770_column: str, 
                 b1780_column: str) -> None:
        self.b1770_column = b1770_column
        self.b1780_column = b1780_column


    def convert(self, 
                report_name: str, 
                report_output: dict) -> pd.DataFrame:
        """
        Converts the given report_output dictionary to a DataFrame.

        Args:
            report_name (str): Name of the report, either 'B1770' or 'B1780'.
            report_output (dict): Dictionary containing the report data.
        """
        try:
            # Check if the report name is one of the expected names
            if report_name == 'B1770':
                column_name = self.b1770_column
            elif report_name == 'B1780':
                column_name = self.b1780_column
            else:
                logger.error(f"{self.__class__.__name__}:Invalid report name provided: {report_name}")
                return None

            df = pd.DataFrame(report_output)

            # Convert settlementDate to datetime
            df['settlementDate'] = pd.to_datetime(df['settlementDate'])
            df['settlementPeriod'] = df['settlementPeriod'].astype(int)
            

            # Compute the timedelta based on the settlementPeriod
            # Subtracting 1 since the period starts from 00:00 for 1
            df['datetime'] = df['settlementDate'] + pd.to_timedelta((df['settlementPeriod'] - 1) * 30, unit='m')
            
            df[column_name] = df[column_name].astype(float)
            
            # Slice the DataFrame to only keep the desired columns
            output_df = df[['datetime', column_name]]
            
            # Set 'datetime' column as the index of output_df
            output_df.set_index('datetime', inplace=True)

            return output_df
        
        except Exception as e:
            logger.error(f"{self.__class__.__name__}: Invalid Df Operation: {report_name}")
            return None
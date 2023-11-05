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
        self.logger = logger
        self.b1770_column = b1770_column
        self.b1780_column = b1780_column
        
    def convert(self, 
                report_name: str, 
                report_output: list[dict]) -> pd.DataFrame:
        """
        Converts the given report_output dictionary to a DataFrame and preprocesses it.

        Args:
            report_name (str): Name of the report, either 'B1770' or 'B1780'.
            report_output (list[dict]): List of dictionaries containing the report data.
        """
        
        try:
            # Determine the column name based on the provided report name
            if report_name == 'B1770':
                column_name = self.b1770_column
            elif report_name == 'B1780':
                column_name = self.b1780_column
            else:
                logger.error(f"{self.__class__.__name__}: Invalid report name provided: {report_name}")
                return None

            # Convert the report output list of dictionaries to a pandas DataFrame
            df = pd.DataFrame(report_output)
            df['settlementDate'] = pd.to_datetime(df['settlementDate'])
            df['settlementPeriod'] = df['settlementPeriod'].astype(int)

            # Calculate the actual datetime for each entry
            df['datetime'] = df['settlementDate'] + pd.to_timedelta((df['settlementPeriod'] - 1) * 30, unit='m')

            # Convert the desired column to float type
            df[column_name] = df[column_name].astype(float)

            # Keep only the necessary columns and set datetime as the index
            output_df = df[['datetime', column_name]].set_index('datetime')

            # Sort by datetime
            output_df.sort_index(inplace=True)

            # Generate a complete range of datetimes at 30-minute intervals and reindex
            full_range = pd.date_range(start=output_df.index.min(),
                                       end=output_df.index.max(),
                                       freq='30T')
            
            missing_datetimes = full_range.difference(output_df.index)

            # Reindex only if there are missing datetime values
            if not missing_datetimes.empty:
                output_df = output_df.reindex(full_range, method='bfill')

            # Ensure all columns are numeric, convert if necessary
            for col in output_df.columns:
                output_df[col] = pd.to_numeric(output_df[col], errors='coerce')

            # Fill NaN values with forward and backward fill
            if output_df.isna().any().any():
                output_df.fillna(method='bfill', inplace=True)
            if output_df.isna().any().any():
                output_df.fillna(method='ffill', inplace=True)
                
            # Validation check for NaN values
            if output_df.isna().any().any():
                self.logger.error(f"{self.__class__.__name__}: NaN values present after preprocessing")
                return None

            self.logger.info(f"{self.__class__.__name__}: Time Series For {report_name} generated of length {len(output_df)}")
            return output_df

        except Exception as e:
            self.logger.error(f"{self.__class__.__name__}: Error in conversion: {e}")
            return None
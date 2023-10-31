import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d

from bmrs.services import logger
from bmrs.services.service_bmrs_dataframe_analyser import ServiceBmrsDataframeAnalyser


class ServicePlot:
    """
    A service to generate plots for BMRS data, focusing on imbalance metrics.
    """
    
    def __init__(self) -> None:
        self.service_bmrs_dataframe_analyser = ServiceBmrsDataframeAnalyser()
        
    def plot(self, 
             report_name: str,
             plot_dataframe: pd.DataFrame) -> None:
        """
        Plot the provided dataframe column against a datetime index.

        Parameters:
            report_name (str): The name of the BMRS report being plotted.
            plot_dataframe (pd.DataFrame): The dataframe containing the data to be plotted.
        """
        
        # Get the first datetime index from the DataFrame
        first_datetime_index = plot_dataframe.index[0]

        # Format the datetime to a pretty string ('dd-mm-yyyy')
        pretty_date = self.service_bmrs_dataframe_analyser.get_pretty_date(\
                                                        timestamp=first_datetime_index)
        
        # Determine the title and column name based on the report type
        if report_name == 'B1770':
            title = f"{pretty_date}: {report_name} Bi-Hourly Imbalance Cost (GBP) "
            column_name = 'Imbalance Cost (GBP)'
        elif report_name == 'B1780':
            title = f"{pretty_date}: {report_name} Bi-Hourly Imbalance rate (MWh) "
            column_name = 'Imbalance rate (MWh)'
        else:
            logger.error(f"{self.__class__.__name__}:Invalid report name provided: {report_name}")
            return None
        
        # Initialize the plot with a defined size
        fig, ax = plt.subplots(figsize=(10,6))
        ax.set_facecolor('#f5f5f5')
        
        # Apply a Gaussian filter to smooth the plotted data
        col = plot_dataframe.columns[0]
        y_smoothed = gaussian_filter1d(plot_dataframe[col], sigma=1)
        ax.plot(plot_dataframe.index, y_smoothed, label=column_name)
        
        # Plot the mean value of the column as a dashed red line
        mean_value = plot_dataframe[col].mean()
        ax.axhline(mean_value, color='red', linestyle='--', label='Mean')
        
        # Plot the mean value of the column as a dashed red line
        plt.title(title)
        plt.xlabel('Datetime')
        plt.ylabel(column_name)
        ax.grid(True, which='both', linestyle='--', linewidth=0.1, alpha=0.6) 
        ax.minorticks_on()
        
        # Add a legend for plot details
        plt.legend(loc='upper left')
        
        # Format x-axis datetime for better visualization and readability
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.gcf().autofmt_xdate()

        # Finalize the layout and display the plot
        plt.tight_layout()
        logger.info(f"{self.__class__.__name__}: Plot Generated. Please close the plot window to continue.")
        plt.show(block=True)

    def _clean_column_name(self, col: str) -> str:
        """Clean and format the column name for presentation."""
        return col.replace("_", " ").title()